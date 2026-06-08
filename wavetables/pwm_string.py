#!/usr/bin/env python3

# Create a wavetable for use with multi_wave.py

import wave, struct
from math import *

# WAV file name
fn = "pwm_string.wav"

# number of samples per waveform
num_samp = 256

# number of waveforms
num_wave = 64

f = wave.open(fn, "w")
f.setnchannels(1)
f.setsampwidth(2)
f.setframerate(44100)
f.setcomptype("NONE", "Not Compressed")

for j in range(num_wave):
    out = 0
    w = 1
    pwm = 0.75 + 0.1 * sin(j / (num_wave - 1) * pi * 10)
    pwm = round(pwm * num_samp)
    for i in range(pwm):
        out += (10000 * w - out) / 10
        f.writeframesraw(struct.pack("h", round(out)))
    w = -1
    for i in range(num_samp - pwm):
        out += (10000 * w - out) / 10
        f.writeframesraw(struct.pack("h", round(out)))


f.writeframes(b"")
f.close()
