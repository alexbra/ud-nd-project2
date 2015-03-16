import xml.etree.ElementTree as ET
import pprint
import re

lower = re.compile(r'^([a-z]|_)*$')
lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

amenities = {}
leisure = {}
railway = {}
public_transport = {}
shop = {}
sport = {}
tourism = {}
emergency = {}

def key_type(element, keys):
   
    if element.tag == "tag":
        """
        if lower.match(element.attrib['k']):
            keys['lower']+=1
        elif lower_colon.match(element.attrib['k']):
            keys['lower_colon']+=1
        elif problemchars.match(element.attrib['k']):
            keys['problemchars']+=1
        else:
            keys['other']+=1
        """
        if problemchars.match(element.attrib['k']):
            keys['problemchars']+=1
            
        if element.attrib['k'] == 'name:en':
            keys['en']+=1
        elif element.attrib['k'] == 'name:ru':
            keys['ru']+=1
        elif element.attrib['k'] == 'name:uk':
            keys['uk']+=1
        
        if element.attrib['k'] == 'amenity' and element.attrib['v']!= '':
            if element.attrib['v'] in amenities.keys():
                amenities[element.attrib['v']]+=1
            else:
                amenities[element.attrib['v']] = 1
        if element.attrib['k'] == 'leisure' and element.attrib['v']!= '':
            if element.attrib['v'] in leisure.keys():
                leisure[element.attrib['v']]+=1
            else:
                leisure[element.attrib['v']] = 1
        if element.attrib['k'] == 'railway' and element.attrib['v']!= '':
            if element.attrib['v'] in railway.keys():
                railway[element.attrib['v']]+=1
            else:
                railway[element.attrib['v']] = 1
        if element.attrib['k'] == 'public_transport' and element.attrib['v']!= '':
            if element.attrib['v'] in public_transport.keys():
                public_transport[element.attrib['v']]+=1
            else:
                public_transport[element.attrib['v']] = 1
        if element.attrib['k'] == 'shop' and element.attrib['v']!= '':
            if element.attrib['v'] in shop.keys():
                shop[element.attrib['v']]+=1
            else:
                shop[element.attrib['v']] = 1
        if element.attrib['k'] == 'sport' and element.attrib['v']!= '':
            if element.attrib['v'] in sport.keys():
                sport[element.attrib['v']]+=1
            else:
                sport[element.attrib['v']] = 1
        if element.attrib['k'] == 'tourism' and element.attrib['v']!= '':
            if element.attrib['v'] in tourism.keys():
                tourism[element.attrib['v']]+=1
            else:
                tourism[element.attrib['v']] = 1                
        if element.attrib['k'] == 'emergency' and element.attrib['v']!= '':
            if element.attrib['v'] in emergency.keys():
                emergency[element.attrib['v']]+=1
            else:
                emergency[element.attrib['v']] = 1  
    return keys



def process_map(filename):
 
    keys = {"lower": 0, "lower_colon": 0, "problemchars": 0, "other": 0, "en":0, "ru":0, "uk":0}
    for _, element in ET.iterparse(filename):
        keys = key_type(element, keys)
    print 'amenities\n', amenities, '\n', 'leisure\n', leisure,  '\n', 'railway\n', railway,  '\n', 'public_transport\n', public_transport,  '\n', 'shop\n', shop,  '\n', 'sport\n', sport,  '\n', 'tourism\n', tourism,  '\n', 'emergency\n', emergency
 
    return keys
process_map('tacoma.osm')
