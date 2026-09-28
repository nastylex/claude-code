# speech

Speech capabilities for SirGent AI: voice narration of responses through
ElevenLabs text-to-speech, voice dictation into your prompts through
ElevenLabs speech-to-text, an on-demand `/speak` command, a `/hush` mute
toggle, and a `/dictate` command for voice input.

## What it does

| Piece | Where | What happens |
| --- | --- | --- |
| Stop hook narrator | `hooks/speak_response.py` | When SirGent finishes a turn, the final assistant message is distilled (markdown stripped, capped at ~400 chars), converted to MP3 with ElevenLabs TTS, and played through the platform's audio player. |
| `/speak` command | `commands/speak.md` | Speak any text the user supplies, on demand. |
| `/hush` command | `commands/hush.md` | Mute/unmute the Stop-hook narrator with a flag file (`~/.sirgent/speech-disabled`). |
| `/dictate` command | `commands/dictate.md` + `hooks/dictate_stt.py` | Voice input: record from the default mic, transcribe with ElevenLabs STT, and deliver the words as your prompt to SirGent. |
| Voice skill | `skills/voice/SKILL.md` | Guidance for preparing natural spoken text, calling the TTS API, and playing audio on macOS/Linux/Windows. |

## Setup

1. Get an API key at [elevenlabs.io](https://elevenlabs.io) (free tier
   available) and set it as `ELEVENLABS_API_KEY` — in Settings →
   Environment, or export it in your shell.
2. Optional voice settings:
   - `ELEVENLABS_VOICE_ID` — any voice from your ElevenLabs library
     (default `21m00Tcm4TlvDq8ikWAM`, "Rachel")
   - `ELEVENLABS_MODEL_ID` — default `eleven_multilingual_v2`
   - `SPEECH_MAX_CHARS` — narration cap, default `400`
   - `SPEECH_DICTATE_SECS` — max dictation length, default `15`
   - `SPEECH_STT_MODEL` — STT model, default `scribe_v1`
3. Make sure a player exists for your platform: `afplay` ships with macOS;
   on Linux install `mpv` or `ffmpeg`; on Windows the PowerShell
   `Media.SoundPlayer` path needs no extra install.
4. For `/dictate`, install a mic recorder: `sox` (recommended, all
   platforms via Homebrew/apt/choco), or use `arecord` (ALSA Linux) /
   `ffmpeg` (macOS avfoundation).

Without an API key the narrator stays silent (one setup hint on first run)
and everything else keeps working.

## Kill switches

- `SPEECH_DISABLE=1` — disables the Stop-hook narrator entirely
- `/hush off` — mutes via the flag file; `/hush on` unmutes
- Removing the plugin disables everything

The hook always exits 0 and never blocks the session: a missing key, an API
error, or a missing player degrades to a `systemMessage` note (or silence),
never to a failed turn. `/dictate` fails soft the same way: it prints a
`speech:` reason on stderr and exits 1 rather than inventing content.

## Testing

Try it without touching hooks:

```sh
echo '{}' | \
  ELEVENLABS_API_KEY=sk-... python3 hooks/speak_response.py <<< '{}'
```

or simply run `sirgent` with the plugin loaded and let it finish a turn:

```sh
sirgent --plugin-dir plugins/speech
```

## File layout

```
speech/
├── .sirgent-plugin/
│   └── plugin.json        # plugin metadata
├── commands/
│   ├── speak.md           # /speak — say arbitrary text aloud
│   ├── hush.md            # /hush — mute/unmute the narrator
│   └── dictate.md         # /dictate — voice input (mic → STT → prompt)
├── hooks/
│   ├── hooks.json         # Stop hook wiring
│   ├── speak_response.py  # the narrator (TTS + playback)
│   ├── dictate_stt.py     # dictation bridge (record → STT → stdout)
│   └── tts-python.sh      # python3 finder shim (Windows-safe)
├── skills/
│   └── voice/SKILL.md     # voice narration guidance
└── README.md
```
