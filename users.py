import xml.etree.ElementTree as ET
import pprint
import re

def get_user(element):
    return element.attrib['uid']


def process_map(filename):
    users = set()
    for _, element in ET.iterparse(filename):
       if 'uid' in element.attrib:
            users.add(get_user(element))

    return users

print len(process_map('tacoma.osm'))
