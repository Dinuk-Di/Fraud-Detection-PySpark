from airflow import DAG
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2023, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'fraud_etl_dag',
    default_args=default_args,
    description='ETL for Fraud Detection System',
    schedule_interval=timedelta(hours=6),
    catchup=False
)

# 1. Reconciliation Task (SQL-based for simplicity)
# Ideally this would read from Parquet (Speed Layer output) and Postgres (Batch Layer)
# Here we simulate the logic by aggregating the 'validated_transactions' table 
# and comparing it against a hypothetical 'ingress_log' or just summarising.

reconciliation_query = """
    INSERT INTO reconciliation_reports (total_ingress_amount, validated_amount, difference_amount)
    SELECT 
        COALESCE(SUM(amount), 0) as total_ingress, 
        COALESCE(SUM(CASE WHEN is_reconciled = true THEN amount ELSE 0 END), 0) as validated,
        COALESCE(SUM(amount) - SUM(CASE WHEN is_reconciled = true THEN amount ELSE 0 END), 0) as diff
    FROM validated_transactions
    WHERE transaction_time >= NOW() - INTERVAL '6 hours';
"""

reconcile_task = PostgresOperator(
    task_id='reconcile_transactions',
    postgres_conn_id='postgres_default',
    sql=reconciliation_query,
    dag=dag,
)

# 2. Daily Volume Report
volume_report_query = """
    -- This is just a placeholder logic to mark transactions as reconciled after processing
    UPDATE validated_transactions
    SET is_reconciled = TRUE
    WHERE transaction_time >= NOW() - INTERVAL '6 hours'
      AND is_reconciled = FALSE;
"""

mark_reconciled_task = PostgresOperator(
    task_id='mark_reconciled',
    postgres_conn_id='postgres_default',
    sql=volume_report_query,
    dag=dag,
)

reconcile_task >> mark_reconciled_task
