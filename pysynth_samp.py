#!/usr/bin/env python

"""
##########################################################################
#                       * * *  PySynth  * * *
#       A very basic audio synthesizer in Python (www.python.org)
#
#          Martin C. Doege, 2017-06-25 (mdoege@compuserve.com)
##########################################################################
# Based on a program by Tyler Eaves (tyler at tylereaves.com) found at
#   http://mail.python.org/pipermail/python-list/2000-August/049968.html
##########################################################################

# 'song' is a Python list (or tuple) in which the song is defined,
#   the format is [['note', value]]

# Notes are 'a' through 'g' of course,
# optionally with '#' or 'b' appended for sharps or flats.
# Finally the octave number (defaults to octave 4 if not given).
# An asterisk at the end makes the note a little louder (useful for the beat).
# 'r' is a rest.

# Note value is a number:
# 1=Whole Note; 2=Half Note; 4=Quarter Note, etc.
# Dotted notes can be written in two ways:
# 1.33 = -2 = dotted half
# 2.66 = -4 = dotted quarter
# 5.33 = -8 = dotted eighth
"""
import sys
assert sys.version >= '3.3', "This program does not work with older versions of Python.\
 Please install Python 3.3 or later."

import wave, struct
import numpy as np
from math import sin, cos, pi, log, exp
from mixfiles import mix_files
from demosongs import *
from mkfreq import getfreq, getfn

pitchhz, keynum = getfreq()

# get filenames for sample layer 10:
fnames = getfn(10)

# path to Salamander piano samples (http://freepats.zenvoid.org/Piano/acoustic-grand-piano.html),
#       48 kHz version:
patchpath = "/usr/share/sounds/SalamanderGrandPianoV3_48khz24bit/48khz24bit/"


##########################################################################
#### Main program starts below
##########################################################################
# Some parameters:

# Beats (quarters) per minute
# e.g. bpm = 95

# Octave shift (neg. integer -> lower; pos. integer -> higher)
# e.g. transpose = 0

# Playing style (e.g., 0.8 = very legato and e.g., 0.3 = very staccato)
# e.g. leg_stac = 0.6

# Volume boost for asterisk notes (1. = no boost)
# e.g. boost = 1.2

# Output file name
#fn = 'pysynth_output.wav'

##########################################################################

def make_wav(song,bpm=120,transpose=0,leg_stac=.9,boost=1.1,repeat=0,fn="out.wav", silent=False):
	f=wave.open(fn,'w')

	f.setnchannels(1)
	f.setsampwidth(2)
	f.setframerate(48000)
	f.setcomptype('NONE','Not Compressed')

	bpmfac = 120./bpm

	def length(l):
	    return 96000./l*bpmfac

	def getval(v):
		a = struct.unpack('i', v + b'\x00')[0] / 256 - 32768
		if a > 0:
			a =  1 - a / 32768
		else:
			a = -1 - a / 32768
		return(a)

	def render2(a, b, vol, pos, knum, note):
		snd_len = int(b)

		wf = wave.open(patchpath + fnames[knum][0], "rb")
		wl = wf.getnframes()
		wd = wf.readframes(wl)
		new = np.zeros(wl // 6)

		for x in range(wl // 6):
			#left: getval( wd[6 * x:6 * x +3] )
			#right: getval( wd[6 * x + 3:6 * x +6] )
			new[x] = getval( wd[6 * x:6 * x +3] )

		wf.close()

		f = fnames[knum][1]
		# Salamander samples every third piano key, so other notes
		# are created by playing these samples faster (with linear interpolation):
		if f > 1:
			f2 = int(len(new) / f)
			new2 = np.zeros(f2)
			for x in range(f2):
				q = x * f - int(x * f)
				new2[x] = (1 - q) * new[int(x * f)] + q * new[int(x * f) + 1]
		else:
			new2 = new
		raw_note = len(new2)

		dec_ind = int(leg_stac*b)
		new2[dec_ind:] *= np.exp(-np.arange(raw_note-dec_ind)/3000.)
		new2[-1001:] *= np.arange(1, -.001,-.001)
		if snd_len > raw_note:
			print("Warning, note too long:", snd_len, raw_note)
			snd_len = raw_note
		data[pos:pos+snd_len] += ( new2[:snd_len] * vol  )

	ex_pos = 0.
	t_len = 0
	for y, x in song:
		if x < 0:
			t_len+=length(-2.*x/3.)
		else:
			t_len+=length(x)
		if y[-1] == '*':
			y = y[:-1]
		if not y[-1].isdigit():
			y += '4'
	data = np.zeros(int((repeat+1)*t_len + 480000))

	for rp in range(repeat+1):
		for nn, x in enumerate(song):
			if not nn % 4 and silent == False:
				print("[%u/%u]\t" % (nn+1,len(song)))
			if x[0]!='r':
				if x[0][-1] == '*':
					vol = boost
					note = x[0][:-1]
				else:
					vol = 1.
					note = x[0]
				if not note[-1].isdigit():
					note += '4'		# default to fourth octave
				a=pitchhz[note]
				kn = keynum[note]
				a = a * 2**transpose
				if x[1] < 0:
					b=length(-2.*x[1]/3.)
				else:
					b=length(x[1])

				render2(a, b, vol, int(ex_pos), kn, note)
				ex_pos = ex_pos + b

			if x[0]=='r':
				b=length(x[1])
				ex_pos = ex_pos + b

	##########################################################################
	# Write to output file (in WAV format)
	##########################################################################
	if silent == False:
		print("Writing to file", fn)

	data = data / (data.max() * 2.)
	out_len = int(2. * 48000. + ex_pos+.5)
	data2 = np.zeros(out_len, np.short)
	data2[:] = 32000. * data[:out_len]
	f.writeframes(data2.tostring())
	f.close()
	print()

##########################################################################
# Synthesize demo songs
##########################################################################

if __name__ == '__main__':
	print("*** SAMPLER ***")
	print()
	print("Creating Demo Songs... (this might take about a minute)")
	print()

	#make_wav((('c', 4), ('e', 4), ('g', 4), ('c5', 1)))
	make_wav(song1, fn = "pysynth_scale.wav")
	#make_wav((('c1', 1), ('r', 1),('c2', 1), ('r', 1),('c3', 1), ('r', 1), ('c4', 1), ('r', 1),('c5', 1), ('r', 1),('c6', 1), ('r', 1),('c7', 1), ('r', 1),('c8', 1), ('r', 1), ('r', 1), ('r', 1), ('c4', 1),('r', 1), ('c4*', 1), ('r', 1), ('r', 1), ('r', 1), ('c4', 16), ('r', 1), ('c4', 8), ('r', 1),('c4', 4), ('r', 1),('c4', 1), ('r', 1),('c4', 1), ('r', 1)), fn = "all_cs.wav")

	make_wav(song4_rh, bpm = 130, transpose = 1, boost = 1.15, repeat = 1, fn = "pysynth_bach_rh.wav")
	make_wav(song4_lh, bpm = 130, transpose = 1, boost = 1.15, repeat = 1, fn = "pysynth_bach_lh.wav")

	#make_wav(song3, bpm = 132/2, leg_stac = 0.9, boost = 1.1, fn = "pysynth_chopin.wav")


