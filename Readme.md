# FinTech Fraud Detection System

A scalable, fault-tolerant **Lambda Architecture** implementation for real-time and batch fraud detection using Apache Kafka, Spark, Airflow, and PostgreSQL.

## 🏗️ Architecture

```
┌─────────────┐     ┌───────────┐     ┌─────────────────────────┐
│  Producer   │────▶│   Kafka   │────▶│  Spark Streaming        │
│ (Synthetic) │     │  (Queue)  │     │  - High Value Detection │
└─────────────┘     └───────────┘     │  - Impossible Travel    │
                          │           └───────────┬─────────────┘
                          │                       │
                          ▼                       ▼
                    ┌───────────┐          ┌────────────┐
                    │ Raw Data  │          │ PostgreSQL │
                    │ (Parquet) │          │  (Alerts)  │
                    └─────┬─────┘          └────────────┘
                          │
         ┌────────────────┼────────────────┐
         │            Airflow              │
         │      (Every 6 hours)            │
         └────────────────┬────────────────┘
                          │
                          ▼
                   ┌─────────────┐     ┌──────────────────┐
                   │ Spark Batch │────▶│ Reconciliation   │
                   │    ETL      │     │ Reports (Postgres)│
                   └─────────────┘     └──────────────────┘
```

## 📁 Project Structure

```
.
├── docker-compose.yml        # Orchestrates all services
├── docker/                   # Dockerfiles
│   ├── producer.Dockerfile
│   └── spark.Dockerfile
├── src/
│   ├── producer/             # Data ingestion
│   │   ├── producer.py
│   │   └── requirements.txt
│   └── spark_jobs/           # Processing
│       ├── streaming_fraud_detection.py
│       ├── batch_etl.py
│       └── requirements.txt
├── dags/                     # Airflow DAGs
│   └── fraud_detection_pipeline.py
└── db/
    └── init.sql              # Database schema
```

## 🚀 Quick Start

### Prerequisites

- Docker Desktop (8GB+ RAM allocated)
- Docker Compose v2+

### Run the Pipeline

```bash
# 1. Start all services
docker-compose up -d --build

# 2. View logs
docker-compose logs -f spark-streaming

# 3. Check fraud alerts (after a few minutes)
docker exec -it postgres psql -U user -d fraud_detection -c "SELECT * FROM fraud_alerts LIMIT 10;"

# 4. Access Airflow UI
# Open http://localhost:8080 (admin/admin)
```

### Stop

```bash
docker-compose down -v
```

## 🔍 Fraud Detection Rules

| Rule                  | Description                                                     | Threshold    |
| --------------------- | --------------------------------------------------------------- | ------------ |
| **High Value**        | Transaction amount exceeds threshold                            | > $5,000     |
| **Impossible Travel** | Same user transacts from different countries within time window | < 10 minutes |

## 📊 Data Flow

1. **Producer** generates 1 transaction/second with 5% High Value and 2% Impossible Travel fraud injection.
2. **Kafka** buffers transactions in `transactions` topic.
3. **Spark Streaming** applies fraud rules in real-time, writes alerts to PostgreSQL.
4. **Airflow** triggers batch ETL every 6 hours for reconciliation.

## 🛠️ Configuration (Environment Variables)

| Variable                  | Default      | Description          |
| ------------------------- | ------------ | -------------------- |
| `KAFKA_BOOTSTRAP_SERVERS` | `kafka:9092` | Kafka broker address |
| `DB_HOST`                 | `postgres`   | Database host        |
| `DB_USER`                 | `user`       | Database username    |
| `DB_PASSWORD`             | `password`   | Database password    |

## 📈 Scalability & Fault Tolerance

- **Kafka**: Horizontal scaling via partitions
- **Spark**: Checkpointing for exactly-once semantics
- **Airflow**: Retry logic on task failures
- **PostgreSQL**: Connection pooling ready

---

_EC8207 ABDA Mini Project - Scenario 2: FinTech Fraud Detection_
