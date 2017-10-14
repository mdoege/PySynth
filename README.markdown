## Overview

PySynth is a simple music synthesizer written in Python 3. The goal is not to produce many different sounds, but to have scripts that can turn ABC notation or MIDI files into a WAV file without too much tinkering.

The current release of the synthesizer can only play one note at a time. (Although successive notes can overlap in PySynth B and S, but not A.) However, two output files can be mixed together to get stereo sound.

The latest git version of PySynth also works in Python 2.

## Synthesizer scripts

| Synth | Synthesis method | Approximate timbre | Note decay | Needs NumPy? |
| --- | --- | --- | --- | --- |
| A | additive (3 sine waves) | flute, organ, piano | variable (depends on note length) | no
| B | additive (5 sine waves) | acoustic piano | medium | yes
| C | subtractive (sawtooth wave) | bowed string, analog synth pad | none | no
| D | subtractive (square wave) | woodwind, analog synth lead | none | no
| E | FM/phase modulation (6 sine waves) | DX7 Rhodes piano | medium | yes
| P | subtractive (white noise) | untuned percussion hit | very fast | no
| S | Karplus-Strong (physical modeling) | plucked string, guitar, koto | fast | yes
| beeper | additive | Nokia phone ringtone | none | no
| samp | sampler | [Salamander Grand Piano][3] | medium | yes

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
[3]: http://freepats.zenvoid.org/Piano/acoustic-grand-piano.html
