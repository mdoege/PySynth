#!/usr/bin/env python3

# Create a wavetable for use with multi_wave.py

import wave, struct
from math import *

# WAV file name
fn = "pluck_filter.wav"

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
    out = 0
    w = 1
    for i in range(num_samp // 3):
        out += (10000 * w / sqrt(j + 1) - out) / (j + 1)
        f.writeframesraw(struct.pack("h", round(out)))
        w *= 0.999
    w = -0.5
    for i in range(num_samp - num_samp // 3):
        out += (10000 * w / sqrt(j + 1) - out) / (j + 1)
        f.writeframesraw(struct.pack("h", round(out)))
        w *= 0.999


f.writeframes(b"")
f.close()
