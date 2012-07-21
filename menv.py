import pysynth
from pyaudio import pyaudio
import wave
import sys
import os
import string

helpContent = "PySynth musical note interpreter.\nUsage: <Duration><Note> <Duration2><Note2> .... <DurationN><NoteN>\nOptional arguments:\n\t--bpm=Beats per minute [Default:120]\n\t--repeat=Number of bars [Default:1]\nSample: 1d 2c 4f --bpm=150 --repeat=2\nCommands: 'exit' and 'help'"
usageHelp = "Notes are 'a' through 'g' of course,\noptionally with '#' or 'b' appended for sharps or flats.\nFinally the octave number (defaults to octave 4 if not given).\nAn asterisk at the end makes the note a little louder (useful for the beat).\n'r' is a rest.\n\nNote value is a number:\n1=Whole Note; 2=Half Note; 4=Quarter Note, etc.\nDotted notes can be written in two ways:\n1.33 = -2 = dotted half\n2.66 = -4 = dotted quarter\n5.33 = -8 = dotted eighth"

class mEnv:
	cliInput = ''
	synthParam = []
	bpmVal = 0
	repeatVal = 0
	inputEntered = False
	def __init__(self):
		cliInput = raw_input(">>> ")

		self.parse(cliInput)

		try:
			if self.bpmVal and self.repeatVal:
				pysynth.make_wav(self.synthParam, fn = 'temp.wav', silent = True, bpm = self.bpmVal, repeat = self.repeatVal)
			elif self.bpmVal:
				pysynth.make_wav(self.synthParam, fn = 'temp.wav', silent = True, bpm = self.bpmVal)
			elif self.repeatVal:
				pysynth.make_wav(self.synthParam, fn = 'temp.wav', silent = True, repeat = self.repeatVal)
			else:
				pysynth.make_wav(self.synthParam, fn = 'temp.wav', silent = True)
		except KeyError:
			print "Improper Syntax - Type 'help' to see usage."
			mEnv()

	def parse(self, cliInput):
		if cliInput == 'exit':
			sys.exit()
		if cliInput == 'help':
			print '\n' + helpContent + '\n-------------------------------------------\n' + usageHelp + '\n'
			mEnv()

		cliInput = cliInput.split()
		self.synthParam = []
		for comp in cliInput:
			if comp.startswith('--'):
				comp = comp.strip('-')
				comp = comp.split('=')
				if comp[0] == 'bpm':
					try:
						self.bpmVal = int(comp[1])
					except IndexError:
						print "Improper Syntax - Type 'help' to see usage."
						mEnv()
				if comp[0] == 'repeat':
					try:
						self.repeatVal = int(comp[1]) - 1
					except IndexError:
						print "Improper Syntax - Type 'help' to see usage."
						mEnv()
				continue

			i = 0
			for alphanum in comp:
				if alphanum.isalpha():
					try:
						self.synthParam.append((comp[i:], int(comp[:i])))
					except ValueError:
						print "Non-existential Command."
						mEnv()
				
					break
				i += 1

	def play(self):
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
		os.remove('temp.wav')

if __name__ == "__main__":
	print helpContent
	while True:
		a = mEnv()
		a.play()
		a.removeFile()
