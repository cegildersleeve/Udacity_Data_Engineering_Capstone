# Capstone project

## Project scope
This project combines data from Twitter (https://www.twitter.com), AWS Comprehend(https://aws.amazon.com/comprehend) 
and static data sources, Covid-19 data from John's Hopkings (https://aws.amazon.com/data-exchange/covid-19/?
cards.sort-by=item.additionalFields.order&cards.sort-order=asc) and government response to Covid-19 data from
Oxford University (https://www.bsg.ox.ac.uk/research/research-projects/coronavirus-government-response-tracker).
The data was gathered to help understand how public sentiment has changed with the development of the Covid-19 pandemic through Twitter and Natural
Language Processing sentiment analysis, e.g. are there more negative tweets as deaths and cases increase or are there more negative tweets when 
more stringent policies are implemented. 

### Implementation details
In order to gather data from Twitter, we need to access its API (https://developer.twitter.com/en/docs), which can be 
accomplished conveniently via tweepy (http://www.tweepy.org/). For this project I decided to work with historical 
tweets from (https://github.com/echen102/COVID-19-TweetIDs).  Due to Twitter sharing privacy restrictions and limitations, the data is
a set of Tweet ID's that need to be "hydrated" (populated with tweet text and information). After the tweet is hydated, it's text can be ran through
AWS Comprehend (c.f. `detect_sentiment()` method in `create_sentiment_files.py`). The Tweet ID's can be hydrated using the hydrate.py script. The Twitter, John's Hopkins, and Oxford data
can be joined together at their country and date fields. However, due to differences in country spelling, the country fields need to be standardized. Once
prepped, note that datasets are also transferred to S3 before they are loaded into Redshift. Using the aforementioned AWS toolstack to process data is 
convenient in our case, since it can scale to large amounts of data/users easily and is fully managed. Since we do not want to run 
individual scripts to manually populate our data source, we use Airflow(https://airflow.apache.org/) to create tables
in Redshift, stage data and derive fact and dimension tables (c.f. `airflow/capstone_dag.py`).

Once this has been done we have access to the following star-schema based data model: 
 
| Table | Description |
--- | ---
| staging_tweets | Staging table for tweets
| users | Dimension table containing user related information derived from staging_tweets
| geo | Dimension table containing location data derived from tweets
| covid | Dimension table containing covid related data (e.g. confirmed cases, deaths, recovery, etc.). Could also be used as the fact table in another schema.
| gov | Dimension table containing government policy information related to Covid-19 (e.g. school closures, lock-down measures, relief packages, overall stringency, etc)
| tweets | Fact table containing tweet related information (including sentiment) and covid data, derived from all tables

Note: The data dictionary (c.f. `DATADICT.md`) contains a description of every attribute for all tables listed above.

Using the data model above we can answer questions regarding relationships between tweets, their sentiment, 
users, their location, the covid-19 pandemic, and their related policies, by country.

### Handling alternative scenarios
This section discusses strategies to deal with the following scenarios:
1. Data is increased 100x  
2. Data pipeline is run on daily basis by 7 am every day
3. Database needs to be accessed by 100+ users simultaneously

#### Data is increased 100x
Since we decided to use scalable, fully managed cloud services to store and process our data, we might only need to 
increase the available resources (e.g. number/CPU/RAM of Redshift nodes) to handle an increase in data volume. 

#### Data pipleline is run on a daily basis by 7 am every day
As the static datasets do not change on a daily basis, the major challenge here, is to process the amount of newly 
captured tweets in an acceptable and scheduled time. Updating the dag to run function fully on the cloud and through a specified
Airflow schedule interval should make this easily feasible.

#### Database needs to be accessed by 100+ users simultaneously
Besides increasing Redshift resources as mentioned above, we could deal with an increase in users by precomputing the 
most complicated (in terms of required processing power) and/or most desired queries and store them in an additional 
table.

## Prerequisites
* Twitter developer account including registered app with consumer key/secret and access token/secret
* Kaggle account in order to access static datasets
* AWS account with dedicated user including access key ID and secret access key
* Access to AWS Kinesis Firehose including existing delivery stream
* Access to AWS Comprehend
* Access to a (running) AWS Redshift cluster, where access means:
    - Having created an attached a security group allowing access on port 5439
    - Having created an attached a role allowing Redshift to access buckets on AWS S3
    - Create/drop/insert/update rights for the Redshift instance
* Working installation of Airflow, where working means:
    - Airflow web server and scheduler are running
    - Connection to AWS is set up using `aws_default` ID
    - Connection to Redshift is set up using `redshift_default` ID
    - AWS IAM role is set up as Airflow variable using `aws_iam_role` as key
* Unix-like environment (Linux, macOS, WSL on Windows)
* Python 3.6+
* Python packages tweepy, boto3, airflow, etc. (c.f. `capstone_env.yml` and `requirements.txt`)

## Usage
1. Double check that you meet all prerequisites specified above
2. Clone this repository
3. Edit `app.cfg` and enter your information in the corresponding sections (aws, twitter, etc.)  
4. Hydrate and geolocate a historical tweet ID's file using the hydrate.py and clean_tweets.py My tweets found here: 
(https://github.com/echen102/COVID-19-TweetIDs)
5. Get the most recent Covid-19 case statistics from John's Hopkins through AWS.(Data is already processed/merged on AWS), found here: https://aws.amazon.com/data-exchange/covid-19/?
cards.sort-by=item.additionalFields.order&cards.sort-order=asc) and 
get the most recent government response data to Covid-19 from Oxford, found here (https://www.bsg.ox.ac.uk/research/research-projects/coronavirus-government-response-tracker):
6. Move the capstone_dag file to your Airflow dags bag and the plugins to your Airflow plugins folder.
7. Verify that the capstone_dag has been correctly parsed by Airflow via `airflow list_tasks capstone_dag --tree`
8. Trigger a DAG run via `airflow trigger_dag capstone_dag`. If just want to run a specific task do so via
`airflow run -i capstone_dag<task_id>`
9. Have fun analyzing the data

## Limitations
* Location of Twitter users are not standardized, may be NULL and may contain data which is not a location at all. 
Further pre-processing, i.e. via geopy(https://github.com/geopy/geopy) and its 
Nomiatim geocoder(https://geopy.readthedocs.io/en/1.10.0/#geopy.geocoders.Nominatim), may be required to derive 
actual countries from users locations. This was done in my case using clean_tweets.py
* Government data and Covid-19 countries were standardized using the pycountry package. However, not all countries 
(particularly smaller countries) were able to be found and matched. Additional time should be put into standardizing country
names, if there is a particular country of interest.
