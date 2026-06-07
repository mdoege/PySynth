#!/usr/bin/env python3

# Play back a MIDI file using mido, with optional transposition

# Only note on and note off events are transmitted,
# other events such as control changes are filtered out.
# This is mainly for playing back MIDI to Dexed:
# If a General MIDI file sends a program change to 0 to select a piano patch,
# Dexed will switch to the first patch of the currently loaded cartridge.
# Which is probably not a piano at all!
# Also, other control changes like the sustain pedal are not implemented
# by my MIDI synthesizers anyway.

import mido
import sys, os.path

# transposition (halftones)
TRANSPOSE = 0

try:
    fn = sys.argv[1]
except:
    fn = os.path.join("docs", "italian.mid")

out = mido.open_output()

allow = "note_on", "note_off"

for msg in mido.MidiFile(fn).play():
    if msg.type in allow:
        msg.note += TRANSPOSE
        out.send(msg)
