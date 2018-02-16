
# coding: utf-8

# # Data Wrangle  - Data Audit and Clean 
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


# ## 3. Imporving Stree Names, Postal Codes and Phone Numbers
4. Mapping the Street name to the expected name.
   After mapped to the expected names write the data to "toronto_canada1.osm" file
# In[5]:



import xml.etree.cElementTree as ET
from collections import defaultdict
import re
import pprint
 
OSM_FILE = "toronto_canada.osm"
#OSM_FILE = "torontosample.osm"
street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)


expected = ["Street", "Avenue", "Boulevard", "Drive", "Court", "Place", "Square", "Lane", "Road", 
            "Trail", "Parkway", "Commons", "Terrace" ,"Expressway", "Crescent", "Close", "Common", "Heights", "Way"]

mapping = { "St": "Street",
            "St.": "Street",
            "ST": "Street",
            "Ben":"Bend",
            "Glenn":"Glen",
            "Hrbr":"Harbour",
            "Ho":"Hollow",
            "Mews":"Medows",
            "Pkwy":"Parkway",
            "Wood":"Woods",
            "Ave": "Avenue",
            "ave": "Avenue",
            "Rd.": "Road",
            "Blvd":"Boulevard",
            "Dr.":"Drive",
            "Ct":"Court",
            "Pl":"Place",
            "Sq":"Square",
            "ln":"Lane",
            "SW": "Southwest ",
            "SE": "Southeast ",
            "NW": "Northwest ",
            "NE": "Northeast ",
            'CT': 'Court',
            'Ct': 'Court',
            'Dr': 'Drive',
            'Dr.': 'Drive',
            'E': 'East',
            'Main St': 'Main Street',
            'N': 'North',
            'NE': 'Northeast',
            'NW': 'Northwest',
            'nw': 'Northwest',
            'PL': 'Place',
            'Pl': 'Place',
            'Rd': 'Road',
            'RD': 'Road',
            'Rd.': 'Road',
            'S': 'South',
            'S.': 'South',
            'SE': 'Southeast',
            'ST': 'Street',
            'SW': 'Southwest',
            'SW,': 'Southwest',
            'Se': 'Southeast',
            'southeast': 'Southeast',
            'St': 'Street',
            'st': 'Street',
            'Ter': 'Terrace',
            'W': 'West',
            'west': 'West',
            'HYW': 'Highway',
            'WY': 'Way',
            "Avebue":"Avenue",
            "Avenu":"Avenue"
            }


def audit_street_type(street_types, street_name):
    m = street_type_re.search(street_name)
    if m:
        street_type = m.group()
        if street_type not in expected:
            street_types[street_type].add(street_name)

def is_street_name(elem):
    return (elem.attrib['k'] == "addr:street")

def audit(osmfile):
    osm_file = open(osmfile, "r")
    street_types = defaultdict(set)
    for event, elem in ET.iterparse(osm_file, events=("start",)):

        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_street_name(tag):
                    audit_street_type(street_types, tag.attrib['v'])
    osm_file.close()
    return street_types

def update_name(name, mapping):
    m = street_type_re.search(name)
    if m:
        street_type = m.group()
        if street_type not in expected:
            if street_type in mapping.keys():
                name = re.sub(street_type_re, mapping[street_type], name)
                               
    return name

#OSM_FILE_UPDATED = "toronto_canada1.osm"

# Mapped to the expected names, save/write the data to "toronto_canada1.osm" file 

OSM_FILE_UPDATED = "toronto_canada1.osm"
# Takes as input osm file and tuple of nodes and yield nodes of types from tuple. 

def get_element(osm_file, tags=('node', 'way', 'relation')):
    context = iter(ET.iterparse(osm_file, events=('start', 'end')))
    _, root = next(context)
    for event, elem in context:
        if event == 'end' and elem.tag in tags:
            yield elem
            root.clear()
            
# Following function will update the abbreviations in osm file

def update_street(original_file, update_file):
    with open(update_file, 'wb') as output:
        output.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        output.write('<osm>\n  ') 
        for i, element in enumerate(get_element(original_file)):
            for tag in element.iter("tag"):
                if is_street_name(tag):
                    tag.set('v',update_name(tag.attrib['v'], mapping))
            output.write(ET.tostring(element, encoding='utf-8'))
        output.write('</osm>')

update_street(OSM_FILE, OSM_FILE_UPDATED)

5. Auditing the for postcode inconsistent
# In[6]:



import xml.etree.cElementTree as ET
from collections import defaultdict
import re

postcode_type_re = re.compile(r'\d{5}-??')

def audit_post_type(post_types, zip):
    m = postcode_type_re.search(zip)
    if m:
        post_type = m.group()
        if post_type not in post_types:
            post_types[post_type].add(zip)
    else:
        post_types['unknown'].add(zip)

def is_pcode(elem):
    return (elem.attrib['k'] == "addr:postcode")

def postcode_audit(osmfile):
    osm_file = open(osmfile, "r")    
    post_types = defaultdict(set)
    for event, elem in ET.iterparse(osm_file, events=("start",)):
        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_pcode(tag):
                    audit_post_type(post_types, tag.attrib['v'])                
    osm_file.close()
    return post_types

postcode_types = postcode_audit(OSM_FILE_UPDATED)

pprint.pprint(dict(postcode_types))

OSM_FILE_UPDATED_PC = "toronto_canada2.osm"
# This function replace abbrevition by right zip
def u_postcode(zip):
    m = postcode_type_re.search(zip)
    if m:
        return m.group()
    else:
        return 'unknown'

# This function replace wrong zip in osm file
def update_postcode(original_file, update_file):
    with open(update_file, 'wb') as output:
        output.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        output.write('<osm>\n  ') 
        for i, element in enumerate(get_element(original_file)):
            for tag in element.iter("tag"):
                if is_pcode(tag):
                    tag.set('v',u_postcode(tag.attrib['v']))
            output.write(ET.tostring(element, encoding='utf-8'))
        output.write('</osm>')

update_postcode(OSM_FILE_UPDATED, OSM_FILE_UPDATED_PC)


6. Auditing for the inconsistent phone numbers or format
# In[7]:



# Compiler for cleaning phone format 
phone_type_re = re.compile(r'\d{3}\)?-?\s?.?\d{3}\s?-?\s?.?\d{4}')
phone_re = re.compile('\.|\)|\s|-')

def audit_phone_type(phone_types, phone):
    m = phone_type_re.search(phone)
    if m:
        phone_type = m.group()
        if phone_type not in phone_types:
            new_phone = phone_re.sub('',phone_type)
            new_phone = ('+1-' + new_phone[:3] + '-' +
                         new_phone[3:6] + '-' + new_phone[6:])
            phone_types[new_phone].add(phone)
    else:
        phone_types['unknown'].add(phone)
        
def is_phone(elem):
    return (elem.attrib['k'] == "phone")

def phone_audit(osmfile):
    osm_file = open(osmfile, "r")    
    phone_types = defaultdict(set)
    for event, elem in ET.iterparse(osm_file, events=("start",)):
        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_phone(tag):
                    audit_phone_type(phone_types, tag.attrib['v'])                
    osm_file.close()
    return phone_types
    
phones_types = phone_audit(OSM_FILE_UPDATED_PC)
# To validate or check the phone numbers format after the changes, uncomment the next line and comment the above one
#phones_types = phone_audit(OSM_FILE_UPDATED_PH) 

pprint.pprint(dict(phones_types))

OSM_FILE_UPDATED_PH = "toronto_canada3.osm"

# Following function update phone numbers to the correct format 

def u_phone(phone):
    m = phone_type_re.search(phone)
    if m:
        new_phone = phone_re.sub('', m.group())
        return ('+1-' + new_phone[:3] + '-' + new_phone[3:6] +
                '-' + new_phone[6:])        
    else:
        return phone

# This function replace the incosistent phone numbers with the right format

def update_phone(original_file, update_file):
    with open(update_file, 'wb') as output:
        output.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        output.write('<osm>\n  ') 
        for i, element in enumerate(get_element(original_file)):
            for tag in element.iter("tag"):
                if is_phone(tag):
                    tag.set('v',u_phone(tag.attrib['v']))
            output.write(ET.tostring(element, encoding='utf-8'))
        output.write('</osm>')

update_phone(OSM_FILE_UPDATED_PC, OSM_FILE_UPDATED_PH)
     


# Seeing abnormal or not regular format phone numbers as following
# 
#  'unknown': set(['(416) 536-SODA',
#                  '+1 905 -90-4110',
#                  '1 905 891 326',
#                  '439-0000'])}
7. Find out how many unique users have contributed to the map in this particular area.
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
    


# ### 4. Prepair for Database SQL 
# 
# After auditing is complete the next step is to prepare the data to be inserted into a SQL database.
#    To do so I will parse the elements in the OSM XML file, transforming them from document format to
#    tabular format.
# 
#    Making it possible to write to .csv files.  These csv files can then easily be imported to a SQL database as tables.
# 
# The process for this transformation is as follows:
# - Use iterparse to iteratively step through each top level element in the XML
# - Shape each element into several data structures using a custom function
# - Utilize a schema and validation library to ensure the transformed data is in the correct format
# - Write each data structure to the appropriate .csv files
# 
# #### From the Case study
# 
# I've already provided the code needed to load the data, perform iterative parsing and write the
# output to csv files. My task is to complete the shape_element function that will transform each
# element into the correct format. To make this process easier we've already defined a schema (schema.py)
# for the .csv files and the eventual tables. Using the cerberus library we can validate the output
# against this schema to ensure it is correct.
# 
# Shape Element Function
# The function should take as input an iterparse Element object and return a dictionary.
# 
# If the element top level tag is "node":
# The dictionary returned should have the format {"node": .., "node_tags": ...}
# 
# The "node" field should hold a dictionary of the following top level node attributes:
# - id
# - user
# - uid
# - version
# - lat
# - lon
# - timestamp
# - changeset
# All other attributes can be ignored
# 
# The "node_tags" field should hold a list of dictionaries, one per secondary tag. Secondary tags are
# child tags of node which have the tag name/type: "tag". Each dictionary should have the following
# fields from the secondary tag attributes:
# - id: the top level node id attribute value
# - key: the full tag "k" attribute value if no colon is present or the characters after the colon if one is.
# - value: the tag "v" attribute value
# - type: either the characters before the colon in the tag "k" value or "regular" if a colon is not present.
# 
# Additionally,
# 
# - if the tag "k" value contains problematic characters, the tag should be ignored
# - if the tag "k" value contains a ":" the characters before the ":" should be set as the tag type
#   and characters after the ":" should be set as the tag key
# - if there are additional ":" in the "k" value they and they should be ignored and kept as part of
#   the tag key. For example:
# 
#   <tag k="addr:street:name" v="Lincoln"/>
#   should be turned into
#   {'id': 12345, 'key': 'street:name', 'value': 'Lincoln', 'type': 'addr'}
# 
# - If a node has no secondary tags then the "node_tags" field should just contain an empty list.

# In[ ]:


#!/usr/bin/env python


import csv
import codecs
import pprint
import re
import xml.etree.cElementTree as ET
import cerberus
import sys
import schema

OSM_PATH = "toronto_canada3.osm"

NODES_PATH = "nodes.csv"
NODE_TAGS_PATH = "nodes_tags.csv"
WAYS_PATH = "ways.csv"
WAY_NODES_PATH = "ways_nodes.csv"
WAY_TAGS_PATH = "ways_tags.csv"

LOWER_COLON = re.compile(r'^([a-z]|_)+:([a-z]|_)+')
PROBLEMCHARS = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

SCHEMA = schema.schema

# Make sure the fields order in the csvs matches the column order in the sql table schema
NODE_FIELDS = ['id', 'lat', 'lon', 'user', 'uid', 'version', 'changeset', 'timestamp']
NODE_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_FIELDS = ['id', 'user', 'uid', 'version', 'changeset', 'timestamp']
WAY_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_NODES_FIELDS = ['id', 'node_id', 'position']


def shape_element(element, node_attr_fields=NODE_FIELDS, way_attr_fields=WAY_FIELDS,
                  problem_chars=PROBLEMCHARS, default_tag_type='regular'):
    """Clean and shape node or way XML element to Python dict"""

    node_attribs = {}
    way_attribs = {}
    way_nodes = []
    tags = []  

    if element.tag == 'node':
        for attrib in element.attrib:
            if attrib in NODE_FIELDS:
                node_attribs[attrib] = element.attrib[attrib]
        
        for child in element:
            node_tag = {}
            if LOWER_COLON.match(child.attrib['k']):
                node_tag['type'] = child.attrib['k'].split(':',1)[0]
                node_tag['key'] = child.attrib['k'].split(':',1)[1]
                node_tag['id'] = element.attrib['id']
                node_tag['value'] = child.attrib['v']
                tags.append(node_tag)
            elif PROBLEMCHARS.match(child.attrib['k']):
                continue
            else:
                node_tag['type'] = 'regular'
                node_tag['key'] = child.attrib['k']
                node_tag['id'] = element.attrib['id']
                node_tag['value'] = child.attrib['v']
                tags.append(node_tag)
        
        return {'node': node_attribs, 'node_tags': tags}
        
    elif element.tag == 'way':
        for attrib in element.attrib:
            if attrib in WAY_FIELDS:
                way_attribs[attrib] = element.attrib[attrib]
        
        position = 0
        for child in element:
            way_tag = {}
            way_node = {}
            
            if child.tag == 'tag':
                if LOWER_COLON.match(child.attrib['k']):
                    way_tag['type'] = child.attrib['k'].split(':',1)[0]
                    way_tag['key'] = child.attrib['k'].split(':',1)[1]
                    way_tag['id'] = element.attrib['id']
                    way_tag['value'] = child.attrib['v']
                    tags.append(way_tag)
                elif PROBLEMCHARS.match(child.attrib['k']):
                    continue
                else:
                    way_tag['type'] = 'regular'
                    way_tag['key'] = child.attrib['k']
                    way_tag['id'] = element.attrib['id']
                    way_tag['value'] = child.attrib['v']
                    tags.append(way_tag)
                    
            elif child.tag == 'nd':
                way_node['id'] = element.attrib['id']
                way_node['node_id'] = child.attrib['ref']
                way_node['position'] = position
                position += 1
                way_nodes.append(way_node)
        
        return {'way': way_attribs, 'way_nodes': way_nodes, 'way_tags': tags}

# ================================================== #
#               Helper Functions                     #
# ================================================== #
def get_element(osm_file, tags=('node', 'way', 'relation')):
    """Yield element if it is the right type of tag"""

    context = ET.iterparse(osm_file, events=('start', 'end'))
    _, root = next(context)
    for event, elem in context:
        if event == 'end' and elem.tag in tags:
            yield elem
            root.clear()


def validate_element(element, validator, schema=SCHEMA):
    """Raise ValidationError if element does not match schema"""
    if validator.validate(element, schema) is not True:
        field, errors = next(validator.errors.iteritems())
        message_string = "\nElement of type '{0}' has the following errors:\n{1}"
        error_string = pprint.pformat(errors)
        
        raise Exception(message_string.format(field, error_string))


class UnicodeDictWriter(csv.DictWriter, object):
    """Extend csv.DictWriter to handle Unicode input"""

    def writerow(self, row):
        super(UnicodeDictWriter, self).writerow({
            k: (v.encode('utf-8') if isinstance(v, unicode) else v) for k, v in row.iteritems()
        })

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)


# ================================================== #
#               Main Function                        #
# ================================================== #
def process_map(file_in, validate):
    """Iteratively process each XML element and write to csv(s)"""

    with codecs.open(NODES_PATH, 'w') as nodes_file,          codecs.open(NODE_TAGS_PATH, 'w') as nodes_tags_file,          codecs.open(WAYS_PATH, 'w') as ways_file,          codecs.open(WAY_NODES_PATH, 'w') as way_nodes_file,          codecs.open(WAY_TAGS_PATH, 'w') as way_tags_file:

        nodes_writer = UnicodeDictWriter(nodes_file, NODE_FIELDS)
        node_tags_writer = UnicodeDictWriter(nodes_tags_file, NODE_TAGS_FIELDS)
        ways_writer = UnicodeDictWriter(ways_file, WAY_FIELDS)
        way_nodes_writer = UnicodeDictWriter(way_nodes_file, WAY_NODES_FIELDS)
        way_tags_writer = UnicodeDictWriter(way_tags_file, WAY_TAGS_FIELDS)

        nodes_writer.writeheader()
        node_tags_writer.writeheader()
        ways_writer.writeheader()
        way_nodes_writer.writeheader()
        way_tags_writer.writeheader()

        validator = cerberus.Validator()

        for element in get_element(file_in, tags=('node', 'way')):
            el = shape_element(element)
            if el:
                if validate is True:
                    validate_element(el, validator)

                if element.tag == 'node':
                    nodes_writer.writerow(el['node'])
                    node_tags_writer.writerows(el['node_tags'])
                elif element.tag == 'way':
                    ways_writer.writerow(el['way'])
                    way_nodes_writer.writerows(el['way_nodes'])
                    way_tags_writer.writerows(el['way_tags'])


if __name__ == '__main__':
    # Note: Validation is ~ 10X slower. For the project consider using a small
    # sample of the map when validating.
    #process_map(OSM_PATH, validate=False)
    process_map(OSM_PATH, validate=True)

