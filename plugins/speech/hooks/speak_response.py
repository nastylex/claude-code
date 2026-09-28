#!/usr/bin/env python3
"""
Speech plugin for SirGent AI — Stop hook narrator with two-way voice.

Reads SirGent's final response from the Stop hook stdin payload, distills it
into a short spoken summary, converts it to speech with the ElevenLabs
text-to-speech API, and plays the audio in the background. While it plays,
the microphone is monitored: the user can talk over the response (barge-in),
which lowers the playback and records their reply. The reply is transcribed
with the ElevenLabs speech-to-text API and, in conversation mode, fed back to
SirGent by blocking the stop with the transcribed words as the reason.

Barge-in detection (the "150 dB" gate):
    Playback only yields to the microphone when the incoming level exceeds
    SPEECH_BARGE_IN_DB, expressed as an SPL-equivalent level derived from the
    mic's RMS energy. The default floor is 150 — deliberately extreme, so
    ordinary background noise (music down the hall, a fan, typing, traffic,
    speech at conversational volume) can never interrupt a response. Only a
    sustained, very loud signal counts. Raise the floor to make interruption
    harder, lower it (carefully) to make it easier.

Configuration (environment variables):
- ELEVENLABS_API_KEY      Required. https://elevenlabs.io
- ELEVENLABS_VOICE_ID     Voice for TTS. Default: 21m00Tcm4TlvDq8ikWAM ("Rachel")
- ELEVENLABS_MODEL_ID     TTS model. Default: eleven_multilingual_v2
- SPEECH_MAX_CHARS        Truncate narration at N characters. Default: 400
- SPEECH_DISABLE          "1" fully disables the plugin
- SPEECH_AUDIO_DIR        Audio cache directory. Default: system temp
- SPEECH_CONVERSATION     "1" enables two-way voice (barge-in + spoken reply
                          is fed back to SirGent). Default: off
- SPEECH_BARGE_IN_DB      SPL-equivalent floor for interruption. Default: 150
- SPEECH_REPLY_SECS       Max seconds to record a spoken reply. Default: 12
- SPEECH_STT_MODEL        STT model id. Default:scribe_v1

Kill-switch behaviour: with SPEECH_DISABLE=1 or no API key, the hook exits 0
silently so the session is never blocked.
"""

import json
import math
import os
import re
import shutil
import subprocess
import sys
import tempfile
import threading
import time
import uuid
import wave
from pathlib import Path

API_URL = "https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
STT_URL = "https://api.elevenlabs.io/v1/speech-to-text"

DEFAULT_VOICE_ID = "21m00Tcm4TlvDq8ikWAM"  # "Rachel"
DEFAULT_MODEL_ID = "eleven_multilingual_v2"
DEFAULT_STT_MODEL = "scribe_v1"

# Reference RMS (16-bit full scale) treated as 194 dB SPL-equivalent.
# dBSPL = 20*log10(rms / REF_RMS) + 194, clamped so silence -> -inf.
REF_RMS = 1.0 / 32768.0
FULL_SCALE_DB = 194.0

BARGE_IN_DB_DEFAULT = 150.0
REPLY_SECS_DEFAULT = 12

# Markdown and noise that should never be spoken aloud
MD_PATTERNS = [
    re.compile(r"```.*?```", re.DOTALL),           # fenced code blocks
    re.compile(r"`[^`\n]+`"),                      # inline code
    re.compile(r"!\[[^\]]*\]\([^)]*\)"),           # images
    re.compile(r"\[([^\]]+)\]\([^)]*\)"),          # links -> keep text
    re.compile(r"^\s{0,3}#{1,6}\s+", re.MULTILINE),  # headings
    re.compile(r"^\s*[-*+]\s+", re.MULTILINE),     # bullets
    re.compile(r"\|"),                             # table pipes
    re.compile(r"^---+\s*$", re.MULTILINE),        # hrules
]

MAX_CHARS_DEFAULT = 400


def env_flag(name: str) -> bool:
    return os.environ.get(name, "").strip() == "1"


def clean_for_speech(text: str) -> str:
    """Strip markdown/noise and collapse whitespace so text reads naturally."""
    for pattern in MD_PATTERNS:
        text = pattern.sub(" " if pattern.pattern != r"\[([^\]]+)\]\([^)]*\)" else r"\1", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def summarize(text: str, limit: int) -> str:
    """Trim to the last complete sentence that fits the limit."""
    if len(text) <= limit:
        return text
    clipped = text[:limit]
    # Prefer cutting at sentence end; fall back to word boundary.
    for sep in (". ", "! ", "? ", " "):
        idx = clipped.rfind(sep)
        if idx > limit * 0.4:
            return clipped[: idx + 1].strip()
    return clipped.strip()


def extract_response(payload: dict) -> str:
    """Pull the transcript's final assistant message out of the Stop payload."""
    transcript = payload.get("transcript_path")
    messages = []
    if transcript and os.path.exists(transcript):
        try:
            with open(transcript, "r", encoding="utf-8", errors="replace") as fh:
                for line in fh:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        entry = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    if entry.get("type") == "assistant":
                        msg = entry.get("message") or {}
                        content = msg.get("content")
                        if isinstance(content, str):
                            messages.append(content)
                        elif isinstance(content, list):
                            for block in content:
                                if isinstance(block, dict) and block.get("type") == "text":
                                    messages.append(block.get("text", ""))
        except OSError:
            pass
    if not messages:
        # Fallback: hook payloads may carry last_message directly.
        messages = [payload.get("last_message") or payload.get("stop_hook_active") and "" or ""]
    return messages[-1] if messages else ""


def synthesize(text: str, api_key: str, out_path: Path) -> bool:
    """POST to ElevenLabs TTS and write MP3 bytes. Returns True on success."""
    import urllib.error
    import urllib.request

    voice_id = os.environ.get("ELEVENLABS_VOICE_ID", DEFAULT_VOICE_ID)
    model_id = os.environ.get("ELEVENLABS_MODEL_ID", DEFAULT_MODEL_ID)
    url = API_URL.format(voice_id=voice_id)
    body = json.dumps({
        "text": text,
        "model_id": model_id,
        "voice_settings": {"stability": 0.5, "similarity_boost": 0.75},
    }).encode("utf-8")

    req = urllib.request.Request(url, data=body, method="POST", headers={
        "xi-api-key": api_key,
        "Content-Type": "application/json",
        "Accept": "audio/mpeg",
    })
    try:
        with urllib.request.urlopen(req, timeout=45) as resp:
            out_path.write_bytes(resp.read())
        return out_path.stat().st_size > 0
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", "replace")[:200]
        print(json.dumps({"systemMessage": f"speech: ElevenLabs HTTP {exc.code}: {detail}"}))
        return False
    except (urllib.error.URLError, OSError, TimeoutError) as exc:
        print(json.dumps({"systemMessage": f"speech: TTS request failed: {exc}"}))
        return False


def transcribe(wav_path: Path, api_key: str) -> str:
    """POST a WAV recording to ElevenLabs speech-to-text; return the text."""
    import mimetypes
    import urllib.error
    import urllib.request

    boundary = uuid.uuid4().hex
    model = os.environ.get("SPEECH_STT_MODEL", DEFAULT_STT_MODEL)
    mime = mimetypes.guess_type(str(wav_path))[0] or "audio/wav"
    payload = wav_path.read_bytes()

    parts = []
    for name, value in (("model_id", model), ("diarize", "false")):
        parts.append(
            f'--{boundary}\r\nContent-Disposition: form-data; name="{name}"'
            f"\r\n\r\n{value}\r\n".encode("utf-8")
        )
    parts.append(
        (
            f"--{boundary}\r\n"
            f'Content-Disposition: form-data; name="file"; filename="{wav_path.name}"\r\n'
            f"Content-Type: {mime}\r\n\r\n"
        ).encode("utf-8")
        + payload
        + b"\r\n"
    )
    parts.append(f"--{boundary}--\r\n".encode("utf-8"))
    body = b"".join(parts)

    req = urllib.request.Request(STT_URL, data=body, method="POST", headers={
        "xi-api-key": api_key,
        "Content-Type": f"multipart/form-data; boundary={boundary}",
        "Accept": "application/json",
    })
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.loads(resp.read().decode("utf-8", "replace"))
        return str(data.get("text", "")).strip()
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", "replace")[:200]
        print(json.dumps({"systemMessage": f"speech: STT HTTP {exc.code}: {detail}"}))
        return ""
    except (urllib.error.URLError, OSError, TimeoutError, ValueError) as exc:
        print(json.dumps({"systemMessage": f"speech: STT request failed: {exc}"}))
        return ""


def player_commands(mp3: Path) -> list:
    """Ordered player candidates for the current platform."""
    plat = sys.platform
    if plat == "darwin":
        return [["afplay", str(mp3)]]
    if plat.startswith("win"):
        ps = (
            "(New-Object Media.SoundPlayer "
            f"'{mp3}').PlaySync()"
        )
        return [["powershell", "-NoProfile", "-Command", ps]]
    # Linux & friends: try the common CLI players. mpv/ffplay handle MP3 best.
    return [
        ["mpv", "--no-video", "--really-quiet", str(mp3)],
        ["ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet", str(mp3)],
        ["paplay", str(mp3)],
        ["aplay", str(mp3)],
        ["play", str(mp3)],
    ]


# ---------------------------------------------------------------------------
# Microphone monitoring and barge-in
# ---------------------------------------------------------------------------

def recorder_command(wav_path: Path, max_secs: int) -> list:
    """First available recorder, writing 16 kHz mono WAV for STT."""
    for cmd in (
        ["sox", "-d", "-q", "-r", "16000", "-c", "1", "-b", "16", str(wav_path),
         "trim", "0", str(max_secs)],
        ["arecord", "-q", "-f", "S16_LE", "-r", "16000", "-c", "1",
         "-d", str(max_secs), str(wav_path)],
        ["ffmpeg", "-y", "-loglevel", "quiet", "-f", "avfoundation", "-i", ":0",
         "-t", str(max_secs), "-ar", "16000", "-ac", "1", str(wav_path)],
    ):
        if shutil.which(cmd[0]):
            return cmd
    return []


def wav_rms(wav_path: Path, chunk_ms: int = 100) -> list:
    """RMS energy per chunk from a 16-bit mono WAV. Empty list on failure."""
    try:
        with wave.open(str(wav_path), "rb") as wf:
            if wf.getsampwidth() != 2 or wf.getnchannels() != 1:
                return []
            rate = wf.getframerate() or 16000
            chunk_frames = max(1, rate * chunk_ms // 1000)
            out = []
            while True:
                frames = wf.readframes(chunk_frames)
                if not frames:
                    break
                n = len(frames) // 2
                if n == 0:
                    continue
                acc = 0
                for i in range(0, len(frames) - 1, 2):
                    sample = frames[i] | (frames[i + 1] << 8)
                    if sample >= 32768:
                        sample -= 65536
                    acc += sample * sample
                out.append(math.sqrt(acc / n))
            return out
    except (OSError, wave.Error):
        return []


def rms_to_db(rms: float) -> float:
    """Map a 16-bit RMS sample to an SPL-equivalent dB value."""
    if rms <= 0:
        return -999.0
    return 20.0 * math.log10(rms / REF_RMS)


def listen_for_barge_in(proc, stop_event: threading.Event, floor_db: float,
                        reply_wav: Path, max_secs: int) -> str:
    """Watch a running playback process; on a loud-enough signal, kill it,
    record the user's reply, and return 'reply' | 'completed' | 'quiet'."""
    reply_cmd = recorder_command(reply_wav, max_secs)
    loud_streak = 0
    poll = 0.1
    while True:
        if proc.poll() is not None:
            # Playback finished on its own. If conversation mode is on, still
            # give the user a moment to start talking (half a second of
            # grace), then close the floor: nothing recorded.
            if reply_cmd and env_flag("SPEECH_CONVERSATION"):
                time.sleep(0.5)
                break
            return "completed"
        if stop_event.is_set():
            return "completed"
        # No barge-in hardware available: let playback run to completion.
        if not reply_cmd:
            time.sleep(poll)
            continue
        # Probe the mic briefly; a level above the floor counts. The default
        # 150 dB floor is intentionally extreme: everyday background noise
        # stays far below it, so only a genuine shout over the speakers
        # interrupts playback.
        probe = reply_wav.with_name(reply_wav.stem + "-probe.wav")
        try:
            probe.unlink(missing_ok=True)
        except OSError:
            pass
        probe_cmd = recorder_command(probe, 1)
        if not probe_cmd:
            time.sleep(poll)
            continue
        try:
            subprocess.run(probe_cmd, stdout=subprocess.DEVNULL,
                           stderr=subprocess.DEVNULL, timeout=3)
        except (OSError, subprocess.TimeoutExpired):
            continue
        levels = [rms_to_db(v) for v in wav_rms(probe)]
        try:
            probe.unlink(missing_ok=True)
        except OSError:
            pass
        if levels and max(levels) >= floor_db:
            loud_streak += 1
            if loud_streak >= 2:  # ~2 s of sustained loudness
                # Kill playback (lower it out of the way) and record the reply.
                try:
                    proc.terminate()
                    proc.wait(timeout=5)
                except Exception:
                    pass
                try:
                    subprocess.run(reply_cmd, stdout=subprocess.DEVNULL,
                                   stderr=subprocess.DEVNULL, timeout=max_secs + 10)
                except (OSError, subprocess.TimeoutExpired):
                    pass
                return "reply"
        else:
            loud_streak = 0
    return "quiet"


def play_with_barge_in(mp3: Path, reply_wav: Path) -> str:
    """Play MP3 in the background while watching the mic for barge-in.

    Returns 'reply' if the user interrupted and a reply was recorded,
    'completed' if playback ran to completion, 'quiet' otherwise.
    """
    floor_db = float(os.environ.get("SPEECH_BARGE_IN_DB", BARGE_IN_DB_DEFAULT))
    max_secs = int(os.environ.get("SPEECH_REPLY_SECS", REPLY_SECS_DEFAULT))

    chosen = None
    for cmd in player_commands(mp3):
        if shutil.which(cmd[0]) or cmd[0] == "powershell":
            chosen = cmd
            break
    if not chosen:
        print(json.dumps({
            "systemMessage": (
                "speech: generated audio but found no player. "
                "Install mpv or ffplay, then retry."
            )
        }))
        return "quiet"

    stop_event = threading.Event()
    try:
        proc = subprocess.Popen(
            chosen, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
    except OSError:
        return "quiet"

    outcome = listen_for_barge_in(proc, stop_event, floor_db, reply_wav, max_secs)
    stop_event.set()
    if proc.poll() is None:
        try:
            proc.terminate()
            proc.wait(timeout=5)
        except Exception:
            pass
    return outcome


def play(mp3: Path) -> bool:
    """Simple synchronous playback (no mic monitoring)."""
    for cmd in player_commands(mp3):
        if not (shutil.which(cmd[0]) or cmd[0] == "powershell"):
            continue
        try:
            proc = subprocess.run(
                cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=120
            )
            if proc.returncode == 0:
                return True
        except (OSError, subprocess.TimeoutExpired):
            continue
    return False


def main() -> None:
    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError:
        payload = {}

    if env_flag("SPEECH_DISABLE"):
        sys.exit(0)

    api_key = os.environ.get("ELEVENLABS_API_KEY", "").strip()
    if not api_key:
        # First-run hint, once, then stay quiet.
        marker = Path(tempfile.gettempdir()) / "sirgent-speech-hint"
        if not marker.exists():
            try:
                marker.write_text("1", encoding="utf-8")
            except OSError:
                pass
            print(json.dumps({
                "systemMessage": (
                    "speech plugin: set ELEVENLABS_API_KEY to enable voice "
                    "narration of responses (https://elevenlabs.io). "
                    "Set SPEECH_DISABLE=1 to hide this hint."
                )
            }))
        sys.exit(0)

    raw = extract_response(payload)
    if not raw.strip():
        sys.exit(0)

    spoken = summarize(clean_for_speech(raw), int(os.environ.get("SPEECH_MAX_CHARS", MAX_CHARS_DEFAULT)))
    if not spoken:
        sys.exit(0)

    audio_dir = Path(os.environ.get("SPEECH_AUDIO_DIR", tempfile.gettempdir())) / "sirgent-speech"
    reply_wav = audio_dir / "reply.wav"

    mp3 = audio_dir / "response.mp3"
    try:
        audio_dir.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        print(json.dumps({"systemMessage": f"speech: {exc}"}))
        sys.exit(0)
    if not synthesize(spoken, api_key, mp3):
        sys.exit(0)

    conversation = env_flag("SPEECH_CONVERSATION")
    if not conversation:
        # /voice writes this flag file; it wins over the env var when present.
        flag = Path.home() / ".sirgent" / "speech-conversation"
        conversation = flag.exists()
    if conversation:
        outcome = play_with_barge_in(mp3, reply_wav)
        if outcome == "reply" and reply_wav.exists():
            heard = transcribe(reply_wav, api_key)
            try:
                reply_wav.unlink(missing_ok=True)
            except OSError:
                pass
            if heard:
                # Two-way voice: stop the turn and hand SirGent the user's
                # spoken words as the next instruction. This is the Stop
                # hook contract for forcing continuation.
                print(json.dumps({
                    "decision": "block",
                    "reason": (
                        f"The user interrupted your spoken response and said "
                        f"this out loud (transcribed): \"{heard}\" — respond "
                        f"to it now."
                    ),
                }))
                sys.exit(0)
        sys.exit(0)

    play(mp3)
    sys.exit(0)


if __name__ == "__main__":
    main()
