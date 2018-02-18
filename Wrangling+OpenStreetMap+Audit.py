
# coding: utf-8

# # Data Wrangle  - Creating and Auditing the Data Set 
# 
# ### Downloaded the file from https://www.openstreetmap.org/relation/324211 
# 
# ### 1. Creating the Sample Toronto OSM file.

# In[1]:


#!/usr/bin/env python


import xml.etree.ElementTree as ET  # Use cElementTree or lxml if too slow

OSM_FILE = "toronto_canada.osm"  # Replace this with your osm file
SAMPLE_FILE = "torontosample.osm"

k = 15 # Parameter: take every k-th top level element

def get_element(osm_file, tags=('node', 'way', 'relation')):
    """Yield element if it is the right type of tag

    Reference:
    http://stackoverflow.com/questions/3095434/inserting-newlines-in-xml-file-generated-via-xml-etree-elementtree-in-python
    """
    context = iter(ET.iterparse(osm_file, events=('start', 'end')))
    _, root = next(context)
    for event, elem in context:
        if event == 'end' and elem.tag in tags:
            yield elem
            root.clear()


with open(SAMPLE_FILE, 'wb') as output:
    output.write('<?xml version="1.0" encoding="UTF-8"?>\n')
    output.write('<osm>\n  ')

    # Write every kth top level element
    for i, element in enumerate(get_element(OSM_FILE)):
        if i % k == 0:
            output.write(ET.tostring(element, encoding='utf-8'))

    output.write('</osm>')


# ### 2. Audit the Data
1. My task is to use the iterative parsing to process the map file and find out not only what tags are there, but also how many, to get the feeling on how much of which data I can expect to have in the map.
# In[1]:


"""
It should return a dictionary with the tag name as the key and number of times this tag can be encountered in 
the map as value.

"""
import xml.etree.cElementTree as ET
import pprint

def count_tags(filename):
    dict_ = {}
    for event,elem in ET.iterparse(filename):
        if elem.tag not in dict_:
            dict_[elem.tag] = 1
        else:
            dict_[elem.tag] += 1
    return dict_

def test():
    tags = count_tags('toronto_canada.osm')
    #tags = count_tags('torontosample.osm')
    pprint.pprint(tags) 

if __name__ == "__main__":
    test()

2. Here my task is to explore the data more. Before I process the data and add it into your database, I am checking the
"k" value for each "<tag>" and see if there are any potential problems.

# In[2]:


"""
From lecture I have 3 regular expressions to check for certain patterns in the tags.
I would like to change the data model and expand the "addr:street" type of keys to a dictionary like this:
{"address": {"street": "Some value"}}

So, I want to see. I have such tags, and if I have any tags with problematic characters.

I have a count of each of four tag categories in a dictionary:
1.  "lower"        - for tags that contain only lowercase letters and are valid
2.  "lower_colon"  - for otherwise valid tags with a colon in their names
3.  "problemchars" - for tags with problematic characters 
4.  "other"        - for other tags that do not fall into the other three categories.

"""
import xml.etree.cElementTree as ET
import pprint
import re

lower = re.compile(r'^([a-z]|_)*$')
lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

osm_file = "toronto_canada.osm"
#osm_file = "torontosample.osm"

def key_type(element, keys):
    if element.tag == "tag":
        att = element.attrib['k'] 
        m = lower.search(att)
        p = problemchars.search(att)
        n = lower_colon.search(att)
        if m:
            keys["lower"] += 1
        elif n:
            keys["lower_colon"] += 1
        elif p:
            keys["problemchars"] += 1
        else:
            keys["other"] += 1
#pass    
    return keys

def process_map(filename):
    keys = {"lower": 0, "lower_colon": 0, "problemchars": 0, "other": 0}
    for _, element in ET.iterparse(filename):
        keys = key_type(element, keys)

    return keys

def test():
    #keys = process_map('torontosample.osm')
    keys = process_map(osm_file)
    pprint.pprint(keys)

if __name__ == "__main__":
    test()


# In[ ]:


3. I am auditing and finding the abbreviated street name.


# In[3]:


"""
The OSM file used is an abbreviated version of the Toronto Mapzen file  
"""

import xml.etree.cElementTree as ET
from collections import defaultdict
import re

#osm_file = open("torontosample.osm", "r")
osm_file = open("toronto_canada.osm", "r")
street_type_re = re.compile(r'\S+\.?$', re.IGNORECASE)
street_types = defaultdict(int)

def audit_street_type(street_types, street_name):
    m = street_type_re.search(street_name)
    if m:
        street_type = m.group()

        street_types[street_type] += 1

def print_sorted_dict(d):
    keys = d.keys()
    keys = sorted(keys, key=lambda s: s.lower())  # Python 2.7 ver
    for k in keys:
        v = d[k]
        print "%s: %d" % (k, v) 

def is_street_name(elem):
    return (elem.tag == "tag") and (elem.attrib['k'] == "addr:street")

def audit():
    for event, elem in ET.iterparse(osm_file):
        if is_street_name(elem):
            audit_street_type(street_types, elem.attrib['v'])    
    print_sorted_dict(street_types)    

if __name__ == '__main__':
    audit()

4. Find out how many unique users have contributed to the map in this particular area.
# In[8]:


#The function process_map should return a set of unique user IDs ("uid")

import xml.etree.cElementTree as ET
import pprint
import re

def get_user(element):
    if element.get('uid'):
        return element.get('uid')
    
def process_map(filename):
    users = set()
    for _, element in ET.iterparse(filename):
        users.add(get_user(element))
        users.discard(None)
    return users

def test():

    users = process_map('toronto_canada3.osm')
    pprint.pprint(users)


if __name__ == "__main__":
    test()
    

