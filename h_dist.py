from scipy.spatial.distance import *
import numpy as np
from pymongo import MongoClient
from utils import *

np.set_printoptions(threshold=np.inf)
# mongo
client = MongoClient('localhost', 27017)
db = client.midibase
col_beats_nolabel = db.beats_nolabel
count = col_beats_nolabel.count()
first = col_beats_nolabel.find_one()
_id = first[u'_id']
for x in range(0, 1):
    new = col_beats_nolabel.find_one({'_id':{'$gt':_id}})
    if new is None:
        exit()
    _id = new[u'_id']
    np_seq = decompress(new[u'beat_zip'])
    np_seq.shape = (-1,128,9) # reshape it
    plot_seq(np_seq[1], 'd', 70)
    #np.mean(np_seq, axis=0)
    # for i in range(0,np_seq.shape[0]):
    #     this = np_seq[i]
    #     others = np_seq[np.arange(len(np_seq))!=i]
    #     for j in range(0,others.shape[0]):
    #         print cdist(this, others[j], 'matching').diagonal().mean();
    #     print "------------------------------------------------------------------------"


    # for a, b in zip(np_seq[::2], np_seq[1::2]):
    #     print a.shape, b.shape
    #print np_seq[0][0]

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
