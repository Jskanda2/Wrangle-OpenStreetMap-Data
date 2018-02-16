# Data-Analyst-ND-OSM-Project-3
Udacity Data Analyst Nano Degree Projects

### 1. MAP AREA: Toronto - Canada

  * http://www.openstreetmap.org/export#map=11/43.7188/-79.3762

  * https://www.openstreetmap.org/relation/324211

  I lived in Toronto, CANADA. I am intrested in find more about the places and streets. I would like to analyse and check its need any      corrections or improvements.

### 2. I have encountered following problems in the Map Dataset.

    1. When I audit the data for the Street and found that some of the street name abbreviation are not what we expected. I able to improve or   update the Stree name abbreviation to the expected name.

        * 'Rd.' -> Road
        * 'st' -> Street
        * 'Ter' -> Terrace
     
    2. When I audit the Postal Code, The right format is :'L1W 3R2'.
    
       * Some of them are missing a space inbetween first 3 digits and last 3 digits as follows 'L1W3R2'.

       * Some of the postal code are missing last 3 digits.
     
       * Couple of them with no postal code
    
    3. When I audit the Phone numbers. some of them are notin the right format. I able to corrected to the right format as follows.

       * '+1 905 990 9220' -> '+1-905-990-9220'
    
      Also I noticed abnormal format as follows,
    
       * 'unknown''(416) 536-SODA', '+1 905 -90-4110', '1 905 891 326', '439-0000'
    

### 3. Exploring the Data

 #### OSM File Size




```python
import os
filename = "toronto_canada.osm"
os.path.getsize(filename)
```




    1232834598L



#### 1. Number of Nodes.

```python
cur.execute("SELECT COUNT(*) from nodes;")
print 'There are {} nodes.'.format(cur.fetchall()[0][0])
```

    There are 341835 nodes.
    

#### 2. Numbers of Ways.


```python
cur.execute("SELECT COUNT(*) from ways;")
print 'There are {} ways in database.'.format(cur.fetchall()[0][0])
```

    There are 50752 ways in database.
    

#### 3. Number of unique Users.


```python
cur.execute("SELECT COUNT(DISTINCT(U.uid)) FROM (SELECT uid FROM nodes UNION ALL SELECT uid FROM ways) U;") 
print 'There are {} uniqe users.'.format(cur.fetchall()[0][0])

```

    There are 1404 uniqe users.
    

#### 4. Top 6 contributing Users.


```python
cur.execute("SELECT U.user, COUNT(*) as num FROM (SELECT user FROM nodes UNION ALL SELECT user FROM ways) U GROUP BY U.user ORDER BY num DESC LIMIT 6;")
rows = cur.fetchall()
print('Top six contributing users:')
pprint(rows)
```

    Top six contributing users:
    [(u'andrewpmk', 226404),
     (u'Kevo', 32266),
     (u'MikeyCarter', 31644),
     (u'Bootprint', 13874),
     (u'Victor Bielawski', 9572),
     (u'Mojgan Jadidi', 6462)]
    

#### 5. Number of users appearing only Once and 100 times.


```python
cur.execute("SELECT COUNT(*) FROM (SELECT U.user, COUNT(*) as num FROM (SELECT user FROM nodes UNION ALL SELECT user FROM ways) U GROUP BY U.user HAVING num=1) u;")
rows = cur.fetchall()
print('Number of users appearing only Once:')
pprint(rows)
```

    Number of users appearing only Once:
    [(468,)]
    


```python
cur.execute("SELECT COUNT(*) FROM (SELECT U.user, COUNT(*) as num FROM (SELECT user FROM nodes UNION ALL SELECT user FROM ways) U GROUP BY U.user HAVING num=100) u;")
rows = cur.fetchall()
print('Number of users appearing 100 times:')
pprint(rows)
```

    Number of users appearing 100 times:
    [(1,)]
    

#### 6. Number of Top 10 Amenities


```python
cur.execute("SELECT VALUE, COUNT(*) as count FROM nodes_tags WHERE key ='amenity' GROUP BY value ORDER BY count DESC LIMIT 10;")
rows = cur.fetchall()
print('Top 10 Amenities:')
pprint(rows)
```

    Top 10 Amenities:
    [(u'restaurant', 208),
     (u'fast_food', 201),
     (u'bench', 155),
     (u'post_box', 145),
     (u'cafe', 113),
     (u'parking', 79),
     (u'waste_basket', 76),
     (u'fuel', 67),
     (u'bank', 60),
     (u'pharmacy', 47)]
    

#### 7. Top 10 Commercial buildings name


```python
cur.execute("SELECT VALUE, COUNT(*) as count FROM nodes_tags WHERE key = 'name' GROUP BY value ORDER BY count DESC LIMIT 10;")
rows = cur.fetchall()
print('Top 10 Commercials:')
pprint(rows)
```

    Top 10 Commercials:
    [(u'Subway', 32),
     (u'Tim Hortons', 30),
     (u'Petro-Canada', 23),
     (u'Esso', 17),
     (u'Pizza Pizza', 16),
     (u'Shoppers Drug Mart', 15),
     (u'Starbucks Coffee', 15),
     (u'Dollarama', 12),
     (u'Scotiabank', 11),
     (u'CIBC', 10)]
    

#### 8. Top 25 Restaurents


```python
cur.execute("SELECT nodes_tags.value, COUNT(*) as count FROM nodes_tags JOIN (SELECT DISTINCT(id) FROM nodes_tags WHERE value='restaurant') rest ON nodes_tags.id=rest.id WHERE nodes_tags.key='cuisine' GROUP BY nodes_tags.value ORDER BY count DESC LIMIT 25;")
rows = cur.fetchall()
print('Top 25 Restaurents:')
pprint(rows)
```

    Top 25 Restaurents:
    [(u'chinese', 12),
     (u'japanese', 11),
     (u'indian', 9),
     (u'burger', 4),
     (u'italian', 4),
     (u'seafood', 4),
     (u'thai', 4),
     (u'american', 3),
     (u'breakfast', 3),
     (u'vietnamese', 3),
     (u'chicken', 2),
     (u'korean', 2),
     (u'steak_house', 2),
     (u'sushi', 2),
     (u'Sandwiches, juice, etc.', 1),
     (u'Sushi', 1),
     (u'Vietnamese', 1),
     (u'afghani', 1),
     (u'asian', 1),
     (u'bar&grill', 1),
     (u'buffet', 1),
     (u'caribbean', 1),
     (u'carribean,_roti', 1),
     (u'diner', 1),
     (u'filipino', 1)]
    
### 4. Conclusion

 Data wrangling is the process of transforming and mapping data from one "raw" data form into another format with the intent of making it more appropriate and valuable for a variety of downstream purposes such as analytics. In our data auditing we used only 3 regular expressions to check for certain patterns in the tags. It is a huge data set and it may have some irregular patterns also. It will take time to find and complete the task in time. 

 In the analysis of OpenStreet Map dataset, I noticed lots of human error or manual entry errors. In the process of auditing the dataset, some of the postal codes are missing the right format, some of them are missing digits and some tags are with no postal codes. Also in the address tags, streets abbreviation in place and need to be mapped to the expected name. I able to improve or update the abbreavited  street name to the expected names. Still I need to do clean up or improve on streets numbers and etc. The file size is very large and takes more time to find the inconsistant ones  and mapped to the ecpected one. Also I encountered that the phone numbers are not entered properly or not strictly followed in the program or code. I able to audit and made them to the right format. Some of them are not able to modify.
 
 After auditing is complete the next step is to prepare the data to be inserted into a SQL database. To do so we parsed the elements in the OSM XML file, transforming them from document format to Tabular format. That maks possible to write to .csv files. Because of the size of the dataset, create and insert the data into the csv files took lots of time.  It was painful to wait for the process to complete. It was confused that the code is working or not. After successful execution these csv files are imported to a SQL database as tables. Finaly I able to run the SQL query in python notebook to analyse the OpenStreet Map. 

### 5. References:

 * https://discussions.udacity.com/c/nd002-data-wrangling
 * http://www.tutorialspoint.com/python/
 * https://www.w3schools.com/xml/xml_whatis.asp
 * https://docs.python.org/2/library/csv.html
 * https://www.tutorialspoint.com/sql/



