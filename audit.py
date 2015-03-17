# -*- coding: utf-8 -*-
import xml.etree.cElementTree as ET
from collections import defaultdict
import re
import pprint
import requests

OSMFILE = "tacoma.osm"
street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)
#zip code validation RegEx
zip_code_re = re.compile(r'^\d{5}(-\d{4})?$')
#mapping for fixng url prefix
url_sub_pattern = re.compile(r'(http://http://|http:/|http//|http:)', re.IGNORECASE)
#url validation RegEx
url_re = re.compile(r'^(http|https|git|ftp+):\/\/([^\/:]+)(:\d*)?([^# ]*)', re.IGNORECASE)

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

#fix url function
def update_url(url): 
    if not url_re.search(url):
        url = 'http://'+url_sub_pattern.sub('',url)
    return url

#update address function
def update_street_name(name): 
    try:
        name = pattern.sub(lambda x: mapping[x.group()], name.strip())
    except:
        pass
    return name.strip('.')

def audit_street_type(street_types, street_name):
    global street_type_re
    m = street_type_re.search(street_name)
    if m:
        street_type = m.group()
        if street_type not in expected:
            street_types[street_type].add(street_name)

#audit url function
def audit_url(websites, url):
    url = update_url(url)
    r = requests.options(url)
    status_code = r.status_code
    try:
        
        
        print url, status_code
        if status_code == 404 or status_code > 500:
            websites.add(url)
    except:
        websites.add(url)
    
#audit zip code function    
def audit_zip_tag(zip_codes, elem):
    if not zip_code_re.match(elem.strip()):
        zip_codes.add(elem)

def is_street_name(elem):
    return (elem.attrib['k'] == "addr:street")

def is_zip_code(elem):
    return (elem.attrib['k'] == "addr:postcode")

def is_old_tag(elem):
    if elem.attrib['k'] == 'natural' and  elem.attrib['v'] == 'land' or elem.attrib['k'] == 'building' and  elem.attrib['v'] == 'entrance':
        return True
    else:
        return False

def audit(osmfile):
    street_names = set()
    zip_codes = set()
    ways_without_nodes = set()
    websites = set()
    amenities_without_names = set()
    old_tags = set()
    street_types = defaultdict(set)

    osm_file = open(osmfile, "r")
    
    for event, elem in ET.iterparse(osm_file, events=("start",)):
        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_street_name(tag):
                    audit_street_type( street_types, tag.attrib['v'] )
                elif tag.attrib['k'] == 'website':
                    audit_url( websites, tag.attrib['v'] )
                elif is_zip_code(tag):
                    audit_zip_tag( zip_codes, tag.attrib['v'] )
                #check if node type 'amenity' don't have Name tag 
                elif tag.attrib['k'] == 'amenity':
                    if elem.find("tag[@k='name']") is None:
                        amenities_without_names.add(tag.attrib['v'])
                #check if tag depreacted 
                elif is_old_tag(tag):
                    old_tags.add(tag.attrib['k']+'='+tag.attrib['v'])

    print 'Broken urls:'
    for p in websites:
        print p

    print '\nAmenities without name'
    for p in amenities_without_names:
        print p

    print '\nWrong zip codes:'
    for p in zip_codes:
        print p

    print '\nOld_tags:'
    for p in old_tags:
        print p        
    
    print '\nStreet names:'
    for p in street_types:
        print p        

    return street_types

street_types = audit(OSMFILE)

for st_type, ways in street_types.iteritems():
    for name in ways:
        better_name = update_street_name(name)
        print name, "=>", better_name
