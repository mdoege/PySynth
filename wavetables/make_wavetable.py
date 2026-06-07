#!/usr/bin/env python3

# Create a wavetable for use with multi_wave.py

import wave, struct
from math import *

# WAV file name
fn = "wavetable.wav"

# number of samples per waveform
num_samp = 256

# number of waveforms
num_wave = 32

f = wave.open(fn, "w")
f.setnchannels(1)
f.setsampwidth(2)
f.setframerate(44100)
f.setcomptype("NONE", "Not Compressed")

for j in range(num_wave):
    for i in range(num_samp):
        phi = 2 * pi * i / num_samp

        # basic wave: sine plus sawtooth
        w = sin(phi) + i / num_samp

        # add some square wave too
        if i > num_samp // 2:
            w -= 0.25

        # decrease amplitude based on position in wavetable
        w = w / sqrt(j + 1)

        f.writeframesraw(struct.pack("h", round(10000 * w)))

f.writeframes(b"")
f.close()
