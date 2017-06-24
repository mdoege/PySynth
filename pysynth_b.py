#!/usr/bin/env python

#print "*** EXPERIMENTAL PIANO VERSION WITH NOTE CACHING ***"

"""
##########################################################################
#                       * * *  PySynth  * * *
#       A very basic audio synthesizer in Python (www.python.org)
#
#          Martin C. Doege, 2009-06-08 (mdoege@compuserve.com)
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
from mkfreq import getfreq

pitchhz, keynum = getfreq()

# Harmonic intensities (dB) for selected piano keys,
# measured with output from a Yamaha P-85
harmo = (
  (1, -15.8, -3., -15.3, -22.8, -40.7),
  (16, -15.8, -3., -15.3, -22.8, -40.7),
  (28, -5.7, -4.4, -17.7, -16., -38.7),
  (40, -6.8, -17.2, -22.4, -16.8, -75.6),
  (52, -8.4, -19.7, -23.5, -21.6, -76.8),
  (64, -9.3, -20.8, -37.2, -36.3, -76.4),
  (76, -18., -64.5, -74.4, -77.3, -80.8),
  (88, -24.8, -53.8, -77.2, -80.8, -90.),
)

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

harmtab = np.zeros((88, 20))

for h in range(1, len(harmo[0])):
	dat = []
	for n in range(len(harmo)):
		dat.append((float(harmo[n][0]), harmo[n][h]))
	for h2 in range(88):
		harmtab[h2,h] = linint(dat, h2+1)

#print harmtab[keynum['c4'],:]
for h2 in range(88):
	for n in range(20):
		ref = harmtab[h2,1]
		harmtab[h2,n] = 10.**((harmtab[h2,n] - ref)/20.)
#print harmtab[keynum['c4'],:]

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

# Other parameters:

# Influences the decay of harmonics over frequency. Lowering the
# value eliminates even more harmonics at high frequencies.
# Suggested range: between 3. and 5., depending on the frequency response
#  of speakers/headphones used
harm_max = 5.
##########################################################################

data = []
note_cache = {}
cache_this = {}

def make_wav(song,bpm=120,transpose=0,leg_stac=.9,boost=1.1,repeat=0,fn="out.wav", silent=False):
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

	att_len = 3000
	att_bass = np.zeros(att_len)
	att_treb = np.zeros(att_len)
	for n in range(att_len):
		att_treb[n] = linint(((0,0.), (100, .2), (300, .7), (400, .6), (600, .25), (800, .9), (1000, 1.25), (2000,1.15), (3000, 1.)), n)
		att_bass[n] = linint(((0,0.), (100, .1), (300, .2), (400, .15), (600, .1), (800, .9), (1000, 1.25), (2000,1.15), (3000, 1.)), n)
	decay = np.zeros(1000)
	for n in range(900):
		decay[n] = exp(linint(( (0,log(3)), (3,log(5)), (5, log(1.)), (6, log(.8)), (9,log(.1)) ), n/100.))

	def render2(a, b, vol, pos, knum, note):
		l=waves2(a, b)
		q=int(l[0]*l[1])

		lf = log(a)
		t = (lf-3.) / (8.5-3.)
		volfac = 1. + .8 * t * cos(pi/5.3*(lf-3.))
		schweb = waves2(lf*100., b)[0]
		schweb_amp = .05 - (lf-5.) / 100.
		att_fac = min(knum / 87. * vol, 1.)
		snd_len = max(int(3.1*q), 44100)
		fac = np.ones(snd_len)
		fac[:att_len] = att_fac * att_treb + (1.-att_fac) * att_bass

		raw_note = 12*44100
		if note not in list(note_cache.keys()):
			x2 = np.arange(raw_note)
			sina = 2. * pi * x2 / float(l[0])
			ov = np.exp(-x2/3./decay[int(lf*100)]/44100.)
			new = (( np.sin(sina)
			      + ov*harmtab[kn,2]*np.sin(2. * sina)
			      + ov*harmtab[kn,3]*np.sin(3. * sina)
			      + ov*harmtab[kn,4]*np.sin(4. * sina)
			      + ov*harmtab[kn,5]*np.sin(8. * sina)
				) * volfac )
			new *= np.exp(-x2/decay[int(lf*100)]/44100.)
			if cache_this[note] > 1:
				note_cache[note] = new.copy()
				#print "Caching", note
		else:
			new = note_cache[note].copy()
		dec_ind = int(leg_stac*q)
		new[dec_ind:] *= np.exp(-np.arange(raw_note-dec_ind)/3000.)
		if snd_len > raw_note:
			print("Warning, note too long:", snd_len, raw_note)
			snd_len = raw_note
		data[pos:pos+snd_len] += ( new[:snd_len] * fac * vol *
		       (1. + schweb_amp * np.sin(2. * pi * np.arange(snd_len)/schweb/32.) )  )

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
		cache_this[y] = cache_this.get(y, 0) + 1
	#print "Note frequencies in song:", cache_this
	data = np.zeros(int((repeat+1)*t_len + 441000))
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
	print("*** EXPERIMENTAL PIANO VERSION WITH NOTE CACHING ***")
	print()
	print("Creating Demo Songs... (this might take about a minute)")
	print()

	#make_wav((('c', 4), ('e', 4), ('g', 4), ('c5', 1)))
	#make_wav(song1, fn = "pysynth_scale.wav")
	#make_wav((('c1', 1), ('r', 1),('c2', 1), ('r', 1),('c3', 1), ('r', 1), ('c4', 1), ('r', 1),('c5', 1), ('r', 1),('c6', 1), ('r', 1),('c7', 1), ('r', 1),('c8', 1), ('r', 1), ('r', 1), ('r', 1), ('c4', 1),('r', 1), ('c4*', 1), ('r', 1), ('r', 1), ('r', 1), ('c4', 16), ('r', 1), ('c4', 8), ('r', 1),('c4', 4), ('r', 1),('c4', 1), ('r', 1),('c4', 1), ('r', 1)), fn = "all_cs.wav")
	make_wav(song4_rh, bpm = 130, transpose = 1, boost = 1.15, repeat = 1, fn = "pysynth_bach_rh.wav")
	make_wav(song4_lh, bpm = 130, transpose = 1, boost = 1.15, repeat = 1, fn = "pysynth_bach_lh.wav")
	mix_files("pysynth_bach_rh.wav", "pysynth_bach_lh.wav", "pysynth_bach.wav")

	make_wav(song3, bpm = 132/2, leg_stac = 0.9, boost = 1.1, fn = "pysynth_chopin.wav")
