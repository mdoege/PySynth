##########################################################################
# Compute and print piano key frequency table
##########################################################################

pitchhz, keynum = {}, {}

keys_s = ('a', 'a#', 'b',  'c',  'c#', 'd', 'd#', 'e',  'f',  'f#', 'g', 'g#')
keys_f = ('a', 'bb', 'b',  'c',  'db', 'd', 'eb', 'e',  'f',  'gb', 'g', 'ab')
keys_e = ('a', 'bb', 'cb', 'b#', 'db', 'd', 'eb', 'fb', 'e#', 'gb', 'g', 'ab')

def getfreq(pr = False):
	if pr:
		print("Piano key frequencies (for equal temperament):")
		print("Key number\tScientific name\tFrequency (Hz)")
	for k in range(88):
		freq = 27.5 * 2.**(k/12.)
		oct = (k + 9) // 12
		note = '%s%u' % (keys_s[k%12], oct)
		if pr:
			print("%10u\t%15s\t%14.2f" % (k+1, note.upper(), freq))
		pitchhz[note] = freq
		keynum[note] = k
		note = '%s%u' % (keys_f[k%12], oct)
		pitchhz[note] = freq
		keynum[note] = k
		note = '%s%u' % (keys_e[k%12], oct)
		pitchhz[note] = freq
		keynum[note] = k
	return pitchhz, keynum


# construct filnames for Salamander piano samples

sampfn = {}
facs = 1, 2**(1/12), 2**(2/12)
nam = "A", "C", "D#", "F#"

def getfn(layer):
	for k in range(88):
		oct = (k + 9) // 12

		sampfn[k] = "%s%uv%u.wav" % (nam[(k // 3) % 4], oct, layer), facs[k % 3]
	return sampfn

#x = getfn()
#for a in x:
#	print(a, x[a])


