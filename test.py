from pymongo import MongoClient
from utils import *
import numpy as np
# make database
# client = MongoClient('localhost', 27017)
# db = client.midibase
# col_beats_nolabel = db.beats_nolabel
# count = col_beats_nolabel.count()
# first = col_beats_nolabel.find_one()
# _id = first[u'_id']
# for x in range(0, count-1):
#     new = col_beats_nolabel.find_one({'_id':{'$gt':_id}})
#     if new is None:
#         exit()
#     _id = new[u'_id']
#     print new[u'beat_num']
