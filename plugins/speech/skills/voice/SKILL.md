---
name: sirgent-voice
description: Narrate content aloud with text-to-speech. Use when the user asks to speak, say, or read aloud a message, summary, or response, or asks how voice output is configured.
---

# SirGent voice (text-to-speech)

Narrate text aloud through the ElevenLabs TTS API. This skill backs the
`/speak` command and the Stop-hook narrator in the speech plugin.

## When to use

- The user says "say that out loud", "read it to me", "speak it"
- The user asks for a spoken summary of a response or document
- The user asks how voice narration works or how to configure it

## Requirements

- `ELEVENLABS_API_KEY` environment variable (get one at https://elevenlabs.io)
- Optional: `ELEVENLABS_VOICE_ID` (default voice: "Rachel",
  `21m00Tcm4TlvDq8ikWAM`), `ELEVENLABS_MODEL_ID`
  (default `eleven_multilingual_v2`)
- A local audio player: `afplay` (macOS), `mpv`/`ffplay` (Linux),
  PowerShell `Media.SoundPlayer` (Windows)

If the API key is missing, tell the user to add it (Settings → Environment or
shell export) rather than failing silently.

## Preparing text to speak

1. Strip markdown: remove code fences, inline code backticks, images, table
   pipes, and heading marks; keep link text without the URL.
2. Collapse whitespace into single spaces.
3. Cap at roughly 400 characters (about 25 seconds of speech) — end at a
   sentence boundary when possible. Long output should be summarized, not
   truncated mid-word.

## Calling the API

```bash
curl -sS --fail-with-body \
  "https://api.elevenlabs.io/v1/text-to-speech/${ELEVENLABS_VOICE_ID:-21m00Tcm4TlvDq8ikWAM}" \
  -H "xi-api-key: $ELEVENLABS_API_KEY" \
  -H "Content-Type: application/json" \
  -H "Accept: audio/mpeg" \
  -d '{"text": "PREPARED_TEXT_HERE", "model_id": "eleven_multilingual_v2"}' \
  -o sirgent-speech.mp3
```

Errors surface as non-zero exit or an HTTP error body: check the key first,
then the voice ID, then plan quota.

## Playing audio

Pick the first available player for the platform:

| Platform | Command |
|---|---|
| macOS | `afplay sirgent-speech.mp3` |
| Linux | `mpv --no-video --really-quiet sirgent-speech.mp3` |
| Linux (fallback) | `ffplay -nodisp -autoexit -loglevel quiet sirgent-speech.mp3` |
| Windows | `powershell -c "(New-Object Media.SoundPlayer 'sirgent-speech.mp3').PlaySync()"` |

Clean up the MP3 after playback. Never print or echo the API key.

## Muting

The Stop-hook narrator honours three silences, checked in order:
`SPEECH_DISABLE=1`, a missing `ELEVENLABS_API_KEY`, and the flag file
`~/.sirgent/speech-disabled` (toggled by the `/hush` command).
