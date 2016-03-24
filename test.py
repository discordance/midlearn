from pymongo import MongoClient
from utils import *
# make database
client = MongoClient('localhost', 27017)
db = client.midibase
col_beats_nolabel = db.beats_nolabel


ziped = col_beats_nolabel.find_one({'beat_num':89})[u'beat_zip']
print plot_seq(decompress(ziped))
