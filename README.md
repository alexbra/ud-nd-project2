##Problems encountered in your map

I made about 10 iterations of map audit and examine osm file for the following:

1.	Validate addr:street tag (extended Lesson 6 example) 
2.	Validate Website address and checked if url exists or available
3.	Existing <tag k="name" > for all amenity type nodes 
4.	Validate zip code
5.	Checked if deprecated features exists 

###`<tag k =”addr:street”>`

####Problem description

Street name in many cases looks like [SW|SE|NW|NE|N|S etc.] street_name [street type][SW|SE|NW|NE|N|S etc.]
I added some additional conditions in rule from lesson 6. All abbreviations such as SW, SE, S.E., S.W. etc  will replaced full names like Southwest, Southeast…

####Audit output example:

  `
  Street types:
  Northeast
  West
  St.
  street
  http://local.safeway.com/wa/tacoma-1594.html
  ........
  410
  SE
  Blvd
  Ave
  NW
  South
  It seems like something wrong
  `

####Solution

To solve this problem I used Regular Expressions:

  <code> 
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
  </code>
