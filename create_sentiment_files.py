#!/usr/bin/env python
# coding: utf-8

# In[1]:


import boto3
import json
import pandas as pd
import os
from pathlib import Path


# In[2]:


import configparser
config = configparser.ConfigParser()
config.read_file(open('dwh.cfg'))

KEY                    = config.get('AWS','KEY')
SECRET                 = config.get('AWS','SECRET')


# In[3]:


comprehend = boto3.client("comprehend", region_name='us-east-2',
                                              aws_access_key_id=KEY,
                                              aws_secret_access_key=SECRET)


# In[4]:


limiter = 5


# In[5]:


def get_sentiment(df, text='full_text', lang='lang'):
    sentiments = df.apply(lambda x: comprehend.detect_sentiment(Text=x[text], LanguageCode=x[lang]),axis=1)
    sentiments = sentiments.apply(pd.Series)
    sent_final = pd.concat([sentiments.Sentiment, sentiments.SentimentScore.apply((pd.Series))],axis=1)
    return sent_final


# In[6]:


def limit(df,limit=5):
    if limit == None:
        df = df
    else:
        df = df.iloc[:limit,:]
    return df


# In[20]:


df = pd.read_json(r"C:\Users\CGilde01\Udacity Data Engineering\Capstone Project\COVID-19-TweetIDs-master\Tweets_Sentiment\2020-01\tweet_sentiments-coronavirus-tweet-id-2020-01-21-22.jsonl.gz",lines=True)


# In[18]:


data_dirs = ['2020-01', '2020-02', '2020-03', '2020-04']


def main():
    if not os.path.exists('Tweets_Sentiment'):
        os.makedirs('Tweets_Sentiment')
    for data_dir in data_dirs:
        if not os.path.exists('Tweets_Sentiment'+'\\'+data_dir):
            os.makedirs('Tweets_Sentiment'+'\\'+data_dir)
        for path in Path('Tweets_Final//'+data_dir).iterdir():
            if path.name.endswith('jsonl.gz') and path.name.strip('jsonl.gz') not in os.listdir('Tweets_Final'+'\\'+data_dir):
                df = pd.read_json(path,lines=True)
                df = limit(df,limiter)
                df = pd.concat([df[['id',"full_text"]],get_sentiment(df)],axis=1)
                df.to_json('Tweets_Sentiment'+'//2020-01//'+'tweet_sentiments-'+(path.name), orient='records', lines=True, compression='gzip')
                print('file updated & added')


# In[22]:


if __name__ == "__main__":
    main()


# In[ ]:




