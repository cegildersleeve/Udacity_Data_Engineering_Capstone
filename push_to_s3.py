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
from pathlib import Path

os.chdir(str(Path(__file__).parent))

# In[2]:


config = configparser.ConfigParser()
config.read_file(open('dwh.cfg'))

KEY                    = config.get('AWS','KEY')
SECRET                 = config.get('AWS','SECRET')

DWH_CLUSTER_TYPE       = config.get("DWH","DWH_CLUSTER_TYPE")
DWH_NUM_NODES          = config.get("DWH","DWH_NUM_NODES")
DWH_NODE_TYPE          = config.get("DWH","DWH_NODE_TYPE")

DWH_CLUSTER_IDENTIFIER = config.get("DWH","DWH_CLUSTER_IDENTIFIER")
DWH_DB                 = config.get("DWH","DWH_DB")
DWH_DB_USER            = config.get("DWH","DWH_DB_USER")
DWH_DB_PASSWORD        = config.get("DWH","DWH_DB_PASSWORD")
DWH_PORT               = config.get("DWH","DWH_PORT")

IAM_ROLE      = config.get("DWH", "DWH_IAM_ROLE_NAME")


# In[3]:


s3 = boto3.resource('s3',
                       region_name="us-east-2",
                       aws_access_key_id=KEY,
                       aws_secret_access_key=SECRET
                   )


# In[4]:


bucket = 'udacity-capstone-cg'
keys = ['jhu','gov']


# In[5]:


def create_bucket(bucket_name, region=None):
    """Create an S3 bucket in a specified region

    If a region is not specified, the bucket is created in the S3 default
    region (us-east-1).

    :param bucket_name: Bucket to create
    :param region: String region to create bucket in, e.g., 'us-west-2'
    :return: True if bucket created, else False
    """

    # Create bucket
    try:
        if region is None:
            s3_client = boto3.client('s3',
                       region_name="us-east-2",
                       aws_access_key_id=KEY,
                       aws_secret_access_key=SECRET)
            s3_client.create_bucket(Bucket=bucket_name)
        else:
            s3_client = boto3.client('s3',
                       region_name="us-east-2",
                       aws_access_key_id=KEY,
                       aws_secret_access_key=SECRET)
            location = {'LocationConstraint': region}
            s3_client.create_bucket(Bucket=bucket_name,
                                    CreateBucketConfiguration=location)
    except ClientError as e:
        logging.error(e)
        return False
    return True


# In[6]:


def load_added_files(keys=keys,bucket=bucket):
    paths =[]
    for key in keys:
        for path in os.listdir():
            if key in path.lower():
                s3.meta.client.upload_file(path, bucket, 'staging/'+key+'/'+path)


# In[7]:


def load_tweets():
    os.chdir('COVID-19-TweetIDs-master/Tweets_Final')
    folders = [x for x in os.listdir()]
    for folder in folders:
        os.chdir(folder)
        for file in os.listdir():
            if '.csv' in file:
                s3.meta.client.upload_file(file, bucket, 'staging/staging_tweets'+'/'+file)
        os.chdir('..')
    os.chdir('..')
    os.chdir('..')


def load_sentiment():
    os.chdir('COVID-19-TweetIDs-master/Tweets_Sentiment')
    folders = [x for x in os.listdir()]
    for folder in folders:
        os.chdir(folder)
        for file in os.listdir():
            if '.csv' in file:
                s3.meta.client.upload_file(file, bucket, 'staging/sentiment'+'/'+file)
        os.chdir('..')
    os.chdir('..')
    os.chdir('..')



# In[8]:


def main():
    create_bucket(bucket, 'us-east-2')
    load_added_files()
    load_tweets()
    load_sentiment()


# In[9]:


if __name__ == "__main__":
    main()
