from scipy.spatial.distance import *
import numpy as np
from pymongo import MongoClient
from utils import *
import midi
from multiprocessing import Pool as ThreadPool

# db.beats_nolabel.update({heuristics:{$exists:true}},{$unset:{heuristics:""}},{multi:true})
# db.beats_nolabel.count({heuristics:{$exists:true}})
np.set_printoptions(threshold=np.inf)
# mongo conf
client = MongoClient('localhost', 27017)
db = client.midibase
col_beats_nolabel = db.beats_nolabel

def diversity(chunks):
    """
    diversity stats
    """
    alldists = []
    for i in range(0,chunks.shape[0]):
        this = chunks[i]
        others = chunks[np.arange(len(chunks))!=i]
        distances = []
        for j in range(0,others.shape[0]):
            distances.append(cdist(this, others[j], 'matching').diagonal().mean())
        alldists.append(( i, np.array(distances).mean() ))
    alldists.sort(key=lambda tup: tup[1])
    allidx = 0
    theme = chunks[alldists[allidx][0]]
    while theme.mean() <= 0.0:
        allidx += 1
        theme = chunks[alldists[allidx][0]]
    diversity = np.array([tup[1] for tup in alldists]).mean()
    return {'diversity':diversity, 'theme':theme}

def get_batch(_id, col, limit):
    if _id is not None:
        return list(col.find({'_id':{'$gt':_id}, "heuristics":{"$exists":False}}).limit(limit))
    else:
        return list(col.find({"heuristics":{"$exists":False}}).limit(limit))

def gridicity(np_seq):
    nb_onsets = 0
    nb_grid = 0
    nb_off_grid = 0
    for x in range(0, len(np_seq)):
        subarr = np_seq[x]
        if len(np.where(subarr > 0.0)[0]) > 0:
            nb_onsets += 1
            if x % (32/4) == 0:
                nb_grid += 1
            else:
                nb_off_grid += 1
    return nb_grid/float(nb_onsets)

def heuristics(beat):
    np_seq = decompress(beat[u'beat_zip'])
    qutr = np.copy(np_seq)
    gridness = gridicity(np_seq)
    qutr.shape = (-1,128,9)
    tri = np.resize(np_seq,(len(qutr)*1.25,96,9)) # resize it
    qutr_div = diversity(qutr)
    tri_div = diversity(tri)
    # heuristics to store
    time_sig = 4
    density = 0
    theme = None
    divers = 0
    drum_avg = None
    bars = 0
    #
    if qutr_div['diversity'] < tri_div['diversity']:
        time_sig = 4
        theme = qutr_div['theme']
        divers = qutr_div['diversity']
        drum_avg = qutr.mean(axis=1).mean(axis=0)
        density = qutr.mean()
        bars = qutr.shape[0]
    else:
        time_sig = 3
        theme = tri_div['theme']
        divers = tri_div['diversity']
        drum_avg = tri.mean(axis=1).mean(axis=0)
        density = tri.mean()
        bars = tri.shape[0]

    res = {
        "beat_id": beat[u'_id'],
        "time_sig":time_sig,
        "theme_zip":compress(theme),
        "diversity": divers,
        "density": density,
        "drum_avg": drum_avg.tolist(),
        "bars": bars,
        "gridness": gridness
    }
    return res

# # # # # # # # # #

def nbatch(_id, limit):
    print 'starting a batch of', limit
    batch = get_batch(_id, col_beats_nolabel, limit)
    last_id = batch[-1][u'_id']
    pool = ThreadPool(8)
    results = pool.map(heuristics, batch)
    pool.close()
    pool.join()
    for i in range(0, len(results)):
        col_beats_nolabel.update_one(
            {"_id": results[i]["beat_id"]},
            {"$set": {"heuristics": results[i]}}
        )
    print 'next batch'
    nbatch(last_id, limit)

nbatch(None, 50)
