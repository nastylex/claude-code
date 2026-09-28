---
description: Dictate a prompt by voice — record, transcribe with ElevenLabs STT, and send as your message
argument-hint: "[optional context for what to dictate]"
allowed-tools: Bash(python3:*), Bash(python:*), Bash(sox:*), Bash(arecord:*), Bash(ffmpeg:*), Bash(test:*), Bash(rm:*)
---

# /dictate — voice input (speech → prompt)

**Argument:** $ARGUMENTS

Records your voice from the default microphone, transcribes it with the
ElevenLabs speech-to-text API, and delivers the recognized words as your
prompt to SirGent. This is the input side of the speech plugin: `/speak`
is SirGent's voice, `/dictate` is yours.

## Steps

1. Check prerequisites in one command each:
   - `test -n "$ELEVENLABS_API_KEY" && echo set || echo missing` — if
     missing, tell the user to add it (Settings → Environment or shell
     export) and stop.
   - `command -v sox || command -v arecord || command -v ffmpeg` — if none
     exist, tell the user to install `sox` (recommended, all platforms) and
     stop. Do not attempt to record without a recorder.
2. Confirm to the user: "🎙️ Listening for up to 15 seconds — speak now…"
   (length is `SPEECH_DICTATE_SECS`, default 15).
3. Run the dictation bridge exactly once:

   ```bash
   python3 "${SIRGENT_PLUGIN_ROOT}/hooks/dictate_stt.py"
   ```

   - stdout = recognized words (plain text)
   - stderr lines starting with `speech:` = the reason it failed
   - exit 1 = no recording or transcription failed
4. On success: take the printed text as the user's message. If `$ARGUMENTS`
   was provided, treat it as context and present the dictation as:
   the dictated text, framed by the argument's intent (e.g. argument
   "refactor plan" + dictation "split the parser module" → the user's
   request is to refactor per the dictated detail). Then act on the request
   as if the user had typed it.
5. If the bridge printed nothing but exited 0 (empty recording): tell the
   user nothing was heard and suggest checking mic input levels.
6. On failure (exit 1): show the `speech:` stderr line verbatim and stop.
   Common causes: missing API key, no recorder, no mic audio, HTTP quota.
7. Never read, print, or echo the API key. Never fabricate dictation
   content — if transcription failed, say so.

## Notes

- Requires `ELEVENLABS_API_KEY` and a recorder: `sox`, `arecord` (ALSA), or
  `ffmpeg` (macOS avfoundation).
- Tune `SPEECH_DICTATE_SECS` for longer dictations; `SPEECH_STT_MODEL`
  overrides the STT model (default `scribe_v1`).
- Pair with `/voice on` for full two-way voice: SirGent speaks responses,
  you dictate replies.
