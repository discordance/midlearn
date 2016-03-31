###
#db.runCommand(    { aggregate: "beats_nolabel",      pipeline: [   { $group: {     _id: { id: "$beat_zip" },     uniqueIds: { $addToSet: "$_id" },     count: { $sum: 1 }    } },    { $match: {      count: { $gte: 2 }    } },   { $sort : { count : -1} }, { $project: {uniqueIds:1, _id:0} } ,  { $limit : 100 } ],      allowDiskUse: true } )
# ##
from pymongo import MongoClient
# make database
client = MongoClient('localhost', 27017)
db = client.midibase
col_beats_nolabel = db.beats_nolabel
col_duplicates = db.beats_nolabel_duplicates

pipeline = [
    {"$group": {"_id": {"id": "$beat_zip"}, "uniqueIds": {"$addToSet": "$_id"}, "count": {"$sum": 1}}},
    {"$match": {"count": {"$gte": 2 }}},
    {"$sort": {"count": -1}},
    {"$project": {"uniqueIds":1, "_id":0}},
    #{"$limit": 100},
    {"$out": 'beats_nolabel_duplicates'}
]

db.command('aggregate', 'beats_nolabel', pipeline=pipeline, allowDiskUse=True)

for dup in col_duplicates.find():
    dup[u'uniqueIds'].pop(0)
    for _id in dup[u'uniqueIds']:
        col_beats_nolabel.delete_one({'_id':_id})
