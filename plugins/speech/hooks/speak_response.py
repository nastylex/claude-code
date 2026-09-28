#!/usr/bin/env python3
"""
Speech plugin for SirGent AI — Stop hook narrator.

Reads SirGent's final response from the Stop hook stdin payload, distills it
into a short spoken summary, converts it to speech with the ElevenLabs
text-to-speech API, and plays the audio through whatever player the platform
offers (afplay on macOS, mpv/ffplay/paplay/aplay on Linux, PowerShell
Win32 SoundPlayer on Windows).

Configuration (environment variables):
- ELEVENLABS_API_KEY   Required for cloud TTS. Get one at https://elevenlabs.io
- ELEVENLABS_VOICE_ID  Voice to use. Default: 21m00Tcm4TlvDq8ikWAM ("Rachel")
- ELEVENLABS_MODEL_ID  Model. Default: eleven_multilingual_v2
- SPEECH_MAX_CHARS     Truncate narration at N characters. Default: 400
- SPEECH_DISABLE       "1" fully disables the plugin
- SPEECH_AUDIO_DIR     Where to cache audio files. Default: system temp

Kill-switch behaviour: with SPEECH_DISABLE=1 or no API key, the hook exits 0
silently so the session is never blocked.
"""

import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

API_URL = "https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"

DEFAULT_VOICE_ID = "21m00Tcm4TlvDq8ikWAM"  # "Rachel"
DEFAULT_MODEL_ID = "eleven_multilingual_v2"

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


def play(mp3: Path) -> bool:
    for cmd in player_commands(mp3):
        try:
            proc = subprocess.run(
                cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=120
            )
            if proc.returncode == 0:
                return True
        except (OSError, subprocess.TimeoutExpired):
            continue
    print(json.dumps({
        "systemMessage": (
            "speech: generated audio but found no player. "
            "Install mpv or ffplay, then retry."
        )
    }))
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
    try:
        audio_dir.mkdir(parents=True, exist_ok=True)
        mp3 = audio_dir / "response.mp3"
        if synthesize(spoken, api_key, mp3) and play(mp3):
            sys.exit(0)
    except OSError as exc:
        print(json.dumps({"systemMessage": f"speech: {exc}"}))
    sys.exit(0)


if __name__ == "__main__":
    main()
