import midi
import numpy as np
from rstr_max.rstr_max import *
from pydash import filter_, max_
import matplotlib.pyplot as plt
import base64
import sys


def decompress(str):
    zipped = base64.decodestring(str)
    b64 = zipped.decode('zlib')
    arr = np.frombuffer(base64.decodestring(b64))
    rshaped = arr.reshape(len(arr)/7, 7)
    return rshaped

def compress(seq):
    b64 = base64.b64encode(seq)
    compressed = base64.encodestring(b64.encode('zlib'))
    return compressed

def plot_seq(seq):
    # seq indexes
    KK = []
    LT = []
    HT = []
    SN = []
    HH = []
    CY = []
    refs = [KK,LT,HT,SN,HH,CY]
    for time, evt in enumerate(seq):
        for idx, val in enumerate(evt[:6]):
            if val > 0:
                refs[idx].append(time)
    x = []
    y = []
    for idx, lst in enumerate((KK, LT, HT, SN, HH, CY)):
        for time in lst:
            x.append(time)
            y.append(idx)
    fig = plt.figure()
    plt.xlim((0,len(seq)))
    plt.ylim((-1,6))
    plt.yticks([0, 1, 2, 3, 4, 5], ['kick', 'lowperc', 'hiperc', 'snare', 'hihat', 'cymba'])
    plt.scatter(x, y, color='r', s=7, marker='|')
    # Get current size
    plt.show()


def seq2midi(sequence):
    """
        Transforms a sequence into midi file
    """
    mp = [36, 41, 48, 40, 42, 49]
    patt = midi.Pattern()
    track = midi.Track()
    patt.resolution = 192
    patt.append(track)
    evct = 0
    offset = 0
    for event in sequence:
        # NTE ON
        n = 0
        stamped = False
        for note in event:
            if note > 0.5 and n < 6:
                on_evt = midi.events.NoteOnEvent()
                on_evt.channel = 10
                on_evt.pitch = mp[n]
                on_evt.velocity = int(event[6]*127)
                if stamped == False and evct > 0:
                    on_evt.tick = patt.resolution/8 + offset - patt.resolution/8
                    stamped = True
                else:
                    on_evt.tick = 0
                track.append(on_evt)
            n += 1
        if stamped == False:
            offset += patt.resolution/8
        else:
            offset = 0
        # NTE OFF
        n = 0
        stamped = False
        for note in event:
            if note > 0.5 and n < 6:
                off_evt = midi.events.NoteOffEvent()
                off_evt.channel = 10
                off_evt.pitch = mp[n]
                if stamped == False and evct > 0:
                    off_evt.tick = patt.resolution/8
                    stamped = True
                else:
                    off_evt.tick = 0
                track.append(off_evt)
            n += 1
        evct += 1
    return patt

# def encode(arr):
#     rez = ''
#     for st in arr:
#         b = ''.join([str(int(a)) for a in st[0:6]])
#         ch = chr(int(b, 2)+46)
#         rez += ch
#     return rez
# def bars_repeats(str):
#     """
#         Finds repeats by time signatures
#     """
#     repeats = str_repeats(str)
#     _44_repeats =  filter_(repeats, lambda x, k: len(k) >= 32 and len(k) < 64)
#     _34_repeats =  filter_(repeats, lambda x, k: len(k) >= 24 and len(k) < 32)
#     _22_repeats =  filter_(repeats, lambda x, k: len(k) >= 16 and len(k) < 24)
#     index = [
#         {"rythm":"4/4", "r": len(_44_repeats)},
#         {"rythm":"3/4", "r": len(_34_repeats)},
#         {"rythm":"2/2", "r": len(_22_repeats)},
#     ]
#     return max_(index, 'r')

# def str_repeats(str):
#     """
#         Finds repeats in a string
#     """
#     rstr = Rstr_max()
#     rstr.add_str(str)
#     r = rstr.go()
#     repdic = {}
#     for (offset_end, nb), (l, start_plage) in r.iteritems():
#         ss = rstr.global_suffix[offset_end-l:offset_end]
#         id_chaine = rstr.idxString[offset_end-1]
#         s = rstr.array_str[id_chaine]
#         repdic[ss] = {'str':ss,'repeat':nb, 'offsets':[]}
#         for o in range(start_plage, start_plage + nb):
#             offset_global = rstr.res[o]
#             offset = rstr.idxPos[offset_global]
#             id_str = rstr.idxString[offset_global]
#             repdic[ss]['offsets'].append(offset)
#     return repdic
