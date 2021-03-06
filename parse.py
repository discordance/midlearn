import os
import midi
from random import randint
import numpy as np
from pymongo import MongoClient
import sys
from utils import compress, decompress

# make database
client = MongoClient('localhost', 27017)
db = client.midibase
collection = db.beats_nolabel

BEAT_DIV = 32

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

def complete_sequence(sequence):
    """
        Make sequences %8 number or bars
    """
    while (len(sequence)/float(BEAT_DIV)/4.0)%8.0 != 0.0:
        try:
            sequence.append([0, 0, 0, 0, 0, 0, 0, 0, 0.0])
        except:
            break;
    return sequence

def add_step(sequence, tick, event):
    """
        Incrementally build a sequence
    """
    blank_vec = [0, 0, 0, 0, 0, 0, 0, 0, 0.0]
    # get vec
    if len(sequence)-1 >= tick:
        tick_vec = sequence[tick]
    else:
        tick_vec = [0, 0, 0, 0, 0, 0, 0, 0, 0.75]
    # mutate vec
    if event.pitch == 36:
        tick_vec[0] = 1
    elif event.pitch == 41:
        tick_vec[1] = 1
    elif event.pitch == 48:
        tick_vec[2] = 1
    elif event.pitch == 61:
        tick_vec[3] = 1
    elif event.pitch == 63:
        tick_vec[4] = 1
    elif event.pitch == 40:
        tick_vec[5] = 1
    elif event.pitch == 42:
        tick_vec[6] = 1
    elif event.pitch == 49:
        tick_vec[7] = 1
    # avg velocity
    tick_vec[8] = (tick_vec[8]+(event.velocity/127.0))/2
    # increment
    if len(sequence)-1 < tick:
        while (len(sequence)-1) < (tick-1):
            sequence.append(blank_vec)
        sequence.append(tick_vec)
    return sequence

def rescale_pitch(event):
    """
        Contraint pitch
    """
    kick_map = [35,36]
    lowperc_map = [41,45,47]
    hiperc_map = [43,48,50,56]
    # extra
    lowld_map = [61,64,66,68,77]
    hiwld_map = [60,62,63,65,67,76,78,79]
    #
    snare_map = [37,38,39,40]
    hat_map = [42,44,53,54,58,69,70,75,80,81]
    cy_map = [46,49,51,52,55,57,59]

    if event.pitch in kick_map:
        event.pitch = 36
    elif event.pitch in lowperc_map:
        event.pitch = 41
    elif event.pitch in hiperc_map:
        event.pitch = 48
    elif event.pitch in lowld_map:
        event.pitch = 61
    elif event.pitch in hiwld_map:
        event.pitch = 63
    elif event.pitch in snare_map:
        event.pitch = 40
    elif event.pitch in hat_map:
        event.pitch = 42
    elif event.pitch in cy_map:
        event.pitch = 49
    return event


files = []
for root, directories, filenames in os.walk('/Users/nunja/Documents/Lab/MIDI/BIGDATAM2'):
    for filename in filenames:
        files.append(os.path.join(root,filename))

files = [ file for file in files if file.endswith( ('.mid','.midi', '.MID') ) ]
ct = 102599
for f in files[ct:len(files)-1]:
    try:
        patterns = midi.read_midifile(f)
    except:
        continue;
    resolution = patterns.resolution
    tick = resolution/BEAT_DIV
    if tick == 0:
        continue;
    drpattern = midi.Pattern()
    drpattern.resolution = patterns.resolution
    # define sequence here will concat tracks :)
    sequence = []
    for track in patterns:
        drumtrack = False
        drtrack = midi.Track()
        tck_ct = 0
        evt_ct = 0
        for event in track:
            if type(event) == type(midi.events.NoteOnEvent()) or \
                type(event) == type(midi.events.NoteOffEvent()):
                    if event.channel == 9:
                        if evt_ct == 0:
                            event.tick = 0
                        drumtrack = True
                        drtrack.append(rescale_pitch(event))
                        tck_ct+=event.tick
                        evt_ct+=1
                        if type(event) == type(midi.events.NoteOnEvent()):
                            try:
                                add_step(sequence, tck_ct/tick, event)
                            except:
                                continue;

                    else:
                        drumtrack = False
            elif type(event) == type(midi.events.EndOfTrackEvent()):
                if drumtrack:
                    drtrack.append(event)
        if drumtrack:
            # finish this sequnce
            complete_sequence(sequence)
            if len(sequence)/BEAT_DIV/4 >= 16:
                #drpattern.append(drtrack)
                #midi.write_midifile("out/"+`ct`+".mid", drpattern)
                #midi.write_midifile("out/"+`ct`+"_16.mid", seq2midi(sequence))
                try:
                    np_seq = np.array(sequence)
                    entry = {
                        "beat_num": ct,
                        "beat_zip": compress(np_seq),
                        "beat_bars": len(np_seq)/BEAT_DIV/4
                    }
                    collection.insert_one(entry)
                except:
                    e = sys.exc_info()[0]
                    print e
                    continue
                print ct
                ct+=1
