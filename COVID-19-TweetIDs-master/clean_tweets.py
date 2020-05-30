#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import numpy as np
import pyspark

import configparser
from datetime import datetime
import os
from pathlib import Path
from pyspark.sql import SparkSession
from pyspark.sql.functions import udf, col
from pyspark.sql.functions import year, month, dayofmonth, hour, weekofyear, date_format


import pandas as pd
import numpy as np
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut


# In[2]:


places = ['country','country_code','state','region','province','city','postcode','county']


# In[3]:


needed = ['created_at', 'id', 'full_text',
            'user', 'geo','handle','description',
           'coordinates', 'place', 'retweeted',
           'retweet_count', 'favorite_count',
           'lang','location','friends','followers','source_url','source_platform','rt']


# In[4]:


data_dirs = ['2020-01', '2020-02', '2020-03', '2020-04']


def main():
    if not os.path.exists('Tweets_Final'):
        os.makedirs('Tweets_Final')
    for data_dir in data_dirs:
        if not os.path.exists('Tweets_Final'+'\\'+data_dir):
            os.makedirs('Tweets_Final'+'\\'+data_dir)
        for path in Path(data_dir).iterdir():
            if path.name.endswith('jsonl.gz') and path.name.strip('jsonl.gz') not in os.listdir('Tweets_Final'+'\\'+data_dir):
                df = finalize_tweet(path)
                df.to_json('Tweets_Final'+'//2020-01//'+(path.name), orient='records', lines=True, compression='gzip')
                print('file updated & added')


# In[5]:


def finalize_tweet(path_name):
    df = pd.read_json(path_name,lines=True)
    df = clean_shrink(df,needed)
    df['geo_codes'] = df['location'].apply(lambda x: create_locators(x,places) if x != None else None)
    df = pd.concat([df,df.geo_codes.apply(pd.Series)],axis=1)
    return df


# In[6]:


def clean_shrink(df,ls):
    df['location'] = df.user.apply(lambda x: x['location'])
    df['handle'] = df.user.apply(lambda x: x['screen_name'])
    df['description'] = df.user.apply(lambda x: x['description'])
    df['friends'] = df.user.apply(lambda x: x['friends_count'])
    df['followers'] = df.user.apply(lambda x: x['followers_count'])
    df['source_url'] = df.source.str.extract(pat='(?<=\")(.*?)(?=\")')
    df['source_platform'] = df.source.str.extract(pat='(?<=\>)(.*?)(?=\<)')
    df['user'] = df.user.apply(pd.Series)['id']
    df['rt'] = np.where(df.full_text.str.startswith("RT @"),1,0)
    df.full_text = np.where(df.rt == 1, df.retweeted_status.str['full_text'], df.full_text)
    df = df[ls]
    return df


# In[9]:


def do_geocode(address):
    geopy = Nominatim()
    try:
        return geopy.geocode(address,exactly_one=True,timeout=10)
    except GeocoderTimedOut:
        return geopy.geocode(address,exactly_one=True,timeout=10)
    else:
        return None

def extract_places(geo_location,places):
    geopy = Nominatim()
    lat, long = geo_location.latitude,geo_location.longitude
    reverse = geopy.reverse([lat,long])
    address = reverse.raw['address']
    final_dict = {}
    for x in places:
        if x in address:
            final_dict[x] = address[x]
        elif x not in address:
            final_dict[x] = None
    if geo_location != None:
            final_dict['latitude'] = lat
            final_dict['longitude'] = long
    else:
        final_dict['latitude'] = None
        final_dict['longitude'] = None


    return final_dict

def create_locators(address,places):
    location = do_geocode(address)
    try:
        locators = extract_places(location,places)
        return locators
    except:
        final_dict = {}
        for place in places:
            final_dict[place] = None
            final_dict['latitude'] = None
            final_dict['longitude'] = None
        return final_dict



# In[ ]:


if __name__ == "__main__":
    main()


# In[ ]:
