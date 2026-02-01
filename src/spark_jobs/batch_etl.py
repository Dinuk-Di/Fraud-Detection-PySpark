# Spark Batch ETL (Batch Layer)
"""
Batch processing job triggered by Airflow.
Reads raw archived transactions, validates, and generates reconciliation reports.
"""
import os
from datetime import datetime, timedelta
from pyspark.sql import SparkSession
from pyspark.sql import functions as F


# --- Configuration ---
DB_HOST = os.environ.get("DB_HOST", "localhost")
DB_PORT = os.environ.get("DB_PORT", "5432")
DB_NAME = os.environ.get("DB_NAME", "fraud_detection")
DB_USER = os.environ.get("DB_USER", "user")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "password")
RAW_DATA_DIR = os.environ.get("RAW_DATA_DIR", "/tmp/raw-transactions")
PROCESSED_DATA_DIR = os.environ.get("PROCESSED_DATA_DIR", "/tmp/processed-transactions")


def get_spark_session() -> SparkSession:
    """Creates and returns a configured SparkSession for batch processing."""
    return (
        SparkSession.builder
        .appName("FraudDetection-BatchLayer")
        .config("spark.jars.packages", "org.postgresql:postgresql:42.7.1")
        .config("spark.sql.shuffle.partitions", "8")
        .getOrCreate()
    )


def run_batch_etl():
    spark = get_spark_session()
    spark.sparkContext.setLogLevel("WARN")
    jdbc_url = f"jdbc:postgresql://{DB_HOST}:{DB_PORT}/{DB_NAME}"

    print("[BatchLayer] Starting Batch ETL...")

    # --- 1. Read Raw Archived Data (from Speed Layer's Parquet sink) ---
    try:
        raw_df = spark.read.parquet(RAW_DATA_DIR)
        print(f"[BatchLayer] Loaded {raw_df.count()} raw transactions from {RAW_DATA_DIR}")
    except Exception as e:
        print(f"[BatchLayer] No raw data found or error: {e}")
        return

    # --- 2. Read Known Fraud Alerts (from Speed Layer's Postgres sink) ---
    fraud_df = (
        spark.read
        .format("jdbc")
        .option("url", jdbc_url)
        .option("dbtable", "fraud_alerts")
        .option("user", DB_USER)
        .option("password", DB_PASSWORD)
        .option("driver", "org.postgresql.Driver")
        .load()
        .select("user_id", "transaction_time")
    )

    # --- 3. Filter out Fraudulent Transactions ---
    # Left anti-join: Keep only transactions that are NOT in fraud_alerts
    valid_df = raw_df.join(
        fraud_df,
        (raw_df["user_id"] == fraud_df["user_id"]) &
        (raw_df["transaction_time"] == fraud_df["transaction_time"]),
        "left_anti"
    )
    valid_count = valid_df.count()
    print(f"[BatchLayer] Valid (non-fraud) transactions: {valid_count}")

    # --- 4. Write Valid Transactions to Processed Parquet (Data Lake) ---
    (
        valid_df.write
        .mode("append")
        .partitionBy("country")
        .parquet(PROCESSED_DATA_DIR)
    )
    print(f"[BatchLayer] Wrote valid transactions to {PROCESSED_DATA_DIR}")

    # --- 5. Generate Reconciliation Report ---
    total_ingress = raw_df.agg(F.sum("amount")).collect()[0][0] or 0.0
    validated_amount = valid_df.agg(F.sum("amount")).collect()[0][0] or 0.0
    difference = total_ingress - validated_amount

    report_df = spark.createDataFrame([
        (datetime.utcnow(), total_ingress, validated_amount, difference)
    ], ["report_date", "total_ingress_amount", "validated_amount", "difference_amount"])

    (
        report_df.write
        .format("jdbc")
        .option("url", jdbc_url)
        .option("dbtable", "reconciliation_reports")
        .option("user", DB_USER)
        .option("password", DB_PASSWORD)
        .option("driver", "org.postgresql.Driver")
        .mode("append")
        .save()
    )
    print(f"[BatchLayer] Reconciliation Report: Ingress=${total_ingress:.2f}, Valid=${validated_amount:.2f}, Diff=${difference:.2f}")

    spark.stop()
    print("[BatchLayer] Batch ETL Complete.")


if __name__ == "__main__":
    run_batch_etl()
