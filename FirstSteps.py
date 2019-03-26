#!/usr/bin/env python
# coding: utf-8

# In[1]:


import json
from PIL import Image, ImageDraw
from pathlib import Path
import base64
import hashlib
import io
from dotenv import load_dotenv
import boto3
import pymongo
import os
from bson import ObjectId


# # Add the Path to the data file
# 
# If you want to use a different data file,  you'll need to specify the path to that below.  I'm using the `data.json`
# file provided in the README.

# In[2]:


DATAFILEPATH='./data.json'
p = Path(DATAFILEPATH)
with p.open() as d:
    data = json.loads(d.read())


# # Support is here for jpegs
# 
# Any other type of image will throw an exception.

# In[3]:


def getheaderbytes(payload):
    header, dbytes = payload.get('image',"None,None").split(',')
    if header == 'data:image/jpeg;base64':
        decoded = base64.decodebytes(dbytes.encode('ascii'))
        return header, decoded
    else:
        raise ValueError(f'Unknown image type: {header}')

def drawrects(payload):
    header, decoded = getheaderbytes(payload)
    img = Image.open(io.BytesIO(decoded))

    for coords in payload.get('canines', []):
        draw = ImageDraw.Draw(img)
        start, end = coords.get('coordinates')
        draw.rectangle(((start[0], start[1]), (end[0], end[1])), outline='#ff0000')
    return img


# In[4]:


def writeout(payload):
    img = drawrects(payload)
    outbuf = io.BytesIO()
    img.save(outbuf, format="jpeg")
    outbuf.seek(0)
    return outbuf


# # .env setup required
# 
# You'll need to create a file named `.env` containing the following:
# 
# <pre>
#   MONGO_URL="&lt;the mongo url with username and password for the mongodb&gt;"
#   MONGO_DB_NAME="&lt;the name of the database you want to use&gt;"
#   S3_BUCKET="&lt;the s3 bucket you want to use, it should already be created and setup to allow website access&gt;"
# </pre>
# 
# This `.env` file will be read by the following code and use to pre-process the images. The mongo database and collection (`dogs`)
# will have the appropriate data written to it for the server/client application.  This code converts the 
# image data and draws the appropriate rectangles and then uploads the images to s3. The document containing
# the image endpoint and the consolidated data is written to mongo.  This operation may be time consuming
# if the number of images is large.  

# In[5]:


load_dotenv()
dbclient = pymongo.MongoClient(os.getenv('MONGO_URL'))
db = dbclient[os.getenv('MONGO_DB_NAME')]
col = db.dogs

def save_to_s3(payload, bucket, objectname):
    client = boto3.client('s3')
    img_data = writeout(payload)
    client.put_object(Bucket=bucket,
                      Body=img_data,
                      Key=f'{objectname}.jpg',
                      ContentType='application/jpeg',  
                      ACL='public-read')

    return f'https://{bucket}.s3.amazonaws.com/{objectname}.jpg'

def consolidate_found_canines(payload):
    counter = {}
    for dog in payload.get('canines',[]):
        sub = counter.setdefault(dog.get('type', 'Unknown'), {})
        age_item = dog.get('age','Unknown')
        counts = sub.setdefault(age_item, 0)
        counts = counts + 1
        sub[age_item] = counts
    acc = []
    for k in counter.keys():
        for j in counter[k].keys():
            acc.append((k,j,counter[k][j]))
    return acc

def save_to_mongo(payload):
    try:
        consolidated = consolidate_found_canines(payload)
        saved_data = dict(title=payload['title'], canines=consolidated)
        oid = col.insert_one(saved_data)
        img_url = save_to_s3(payload, os.getenv('S3_BUCKET'), str(oid.inserted_id))
        saved_data['img_url'] = img_url
        col.update_one({"_id": oid.inserted_id}, {"$set": saved_data})
    except ValueError:
        print("Failed to import payload, is it a JPG?")
        print(payload)


# # Import the data
# 
# The next cell runs through all elements in the datafile and loads the data into mongo. This could take a while if there are many 
# images.  

# In[6]:


for i in data:
    save_to_mongo(i)


# # Verify The Data
# 
# This is a crude verification step.  Do NOT run this if you've imported a lot of images.  

# In[7]:


class MongoEncoder(json.JSONEncoder):

    def default(self, obj):
        try:
            if isinstance(obj, ObjectId):
                return str(obj)
            iterable = iter(obj)
        except TypeError:
            pass
        else:
            return list(iterable)
        return JSONEncoder.default(self, obj)

print(json.dumps([x for x in col.find({})], indent=2, cls=MongoEncoder))


# In[ ]:




