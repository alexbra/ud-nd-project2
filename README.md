I’ve choose to examine Tacoma, WA. It is the place where live my close friend with his wife and children. The second reason is I won’t select a big city. 
Here's the link to my map:
[http://www.openstreetmap.org/export#map=12/47.2220/-122.3860][osmap]

##Problems encountered in my map

I've made about 10 iterations of map audit and examine osm file for the following:

1.Validate addr:street tag (extended Lesson 6 example)
2.Validate Website address and checked if url exists or available
3.Existing <tag k="name" > for all amenity type nodes 
4.Validate zip code
5.Checked if deprecated features exists 

###`<tag k =”addr:street”>`

####Problem description

Street name in many cases looks like [SW|SE|NW|NE|N|S etc.] street_name [street type][SW|SE|NW|NE|N|S etc.]
I added some additional conditions in rule from lesson 6. All abbreviations such as SW, SE, S.E., S.W. etc will replaced full names like Southwest, Southeast…

####Audit output example:

```
Street types:
Northeast
West
St.
street
http://local.safeway.com/wa/tacoma-1594.html
........
410
Ave
NW
South
```

It seems like something wrong

####Solution

To solve this problem I used Regular Expressions:
``` 
mapping = {
    "St": "Street",
    "St.": "Street",
    "Ave": "Avenue",
    "Rd." : "Road",
	..........
		
	        "N.W." : "Northwest",
    "N." : "North",
    "S ":"South"
}
 
pattern = re.compile(r'\b(' + '|'.join(mapping.keys()) + r')\b')
```
As a result I received list of fixed street addresses.

>It is extremely important check whole words from mapping keys. For example, to ignore "St" if it appears as part of other word.

###`<tag k= “website”>`

####Problem description

The tag with k="website" has an URL as a value. There are two possible problems:

•	Incorrect URL format
•	Broken URL or unavailable website

```
Audit output example
Broken urls:
http://www.iaff726.org
http:///
http://www.
.........
http://www5.riteaid.com/savenow/locator/store-results?storenum=5186
http://(253) 853-4653
```

####Solution

1st Step. Parse and validate URL. If need fix it. To validate URL I used regular expressions: 

```url_re = re.compile(r'^(http|https|git|ftp+):\/\/([^\/:]+)(:\d*)?([^# ]*)', re.IGNORECASE)```

One of the appeared problems was mistakes in URL prefix. For example, `http//` or `http:/`
To fix these mistakes I create map:

```url_sub_pattern = re.compile(r'(http://http://|http:/|http//|http:)', re.IGNORECASE)```

2nd step. Check if URL works. Requests library is very useful for it. ( [https://pypi.python.org/pypi/requests][1] )
Script send HTTP requests to every URL from osm file and receive response code.  
If code equal to __404 or equal or greater __500 (server error) than URL has some problems. 
If URL unavailable, script would ignore it and not to add into database (more about HTTP status codes here [https://en.wikipedia.org/wiki/List_of_HTTP_status_codes][List_of_HTTP_status_codes] )

>URL check takes most of scripts launching time. In this case it's suits me, but in case of bigger osm file it'll unacceptable.


###`<tag k=”addr:postalcode”>`

####Problem description

To validate Zip Code I used RegEx:

```zip_code_re = re.compile(r'^\d{5}(-\d{4})?$')```

####Solution
Only one zip code looks like incorrect. In this case easier to fix code manually.


###`<node><tag k = ‘amenity’>`

####Problem description

Not all amenity type nodes has tag  `<tag k="name">`

Audit result
```
Amenities without name:
public_building
car_wash
telephone
..........
bicycle_parking
fire_station
place_of_worship
school
restaurant
```

Solution
For those sityations I create name as a value of amenity tag and write it in database.

```node["name"] = val.attrib['v'].capitalize().replace('_', ' ')```

For example: place_of_worship => Place of worship

###Deprecated features

####Problem description

There are some tags which has deprecated features.
in according to [http://wiki.openstreetmap.org/wiki/Deprecated_features][Deprecated_features]

>"OpenStreetMap does not have "banned features", as anybody is allowed and encouraged to use any tag they think is useful. 
>However, from time to time the wiki community suggests a new feature instead of an older one, to improve tagging clarity or structure."

I choose most frequency elements from deprecated features table. 
There are `building=entrance` (72 799 times appear in the nodes of all OSM database) and `natural=land` (46 106 times appear in the nodes of all OSM database). 
For example, instead of `building=entrance` more convenient use `entrance=*`. Entrance can be equal to the following ( yes | main | exit | service | emergency | staircase | home )

Audit output
```
Old_tags:
building=entrance
```

So, there is only one type of deprecated features detected on my map area

####Solution
All automatic or semiautomatic changes for deprecated features are disable. Thus, I can only output all Nodes with such elements.

##Overview of the data

1. size of the file  - 63 327 Kb
2. number of unique users  - 266 
3. number of nodes and ways:

	- nodes – 263688
	- ways – 29422 

4. Furthermore, there are other features of tag <tag> exists on this map:

###Some queries to MongoDB 

Frequently met URLs and its quantity:
```
pipeline = [{"$match" : {"website": {"$exists":True}}},
            {"$group" : {"_id":"$website",
                         "count":{"$sum":1}}},
            {"$sort": {"count":-1}},
            {"$limit" : 10}
            ]

websites = db.tacomaosm.aggregate(pipeline)
```

Ways without nodes (“ndrf” field size = 0):
```
query = {"type":"way", "ndrf":{"$size":0}}
ways = db.tacomaosm.find(query)
print '\nWays without nodes -', ways.count()
```

Quantity of deprecated features created by user:
```
pipeline = [{"$match" : {"building": "entrance"}},
            {"$group" : {"_id":"$created.user",
                         "count":{"$sum":1}}},
            {"$sort": {"count":-1}}
            ]
deprecated = db.tacomaosm.aggregate(pipeline)
```

##Other ideas about the datasets

Before this project I'd never used open street maps. It’s amazing!
So, as a newbie in OSM I would like to share some of my ideas about dataset.

###addr:street tag 
Street address validation is one of the most complicated task. Furthermore, every country has own rules and traditions address writing.
There are some possible additions for validate street address function:

- Often addresses writes in lower or upper cases.  <address>.lower().title() methods can capitalize all words in address. There are one tricky moment. We can’t capitalize such words as th, nd, rd.
- Also should be careful with replace such as St.=>Street. "St." can be not STREET but SAINT

###Website tag 

Method which I apply to check URL availability works not so fast. Script execution time slows in several times.
It's main shortage of this method.
To improve website check should execute only first step (URL validation).
Second step (website availability) will be run after import data into the database as a server script.

However, full URL validation on the first stage allows getting more clear data.Solution which approach to choose depends on the situation and application where data were used.

###List of languages 
In cases when object has descriptions on several languages, for example:
```
	<tag k="name:en" v="Delta Bank"/>
	<tag k="name:ru" v="Äåëüòà Áàíê"/>
	<tag k="name:uk" v="Äåëüòà Áàíê"/>
```
In MongoDB document structure may add "name_lngs" subdictioanry:
```
“name_lngs” : { “ru”  :  “”,
		   “uk” :  “”,
		    “es” :  “”
}
```

###Object alias 

Sometimes, there are more widespread aliases rather than official name of places. 
Goes so far as official name nobody knows unless documents and maps :)

Also, it'll be good to save old names of places and streets. Especially, when it's renamed.
For example, Kyiv city government decided to rename more than 40 streets in the city. 
Not all people get used to and will learn it quickly. 

In both cases could use tag `<tag k='alias'>`



[1]: [https://pypi.python.org/pypi/requests] 
[osmap]:[http://www.openstreetmap.org/export#map=12/47.2220/-122.3860]
[List_of_HTTP_status_codes]: [https://en.wikipedia.org/wiki/List_of_HTTP_status_codes]
[Deprecated_features]:[http://wiki.openstreetmap.org/wiki/Deprecated_features]