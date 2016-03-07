import midi
import numpy as np
from rstr_max.rstr_max import *

def str_repeats(str):
    rstr = Rstr_max()
    rstr.add_str(str)
    r = rstr.go()
    repdic = {}
    for (offset_end, nb), (l, start_plage) in r.iteritems():
        ss = rstr.global_suffix[offset_end-l:offset_end]
        id_chaine = rstr.idxString[offset_end-1]
        s = rstr.array_str[id_chaine]
        repdic[ss] = {'repeat':nb, 'offsets':[]}
        for o in range(start_plage, start_plage + nb):
            offset_global = rstr.res[o]
            offset = rstr.idxPos[offset_global]
            id_str = rstr.idxString[offset_global]
            repdic[ss]['offsets'].append(offset)
    return repdic


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
