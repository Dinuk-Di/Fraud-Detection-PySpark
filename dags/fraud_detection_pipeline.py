# Fraud Detection Pipeline DAG
"""
Airflow DAG to orchestrate the batch layer of the fraud detection system.
Triggers Spark batch ETL job every 6 hours.
"""
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator
from datetime import datetime, timedelta

# --- DAG Configuration ---
default_args = {
    'owner': 'fraud-detection-team',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    dag_id='fraud_detection_pipeline',
    default_args=default_args,
    description='Batch ETL and Reconciliation for Fraud Detection System',
    schedule_interval=timedelta(hours=6),
    catchup=False,
    tags=['fraud', 'etl', 'spark'],
)

# --- Task 1: Run Spark Batch ETL ---
# This triggers the batch_etl.py script to process raw data
run_spark_batch = BashOperator(
    task_id='run_spark_batch_etl',
    bash_command='''
        docker exec spark-processor spark-submit \
            --master local[*] \
            /app/batch_etl.py
    ''',
    dag=dag,
)

# --- Task 2: Generate Merchant Fraud Report ---
# SQL query to generate fraud statistics by merchant category
merchant_fraud_report_sql = """
    INSERT INTO merchant_fraud_report (report_date, merchant_category, fraud_count, total_fraud_amount)
    SELECT 
        NOW() as report_date,
        merchant_category,
        COUNT(*) as fraud_count,
        SUM(amount) as total_fraud_amount
    FROM fraud_alerts
    WHERE detected_at >= NOW() - INTERVAL '6 hours'
    GROUP BY merchant_category
    ON CONFLICT DO NOTHING;
"""

generate_merchant_report = PostgresOperator(
    task_id='generate_merchant_fraud_report',
    postgres_conn_id='fraud_detection_db',
    sql=merchant_fraud_report_sql,
    dag=dag,
)

# --- Task 3: Cleanup Old Raw Data (Optional, for disk management) ---
cleanup_old_data = BashOperator(
    task_id='cleanup_old_raw_data',
    bash_command='''
        # Keep only last 7 days of raw data
        find /tmp/raw-transactions -type f -mtime +7 -delete 2>/dev/null || true
    ''',
    dag=dag,
)

# --- DAG Dependencies ---
run_spark_batch >> generate_merchant_report >> cleanup_old_data
