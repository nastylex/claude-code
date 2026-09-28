---
description: Speak a message aloud through ElevenLabs text-to-speech
argument-hint: "[text to speak]"
allowed-tools: Bash(python3:*), Bash(python:*), Bash(afplay:*), Bash(mpv:*), Bash(ffplay:*), Bash(powershell:*)
---

# /speak — voice narration

Convert the user's text to speech with the ElevenLabs TTS API and play it.

**Text to speak:** $ARGUMENTS

If no text was provided, ask the user what they'd like spoken and stop.

## Steps

1. Check that the `ELEVENLABS_API_KEY` environment variable is set (run
   `test -n "$ELEVENLABS_API_KEY" && echo set || echo missing`). If missing,
   tell the user to add it in Settings → Environment (or export it in their
   shell) and stop — do not attempt the call without a key.
2. Write the text to a temporary file `speech-input.txt` (one line, no
   markdown) using a heredoc so quoting survives.
3. Call the TTS API and save MP3 output to `sirgent-speech.mp3`:

   ```bash
   curl -sS --fail-with-body https://api.elevenlabs.io/v1/text-to-speech/21m00Tcm4TlvDq8ikWAM \
     -H "xi-api-key: $ELEVENLABS_API_KEY" \
     -H "Content-Type: application/json" \
     -H "Accept: audio/mpeg" \
     -d "{\"text\": \"$(cat speech-input.txt)\", \"model_id\": \"eleven_multilingual_v2\"}" \
     -o sirgent-speech.mp3
   ```

   Replace the voice ID in the URL with `$ELEVENLABS_VOICE_ID` when set.
4. Play the audio with the first available player for the platform:
   - macOS: `afplay sirgent-speech.mp3`
   - Linux: `mpv --no-video --really-quiet sirgent-speech.mp3`
     (or `ffplay -nodisp -autoexit -loglevel quiet sirgent-speech.mp3`)
   - Windows: `powershell -c "(New-Object Media.SoundPlayer 'sirgent-speech.mp3').PlaySync()"`
5. Delete `speech-input.txt` and `sirgent-speech.mp3` afterwards.
6. Report success or, if the API returned an error, show its message and
   suggest checking the API key, voice ID, and quota.

Do not read or print the API key itself at any point.
