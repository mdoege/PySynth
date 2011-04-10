import wave, math, struct

SAMPLING_RATE = 44100

PITCHHZ = {}
keys_s = ('a', 'a#', 'b', 'c', 'c#', 'd', 'd#', 'e', 'f', 'f#', 'g', 'g#')
for k in range(88):
    freq = 27.5 * 2. ** (k / 12.)
    oct = (k + 9) // 12
    note = '%s%u' % (keys_s[k % 12], oct)
    PITCHHZ[note] = freq

def make_wav(song, bpm=120, transpose=0, fn="out.wav"):
    f = wave.open(fn, 'w')

    f.setnchannels(1)
    f.setsampwidth(2)
    f.setframerate(SAMPLING_RATE)
    f.setcomptype('NONE', 'Not Compressed')

    # Define a waveform that looks something like this
    # \        /
    #__\_____ /__
    #   \  /\/
    #    \/
    
    # Format:  [(start, end, start_level, end_level), ...]        
    waveform = [(0.0, 0.3,  1.0, -1.0), 
                (0.3, 0.5, -1.0,  0.0), 
                (0.5, 0.6,  0.0, -0.5), 
                (0.6, 1.0, -0.5,  1.0)]

    # BPM is "quarter notes per minute"
    full_notes_per_second = float(bpm) / 60 / 4 
    full_note_in_samples = SAMPLING_RATE / full_notes_per_second

    def sixteenbit(sample):
        return struct.pack('h', round(32000 * sample))

    def beep(freq, duration, sink):
        asin = lambda x: math.sin(2. * math.pi * x)
    
        ow = ""
        period = SAMPLING_RATE / 4 / freq
        for x in xrange(duration):
            fade_multiplier = 1
            distance_from_border = min(x, duration - x)
            if distance_from_border < 100:
                fade_multiplier = distance_from_border / 100.0 
                 
            # Position inside current period, 0..1            
            pos = float((x % period)) / period
            
            # Synth 1, using sine waves
            level1 = (asin(pos) + asin(pos * 2)) / 2
            
            # Synth 2, discrete, using waveform definition
            for start, finish, start_level, finish_level in waveform:
                if pos >= start and pos <= finish:
                    localpos = (pos - start) / (finish - start)
                    level2 = (finish_level - start_level) * localpos + start_level
                    break
            
            # Put both samples together, apply fadein/fadeout
            level = ((level1 + level2) / 2) * fade_multiplier
            ow = ow + sixteenbit(level)

        sink.writeframesraw(ow)

    def silence(duration, sink):
        sink.writeframesraw(sixteenbit(0) * int(duration))

    for note_pitch, note_duration in song:
        # note_duration is 1, 2, 4, 8, ... and actually means 1, 1/2, 1/4, ...
        duration = full_note_in_samples / note_duration 
        
        if note_pitch == "r":
            print "Silence for %d samples" % duration
            silence(duration, f)
        else:
            freq = PITCHHZ[note_pitch]
            freq *= 2 ** transpose
            print "%d Hz for %d samples" % (freq, duration)
            beep(freq, duration, f)

    f.close()
