#!/usr/bin/env python
# -*- coding: utf-8 -*-

import xml.etree.ElementTree as ET
import pprint
import re
import codecs
import json
import requests

lower = re.compile(r'^([a-z]|_)*$')
lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')
#zip code validation RegEx
zip_code_re = re.compile(r'^\d{5}(-\d{4})?$')
#mapping for fixng url prefix
url_sub_pattern = re.compile(r'(http:/|http//|http:)', re.IGNORECASE)
#url validation RegEx
url_re = re.compile(r'^(http|https|git|ftp+):\/\/([^\/:]+)(:\d*)?([^# ]*)', re.IGNORECASE)
street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)

CREATED = [ "version", "changeset", "timestamp", "user", "uid"]

expected = ["Street", "Avenue", "Boulevard", "Drive", "Court", "Place", "Square", "Lane", "Road", 
            "Trail", "Parkway"]

mapping = {
            "St " : "Street ",
            "St": "Street",
            "St.": "Street",
            "Ave": "Avenue",
            "Rd." : "Road",
            "Rd" : "Road",
            "Blvd" : "Boulevard",
            "SE" : "Southeast",
            "SW" : "Southwest",
            "NE" : "Northeast",
            "NW" : "Northwest",
            "Se" : "Southeast",
            "Sw" : "Southwest",
            "Ne" : "Northeast",
            "Nw" : "Northwest",            
            "S.E." : "Southeast",
            "S.W." : "Southwest",
            "N.E." : "Northeast",
            "N.W." : "Northwest",
            "N." : "North",
            "S ":"South",
            "S.":"South",
            "E.":"East",
            "W.":"West"            
          }

#pattern for fixing address
pattern = re.compile(r'\b(' + '|'.join(mapping.keys()) + r')\b')

def audit_address(name):
    m = street_type_re.search(name)
    if m:
        street_type = m.group()
        if street_type not in expected:
            try:
                name = pattern.sub(lambda x: mapping[x.group()], name).strip('.').strip()
            except:
                pass
    return name
            
#fix url function
def audit_url(url):
    if not url_re.search(url):
        url = 'http://'+url_sub_pattern.sub('',url)
    try:
        r = requests.options(url)
        status_code = r.status_code
        if status_code == 404 or status_code > 500:
            url = None
    except:
        url = None
    return url           
        
def shape_element(element):
    node = {}
    created_dict = {}
    address_dict = {}
    
    if element.tag == "node" or element.tag == "way" :
        node["id"] = element.attrib["id"]
        node["type"] = element.tag

        if 'visible' in element.attrib.keys():
            node["visible"] = element.attrib["visible"]
            
        for key in CREATED:
            if key in element.attrib.keys():
                created_dict[key] = element.attrib[key]
        node['created'] = created_dict
        
        if 'lat' in element.attrib.keys():
            node['pos'] = [float(element.attrib['lat']), float(element.attrib['lon'])]
        
        for val in element.iter("tag"):
            #ignore all problem chars
            if problemchars.match(val.attrib['k']) != None:
                continue
            #all address field add to dict
            elif val.attrib['k'].startswith('addr:'):
                if val.attrib['k'].count(':') == 1:
                    addr_key = val.attrib['k'].split(':')[1]
                    if val.attrib['k'] == 'addr:street':
                        address_value = audit_address(val.attrib['v'])
                        address_dict[addr_key] = address_value
                    else:
                        address_dict[addr_key] = val.attrib['v']
            #check website field
            elif val.attrib['k'] == 'website':
                url = audit_url(val.attrib['v'])
                if url!=None:
                    node["website"] = url
            #check amnity type node 
            elif val.attrib['k'] == 'amenity' and element.find("tag[@k='name']") is None:
                node["name"] = val.attrib['v'].capitalize().replace('_', ' ')
            else:
                node[val.attrib['k']] = val.attrib['v']
                               
        if element.tag == "way":
            node['ndrf'] = [ nd.attrib['ref'] for nd in element.iter("nd") ]
            
        if(address_dict!= {}):
            node["address"] = address_dict
        
        return node
    else:
        return None


def process_map(file_in, pretty = False):
    file_out = "{0}.json".format(file_in)
    data = []
    with codecs.open(file_out, "w") as fo:
        for _, element in ET.iterparse(file_in):
            el = shape_element(element)
            if el:
                data.append(el)
                if pretty:
                    fo.write(json.dumps(el, indent=2)+"\n")
                else:
                    fo.write(json.dumps(el) + "\n")
    
    return data

process_map('tacoma.osm')

"""
if __name__ == "__main__":
    
    from pymongo import MongoClient
    client = MongoClient("mongodb://<>:<>@ds061548.mongolab.com:61548/datascience")
    db = client.datascience

    #with open('tacoma.osm.json') as f:
    #    data = json.loads(f.read())
    #    insert_data(json_data, db)

"""
