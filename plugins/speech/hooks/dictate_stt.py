#!/usr/bin/env python3
"""
Speech plugin for SirGent AI — dictation bridge (speech → text).

Records a short clip from the default microphone, transcribes it with the
ElevenLabs speech-to-text API, and prints the recognized words to stdout as
plain text. Designed to be called by the /dictate command so spoken words
flow into the prompt like typed text.

Output contract (for the calling command):
- recognized words  -> stdout, plain text, nothing else
- empty recording   -> prints nothing (caller falls back to asking the user)
- any error         -> a single line starting with "speech:" on stderr,
                       exit code 1 (caller surfaces it and stops gracefully)

Configuration (environment variables):
- ELEVENLABS_API_KEY   Required. https://elevenlabs.io
- SPEECH_STT_MODEL     STT model id. Default: scribe_v1
- SPEECH_DICTATE_SECS  Max recording length in seconds. Default: 15
- SPEECH_AUDIO_DIR     Temp audio directory. Default: system temp
"""

import json
import mimetypes
import os
import shutil
import subprocess
import sys
import tempfile
import uuid
from pathlib import Path

STT_URL = "https://api.elevenlabs.io/v1/speech-to-text"
DEFAULT_STT_MODEL = "scribe_v1"
DICTATE_SECS_DEFAULT = 15


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


def has_recorder() -> bool:
    return bool(shutil.which("sox") or shutil.which("arecord") or shutil.which("ffmpeg"))


def transcribe(wav_path: Path, api_key: str) -> str:
    """POST a WAV recording to ElevenLabs speech-to-text; return the text."""
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
        print(f"speech: STT HTTP {exc.code}: {detail}", file=sys.stderr)
        return ""
    except (urllib.error.URLError, OSError, TimeoutError, ValueError) as exc:
        print(f"speech: STT request failed: {exc}", file=sys.stderr)
        return ""


def main() -> None:
    api_key = os.environ.get("ELEVENLABS_API_KEY", "").strip()
    if not api_key:
        print("speech: set ELEVENLABS_API_KEY to use dictation (https://elevenlabs.io)",
              file=sys.stderr)
        sys.exit(1)

    if not has_recorder():
        print("speech: no mic recorder found. Install sox (recommended), arecord, "
              "or ffmpeg, then retry.", file=sys.stderr)
        sys.exit(1)

    max_secs = int(os.environ.get("SPEECH_DICTATE_SECS", DICTATE_SECS_DEFAULT))
    audio_dir = Path(os.environ.get("SPEECH_AUDIO_DIR", tempfile.gettempdir())) / "sirgent-speech"
    try:
        audio_dir.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        print(f"speech: {exc}", file=sys.stderr)
        sys.exit(1)

    wav_path = audio_dir / "dictate.wav"
    try:
        wav_path.unlink(missing_ok=True)
    except OSError:
        pass

    cmd = recorder_command(wav_path, max_secs)
    try:
        proc = subprocess.run(cmd, stdout=subprocess.DEVNULL,
                              stderr=subprocess.DEVNULL, timeout=max_secs + 10)
    except (OSError, subprocess.TimeoutExpired):
        print("speech: recording failed or timed out.", file=sys.stderr)
        sys.exit(1)

    if not wav_path.exists() or wav_path.stat().st_size == 0:
        print("speech: recording produced no audio. Check your microphone.", file=sys.stderr)
        sys.exit(1)

    text = transcribe(wav_path, api_key)
    try:
        wav_path.unlink(missing_ok=True)
    except OSError:
        pass

    if not text:
        # transcribe() already reported the reason on stderr
        sys.exit(1)

    print(text)
    sys.exit(0)


if __name__ == "__main__":
    main()
