#!/usr/bin/env python3

# Polyphonic Python wavetable MIDI synthesizer

import pyaudio
import mido
import struct, math, time, wave

# sleep time in main loop
SLEEP = .01

# audio buffer size (determines latency)
#      Increase this to e.g. 256 or 512 if there is crackling audio output.
BSIZE = 128

# sample rate
ARATE = 44100

# maximum polyphony
MAXPOLY = 8

# volume
VOLUME = .2

# sustain notes?
SUSTAIN = False

################################################################################

# read wavetable file

# WAV file name
fn = "/usr/share/surge-xt/wavetables_3rdparty/Emu VSCO/Keys/Upright Piano Medium.wav"

# number of samples per waveform
num_samp = 256

# waveform change speed (lower = faster)
wave_adv = 55000

wf = wave.open(fn)
print(wf.getparams())

num_wave = wf.getnframes() // num_samp
wt = []
for j in range(num_wave):
    for i in range(num_samp):
        d = struct.unpack("h", wf.readframes(1))[0]
        wt.append(d)

# list of currently active notes
notes = []

# callback function for audio data
def callback(in_data, frame_count, time_info, status):
    data = b""
    for i in range(frame_count):
        v = 0
        for n in notes:
            pind = int((n[0] % (2 * math.pi)) / (2 * math.pi) * num_samp)
            v += n[2] * wt[pind + int(n[5]) * num_samp]
            n[0] += 2 * math.pi / ARATE * n[1]
            n[2] *= n[3]
            n[5] += 2 * math.pi / ARATE / wave_adv
            n[5] = min(n[5], num_wave - 1)
        b = struct.pack("h", round(VOLUME * v))
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
                            n[3] = n[3]**6
            else:
                # get note frequency in Hz
                freq = 440 * 2**((msg.note - 69) / 12)

                # get amplitude loss factor per sample
                #   (higher frequencies decay more quickly)
                a_min, a_max, a_sel = math.log(21), math.log(108), math.log(msg.note)
                lossfac = 50000 - 49000 * ((a_sel - a_min) / (a_max - a_min))
                lossfac *= ARATE / 44100
                amp_loss = 1 - 1 / lossfac

                # append new note to list of active notes
                #   note data:
                #     * current oscillator phase
                #     * frequency in Hz
                #     * current amplitude
                #     * amplitude loss factor
                #     * MIDI key number
                #     * current wavetable position
                notes.append([0, freq, 1, amp_loss, msg.note, 0])

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
                    n[3] = n[3]**6

    try:
        time.sleep(SLEEP)
    except:     # exception handler hides ugly backtrace when pressing Ctrl-C
        break

stream.close()
paud.terminate()
inport.close()

