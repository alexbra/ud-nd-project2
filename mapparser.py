#!/usr/bin/env python
# -*- coding: utf-8 -*-

import xml.etree.ElementTree as ET
import pprint

def count_tags(filename):
    d ={}
    for event, elem in ET.iterparse(filename):
        if elem.tag in d.keys():
            d[elem.tag]+=1
        else:
            d[elem.tag]=1
            
    return d

print count_tags('map.osm')
