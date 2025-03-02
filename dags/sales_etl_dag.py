# dags/sales_etl_dag.py
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator

import sys
sys.path.append('/opt/airflow/scripts')  # Add this line before importing your script

from etl_pipeline import extract_data, transform_data, load_data

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
    'start_date': datetime(2023, 1, 1),
}

dag = DAG(
    'sales_etl_pipeline',
    default_args=default_args,
    description='ETL pipeline for sales data',
    schedule_interval=timedelta(days=1),
    catchup=False,
)

# Task to extract data
extract_task = PythonOperator(
    task_id='extract_data',
    python_callable=extract_data,
    dag=dag,
)

# Task to transform data
transform_task = PythonOperator(
    task_id='transform_data',
    python_callable=transform_data,
    op_args=[extract_task.output],
    dag=dag,
)

# Task to load data
load_task = PythonOperator(
    task_id='load_data',
    python_callable=load_data,
    op_args=[transform_task.output],
    dag=dag,
)

# Task to validate data quality
validate_task = BashOperator(
    task_id='validate_data',
    bash_command='echo "Data validation complete"',
    dag=dag,
)

# Define task dependencies
extract_task >> transform_task >> load_task >> validate_task