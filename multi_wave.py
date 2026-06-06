#!/usr/bin/env python3

# Polyphonic Python wavetable MIDI synthesizer

import pyaudio
import mido
import struct, math, time, wave

# sleep time in main loop
SLEEP = .01

# audio buffer size (determines latency)
#      Increase this to e.g. 256 or 512 if there is crackling audio output.
BSIZE = 256

# sample rate
ARATE = 44100

# maximum polyphony
MAXPOLY = 12

# sustain notes?
SUSTAIN = False

################################################################################

# read wavetable file

# WAV file name, number of samples per waveform, volume

#   (Uncomment the line with the wavetable you want to load.)

# 256x32 (mix of sine/sawtooth/square wave)
fn, num_samp, volume = "wavetable.wav", 256, .5

# 256x32 (pluck sound with a closing low-pass filter)
#fn, num_samp, volume = "wavetables/pluck_filter.wav", 256, .5

# 2048x2 (morph between sawtooth and sine wave)
#fn, num_samp, volume = "wavetables/sawsine.wav", 2048, .05

# 256x32 (piano sound from Surge XT)
#fn, num_samp, volume = "/usr/share/surge-xt/wavetables_3rdparty/Emu VSCO/Keys/Upright Piano Medium.wav", 256, .2

# waveform change speed
wave_adv = .16

wf = wave.open(fn)
print(wf.getparams())

num_wave = wf.getnframes() // num_samp
wt = []
for j in range(num_wave):
    for i in range(num_samp):
        d = struct.unpack("h", wf.readframes(1))[0]
        wt.append(d)
print("loaded", num_wave, "waveforms")

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
            # fade out note when it has reached the end of the wavetable:
            if n[5] > num_wave - 1:
                n[5] = num_wave - 1
                n[3] = .9999
        b = struct.pack("h", round(volume * v))
        data += b
    return data, pyaudio.paContinue

# open mido and pyaudio inputs/outputs
inport = mido.open_input()
paud = pyaudio.PyAudio()
stream = paud.open(format = paud.get_format_from_width(2),
                    channels = 1,
                    rate = ARATE,
                    output = True,
                    frames_per_buffer = BSIZE,
                    stream_callback = callback)

#print("latency [s] = %.5f" % stream.get_output_latency())

while True:
    for msg in inport.iter_pending():
        # process new note
        if msg.type == "note_on":
            if msg.velocity == 0:
                # turn note off (if velocity = 0)
                if not SUSTAIN:
                    for n in notes:
                        if n[4] == msg.note:
                            n[3] = .9999
            else:
                # get note frequency in Hz
                freq = 440 * 2**((msg.note - 69) / 12)

                # get wavetable increment factor
                #   (higher pitch = faster increment)
                a_min, a_max, a_sel = math.log(21), math.log(108), math.log(msg.note)
                wav_inc_fac = 1 + 15 * ((a_sel - a_min) / (a_max - a_min))

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
                notes.append([0, freq, 1, 1, msg.note, 0, wav_inc])

                # remove notes that have gone almost silent
                newnotes = []
                for n in notes:
                    if n[2] > .001:
                        newnotes.append(n)
                notes = newnotes

                # apply maximum polyphony cutoff with priority for latest notes
                if len(notes) > MAXPOLY:
                    notes = notes[-MAXPOLY:]

        # increase amplitude loss of note when note_off event happens
        if msg.type == "note_off" and not SUSTAIN:
            for n in notes:
                if n[4] == msg.note:
                    n[3] = .9999

    try:
        time.sleep(SLEEP)
    except:     # exception handler hides ugly backtrace when pressing Ctrl-C
        break

stream.close()
paud.terminate()
inport.close()

