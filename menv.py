#!/usr/bin/env python

"""
Python Command Line Musical Interpreter for PySynth.
Pranav Ravichandran (me@onloop.net)
"""

import pysynth, pysynth_b, pysynth_s
from pyaudio import pyaudio
import wave
import sys
import os
import string

#Type 'help' to access.
helpContent = "------------------------------\nPySynth musical note interpreter.\nUsage: <Duration><Note> <Duration2><Note2> .... <DurationN><NoteN>\nOptional arguments:\n\t--bpm=Beats per minute [Default:120]\n\t--repeat=Number of bars [Default:1]\n\t--sound=Instrument [a = Flute/Organ, b = piano, s = plucked string, Default = a]\nSample: 1d 2c 4f --bpm=150 --repeat=2 --sound=s\nCommands: 'exit' and 'help'\n------------------------------"

usageHelp = "Notes are 'a' through 'g' of course,\noptionally with '#' or 'b' appended for sharps or flats.\nFinally the octave number (defaults to octave 4 if not given).\nAn asterisk at the end makes the note a little louder (useful for the beat).\n'r' is a rest.\n\nNote value is a number:\n1=Whole Note; 2=Half Note; 4=Quarter Note, etc.\nDotted notes can be written in two ways:\n1.33 = -2 = dotted half\n2.66 = -4 = dotted quarter\n5.33 = -8 = dotted eighth\n--------------------------------"

warningStr = "Improper Syntax - Type 'help' to see usage."

invalidCmd = "Non-existential command."

invalidOption = "Invalid Option."

class mEnv:
	cliInput = ''
	synthParam = []
	bpmVal = 0
	repeatVal = 0
	inputEntered = False
	instrument = ''
	trashFile = True 
	def __init__(self):
		''' Constructor class. '''

		# Get the user input.
		cliInput = raw_input(">>> ")

		self.parse(cliInput)
		
		# Different cases of input, when optional argument 'sound' is given.
		if self.instrument == 'a' or self.instrument == '':
			self.synthSounds(pysynth)
		elif self.instrument == 'b':
			self.synthSounds(pysynth_b)
		elif self.instrument == 's':
			self.synthSounds(pysynth_s)
		else:
			print invalidOption
			mEnv()

	def parse(self, cliInput):
		''' Parse command line input.'''

		# 'exit' command.
		if cliInput == 'exit':
			sys.exit()
		# 'help' command.
		if cliInput == 'help':
			print '\n' + helpContent + '\n' + usageHelp + '\n'
			mEnv()

		# List with whitespace as delimiter.
		cliInput = cliInput.split()
		self.synthParam = []
		
		for comp in cliInput:
			# Optional arguments.
			if comp.startswith('--'):
				comp = comp.strip('-')
				comp = comp.split('=')
				if comp[0] == 'bpm':
					try:
						self.bpmVal = int(comp[1])
					except IndexError:
						print warningStr
						mEnv()
				elif comp[0] == 'repeat':
					try:
						self.repeatVal = int(comp[1]) - 1
					except IndexError:
						print warningStr
						mEnv()
				elif comp[0] == 'sound':
					try:
						self.instrument = str(comp[1])
					except IndexError:
						print warningStr
						mEnv()
				elif comp[0] == 'save':
					try:
						self.trashFile = False
					except IndexError:
						print warningStr
						mEnv()
				continue

			# Notes and beats.
			i = 0
			for alphanum in comp:
				if alphanum.isalpha():
					try:
						self.synthParam.append((comp[i:], int(comp[:i])))
					except ValueError:
						print invalidCmd 
						mEnv()
				
					break
				i += 1

	def play(self):
		''' Open the .wav file and play it.'''

		chunk = 1024
		wf = wave.open('temp.wav', 'rb')
		p = pyaudio.PyAudio()

		# open stream
		stream = p.open(format =
	         		p.get_format_from_width(wf.getsampwidth()),
        		        channels = wf.getnchannels(),
		                rate = wf.getframerate(),
		                output = True)

		# read data
		data = wf.readframes(chunk)

		# play stream
		while data != '':
		    stream.write(data)
		    data = wf.readframes(chunk)

		stream.stop_stream()
		stream.close()

		p.terminate()
	
	def removeFile(self):
		''' Delete the .wav file.'''
		
		if self.trashFile:
			os.remove('temp.wav')

	def synthSounds(self, renderSound):
		''' Render sound with pysynth_a, pysynth_b or pysynth_s based on user preference.'''

		try:
			# Different cases of input, when optional arguments 'bpm' and 'repeat' are given.
			if self.bpmVal and self.repeatVal:
				renderSound.make_wav(self.synthParam, fn = 'temp.wav', silent = True, bpm = self.bpmVal, repeat = self.repeatVal)
			elif self.bpmVal:
				renderSound.make_wav(self.synthParam, fn = 'temp.wav', silent = True, bpm = self.bpmVal)
			elif self.repeatVal:
				renderSound.make_wav(self.synthParam, fn = 'temp.wav', silent = True, repeat = self.repeatVal)
			else:
				renderSound.make_wav(self.synthParam, fn = 'temp.wav', silent = True)
		except KeyError:
			print warningStr 
			mEnv()



if __name__ == "__main__":
	# Print introductory help content.
	print helpContent

	# Interpreter loop.
	while True:
		a = mEnv()
		try:
			a.play()
		except:
			a.trashFile = False
			print 'Could not play file. Saved to temp.wav'
		a.removeFile()
