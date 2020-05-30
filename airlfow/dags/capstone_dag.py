from datetime import datetime, timedelta
from pathlib import Path
from airflow import DAG
from airflow.models import Variable
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.bash_operator import BashOperator
from airflow.operators.postgres_operator import PostgresOperator
from airflow.operators.s3_to_redshift_operator import S3ToRedshiftTransfer
from airflow.operators.check_operator import CheckOperator, ValueCheckOperator
from operators.load_dimensions import LoadDimensionOperator
from operators.load_fact import LoadFactOperator
from operators.basic_check import DataQualityOperator

import os


master_path = '/c/Users/CGilde01/Udacity_Data_Engineering/Capstone_Project/'
pybash='python3 '+master_path

import sql_queries
from sql_queries import SqlQueries

# specify DAG default arguments
default_args = {
    'owner': 'chad',
    'start_date': datetime(2020, 4, 1),
    'depends_on_past': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
    'catchup': False,
    'email_on_retry': False,
    'aws_conn_id': 'aws_default',
    'postgres_conn_id': 'redshift_default',
    'redshift_conn_id': 'redshift_default',
    'params': {
        's3_bucket':'udacity-capstone-cg',
        's3_region': 'us-east-2',
        'redshift_schema': 'public',
        'aws_iam_role': "arn:aws:iam::794471706531:role/dwhRole"
    }
}

# define DAG
dag = DAG(dag_id='capstone_dag',
         description='Load and transform data data from S3 into Redshift',
         default_args=default_args,
         schedule_interval=None)

# define tasks
start = DummyOperator(task_id='start_execution',
                    dag=dag)


standardize_countries = BashOperator(
    task_id='standardize_countries',
    bash_command=pybash+'standardize_countries.py',
    dag=dag
)
upload_raw_data = BashOperator(
    task_id='upload_raw_data_to_s3',
    bash_command=pybash+'push_to_s3.py',
    dag=dag
)

create_tables = PostgresOperator(
    task_id='create_tables',
    sql=SqlQueries.create_tables,
    dag=dag
)

stage_tweets = S3ToRedshiftTransfer(
    task_id='stage_tweets_to_redshift',
    schema='public',
    table='staging_tweets',
    s3_bucket='udacity-capstone-cg',
    s3_key='staging',
    copy_options=['CSV', 'IGNOREHEADER 1', 'FILLRECORD', 'COMPUPDATE OFF', 'STATUPDATE OFF', 'TRUNCATECOLUMNS'],
    dag=dag
)

stage_sentiment = S3ToRedshiftTransfer(
    task_id='stage_sentiment_to_redshift',
    schema='public',
    table='sentiment',
    s3_bucket='udacity-capstone-cg',
    s3_key='staging',
    copy_options=['CSV', 'IGNOREHEADER 1', 'FILLRECORD', 'COMPUPDATE OFF', 'STATUPDATE OFF', 'TRUNCATECOLUMNS'],
    dag=dag
)

stage_covid = S3ToRedshiftTransfer(
    task_id='stage_covid_to_redshift',
    schema='public',
    table='jhu',
    s3_bucket='udacity-capstone-cg',
    s3_key='staging',
    copy_options=['CSV', 'IGNOREHEADER 1', 'FILLRECORD', 'COMPUPDATE OFF', 'STATUPDATE OFF', 'TRUNCATECOLUMNS'],
    dag=dag
)

stage_gov = S3ToRedshiftTransfer(
    task_id='stage_gov_to_redshift',
    schema='public',
    table='gov',
    s3_bucket='udacity-capstone-cg',
    s3_key='staging',
    copy_options=['CSV', 'IGNOREHEADER 1', 'FILLRECORD', 'COMPUPDATE OFF', 'STATUPDATE OFF', 'TRUNCATECOLUMNS'],
    dag=dag
)

get_ready_to_load = DummyOperator(task_id='Get_ready_to_load',
                    dag=dag)

load_tweets_table = LoadFactOperator(
    task_id='Load_tweets_fact_table',
    dag=dag,
    aws_credentials_id="aws_credentials",
    table="tweets",
    sql_query=SqlQueries.tweets_table_insert
)
load_user_dimension_table = LoadDimensionOperator(
    task_id='Load_user_dim_table',
    dag=dag,
    table='"user"',
    sql_query=SqlQueries.user_table_insert
)

load_geo_dimension_table = LoadDimensionOperator(
    task_id='Load_geo_dim_table',
    dag=dag,
    table="geo",
    sql_query=SqlQueries.geo_table_insert
)

run_basic_checks = DataQualityOperator(
    task_id='Run_basic_checks',
    dag=dag,
    tables=['tweets', 'user', 'geo', 'jhu', 'gov'],
)
end = DummyOperator(task_id='stop_execution',dag=dag)

# define task dependencies
start >> standardize_countries >> upload_raw_data
upload_raw_data >> create_tables
create_tables >> [stage_gov,stage_sentiment,stage_covid, stage_tweets] >> get_ready_to_load >> [load_user_dimension_table, load_geo_dimension_table, load_tweets_table]
[load_user_dimension_table, load_geo_dimension_table, load_tweets_table] >> run_basic_checks >> end
