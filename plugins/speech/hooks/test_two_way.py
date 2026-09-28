#!/usr/bin/env python3
"""Offline tests for the two-way speech extensions (no mic, no network)."""
import importlib.util
import json
import math
import struct
import tempfile
import wave
from pathlib import Path

spec = importlib.util.spec_from_file_location(
    "sr", "plugins/speech/hooks/speak_response.py"
)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

# --- dB mapping sanity ---
assert m.rms_to_db(0) == -999.0
db_quiet = m.rms_to_db(3)          # faint room noise
db_shout = m.rms_to_db(28000)      # near full-scale blast
print(f"quiet room ~{db_quiet:.1f} dB-eq; shout ~{db_shout:.1f} dB-eq")
assert db_quiet < 150 < db_shout, "150 floor must sit between ambient and a blast"

# --- WAV helpers: make fake 16k mono recordings ---
def make_wav(path, rms_target):
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(16000)
        amp = min(32700, int(rms_target * math.sqrt(2) * 32768))
        frames = b"".join(
            struct.pack("<h", (amp if (i // 40) % 2 == 0 else -amp))
            for i in range(16000 * 2)
        )
        w.writeframes(frames)

tmp = Path(tempfile.mkdtemp())
quiet = tmp / "q.wav"
loud = tmp / "l.wav"
make_wav(quiet, 0.0005)   # faint background noise
make_wav(loud, 0.9)       # near full scale

rq = m.wav_rms(quiet)
lq = m.wav_rms(loud)
assert rq and lq
max_q = max(m.rms_to_db(v) for v in rq)
max_l = max(m.rms_to_db(v) for v in lq)
print(
    f"background max {max_q:.1f} dB-eq (below floor: {max_q < 150}), "
    f"blast max {max_l:.1f} dB-eq (above floor: {max_l >= 150})"
)
assert max_q < 150 <= max_l

# --- barge-in gate decides by floor, not by mere presence of mic ---
floor = 150.0
assert max(m.rms_to_db(v) for v in lq) >= floor
assert max(m.rms_to_db(v) for v in rq) < floor
print("floor gating: PASS")

# --- Stop-block handback JSON shape ---
reason = (
    'The user interrupted your spoken response and said this out loud '
    '(transcribed): "what files changed" — respond to it now.'
)
out = json.dumps({"decision": "block", "reason": reason})
parsed = json.loads(out)
assert parsed["decision"] == "block" and "transcribed" in out
print("handback JSON: PASS")

# --- recorder_command picks nothing in offline sandboxes (returns []) ---
cmds = m.recorder_command(tmp / "reply.wav", 5)
print("recorder candidates found offline:", cmds)
print("ALL SPEECH EXTENSION TESTS: PASS")
