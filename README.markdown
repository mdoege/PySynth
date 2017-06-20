## Overview

PySynth is a simple music synthesizer written in Python 3. The goal is not to produce many different sounds, but to have scripts that can turn ABC notation or MIDI files into a WAV file without too much tinkering.

The current release of the synthesizer can only play one note at a time. (Although successive notes can overlap in PySynth B and S, but not A.) However, two output files can be mixed together to get stereo sound.

## Synthesizer scripts

| Synth  | Synthesis method | Timbre | Needs NumPy? |
| --- | --- | --- | --- |
| A | additive (3 sine waves) | flute/organ/piano | no
| B | additive (5 sine waves) | acoustic piano | yes
| C | subtractive (sawtooth wave) | bowed string | no
| D | subtractive (square wave) | woodwind/synth lead | no
| E | FM/phase modulation (6 sine waves) | DX7 Rhodes | yes
| P | subtractive (white noise) | untuned percussion | no
| S | Karplus-Strong (physical modeling) | plucked string | yes
| beeper | additive | Nokia phone | no

## Installation

### Linux
Clone the repository:

`git clone git@github.com:mdoege/PySynth.git`

or

`git clone https://github.com/mdoege/PySynth.git`

Enter the directory (`cd PySynth`) and run 

`python3 setup.py install`

## Sample usage

Basic usage:

```python3
import pysynth as ps
test = (('c', 4), ('e', 4), ('g', 4),
		('c5', -2), ('e6', 8), ('d#6', 2))
ps.make_wav(test, fn = "test.wav")
```

More advanced usage:

```python3
import pysynth_b as psb # a, b, e, and s variants available

''' (note, duration)
Note name (a to g), then optionally a '#' for sharp or
'b' for flat, then optionally the octave (defaults to 4).
An asterisk at the end means to play the note a little 
louder.  Duration: 4 is a quarter note, -4 is a dotted 
quarter note, etc.'''
song = (
  ('c', 4), ('c*', 4), ('eb', 4), 
  ('g#', 4),  ('g*', 2), ('g5', 4),
  ('g5*', 4), ('r', 4), ('e5', 16),
  ('f5', 16),  ('e5', 16),  ('d5', 16),
  ('e5*', 4) 
)

# Beats per minute (bpm) is really quarters per minute here
psb.make_wav(song, fn = "danube.wav", leg_stac = .7, bpm = 180)
```

Read ABC file and output WAV:

`python3 read_abc.py straw.abc`

## Documentation

More documentation and examples at the [PySynth homepage][1].

[1]: http://mdoege.github.io/PySynth/
[2]: http://numpy.scipy.org/
