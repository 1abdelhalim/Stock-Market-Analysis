from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime, timedelta
import os
import sys

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

from data_ingestion import fetch_stock_data, validate_data, save_data_to_csv
from delta_lake_processing import partition_data, clean_and_transform_data
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get CSV path from environment variables or use default
CSV_FILE_PATH = os.getenv("CSV_FILE_PATH", "data/tech_stocks.csv")

# Default arguments for the DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Define the DAG
dag = DAG(
    'stock_market_pipeline',
    default_args=default_args,
    description='Stock Market Analysis Pipeline',
    schedule_interval=timedelta(days=1),
    start_date=datetime(2025, 4, 30),
    catchup=False,
)

# Task 1: Ingest data
def ingest_data():
    stock_data = fetch_stock_data()
    validated_data = validate_data(stock_data)
    save_data_to_csv(validated_data, CSV_FILE_PATH)

ingest_task = PythonOperator(
    task_id='ingest_data',
    python_callable=ingest_data,
    dag=dag,
)

# Task 2: Partition data
def partition_data_task():
    partition_data()

partition_task = PythonOperator(
    task_id='partition_data',
    python_callable=partition_data_task,
    dag=dag,
)

# Task 3: Clean and transform data
def clean_transform_data_task():
    clean_and_transform_data()

clean_transform_task = PythonOperator(
    task_id='clean_transform_data',
    python_callable=clean_transform_data_task,
    dag=dag,
)



compute_metrics = PythonOperator(
    task_id='compute_metrics',
    python_callable=compute_metrics_task,
    dag=dag,
)

# Define task dependencies
ingest_task >> partition_task >> clean_transform_task 
