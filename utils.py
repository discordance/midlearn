import midi
import numpy as np
import matplotlib.pyplot as plt
import base64
import sys

BEAT_DIV = 32

def decompress(str):
    zipped = base64.decodestring(str)
    b64 = zipped.decode('zlib')
    arr = np.frombuffer(base64.decodestring(b64))
    rshaped = arr.reshape(len(arr)/9, 9)
    return rshaped

def compress(seq):
    b64 = base64.b64encode(seq)
    compressed = base64.encodestring(b64.encode('zlib'))
    return compressed

def plot_seq(seq, marker='|', size='7', quant=32):
    # seq indexes
    KK = []
    LT = []
    HT = []
    LW = []
    HW = []
    SN = []
    HH = []
    CY = []
    refs = [KK,LT,HT,LW,HW,SN,HH,CY]
    for time, evt in enumerate(seq):
        for idx, val in enumerate(evt[:8]):
            if val > 0:
                refs[idx].append(time)
    x = []
    y = []
    for idx, lst in enumerate((KK, LT, HT, LW, HW, SN, HH, CY)):
        for time in lst:
            x.append(time)
            y.append(idx)
    fig = plt.figure()
    plt.xlim((0,len(seq)))
    plt.ylim((-1,8))
    plt.xticks(np.arange(0,len(seq),quant))
    plt.yticks([0, 1, 2, 3, 4, 5, 6, 7], ['kick', 'lowperc', 'hiperc', 'loworld', 'hiworld', 'snare', 'hihat', 'cymba'])
    plt.scatter(x, y, color='r', s=size, marker=marker)
    # Get current size
    plt.grid()
    plt.show()


def seq2midi(sequence):
    """
        Transforms a sequence into midi file
    """
    mp = [36, 41, 48, 61, 63, 40, 42, 49]
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
            if note > 0.5 and n < 8:
                on_evt = midi.events.NoteOnEvent()
                on_evt.channel = 10
                on_evt.pitch = mp[n]
                on_evt.velocity = int(event[8]*127)
                if stamped == False and evct > 0:
                    on_evt.tick = patt.resolution/BEAT_DIV + offset - patt.resolution/BEAT_DIV
                    stamped = True
                else:
                    on_evt.tick = 0
                track.append(on_evt)
            n += 1
        if stamped == False:
            offset += patt.resolution/BEAT_DIV
        else:
            offset = 0
        # NTE OFF
        n = 0
        stamped = False
        for note in event:
            if note > 0.5 and n < 8:
                off_evt = midi.events.NoteOffEvent()
                off_evt.channel = 10
                off_evt.pitch = mp[n]
                if stamped == False and evct > 0:
                    off_evt.tick = patt.resolution/BEAT_DIV
                    stamped = True
                else:
                    off_evt.tick = 0
                track.append(off_evt)
            n += 1
        evct += 1
    return patt
