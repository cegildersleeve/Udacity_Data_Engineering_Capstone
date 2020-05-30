#!/usr/bin/env python
# coding: utf-8

# In[133]:


import pandas as pd
import numpy as np
import pycountry
import os
from pathlib import Path
import datetime as dt
# In[134]:

os.chdir(str(Path(__file__).parent))

def get_country_code(name=None,alpha_2=None,alpha_3=None):
    code = ''
    if name != None:
        try:
            code = pycountry.countries.get(name=name).alpha_2.lower()
        except:
            pass
    if alpha_2 != None:
        try:
            code = pycountry.countries.get(alpha_2=alpha_2).alpha_2.lower()
        except:
            pass
    if alpha_3 != None:
        try:
            code = pycountry.countries.get(alpha_3=alpha_3).alpha_2.lower()
        except:
            pass
    return code


# In[135]:


jhu_file = [x for x in os.listdir() if 'jhu' in x][0]


# In[136]:


gov_file = [x for x in os.listdir() if 'gov' in x][0]


# In[137]:


if __name__ == '__main__':
    jhu = pd.read_csv(jhu_file)
    jhu.date = pd.to_datetime(jhu['date']).dt.strftime('%Y-%m-%d')
    jhu['country_code'] = jhu.apply(lambda x: get_country_code(name=x.country_region,alpha_3=x.iso3),axis=1)
    jhu.to_csv(jhu_file,index=False)

    gov = pd.read_csv(gov_file)
    gov.Date = pd.to_datetime(gov['Date']).dt.strftime('%Y-%m-%d')
    gov['country_code'] = gov.apply(lambda x: get_country_code(name=x.CountryName,alpha_3=x.CountryCode),axis=1)
    gov.to_csv(gov_file,index=False)


# In[ ]:
