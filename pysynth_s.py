#!/usr/bin/env python

#print "*** KARPLUS-STRONG STRING ***"

"""
##########################################################################
#                       * * *  PySynth  * * *
#       A very basic audio synthesizer in Python (www.python.org)
#
#          Martin C. Doege, 2009-06-13 (mdoege@compuserve.com)
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
from math import sin, cos, pi, log, exp, floor, ceil
from mixfiles import mix_files
from demosongs import *
from mkfreq import getfreq

pitchhz, keynum = getfreq()

def linint(arr, x):
	"Interpolate an (X, Y) array linearly."
	for v in arr:
		if v[0] == x: return v[1]
	xvals = [v[0] for v in arr]
	ux = max(xvals)
	lx = min(xvals)
	try: assert lx <= x <= ux
	except:
		#print lx, x, ux
		raise
	for v in arr:
		if v[0] > x and v[0] - x <= ux - x:
			ux = v[0]
			uy = v[1]
		if v[0] < x and x - v[0] >= lx - x:
			lx = v[0]
			ly = v[1]		
	#print lx, ly, ux, uy
	return (float(x) - lx) / (ux - lx) * (uy - ly) + ly

##########################################################################
#### Main program starts below
##########################################################################
# Some parameters:

# Beats (quarters) per minute
# e.g. bpm = 95

# Octave shift (neg. integer -> lower; pos. integer -> higher)
# e.g. transpose = 0

# Pause between notes as a fraction (0. = legato and e.g., 0.5 = staccato)
# e.g. pause = 0.05

# Volume boost for asterisk notes (1. = no boost)
# e.g. boost = 1.2

# Output file name
#fn = 'pysynth_output.wav'

data = []

def make_wav(song,bpm=120,transpose=0,pause=0.,boost=1.1,repeat=0,fn="out.wav",silent=False):
	f=wave.open(fn,'w')

	f.setnchannels(1)
	f.setsampwidth(2)
	f.setframerate(44100)
	f.setcomptype('NONE','Not Compressed')

	bpmfac = 120./bpm

	def length(l):
	    return 88200./l*bpmfac

	def waves2(hz,l):
	    a=44100./hz
	    b=float(l)/44100.*hz
	    return [a,round(b)]

	def asin(x):
	    return sin(2.*pi*x)

	def render2(a, b, vol, pos, knum, note, endamp = .25, sm = 10):
		b2 = (1. - pause) * b
		l=waves2(a, b2)
		ow=b''
		q=int(l[0]*l[1])

		lf = log(a)
		t = (lf-3.) / (8.5-3.)
		volfac = 1. + .8 * t * cos(pi/5.3*(lf-3.))
		snd_len = int((10.-lf)*q)
		if lf < 4: snd_len *= 2
		x = np.arange(snd_len)
		s = x / float(q)

		ls = np.log(1. + s)
		kp_len = int(l[0])
		kps1 = np.zeros(snd_len)
		kps2 = np.zeros(snd_len)
		kps1[:kp_len] = np.random.normal(size = kp_len)

		for t in range(kp_len):
			kps2[t] = kps1[t:t+sm].mean()
		delt = float(l[0])
		li = int(floor(delt))
		hi = int(ceil(delt))
		ifac = delt % 1
		delt2 = delt * (floor(delt) - 1) / floor(delt)
		ifac2 = delt2 % 1
		falloff = (4./lf*endamp)**(1./l[1])
		for t in range(hi, snd_len):
			v1 = ifac * kps2[t-hi]   + (1.-ifac) * kps2[t-li]
			v2 = ifac2 * kps2[t-hi+1] + (1.-ifac2) * kps2[t-li+1]
			kps2[t] += .5 * (v1 + v2) * falloff
		data[pos:pos+snd_len] += kps2*vol*volfac

	ex_pos = 0.
	t_len = 0
	for y, x in song:
		if x < 0:
			t_len+=length(-2.*x/3.)
		else:
			t_len+=length(x)
	data = np.zeros(int((repeat+1)*t_len + 20 * 44100))
	#print len(data)/44100., "s allocated"

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
	out_len = int(2. * 44100. + ex_pos+.5)
	data2 = np.zeros(out_len, np.short)
	data2[:] = 32000. * data[:out_len]
	f.writeframes(data2.tostring())
	f.close()
	print()

##########################################################################
# Synthesize demo songs
##########################################################################

if __name__ == '__main__':
	print("*** KARPLUS-STRONG STRING ***")
	print()
	print("Creating Demo Songs... (this might take a few minutes)")
	print()

	#make_wav((('c2', 4), ('e2', 4), ('g2', 4), ('c3', 1)))
	#make_wav(song1, fn = "pysynth_scale.wav")
	#make_wav((('c1', 1), ('r', 1),('c2', 1), ('r', 1),('c3', 1), ('r', 1), ('c4', 1), ('r', 1),('c5', 1), ('r', 1),('c6', 1), ('r', 1),('c7', 1), ('r', 1),('c8', 1), ('r', 1), ('r', 1), ('r', 1), ('c4', 1),('r', 1), ('c4*', 1), ('r', 1), ('r', 1), ('r', 1), ('c4', 16), ('r', 1), ('c4', 8), ('r', 1),('c4', 4), ('r', 1),('c4', 1), ('r', 1),('c4', 1), ('r', 1)), fn = "all_cs.wav")
	make_wav(song4_rh, bpm = 130, transpose = 1, boost = 1.15, repeat = 1, fn = "pysynth_bach_rh.wav")
	make_wav(song4_lh, bpm = 130, transpose = 1, boost = 1.15, repeat = 1, fn = "pysynth_bach_lh.wav")
	mix_files("pysynth_bach_rh.wav", "pysynth_bach_lh.wav", "pysynth_bach.wav")

	#make_wav(song3, bpm = 132/2, pause = 0., boost = 1.1, fn = "pysynth_chopin.wav")
	#make_wav(song2, bpm = 95, boost = 1.2, fn = "pysynth_anthem.wav")
