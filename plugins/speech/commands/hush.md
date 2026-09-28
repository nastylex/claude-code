---
description: Toggle voice narration of SirGent's responses on or off
argument-hint: "[on|off]"
allowed-tools: Bash(test:*), Bash(mkdir:*), Bash(rm:*)
---

# /hush — mute or unmute voice narration

**Argument:** $ARGUMENTS

The speech plugin narrates SirGent's final responses through a Stop hook. It
is controlled by the `SPEECH_DISABLE` environment variable and a local flag
file this command manages.

## Behaviour

1. If the argument (case-insensitive) is `off`, create the flag file:
   `mkdir -p ~/.sirgent && touch ~/.sirgent/speech-disabled`
   Then confirm: "🔇 Voice narration muted. Run `/hush on` to unmute."
2. If the argument (case-insensitive) is `on`, delete it:
   `rm -f ~/.sirgent/speech-disabled`
   Then confirm: "🔊 Voice narration enabled. SirGent will speak responses
   aloud (requires ELEVENLABS_API_KEY)."
3. With no argument: check whether `~/.sirgent/speech-disabled` exists
   (`test -f ~/.sirgent/speech-disabled && echo muted || echo unmuted`) and
   report the current state, plus a reminder of the on/off usage.
4. Treat any other value as invalid: show usage `/hush [on|off]` and stop.

Note for the user: muting here only affects this machine's flag file; the
hook also honours `SPEECH_DISABLE=1` and an unset `ELEVENLABS_API_KEY`
(always silent). The Stop hook script checks the same flag file path, so
`/hush off` wins even when the API key is configured.
