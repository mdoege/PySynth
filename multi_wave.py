#!/usr/bin/env python3

# Polyphonic Python wavetable MIDI synthesizer

import pyaudio
import mido
import sys, struct, math, time, wave

# sleep time in main loop
SLEEP = 0.01

# audio buffer size (determines latency)
#      Increase this to e.g. 256 or 512 if there is crackling audio output.
BSIZE = 256

# sample rate
ARATE = 44100

# maximum polyphony
MAXPOLY = 12

# fade in and out parameters
FADE_NORMAL = 0.9999
FADE_PAD = 0.99995
FADEIN_PAD = 30000

################################################################################

# read wavetable file

# description, WAV file name, samples per waveform, volume, [ pad/sustained sound? ]

presets = [
    # 256x32 (pluck sound with a closing low-pass filter)
    ("pluck", "wavetables/pluck_filter.wav", 256, 0.5),

    # 256x64 (PWM string pad sound)
    ("strings", "wavetables/pwm_string.wav", 256, 0.5, True),

    # 256x32 (mix of sine/sawtooth/square wave)
    ("wave mix", "wavetables/wavetable.wav", 256, .5),

    # 2048x31 (Fairlight CMI sound from Groove Synthesis 3rd Wave; lowest octave)
    ("Fairlight", "wavetables/fairlight_mode1_riser.wav", 2048, 0.5),

    # 256x32 (piano sound from Surge XT)
    ("piano", "wavetables/upright_piano_medium.wav", 256, .2),

    # 2048x2 (morph between sawtooth and sine wave from VAST Vaporizer2)
    ("saw2sine", "wavetables/sawsine.wav", 2048, .05),

    # ?x? (DECtalk speech output)
    # Try this with different sample lengths, such as 64/128/256/512/1024.
    ("DECtalk", "wavetables/speech.wav", 128, 0.5),
]

# print and select presets based on commandline argument

try:
    sel_pres = int(sys.argv[1])
except:
    sel_pres = 0

print(80 * "=")
print("Available presets (select with preset number as commandline argument):")
print(80 * "-")
for i in range(len(presets)):
    if i == sel_pres:
        print("*" ,i, presets[i][0])
        if len(presets[i]) == 4:
            descr, fn, num_samp, volume = presets[i]
            is_pad = False
        else:
            descr, fn, num_samp, volume, is_pad = presets[i]
    else:
        print(" ", i, presets[i][0])
print(80 * "=")

# waveform change speed
if not is_pad:
    wave_adv = 0.16
else:
    wave_adv = 0.5

wf = wave.open(fn)
print(wf.getparams())

num_wave = wf.getnframes() // num_samp
wt = []
for j in range(num_wave):
    for i in range(num_samp):
        d = struct.unpack("h", wf.readframes(1))[0]
        wt.append(d)
print("*** loaded", num_wave, "waveforms ***")

# add padding so the interpolation works for the final wavetable entry
for i in range(num_samp):
    wt.append(0)

# list of currently active notes
notes = []


# callback function for audio data
def callback(in_data, frame_count, time_info, status):
    data = b""
    for i in range(frame_count):
        v = 0
        for n in notes:
            pind = int((n[0] % (2 * math.pi)) / (2 * math.pi) * num_samp)
            v1 = wt[pind + int(n[5]) * num_samp]
            v2 = wt[pind + (int(n[5]) + 1) * num_samp]
            fac = n[5] % 1
            v += n[2] * ((1 - fac) * v1 + fac * v2)
            n[0] += 2 * math.pi / ARATE * n[1]
            n[2] *= n[3]
            n[5] += n[6]
            if n[5] > num_wave - 1:
                # fade out note when it has reached the end of the wavetable
                if not is_pad:
                    n[5] = num_wave - 1
                    n[3] = FADE_NORMAL
                # reset pad sound
                else:
                    n[5] = 0
            # slowly fade in new pad sounds
            if is_pad and n[3] == 1:
                n[2] += (1 - n[2]) / FADEIN_PAD
        b = struct.pack("h", round(volume * v))
        data += b
    return data, pyaudio.paContinue


# open mido and pyaudio inputs/outputs
inport = mido.open_input()
paud = pyaudio.PyAudio()
stream = paud.open(
    format=paud.get_format_from_width(2),
    channels=1,
    rate=ARATE,
    output=True,
    frames_per_buffer=BSIZE,
    stream_callback=callback,
)

# print("latency [s] = %.5f" % stream.get_output_latency())

while True:
    for msg in inport.iter_pending():
        # process new note
        if msg.type == "note_on":
            if msg.velocity == 0:
                # turn note off (if velocity = 0)
                for n in notes:
                    if n[4] == msg.note:
                        if not is_pad:
                            n[3] = FADE_NORMAL
                        else:
                            n[3] = FADE_PAD
            else:
                # get note frequency in Hz
                freq = 440 * 2 ** ((msg.note - 69) / 12)

                # get wavetable increment factor
                #   (higher pitch = faster increment, for non-pad sounds)
                a_min, a_max, a_sel = math.log(21), math.log(108), math.log(msg.note)
                if not is_pad:
                    wav_inc_fac = 1 + 15 * ((a_sel - a_min) / (a_max - a_min))
                else:
                    wav_inc_fac = 1

                # append new note to list of active notes
                #   note data:
                #   0  * current oscillator phase
                #   1  * frequency in Hz
                #   2  * current amplitude
                #   3  * amplitude loss factor
                #   4  * MIDI key number
                #   5  * current wavetable position
                #   6  * wavetable increment
                wav_inc = 1 / ARATE * wave_adv * wav_inc_fac
                # scale wav_inc by wavetable length
                wav_inc *= num_wave - 1
                # normal sounds start at full amplitude; pad sounds at low amplitude
                if not is_pad:
                    notes.append([0, freq, 1, 1, msg.note, 0, wav_inc])
                else:
                    notes.append([0, freq, 0.01, 1, msg.note, 0, wav_inc])

                # remove notes that have gone almost silent
                newnotes = []
                for n in notes:
                    if n[2] > 0.001:
                        newnotes.append(n)
                notes = newnotes

                # apply maximum polyphony cutoff with priority for latest notes
                if len(notes) > MAXPOLY:
                    notes = notes[-MAXPOLY:]

        # increase amplitude loss of note when note_off event happens
        if msg.type == "note_off":
            for n in notes:
                if n[4] == msg.note:
                    if not is_pad:
                        n[3] = FADE_NORMAL
                    else:
                        n[3] = FADE_PAD

    try:
        time.sleep(SLEEP)
    except:  # exception handler hides ugly backtrace when pressing Ctrl-C
        break

stream.close()
paud.terminate()
inport.close()
