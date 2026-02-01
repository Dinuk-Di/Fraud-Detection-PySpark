from pyspark.sql import SparkSession
from pyspark.sql import functions as F
import pandas as pd

# 1. Start the Spark Session
spark = SparkSession.builder \
    .appName("Scalability-Simulation-2026") \
    .getOrCreate()

# 2. Simulate Data Source 1: "User Activity" (Distributed across executors)
# Generating 10 million rows to stress the system
user_activity = spark.range(0, 100000).select(
    F.col("id").alias("user_id"),
    (F.rand() * 100).alias("session_duration"),
    F.when(F.rand() > 0.5, "Mobile").otherwise("Desktop").alias("device")
)

# 3. Simulate Data Source 2: "User Metadata" 
# Generating 1 million rows
user_metadata = spark.range(0, 100000).select(
    F.col("id").alias("user_id"),
    F.when(F.rand() > 0.8, "Gold").otherwise("Silver").alias("membership")
)

# 4. DISTRIBUTED JOIN (This triggers the "Shuffle" - true scalability test)
# Combined dataset simulates combining different source data
enriched_data = user_activity.join(user_metadata, on="user_id", how="inner")

# 5. Analysis & Scalability Simulation
# We calculate the average session duration per membership type
analysis_result = enriched_data.groupBy("membership", "device").agg(
    F.avg("session_duration").alias("avg_duration"),
    F.count("user_id").alias("total_users")
)

# 6. PANDAS CONVERSION (Distributed to Local Analysis)
# IMPORTANT: .toPandas() brings data from executors back to the driver
# Use .limit() to ensure the driver doesn't crash if the analysis is huge
print("\n--- DISTRIBUTED ANALYSIS COMPLETE ---")
final_pdf = analysis_result.toPandas()

print("\n--- PANDAS.INFO() SUMMARY ---")
print(final_pdf.info())

print("\n--- FINAL DATASET PREVIEW ---")
print(final_pdf)

spark.stop()