#!/usr/bin/env python3

# Monophonic Python MIDI synthesizer

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

################################################################################

last_note = 0
xpos = 0
freq = 0
amp = 0
amp_loss = 0

# callback function for audio data
def callback(in_data, frame_count, time_info, status):
    global xpos, amp

    data = b""
    delt = 2 * math.pi / ARATE * freq
    for i in range(frame_count):
        if freq > 0:
            v = math.sin(xpos) + .5 * math.sin(2 * xpos) + .25 * math.sin(4 * xpos)
            b = struct.pack('h', round(18000 * amp * v))
            xpos += delt
            amp *= amp_loss
        else:
            b = struct.pack('h', 0)
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
            last_note = msg.note
            xpos = 0
            amp = 1
            a_min, a_max, a_sel = math.log(21), math.log(108), math.log(msg.note)
            lossfac = 50000 - 49000 * ((a_sel - a_min) / (a_max - a_min))
            lossfac *= ARATE / 44100
            amp_loss = 1 - 1 / lossfac
        if msg.type == "note_off":
            if msg.note == last_note:
                freq = 0
                last_note = 0
    try:
        time.sleep(SLEEP)
    except:
        break

stream.close()
paud.terminate()
inport.close()

