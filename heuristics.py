from scipy.spatial.distance import *
import numpy as np
from pymongo import MongoClient
from utils import *
import midi

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
    theme = chunks[alldists[0][0]]
    diversity = np.array([tup[1] for tup in alldists]).mean()
    return {'diversity':diversity, 'theme':theme}
# # # # # # # # # #

np.set_printoptions(threshold=np.inf)
# mongo
client = MongoClient('localhost', 27017)
db = client.midibase
col_beats_nolabel = db.beats_nolabel
count = col_beats_nolabel.count()
first = col_beats_nolabel.find_one()
_id = first[u'_id']
for x in range(0, count-1):
    new = col_beats_nolabel.find_one({'_id':{'$gt':_id}})
    if new is None:
        exit()
    _id = new[u'_id']
    np_seq = decompress(new[u'beat_zip'])
    qutr = np.copy(np_seq)
    qutr.shape = (-1,128,9)
    tri = np.resize(np_seq,(len(qutr)*1.25,96,9)) # resize it
    #plot_seq(qutr[84], "d", 70, 8)
    qutr_div = diversity(qutr)
    tri_div = diversity(tri)
    if qutr_div['diversity'] < tri_div['diversity']:
        print new[u'beat_num'], '4/4'
    else:
        print new[u'beat_num'], '3/4'


# XA = np.array(
#     [
#         [1,0,0,0],
#         [0,0,0,0],
#         [1,0,0,0],
#         [0,0,0,0]
#     ]
# )
# XB = np.array(
#     [
#         [1,0,0,0],
#         [0,0,1,0],
#         [1,0,0,0],
#         [0,0,0,0]
#     ]
# )

# distance of two matrix
# print cdist(XA, XB, 'matching').diagonal().mean();
# mean two matrix
# print np.mean( np.array([ XA, XB ]), axis=0 )
