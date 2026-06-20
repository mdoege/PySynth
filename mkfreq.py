#!/usr/bin/env python

##########################################################################
# Compute and print piano key frequency table
##########################################################################

from __future__ import division

pitchhz, keynum = {}, {}

# English note names
keys_s = ("a", "a#", "b", "c", "c#", "d", "d#", "e", "f", "f#", "g", "g#")
keys_sf = ("a", "bb", "cb", "b#", "db", "d", "eb", "fb", "e#", "gb", "g", "ab")

# Romance-language note names
keys_doremi_s = ("la", "la#", "si", "do", "do#", "re", "re#", "mi", "fa", "fa#", "sol", "sol#")
keys_doremi_sf = ("la", "sib", "dob", "si#", "reb", "re", "mib", "fab", "mi#", "solb", "sol", "lab")

key_names = [keys_s, keys_sf, keys_doremi_s, keys_doremi_sf]

def getfreq(pr=False):
    if pr:
        print("Piano key frequencies (for equal temperament):")
        print("Key number\tScientific name\tFrequency (Hz)")

    for k in range(88):
        freq = 27.5 * 2.0 ** (k / 12.0)
        oct = (k + 9) // 12

        for i, keys in enumerate(key_names):
            note = "%s%u" % (keys[k % 12], oct)
            pitchhz[note] = freq
            keynum[note] = k
            pitchhz[note.upper()] = freq
            keynum[note.upper()] = k

            # print English note names with sharp accidentals
            if i == 0 and pr:
                print("%10u\t%15s\t%14.2f" % (k + 1, note.upper(), freq))

    # print(pitchhz)
    return pitchhz, keynum


# construct filenames for Salamander piano samples

sampfn = {}
facs = 1, 2 ** (1 / 12), 2 ** (2 / 12)
nam = "A", "C", "D#", "F#"


def getfn(layer):
    for k in range(88):
        oct = (k + 9) // 12

        sampfn[k] = "%s%uv%u.wav" % (nam[(k // 3) % 4], oct, layer), facs[k % 3]
    return sampfn


# x = getfn()
# for a in x:
#    print(a, x[a])

if __name__ == "__main__":
    p, k = getfreq(pr=True)
