#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pprint
from bson.code import Code

def get_db():
    from pymongo import MongoClient
    client = MongoClient('mongodb://alexbra:avb790602@ds061548.mongolab.com:61548/datascience')
    db = client.datascience
    return db

db = get_db()

mapper = Code("""
    function() {
                  for (var key in this) { emit(key, null); }
               }
""")

reducer = Code("""
    function(key, stuff) { return null; }
""")

distinctThingFields = db.tacomaosm.map_reduce(mapper, reducer
    , out = {'inline' : 1}
    , full_response = True)
print 'Count of all exists keys in collection - ', len(distinctThingFields["results"])
print 'All keys in collection:'
for i in distinctThingFields["results"]:
    print i["_id"]

#count ways without nodes
query = {"type":"way", "ndrf":{"$size":0}}
ways = db.tacomaosm.find(query)
print '\nWays without nodes -', ways.count()


#list unique websites
pipeline = [{"$match" : {"url": {"$exists":True}}},
            {"$group" : {"_id":"$url",
                         "count":{"$sum":1}}},
            {"$sort": {"count":-1}}
            ]
websites = db.tacomaosm.aggregate(pipeline)
#print 'Websites found: ',websites["result"].count()
for result in websites["result"]:
    print result["_id"], '-', result["count"]


#подсчет, сколько каждый пользователь создал устаревших тегов
pipeline = [{"$match" : {"building": "entrance"}},
            {"$group" : {"_id":"$created.user",
                         "count":{"$sum":1}}},
            {"$sort": {"count":-1}}
            ]
deprecated = db.tacomaosm.aggregate(pipeline)
for result in deprecated["result"]:
    print result["_id"], '-', result["count"]
