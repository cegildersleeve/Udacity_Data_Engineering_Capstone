#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import boto3
import json
import os
import psycopg2
import logging
from botocore.exceptions import ClientError
import configparser


# In[2]:


config = configparser.ConfigParser()
config.read_file(open('dwh.cfg'))

KEY                    = config.get('AWS','KEY')
SECRET                 = config.get('AWS','SECRET')


# In[3]:


bucket = 'udacity-capstone-cg'


# In[4]:


s3 = boto3.resource('s3',
                       region_name="us-east-2",
                       aws_access_key_id=KEY,
                       aws_secret_access_key=SECRET
                   )


# In[5]:


def clear_bucket(bucket=bucket):
    bucket = s3.Bucket(bucket)
    bucket.objects.all().delete()


# In[6]:


def delete_bucket(bucket=bucket):
    bucket = s3.Bucket(bucket)
    bucket.delete()


# In[7]:


def main():
    clear_bucket()
    delete_bucket()
    


# In[8]:


if __name__ == "__main__":
    main()


# In[ ]:




