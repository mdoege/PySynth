#!/usr/bin/env python

# Read MIDI file track and synthesize with PySynth A

# Usage:

# python readmidi.py file.mid [tracknum] [file.wav]  [--syn_b/--syn_c/--syn_d/--syn_e/--syn_p/--syn_s/--syn_samp]

# Based on code from https://github.com/osakared/midifile.py
# which appears to be based on
# https://github.com/gasman/jasmid/blob/master/midifile.js

# Original license:

"""
Copyright (c) 2014, Thomas J. Webb
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

* Redistributions of source code must retain the above copyright notice, this
  list of conditions and the following disclaimer.

* Redistributions in binary form must reproduce the above copyright notice,
  this list of conditions and the following disclaimer in the documentation
  and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""

import struct
import sys
assert sys.version >= '3.3', "This program does not work with older versions of Python.\
 Please install Python 3.3 or later."

class Note(object):
	"Represents a single MIDI note"
	
	note_names = ['A', 'A#', 'B', 'C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#']
	
	def __init__(self, channel, pitch, velocity, start, duration = 0):
		self.channel = channel
		self.pitch = pitch
		self.velocity = velocity
		self.start = start
		self.duration = duration
	
	def __str__(self):
		s = Note.note_names[(self.pitch - 9) % 12]
		s += str(self.pitch // 12 - 1)
		s += " " + str(self.velocity)
		s += " " + str(self.start) + " " + str(self.start + self.duration) + " "
		return s
	
	def get_end(self):
		return self.start + self.duration

class MidiFile(object):
	"Represents the notes in a MIDI file"
	
	def read_byte(self, file):
		return struct.unpack('B', file.read(1))[0]
	
	def read_variable_length(self, file, counter):
		counter -= 1
		num = self.read_byte(file)
		
		if num & 0x80:
			num = num & 0x7F
			while True:
				counter -= 1
				c = self.read_byte(file)
				num = (num << 7) + (c & 0x7F)
				if not (c & 0x80):
					break
		
		return (num, counter)
	
	def __init__(self, file_name):
		self.tempo = 120
		try:
			file = open(file_name, 'rb')
			if file.read(4) != b'MThd': raise Exception('Not a MIDI file')
			self.file_name = file_name
			size = struct.unpack('>i', file.read(4))[0]
			if size != 6: raise Exception('Unusual MIDI file with non-6 sized header')
			self.format = struct.unpack('>h', file.read(2))[0]
			self.track_count = struct.unpack('>h', file.read(2))[0]
			self.time_division = struct.unpack('>h', file.read(2))[0]

			# Now to fill out the arrays with the notes
			self.tracks = []
			for i in range(0, self.track_count):
				self.tracks.append([])

			for nn, track in enumerate(self.tracks):
				abs_time = 0.

				if file.read(4) != b'MTrk': raise Exception('Not a valid track')
				size = struct.unpack('>i', file.read(4))[0]

				# To keep track of running status
				last_flag = None
				while size > 0:
					delta, size = self.read_variable_length(file, size)
					delta /= float(self.time_division)
					abs_time += delta

					size -= 1
					flag = self.read_byte(file)
					# Sysex messages
					if flag == 0xF0 or flag == 0xF7:
						# print "Sysex"
						while True:
							size -= 1
							if self.read_byte(file) == 0xF7: break
					# Meta messages
					elif flag == 0xFF:
						size -= 1
						type = self.read_byte(file)
						if type == 0x2F:	# end of track event
							self.read_byte(file)
							size -= 1
							break
						print("Meta: " + str(type))
						length, size = self.read_variable_length(file, size)
						message = file.read(length)
						# if type not in [0x0, 0x7, 0x20, 0x2F, 0x51, 0x54, 0x58, 0x59, 0x7F]:
						print(length, message)
						if type == 0x51:	# qpm/bpm
							# http://www.recordingblogs.com/sa/Wiki?topic=MIDI+Set+Tempo+meta+message
							self.tempo = 6e7 / struct.unpack('>i', b'\x00' + message)[0]
							print("tempo =", self.tempo, "bpm")
					# MIDI messages
					else:
						if flag & 0x80:
							type_and_channel = flag
							size -= 1
							param1 = self.read_byte(file)
							last_flag = flag
						else:
							type_and_channel = last_flag
							param1 = flag
						type = ((type_and_channel & 0xF0) >> 4)
						channel = type_and_channel & 0xF
						if type == 0xC:	# detect MIDI program change
							print("program change, channel", channel, "=", param1)
							continue
						size -= 1
						param2 = self.read_byte(file)
						
						# detect MIDI ons and MIDI offs
						if type == 0x9:
							track.append(Note(channel, param1, param2, abs_time))
						elif type == 0x8:
							for note in reversed(track):
								if note.channel == channel and note.pitch == param1:
									note.duration = abs_time - note.start
									break

		except Exception as e:
			print("Cannot parse MIDI file: " + str(e))
		finally:
			file.close()
	
	def __str__(self):
		s = ""
		for i, track in enumerate(self.tracks):
			s += "Track " + str(i+1) + "\n"
			for note in track:
				s += str(note) + "\n"
		return s

def getdur(a, b):
	"Calculate note length for PySynth"
	return 4 / (b - a)

if __name__ == "__main__":
	import sys
	m = MidiFile(sys.argv[1])
	if len(sys.argv) > 2:
		tracknum = int(sys.argv[2])
	else:
		tracknum = 1
	if len(sys.argv) > 3:
		filename = sys.argv[3]
	else:
		filename = "midi.wav"
	print()
	print("Track first notes")
	for t, n in enumerate(m.tracks):
		if len(n) > 0:
			print(t, n[0], len(n))
	song = []
	notes = {}

	def getnote(q):
		for x in q.keys():
			if q[x] >= 0:
				return x
		return None

	def gettotal():
		t = 0
		for x, y in song:
			t += 4 / y
		return t

	for n in m.tracks[tracknum]:
		print(n)
		nn = str(n).split()
		start, stop = float(nn[2]), float(nn[3])

		if start != stop:	# note ends because of NOTE OFF event
			if start - gettotal() > 0:
				song.append(('r', getdur(gettotal(), start)))
				print("r1")
			song.append((nn[0].lower(), getdur(start, stop)))
		elif float(nn[1]) == 0 and notes.get(nn[0].lower(), -1) >= 0: # note ends because of NOTE ON with velocity = 0
			if notes[nn[0].lower()] - gettotal() > 0:
				song.append(('r', getdur(gettotal(), notes[nn[0].lower()])))
				print("r2")
			song.append((nn[0].lower(), getdur(notes[nn[0].lower()], start)))
			notes[nn[0].lower()] = -1
		elif float(nn[1]) > 0 and notes.get(nn[0].lower(), -1) == -1: # note ends because of new note
			old = getnote(notes)
			if old != None:
				if notes[old] != start:
					song.append((old, getdur(notes[old], start)))
				notes[old] = -1
			elif start - gettotal() > 0:
				song.append(('r', getdur(gettotal(), start)))
				print("r3")
			notes[nn[0].lower()] = start
	print()
	print("Song")
	print(song)
	if "--syn_b" in sys.argv:
		import pysynth_b as pysynth
	elif "--syn_s" in sys.argv:
		import pysynth_s as pysynth
	elif "--syn_e" in sys.argv:
		import pysynth_e as pysynth
	elif "--syn_c" in sys.argv:
		import pysynth_c as pysynth
	elif "--syn_d" in sys.argv:
		import pysynth_d as pysynth
	elif "--syn_p" in sys.argv:
		import pysynth_p as pysynth
	elif "--syn_samp" in sys.argv:
		import pysynth_samp as pysynth
	else:
		import pysynth
	pysynth.make_wav(song, fn = filename, bpm = m.tempo)

