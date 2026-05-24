#!/usr/bin/env python3

# Polyphonic Python MIDI synthesizer

import pyaudio
import mido
import struct, math, time

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
VOLUME = 3000

################################################################################

notes = []

# callback function for audio data
def callback(in_data, frame_count, time_info, status):
    global xpos, amp

    data = b""
    for i in range(frame_count):
        v = 0
        for n in notes:
            v += n[2] * (math.sin(n[0]) + .5 * math.sin(2 * n[0]) + .25 * math.sin(4 * n[0]))
            delt = 2 * math.pi / ARATE * n[1]
            n[0] += delt
            n[2] *= n[3]
        b = struct.pack('h', round(VOLUME * v))
        data += b
    return data, pyaudio.paContinue

inport = mido.open_input()
paud = pyaudio.PyAudio()
stream = paud.open(format = paud.get_format_from_width(2),
                    channels = 1,
                    rate = ARATE,
                    output = True,
                    frames_per_buffer = BSIZE,
                    stream_callback = callback)

print("latency [s] = %.5f" % stream.get_output_latency())

while True:
    for msg in inport.iter_pending():
        if msg.type == "note_on":
            freq = 440 * 2**((msg.note - 69) / 12)
            a_min, a_max, a_sel = math.log(21), math.log(108), math.log(msg.note)
            lossfac = 50000 - 49000 * ((a_sel - a_min) / (a_max - a_min))
            lossfac *= ARATE / 44100
            amp_loss = 1 - 1 / lossfac
            notes.append([0, freq, 1, amp_loss])

            newnotes = []
            for n in notes:
                if n[2] > .001:
                    newnotes.append(n)
            notes = newnotes

            if len(notes) > MAXPOLY:
                notes = notes[-MAXPOLY:]
            #print(notes)

    time.sleep(SLEEP)

stream.close()
paud.terminate()
inport.close()

