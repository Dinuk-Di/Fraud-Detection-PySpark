# README: FinTech Fraud Detection System (Lambda Architecture)

## 1. Project Objective & Context

The goal is to architect and implement an end-to-end data pipeline for a digital wallet provider to detect fraudulent transactions in real-time while maintaining a daily ledger of transaction volumes. The system simulates a real-world environment where data is ingested, processed for immediate insights, and orchestrated for historical reporting.

### Architecture Overview (Lambda Design)

* 
**Producer:** Python script simulating credit card transactions: `{user_id, timestamp, merchant_category, amount, location}`.


* 
**Ingestion (Kafka):** Acts as the buffer for incoming transaction streams.


* 
**Speed Layer (Spark Streaming):** Real-time ML inference and windowing logic to filter and flag fraudulent activities.


* 
**Batch Layer (Airflow):** Scheduled ETL process every 6 hours to move validated data to a Data Warehouse (Parquet files) and calculate total volumes.


* 
**Serving Layer (PostgreSQL & React):** Stores alerts and reconciliation reports for visualization on a dashboard.



---

## 2. Technical Stack

As per the project requirements, the solution utilizes:

* 
**Ingestion:** Apache Kafka (Producers, Topics, Partitions).


* 
**Stream Processing:** Apache Spark Structured Streaming.


* 
**Orchestration:** Apache Airflow.


* 
**Storage/Sink:** PostgreSQL (for alerts/reports) and File System (Parquet).


* 
**Frontend:** React.js for the Analytic Report dashboard.



---

## 3. Database Schema & Initialization

The following tables are required in PostgreSQL to support the pipeline deliverables.

```sql
-- 1. Real-Time Fraud Alerts (Speed Layer Sink)
CREATE TABLE fraud_alerts (
    alert_id SERIAL PRIMARY KEY,
    user_id VARCHAR(50),
    transaction_time TIMESTAMP,
    amount DECIMAL(10, 2),
    location VARCHAR(100),
    merchant_category VARCHAR(100),
    fraud_type VARCHAR(50), -- 'High Value', 'Impossible Travel', or 'ML Prediction'
    detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Validated Transactions (Batch Layer Sink)
CREATE TABLE validated_transactions (
    transaction_id SERIAL PRIMARY KEY,
    user_id VARCHAR(50),
    transaction_time TIMESTAMP,
    amount DECIMAL(10, 2),
    location VARCHAR(100),
    merchant_category VARCHAR(100),
    is_reconciled BOOLEAN DEFAULT FALSE
);

-- 3. Reconciliation Reports (Orchestration Output)
CREATE TABLE reconciliation_reports (
    report_id SERIAL PRIMARY KEY,
    report_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    total_ingress_amount DECIMAL(15, 2), -- Sum of all raw data
    validated_amount DECIMAL(15, 2),     -- Sum of non-fraud data
    [cite_start]difference_amount DECIMAL(15, 2)     -- Total Ingress vs Validated [cite: 69]
);

```

---

## 4. Implementation Requirements for Cursor

### A. Data Producer (`producer.py`)

* Generate clean, self-explainable logs.


* Inject occasional high-value transactions (>$5000).


* Inject "Impossible Travel" scenarios: Same `user_id` from two different countries within 10 minutes.



### B. Real-Time Logic (`spark_processor.py`)

* **ML Inference:** Use a pre-trained Scikit-learn model (Random Forest) to flag fraud based on `amount` and `location`.
* 
**Windowing:** Handle Event Time vs. Processing Time to detect impossible travel within a 10-minute window.


* 
**Trigger:** Immediately push flagged transactions to the `fraud_alerts` table.



### C. Batch Orchestration (`airflow_dag.py`)

* Trigger an ETL process every 6 hours.


* Calculate total volume processed.


* 
**Deliverable:** Generate a "Reconciliation Report" comparing Total Ingress Amount vs. Validated Amount.



### D. Analytic Report (React Frontend)

* 
**Requirement:** A visualization or table showing "Fraud Attempts by Merchant Category".


* Display the Reconciliation status from the database.

---

## 5. Folder Structure

```text
project-root/
[cite_start]├── docker-compose.yml       # Kafka, Spark, Postgres, Airflow [cite: 23]
├── ml_model/
│   ├── train.py             # Script to train and save the .pkl model
│   └── model.pkl            # Trained fraud detection model
├── scripts/
[cite_start]│   ├── producer.py          # Python mock data generator [cite: 20]
[cite_start]│   └── spark_streaming.py   # Spark processing script [cite: 21]
├── dags/
[cite_start]│   └── fraud_etl_dag.py     # Airflow DAG for batch jobs [cite: 22]
[cite_start]├── frontend/                # React Dashboard [cite: 24]
└── report/
    [cite_start]└── assessment_report.md # 1500-word justification and ethics [cite: 26]

```

---

## 6. Project Ethics & Governance

The final report must include a discussion on:

* 
**Privacy Implications:** User profiling in FinTech and location tracking.


* 
**Data Governance:** How to apply policies to sensitive financial data.