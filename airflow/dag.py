# dag.py

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago

from pipeline import get_default_args, get_task_callables


with DAG(
    dag_id="fraud_etl_pipeline",
    description="FinTech Fraud Detection — ETL and reconciliation every 6 hours",
    default_args=get_default_args(),
    schedule_interval="0 */6 * * *",  # Every 6 hours
    start_date=days_ago(1),
    catchup=False,
    tags=["fraud-detection", "fintech", "etl"],
    doc_md="""
## Fraud ETL Pipeline

Runs every 6 hours. Tasks:
1. `extract_window_data` — Query raw transactions for the last 6 hours
2. `reconcile_fraud_vs_valid` — Compute fraud vs validated metrics
3. `write_parquet` — Persist validated records to Parquet (Data Warehouse)
4. `insert_reconciliation` — Save reconciliation record to PostgreSQL
5. `generate_fraud_report` — CSV: fraud attempts by merchant category
6. `generate_reconciliation_report` — CSV: ingress vs validated amounts
    """,
) as dag:

    callables = get_task_callables()

    t1_extract = PythonOperator(
        task_id="extract_window_data",
        python_callable=callables["extract_window_data"],
        provide_context=True,
    )

    t2_reconcile = PythonOperator(
        task_id="reconcile_fraud_vs_valid",
        python_callable=callables["reconcile_fraud_vs_valid"],
        provide_context=True,
    )

    t3_parquet = PythonOperator(
        task_id="write_parquet",
        python_callable=callables["write_parquet"],
        provide_context=True,
    )

    t4_insert = PythonOperator(
        task_id="insert_reconciliation",
        python_callable=callables["insert_reconciliation"],
        provide_context=True,
    )

    t5_fraud_report = PythonOperator(
        task_id="generate_fraud_report",
        python_callable=callables["generate_fraud_report"],
        provide_context=True,
    )

    t6_reconciliation_report = PythonOperator(
        task_id="generate_reconciliation_report",
        python_callable=callables["generate_reconciliation_report"],
        provide_context=True,
    )

    t1_extract >> t2_reconcile >> t3_parquet >> t4_insert >> [t5_fraud_report, t6_reconciliation_report]