#!/usr/bin/env python

from distutils.core import setup

setup(name="PySynth",
        version="2.3",
        description="A simple music synthesizer for Python 3",
        author="Martin C. Doege",
        author_email="mdoege@compuserve.com",
	url="http://mdoege.github.io/PySynth/",
        py_modules=["pysynth", "pysynth_b", "pysynth_c", "pysynth_d", "pysynth_e", "pysynth_p", "pysynth_s", "pysynth_beeper", "pysynth_samp", "play_wav", "mixfiles", "mkfreq", "demosongs"],
	scripts=["read_abc.py", "readmidi.py", "nokiacomposer2wav.py", "test_nokiacomposer2wav.py", "menv.py"],
)

