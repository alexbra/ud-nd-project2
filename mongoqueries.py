#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pprint
"""
This file include all queries to MongoDB
"""

def get_db():
    from pymongo import MongoClient
    client = MongoClient('localhost:27017')
    db = client.datascience
    return db

db = get_db()

print db.tacomaosm.count()

#list unique websites
pipeline = [{"$match" : {"website": {"$exists":True}}},
            {"$group" : {"_id":"$website",
                         "count":{"$sum":1}}},
            {"$sort": {"count":-1}},
            {"$limit" : 10}
            ]
websites = db.tacomaosm.aggregate(pipeline)

for result in websites["result"]:
    print result["_id"], '-', result["count"]

#count ways without nodes
query = {"type":"way", "ndrf":{"$size":0}}
ways = db.tacomaosm.find(query)
print '\nWays without nodes -', ways.count()

#counting of deprecated features grouped by user
pipeline = [{"$match" : {"building": "entrance"}},
            {"$group" : {"_id":"$created.user",
                         "count":{"$sum":1}}},
            {"$sort": {"count":-1}}
            ]
deprecated = db.tacomaosm.aggregate(pipeline)
for result in deprecated["result"]:
    print result["_id"], '-', result["count"]


