## Overview

PySynth is a simple music synthesizer written in Python. The goal is not to produce many different sounds, but to have scripts that can turn ABC notation into a WAV file without too much tinkering.

There are three variants: **PySynth A** is faster, only depends on Python 3, and sounds like a cross between a flute and organ. **PySynth B** is more complex in sound and needs [NumPy][2]. It's supposed to be a little closer to a piano. **PySynth S** is more comparable to a guitar, banjo, or harpsichord, depending on note length and pitch. Finally, **PySynth E** is an FM-synthesized e-piano.

The current release of the synthesizer can only play one note at a time. (Although successive notes can overlap in PySynth B and S, but not A.) However, two output files can be mixed together to get stereo sound.

## Installation

### Linux
Clone the repository:

`git clone git@github.com:mdoege/PySynth.git`

or

`git clone https://github.com/mdoege/PySynth.git`

Enter the directory (`cd PySynth`) and run 

`python setup.py install`

## Sample usage

Basic usage:

```python
import pysynth as ps
test = (('c', 4), ('e', 4), ('g', 4),
		('c5', -2), ('e6', 8), ('d#6', 2))
ps.make_wav(test, fn = "test.wav")
```

More advanced usage:

```python
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

`python read_abc.py straw.abc`

## Documentation

More documentation and examples at the [PySynth homepage][1].

[1]: http://mdoege.github.io/PySynth/
[2]: http://numpy.scipy.org/

## Current limitations

In v1.1, flats and sharps do not work in cases such as e-sharp or c-flat.
This has been fixed in the latest git version.

