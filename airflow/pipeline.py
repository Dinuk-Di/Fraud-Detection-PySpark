# pipeline.py

from datetime import timedelta

from tasks import (
    extract_window_data,
    reconcile_fraud_vs_valid,
    write_parquet,
    insert_reconciliation,
    generate_fraud_report,
    generate_reconciliation_report,
)

DEFAULT_ARGS = {
    "owner": "fraud-pipeline",
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
}


def get_default_args():
    """Expose default args to DAG file."""
    return DEFAULT_ARGS


def get_task_callables():
    """
    Small helper to return all Python callables for the DAG definition.
    Keeps dag.py shorter.
    """
    return {
        "extract_window_data": extract_window_data,
        "reconcile_fraud_vs_valid": reconcile_fraud_vs_valid,
        "write_parquet": write_parquet,
        "insert_reconciliation": insert_reconciliation,
        "generate_fraud_report": generate_fraud_report,
        "generate_reconciliation_report": generate_reconciliation_report,
    }