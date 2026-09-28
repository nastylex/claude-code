---
description: Toggle two-way voice conversation (talk over responses; SirGent hears you)
argument-hint: "[on|off]"
allowed-tools: Bash(test:*), Bash(mkdir:*), Bash(rm:*)
---

# /voice — two-way conversation mode

**Argument:** $ARGUMENTS

Two-way mode lets you interrupt SirGent's spoken responses by talking over
them (barge-in) and have your words transcribed and answered. The
interruption floor is deliberately extreme — **150 dB-equivalent by default**
— so ordinary background noise can never trigger it; only a sustained, very
loud signal (a genuine shout toward the mic) does.

## Behaviour

1. If the argument (case-insensitive) is `on`, create the flag file:
   `mkdir -p ~/.sirgent && touch ~/.sirgent/speech-conversation`
   Then confirm: "🎙️ Two-way voice ON. Talk over a response — loudly — to
   interrupt; your words are transcribed and answered. Requires a working
   `sox` or `arecord`/`ffmpeg` mic recorder. Floor: 150 dB-equivalent
   (raise with SPEECH_BARGE_IN_DB)."
2. If the argument (case-insensitive) is `off`, delete it:
   `rm -f ~/.sirgent/speech-conversation`
   Then confirm: "🔇 Two-way voice OFF. Responses are narrated; the mic is
   not monitored."
3. With no argument: check state with
   `test -f ~/.sirgent/speech-conversation && echo on || echo off`
   and report it plus current usage.
4. Any other value: show usage `/voice [on|off]` and stop.

## Notes

- The Stop hook honours `SPEECH_CONVERSATION=1` as well; the flag file wins
  so `/voice off` always silences monitoring immediately.
- Recording needs a local recorder: `sox`, `arecord` (ALSA), or `ffmpeg`
  (macOS avfoundation). Transcription reuses `ELEVENLABS_API_KEY`
  (scribe model, override with `SPEECH_STT_MODEL`).
- Max reply length is `SPEECH_REPLY_SECS` (default 12 s).
