
# coding: utf-8

# ## Data Wrangling  - OpenStreetMap Project with SQL

# Wrangling Toronto, Canada OpenStreetMap Data
# 
# This project involved applying data munging (or wrangling/cleaning) techniques on OpenStreetMap data for an area of our choice. These techniques included assessing the quality of the data for validity, accuracy, completeness, consistency and uniformity, and then correcting the issues identified in the data.
# 
# 1. MAP AREA: Toronto - Canada
# 
# http://www.openstreetmap.org/export#map=11/43.7188/-79.3762
# 
# https://www.openstreetmap.org/relation/324211
# 
# I lived in Toronto, CANADA. I am intrested in find more about the places and streets. I would like to analyse and check its need any corrections or improvements.

# 2. I have encountered following problems in the Map Dataset.
# 1. When I audit the data for the Street and found that some of the street name abbreviation are not what we expected. I able to improve or   update the Stree name abbreviation to the expected name.
# 
#     * 'Rd.' -> Road
#     * 'st' -> Street
#     * 'Ter' -> Terrace
#  
# 2. When I audit the Postal Code, The right format is :'L1W 3R2'.
# 
#    * Some of them are missing a space inbetween first 3 digits and last 3 digits as follows 'L1W3R2'.
# 
#    * Some of the postal code are missing last 3 digits.
#  
#    * Couple of them with no postal code
# 
# 3. When I audit the Phone numbers. some of them are notin the right format. I able to corrected to the right format as follows.
# 
#    * '+1 905 990 9220' -> '+1-905-990-9220'
# 
#   Also I noticed abnormal format as follows,
# 
#    * 'unknown''(416) 536-SODA', '+1 905 -90-4110', '1 905 891 326', '439-0000'

# ### 1. Using Sqlite DB and Connect to the database named "jsrosmp3.db"

# In[1]:


# 1. Import the modules that I will need:
import sqlite3
import csv
from pprint import pprint

sqlite3.sqlite_version


# In[2]:


# 2. Create a new sqlite database named "Jsrosmp3" 

sqlite_db = 'C:\\Users\\Skanda\\Jsrosmp3.db'

# Connect to the database
conn = sqlite3.connect(sqlite_db)


# ### 2. Create Tables and Insert Data from CSV files

# In[3]:


#Create a cursor object
cur = conn.cursor()


# 1. Create the nodes table. Drop drop the table if it already exists
cur.execute('''DROP TABLE IF EXISTS nodes''')
conn.commit()

query = '''CREATE TABLE nodes
(
    id INTEGER PRIMARY KEY NOT NULL,
    lat REAL,
    lon REAL,
    user TEXT,
    uid INTEGER,
    version INTEGER,
    changeset INTEGER,
    timestamp TEXT
);'''

cur.execute(query)

# commit the changes
conn.commit()


# In[5]:


# Read in the data:
# Read in the csv file as a dictionary, format the data as a list of tuples:

with open('nodes.csv','rb') as fin:
    dr = csv.DictReader(fin)
    to_db = [(i['id'].decode("utf-8"), i['lat'].decode("utf-8"), i['lon'].decode("utf-8"), i['user'].decode("utf-8"), i['uid'].decode("utf-8"), i['version'].decode("utf-8"), i['changeset'].decode("utf-8"), i['timestamp'].decode("utf-8")) for i in dr]

# Insert the formatted data
cur.executemany("INSERT INTO nodes(id, lat, lon, user, uid, version, changeset, timestamp) VALUES (?, ?, ?, ?, ?, ?, ?, ?);", to_db)

# Commit 
conn.commit()


# In[ ]:


# Validate and query the data
cur = conn.cursor()
query = "SELECT * FROM nodes LIMIT 5;"
cur.execute(query)
rows = cur.fetchall()

#Check that the data imported correctly
print "Results:"
pprint(rows)


# In[11]:


# 2. Create the nodes_tags table and insert the data.
#    Drop drop the table if it already exists

cur.execute('''DROP TABLE IF EXISTS nodes_tags''')
conn.commit()

query = '''CREATE TABLE nodes_tags (
    id INTEGER,
    key TEXT,
    value TEXT,
    type TEXT,
    FOREIGN KEY (id) REFERENCES nodes(id)
);'''

cur.execute(query)
conn.commit()

with open('nodes_tags.csv','rb') as fin:
    dr = csv.DictReader(fin)
    to_db = [(i['id'].decode("utf-8"), i['key'],i['value'].decode("utf-8"),i['type']) for i in dr]

cur.executemany("INSERT INTO nodes_tags(id, key, value,type) VALUES (?, ?, ?, ?);", to_db)
conn.commit()


# In[11]:


# Check that the data imported correctly
cur.execute('SELECT * FROM nodes_tags LIMIT 10')
rows = cur.fetchall()
print('Results:')
pprint(rows)


# In[15]:


# 3. Create the ways table and Insert the data.
#    Drop drop the table if it already exists

cur.execute('''DROP TABLE IF EXISTS ways''')
conn.commit()

query = '''CREATE TABLE ways
(
    id INTEGER PRIMARY KEY NOT NULL,
    user TEXT,
    uid INTEGER,
    version TEXT,
    changeset INTEGER,
    timestamp TEXT
);'''

cur.execute(query)
conn.commit()
    
with open('ways.csv','rb') as fin:
    dr=csv.DictReader(fin)
    to_db=[(i['id'],i['user'].decode("utf-8"),i['uid'],i['version'],i['changeset'],i['timestamp']) for i in dr]

cur.executemany("INSERT INTO ways(id, user, uid, version, changeset, timestamp) VALUES (?, ?, ?, ?, ?, ?);", to_db)

conn.commit()


# In[12]:


# Check that the data imported correctly
cur.execute('SELECT * FROM ways LIMIT 10')
rows = cur.fetchall()
print('Results:')
pprint(rows)


# In[19]:


# 4. Create the ways_tags table. 
#    Drop drop the table if it already exists

cur.execute('''DROP TABLE IF EXISTS ways_tags''')
conn.commit()

query = '''CREATE TABLE ways_tags (
    id INTEGER NOT NULL,
    key TEXT NOT NULL,
    value TEXT NOT NULL,
    type TEXT,
    FOREIGN KEY (id) REFERENCES ways(id)
);'''

cur.execute(query)
conn.commit()

with open('ways_tags.csv','rb') as fin:
    dr=csv.DictReader(fin)
    to_db=[(i['id'],i['key'],i['value'].decode("utf-8"),i['type']) for i in dr]

cur.executemany("INSERT INTO ways_tags(id, key, value,type) VALUES (?, ?, ?, ?);", to_db)

conn.commit()


# In[13]:


# Check that the data imported correctly
cur.execute('SELECT * FROM ways_tags LIMIT 10')
rows = cur.fetchall()
print('Results:')
pprint(rows)


# In[21]:


# 5. Create the ways_nodes table. 
#    Drop drop the table if it already exists

cur.execute('''DROP TABLE IF EXISTS ways_nodes''')
conn.commit()

query = '''CREATE TABLE ways_nodes
(
    id INTEGER NOT NULL,
    node_id INTEGER NOT NULL,
    position INTEGER NOT NULL,
    FOREIGN KEY (id) REFERENCES ways(id),
    FOREIGN KEY (node_id) REFERENCES nodes(id)
);'''
    
cur.execute(query)
conn.commit()

with open('ways_nodes.csv','rb') as fin:
    dr=csv.DictReader(fin)
    to_db=[(i['id'],i['node_id'],i['position']) for i in dr]

cur.executemany("INSERT INTO ways_nodes(id, node_id, position) VALUES (?, ?, ?);", to_db)

conn.commit()


# In[14]:


# Check that the data imported correctly
cur.execute('SELECT * FROM ways_nodes LIMIT 5')
rows = cur.fetchall()
print('Results:')
pprint(rows)


# ### 3. Exploring the Data

# #### 1. Number of Nodes.

# In[15]:


cur.execute("SELECT COUNT(*) from nodes;")
print 'There are {} nodes.'.format(cur.fetchall()[0][0])


# #### 2. Numbers of Ways.

# In[16]:


cur.execute("SELECT COUNT(*) from ways;")
print 'There are {} ways in database.'.format(cur.fetchall()[0][0])


# #### 3. Number of unique Users.

# In[17]:


cur.execute("SELECT COUNT(DISTINCT(U.uid)) FROM (SELECT uid FROM nodes UNION ALL SELECT uid FROM ways) U;") 
print 'There are {} uniqe users.'.format(cur.fetchall()[0][0])


# #### 4. Top 6 contributing Users.

# In[18]:


cur.execute("SELECT U.user, COUNT(*) as num FROM (SELECT user FROM nodes UNION ALL SELECT user FROM ways) U GROUP BY U.user ORDER BY num DESC LIMIT 6;")
rows = cur.fetchall()
print('Top six contributing users:')
pprint(rows)


# #### 5. Number of users appearing only Once and 100 times.

# In[19]:


cur.execute("SELECT COUNT(*) FROM (SELECT U.user, COUNT(*) as num FROM (SELECT user FROM nodes UNION ALL SELECT user FROM ways) U GROUP BY U.user HAVING num=1) u;")
rows = cur.fetchall()
print('Number of users appearing only Once:')
pprint(rows)


# In[20]:


cur.execute("SELECT COUNT(*) FROM (SELECT U.user, COUNT(*) as num FROM (SELECT user FROM nodes UNION ALL SELECT user FROM ways) U GROUP BY U.user HAVING num=100) u;")
rows = cur.fetchall()
print('Number of users appearing 100 times:')
pprint(rows)


# #### 6. Number of Top 10 Amenities

# In[21]:


cur.execute("SELECT VALUE, COUNT(*) as count FROM nodes_tags WHERE key ='amenity' GROUP BY value ORDER BY count DESC LIMIT 10;")
rows = cur.fetchall()
print('Top 10 Amenities:')
pprint(rows)


# #### 7. Top 10 Commercial buildings name

# In[23]:


cur.execute("SELECT VALUE, COUNT(*) as count FROM nodes_tags WHERE key = 'name' GROUP BY value ORDER BY count DESC LIMIT 10;")
rows = cur.fetchall()
print('Top 10 Commercials:')
pprint(rows)


# #### 8. Top 25 Restaurents

# In[25]:


cur.execute("SELECT nodes_tags.value, COUNT(*) as count FROM nodes_tags JOIN (SELECT DISTINCT(id) FROM nodes_tags WHERE value='restaurant') rest ON nodes_tags.id=rest.id WHERE nodes_tags.key='cuisine' GROUP BY nodes_tags.value ORDER BY count DESC LIMIT 25;")
rows = cur.fetchall()
print('Top 25 Restaurents:')
pprint(rows)


# ### 4. Ideas for additional Improvements 

# The first step in data analysis is to improve data quality. Data scientists correct spelling mistakes, handle missing data and weed out nonsense information. This is the most critical step in the data value chain, junk data will generate wrong results and mislead. It is especially important that this step will scale, since having continuous data value chain requires that incoming data will get cleaned immediately and at very high rates.
# 
# Here, in the project we downloaded the metro extract from MapZen. Users have created scripts to import massive amounts of data from other sources, sometimes this can introduce additional issues such as incorrect values or superfluous information. 
# 
# The city and postcode values could be crosschecked when inputing a new address. Most countries have public APIs to retrieve addresses from postcodes, so it could be done, with the help of contributors around the world. This improvement could prevent a lot of wrong data inputs. It would definitely cause a positive impact which would affect users througout the world. On the other hand, a change like this decreases the freedom of the user when inputing new addresses. Since data could only be submitted if it was in accordance with the crosschecked value from another data source. These positive and negative impacts should be weighted before implementing this kind of improvement to the process.
# 
# The Open Street Map input tool could have a phone format validator, varying from country to country, to avoid such a mess on the phones format. It could also separate multiple phones with a standard separator. It was one of the most difficult steps of the phone values wrangling. The fact that each country has a different standard format makes it difficult to implement this, but with the help of the open software community around Open Street Map it could be done. It would decrease the freedom of the user inputing the data, since the phone format would have to be validated to the standards. And every time the standards change, the validators would have to be updated.
# 
# Also we can make some rules or patterns to input data which users follow everytime to input their data. This will also restrict users input in their native language and use unnecessary inputs.
# 
# We can also use third part tools such as Mapbox and other. Mapbox provides a suite of digital mapping tools that allow custom maps to be quickly and easily added to applications. The Mapbox platform is open source and features textures, illustrations, custom markers, vector tiles, static maps, geocoding and more. Mapbox offers five plans, ranging from a free starter plan to a high-volume enterprise plan. Any GIS system is only as good as the data that's in it. ArcGIS provides a complete set of tools that give you the flexibility to store, edit, and manage data in a way that fits with your existing processes.

# ### 5. Conclusion

# 
# Data wrangling is the process of transforming and mapping data from one "raw" data form into another format with the intent of making it more appropriate and valuable for a variety of downstream purposes such as analytics. In our data auditing we used only 3 regular expressions to check for certain patterns in the tags. It is a huge data set and it may have some irregular patterns also. It will take time to find and complete the task in time.
# 
# In the analysis of OpenStreet Map dataset, I noticed lots of human error or manual entry errors. In the process of auditing the dataset, some of the postal codes are missing the right format, some of them are missing digits and some tags are with no postal codes. Also in the address tags, streets abbreviation in place and need to be mapped to the expected name. I able to improve or update the abbreavited street name to the expected names. Still I need to do clean up or improve on streets numbers and etc. The file size is very large and takes more time to find the inconsistant ones and mapped to the ecpected one. Also I encountered that the phone numbers are not entered properly or not strictly followed in the program or code. I able to audit and made them to the right format. Some of them are not able to modify.
# 
# After auditing is complete the next step is to prepare the data to be inserted into a SQL database. To do so we parsed the elements in the OSM XML file, transforming them from document format to Tabular format. That maks possible to write to .csv files. Because of the size of the dataset, create and insert the data into the csv files took lots of time. It was painful to wait for the process to complete. It was confused that the code is working or not. After successful execution these csv files are imported to a SQL database as tables. Finaly I able to run the SQL query in python notebook to analyse the OpenStreet Map.
# 

# ### 6. References

# https://discussions.udacity.com/c/nd002-data-wrangling
# 
# http://www.tutorialspoint.com/python/
# 
# https://www.w3schools.com/xml/xml_whatis.asp
# 
# https://docs.python.org/2/library/csv.html
# 
# https://www.tutorialspoint.com/sql/
