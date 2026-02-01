# Spark Structured Streaming - Fraud Detection (Speed Layer)
"""
Real-time fraud detection using Spark Structured Streaming.
Detects: High Value transactions (>$5000), Impossible Travel (same user, different countries, <10 min).
Sinks: Fraud alerts to PostgreSQL, raw data to local storage for batch layer.
"""
import os
from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import StructType, StructField, StringType, DoubleType
from pyspark.sql.window import Window


# --- Configuration ---
KAFKA_BOOTSTRAP = os.environ.get("KAFKA_BOOTSTRAP_SERVERS", "localhost:29092")
KAFKA_TOPIC = os.environ.get("KAFKA_TOPIC", "transactions")
DB_HOST = os.environ.get("DB_HOST", "localhost")
DB_PORT = os.environ.get("DB_PORT", "5432")
DB_NAME = os.environ.get("DB_NAME", "fraud_detection")
DB_USER = os.environ.get("DB_USER", "user")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "password")
CHECKPOINT_DIR = os.environ.get("CHECKPOINT_DIR", "/tmp/spark-checkpoints")
RAW_DATA_DIR = os.environ.get("RAW_DATA_DIR", "/tmp/raw-transactions")


# --- Schema ---
TRANSACTION_SCHEMA = StructType([
    StructField("user_id", StringType(), True),
    StructField("timestamp", StringType(), True),
    StructField("merchant_category", StringType(), True),
    StructField("amount", DoubleType(), True),
    StructField("location", StringType(), True),
    StructField("country", StringType(), True),
])


def get_spark_session() -> SparkSession:
    """Creates and returns a configured SparkSession."""
    return (
        SparkSession.builder
        .appName("FraudDetection-SpeedLayer")
        .config("spark.jars.packages",
                "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0,"
                "org.postgresql:postgresql:42.7.1")
        .config("spark.sql.shuffle.partitions", "8")  # Tune for local
        .config("spark.streaming.stopGracefullyOnShutdown", "true")
        .getOrCreate()
    )


def write_fraud_to_postgres(batch_df, batch_id):
    """Writes a micro-batch of fraud alerts to PostgreSQL."""
    if batch_df.isEmpty():
        return

    jdbc_url = f"jdbc:postgresql://{DB_HOST}:{DB_PORT}/{DB_NAME}"

    (
        batch_df
        .select(
            F.col("user_id"),
            F.col("transaction_time"),
            F.col("amount"),
            F.col("location"),
            F.col("merchant_category"),
            F.col("fraud_type"),
        )
        .write
        .format("jdbc")
        .option("url", jdbc_url)
        .option("dbtable", "fraud_alerts")
        .option("user", DB_USER)
        .option("password", DB_PASSWORD)
        .option("driver", "org.postgresql.Driver")
        .mode("append")
        .save()
    )
    print(f"[Batch {batch_id}] Wrote {batch_df.count()} fraud alerts to Postgres.")


def main():
    spark = get_spark_session()
    spark.sparkContext.setLogLevel("WARN")
    print("[SpeedLayer] Starting Spark Structured Streaming...")

    # --- Read from Kafka ---
    raw_stream = (
        spark.readStream
        .format("kafka")
        .option("kafka.bootstrap.servers", KAFKA_BOOTSTRAP)
        .option("subscribe", KAFKA_TOPIC)
        .option("startingOffsets", "latest")
        .option("failOnDataLoss", "false")
        .load()
    )

    # --- Parse JSON ---
    parsed_df = (
        raw_stream
        .select(F.from_json(F.col("value").cast("string"), TRANSACTION_SCHEMA).alias("data"))
        .select("data.*")
        .withColumn("transaction_time", F.to_timestamp(F.col("timestamp")))
        .drop("timestamp")
    )

    # =========================================================================
    # RULE 1: High Value Transaction (amount > $5000)
    # =========================================================================
    high_value_df = (
        parsed_df
        .filter(F.col("amount") > 5000)
        .withColumn("fraud_type", F.lit("High Value"))
        .drop("country")  # Drop to match impossible_travel_df schema
    )

    # =========================================================================
    # RULE 2: Impossible Travel Detection (Stateful Processing)
    # Same user_id, different country, within 10 minutes.
    # Uses a Watermark + Self-Join approach.
    # =========================================================================
    watermarked_df = (
        parsed_df
        .withWatermark("transaction_time", "15 minutes")  # Allow late data up to 15 min
    )

    # Self-join on user_id within a time window
    # We compare each transaction with previous transactions from the same user
    df_left = watermarked_df.alias("t1")
    df_right = watermarked_df.alias("t2")

    impossible_travel_df = (
        df_left.join(
            df_right,
            (F.col("t1.user_id") == F.col("t2.user_id")) &
            (F.col("t1.transaction_time") > F.col("t2.transaction_time")) &
            (F.col("t1.transaction_time") <= F.col("t2.transaction_time") + F.expr("INTERVAL 10 MINUTES")) &
            (F.col("t1.country") != F.col("t2.country")),
            "inner"
        )
        .select(
            F.col("t1.user_id").alias("user_id"),
            F.col("t1.transaction_time").alias("transaction_time"),
            F.col("t1.amount").alias("amount"),
            F.col("t1.location").alias("location"),
            F.col("t1.merchant_category").alias("merchant_category"),
        )
        .withColumn("fraud_type", F.lit("Impossible Travel"))
        .dropDuplicates(["user_id", "transaction_time"])  # Avoid duplicate alerts
    )

    # =========================================================================
    # UNION both fraud streams
    # =========================================================================
    all_fraud_df = high_value_df.unionByName(impossible_travel_df)

    # =========================================================================
    # SINK 1: Write Fraud Alerts to PostgreSQL
    # =========================================================================
    fraud_query = (
        all_fraud_df.writeStream
        .foreachBatch(write_fraud_to_postgres)
        .outputMode("append")
        .option("checkpointLocation", f"{CHECKPOINT_DIR}/fraud-alerts")
        .trigger(processingTime="5 seconds")
        .start()
    )

    # =========================================================================
    # SINK 2: Archive Raw Data to Local Parquet (for Batch Layer)
    # =========================================================================
    archive_query = (
        parsed_df.writeStream
        .format("parquet")
        .option("path", RAW_DATA_DIR)
        .option("checkpointLocation", f"{CHECKPOINT_DIR}/raw-archive")
        .partitionBy("country")
        .trigger(processingTime="30 seconds")
        .start()
    )

    print("[SpeedLayer] Streaming queries started. Waiting for termination...")
    spark.streams.awaitAnyTermination()


if __name__ == "__main__":
    main()
