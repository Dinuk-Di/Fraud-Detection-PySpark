# 🛡️ FinTech Fraud Detection System (Lambda Architecture)

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.9+-3776AB.svg)
![React](https://img.shields.io/badge/react-%2320232a.svg?style=flat&logo=react&logoColor=%2361DAFB)
![Apache Spark](https://img.shields.io/badge/Apache%20Spark-FMR-E25A1C.svg)
![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=flat&logo=docker&logoColor=white)

A comprehensive real-time fraud detection pipeline built using **Lambda Architecture**. This system processes transaction streams for immediate fraud flagging while maintaining accurate batch reconciliation for historical reporting.

---

## 🏗️ Architecture Overview

The system simulates a digital wallet environment where transactions are generated, ingested, processed for real-time insights, and archived for batch reporting.

**Key Layers:**

1.  **Ingestion:** Apache Kafka buffers high-throughput transaction streams.
2.  **Speed Layer:** Spark Structured Streaming performs real-time ML inference (Random Forest) and window-based logic (Impossible Travel detection).
3.  **Batch Layer:** Apache Airflow orchestrates periodic ETL jobs to validate and reconcile data in PostgreSQL.
4.  **Serving Layer:** A FastAPI + React dashboard provides real-time alerts and analytic reports.

---

## 🚀 Getting Started

### Prerequisites

- **Docker & Docker Compose** (Desktop version recommended for Windows/Mac)
- **Git**

### Installation & Running

The entire stack is containerized. You can launch it with a single command.

1.  **Clone the repository:**

    ```bash
    git clone <repository_url>
    cd <repository_folder>
    ```

2.  **Start the application:**

    ```bash
    docker-compose up --build
    ```

    > **Note:** The first build may take a few minutes as it downloads base images (Spark, Kafka, etc.).

3.  **Access the interfaces:**
    - 📊 **Dashboard:** [http://localhost:5173](http://localhost:5173)
    - 🌪️ **Airflow:** [http://localhost:8081](http://localhost:8081) (User: `admin`, Pass: `admin`)
    - 🔧 **Spark Master:** [http://localhost:8080](http://localhost:8080)

---

## 💻 Tech Stack

| Component          | Technology                 | Description                             |
| ------------------ | -------------------------- | --------------------------------------- |
| **Ingestion**      | Apache Kafka               | Event streaming platform                |
| **Streaming**      | Spark Structured Streaming | Real-time processing engine             |
| **Orchestration**  | Apache Airflow             | Workflow automation for batch jobs      |
| **Database**       | PostgreSQL                 | Relational storage for alerts & reports |
| **ML Model**       | Scikit-Learn               | Random Forest Classifier                |
| **Backend**        | FastAPI (Python)           | REST API to serve data                  |
| **Frontend**       | React + Tailwind CSS       | Interactive analytic dashboard          |
| **Infrastructure** | Docker Compose             | Container orchestration                 |

---

## 📂 Project Structure

```text
├── dags/                  # Airflow DAGs for batch processing
├── frontend/              # React Application (Vite + Tailwind)
├── ml_model/              # ML Training scripts and artifacts
├── scripts/
│   ├── producer.py        # Simulates transaction traffic
│   └── spark_streaming.py # Real-time processing logic
├── server/                # FastAPI Backend
├── report/                # Assessment and Ethics report
├── docker-compose.yml     # Infrastructure definition
└── Readme.md              # Project documentation
```

---

## 🕵️ Features

- **Real-time Fraud Alerts**: flags transactions >$5000 or from suspicious locations immediately.
- **Impossible Travel Detection**: Identifies users physically moving between distant cities in unrealistic timeframes.
- **Machine Learning**: Uses a trained Random Forest model to predict fraud based on patterns.
- **Reconciliation Reporting**: Automated Airflow jobs compare ingress vs. processed data to ensure integrity.
- **Interactive Dashboard**: Live feed of alerts and charts visualization.

---

## 📜 License

This project is open-source and available under the [MIT License](LICENSE).
