# speech

Speech capabilities for SirGent AI: voice narration of responses through
ElevenLabs text-to-speech, an on-demand `/speak` command, a `/hush` mute
toggle, and **two-way voice conversation** — talk over a response to
interrupt it (barge-in, gated at a 150 dB-equivalent floor) and SirGent
hears your reply.

## What it does

| Piece | Where | What happens |
| --- | --- | --- |
| Stop hook narrator | `hooks/speak_response.py` | When SirGent finishes a turn, the final assistant message is distilled (markdown stripped, capped at ~400 chars), converted to MP3 with ElevenLabs TTS, and played through the platform's audio player. |
| Two-way voice (barge-in) | same hook, `/voice on` | While the response plays, the mic is monitored. A signal above the barge-in floor lowers (kills) playback and records your reply; ElevenLabs speech-to-text transcribes it and SirGent responds to your words. |
| `/speak` command | `commands/speak.md` | Speak any text the user supplies, on demand. |
| `/hush` command | `commands/hush.md` | Mute/unmute the Stop-hook narrator with a flag file (`~/.sirgent/speech-disabled`). |
| `/voice` command | `commands/voice.md` | Toggle two-way conversation mode (`~/.sirgent/speech-conversation`). |
| Voice skill | `skills/voice/SKILL.md` | Guidance for preparing natural spoken text, calling the TTS/STT APIs, and playing audio on macOS/Linux/Windows. |

## The 150 dB barge-in floor

Interruption is gated by `SPEECH_BARGE_IN_DB`, an SPL-equivalent level
derived from the mic's RMS energy (16-bit reference). The default floor of
**150** is deliberately extreme — louder than a jet engine — so everyday
background noise (music, fans, typing, normal conversation, TV) can never
interrupt a response. Only a sustained, very loud signal — roughly a shout
directed at the microphone at close range, held for ~2 seconds — counts.

- Raise it (e.g. `SPEECH_BARGE_IN_DB=170`) to make interruption even harder.
- Lower it (e.g. `SPEECH_BARGE_IN_DB=120`, conversational-loud) only if you
  want hands-free interruptibility and accept false triggers from ambient
  noise.
- Measured levels: typical quiet room ≈ 100 dB-eq, loud playback bleed
  ≈ 130–140 dB-eq, close-range shout ≈ 180 dB-eq.

## Two-way voice setup

1. Enable it: `/voice on` (or `SPEECH_CONVERSATION=1`).
2. Install a mic recorder if missing: `sox` (all platforms via Homebrew/
   apt/choco), or use `arecord` (ALSA Linux) / `ffmpeg` (macOS avfoundation).
3. Keep `ELEVENLABS_API_KEY` set — transcription uses the ElevenLabs
   `scribe_v1` model (override with `SPEECH_STT_MODEL`).
4. Reply length is capped by `SPEECH_REPLY_SECS` (default 12 s).

When a barge-in happens, playback stops, your reply is recorded and
transcribed, and the hook hands the transcribed words back to SirGent as
the next instruction (Stop-hook `decision: block` with the reply as the
reason), so the conversation continues by voice.

## Setup

1. Get an API key at [elevenlabs.io](https://elevenlabs.io) (free tier
   available) and set it as `ELEVENLABS_API_KEY` — in Settings →
   Environment, or export it in your shell.
2. Optional voice settings:
   - `ELEVENLABS_VOICE_ID` — any voice from your ElevenLabs library
     (default `21m00Tcm4TlvDq8ikWAM`, "Rachel")
   - `ELEVENLABS_MODEL_ID` — default `eleven_multilingual_v2`
   - `SPEECH_MAX_CHARS` — narration cap, default `400`
3. Make sure a player exists for your platform: `afplay` ships with macOS;
   on Linux install `mpv` or `ffmpeg`; on Windows the PowerShell
   `Media.SoundPlayer` path needs no extra install.
4. For two-way voice, install a mic recorder (`sox`, `arecord`, or
   `ffmpeg`) and run `/voice on`.

Without an API key the narrator stays silent (one setup hint on first run)
and everything else keeps working.

## Kill switches

- `SPEECH_DISABLE=1` — disables the Stop-hook narrator entirely
- `/hush off` — mutes via the flag file; `/hush on` unmutes
- `/voice off` — disables mic monitoring / barge-in
- Removing the plugin disables everything

The hook always exits 0 and never blocks the session: a missing key, an API
error, or a missing player degrades to a `systemMessage` note (or silence),
never to a failed turn.

## Testing

Try it without touching hooks:

```sh
echo '{"transcript_path": ""}' | \
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
│   └── voice.md           # /voice — toggle two-way conversation mode
├── hooks/
│   ├── hooks.json         # Stop hook wiring
│   ├── speak_response.py  # narrator + barge-in + STT handback
│   ├── tts-python.sh      # python3 finder shim (Windows-safe)
│   └── test_two_way.py    # offline tests for the two-way logic
├── skills/
│   └── voice/SKILL.md     # voice narration guidance
└── README.md
```
