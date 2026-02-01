# Fraud Detection API Backend
"""
FastAPI backend for the Fraud Detection Dashboard.
Provides endpoints for fraud alerts, statistics, and transaction file uploads.
"""
import os
import json
import csv
from io import StringIO
from datetime import datetime
from typing import List, Optional

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import psycopg2
from psycopg2.extras import RealDictCursor
from kafka import KafkaProducer


# --- Configuration ---
DB_HOST = os.environ.get("DB_HOST", "localhost")
DB_PORT = os.environ.get("DB_PORT", "5432")
DB_NAME = os.environ.get("DB_NAME", "fraud_detection")
DB_USER = os.environ.get("DB_USER", "user")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "password")
KAFKA_BOOTSTRAP = os.environ.get("KAFKA_BOOTSTRAP_SERVERS", "localhost:29092")
KAFKA_TOPIC = os.environ.get("KAFKA_TOPIC", "transactions")


# --- FastAPI App ---
app = FastAPI(
    title="Fraud Detection API",
    description="API for fraud alerts, statistics, and transaction uploads",
    version="1.0.0",
)

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Database Connection ---
def get_db_connection():
    """Get a PostgreSQL connection."""
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        cursor_factory=RealDictCursor,
    )


# --- Kafka Producer ---
kafka_producer = None

def get_kafka_producer():
    """Get or create a Kafka producer."""
    global kafka_producer
    if kafka_producer is None:
        try:
            kafka_producer = KafkaProducer(
                bootstrap_servers=KAFKA_BOOTSTRAP,
                value_serializer=lambda v: json.dumps(v).encode("utf-8"),
            )
        except Exception as e:
            print(f"[API] Failed to connect to Kafka: {e}")
            return None
    return kafka_producer


# --- Pydantic Models ---
class FraudAlert(BaseModel):
    alert_id: int
    user_id: str
    transaction_time: Optional[datetime]
    amount: float
    location: str
    merchant_category: str
    fraud_type: str
    detected_at: datetime


class MerchantStats(BaseModel):
    merchant_category: str
    count: int
    total_amount: float


class ReconciliationReport(BaseModel):
    report_id: int
    report_date: datetime
    total_ingress_amount: float
    validated_amount: float
    difference_amount: float


class Transaction(BaseModel):
    user_id: str
    merchant_category: str
    amount: float
    location: str
    country: str


# --- API Endpoints ---
@app.get("/")
def root():
    return {"status": "online", "service": "Fraud Detection API"}


@app.get("/api/alerts", response_model=List[FraudAlert])
def get_alerts(limit: int = 50):
    """Get recent fraud alerts."""
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT alert_id, user_id, transaction_time, amount, 
                       location, merchant_category, fraud_type, detected_at
                FROM fraud_alerts
                ORDER BY detected_at DESC
                LIMIT %s
                """,
                (limit,),
            )
            alerts = cur.fetchall()
            return [dict(a) for a in alerts]
    finally:
        conn.close()


@app.get("/api/stats", response_model=List[MerchantStats])
def get_stats():
    """Get fraud statistics by merchant category."""
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT merchant_category, 
                       COUNT(*) as count, 
                       COALESCE(SUM(amount), 0) as total_amount
                FROM fraud_alerts
                GROUP BY merchant_category
                ORDER BY count DESC
                """
            )
            stats = cur.fetchall()
            return [dict(s) for s in stats]
    finally:
        conn.close()


@app.get("/api/reports", response_model=List[ReconciliationReport])
def get_reports(limit: int = 10):
    """Get reconciliation reports."""
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT report_id, report_date, total_ingress_amount, 
                       validated_amount, difference_amount
                FROM reconciliation_reports
                ORDER BY report_date DESC
                LIMIT %s
                """,
                (limit,),
            )
            reports = cur.fetchall()
            return [dict(r) for r in reports]
    finally:
        conn.close()


@app.get("/api/fraud-types")
def get_fraud_types():
    """Get count of each fraud type."""
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT fraud_type, COUNT(*) as count
                FROM fraud_alerts
                GROUP BY fraud_type
                """
            )
            return cur.fetchall()
    finally:
        conn.close()


@app.post("/api/transactions")
def send_transaction(transaction: Transaction):
    """Send a single transaction to Kafka."""
    producer = get_kafka_producer()
    if not producer:
        raise HTTPException(status_code=503, detail="Kafka unavailable")

    txn = {
        "user_id": transaction.user_id,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "merchant_category": transaction.merchant_category,
        "amount": transaction.amount,
        "location": transaction.location,
        "country": transaction.country,
    }
    producer.send(KAFKA_TOPIC, txn)
    producer.flush()
    return {"status": "sent", "transaction": txn}


@app.post("/api/upload")
async def upload_transactions(file: UploadFile = File(...)):
    """
    Upload a CSV file with transactions.
    Expected columns: user_id, merchant_category, amount, location, country
    """
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are allowed")

    producer = get_kafka_producer()
    if not producer:
        raise HTTPException(status_code=503, detail="Kafka unavailable")

    try:
        content = await file.read()
        decoded = content.decode("utf-8")
        reader = csv.DictReader(StringIO(decoded))

        count = 0
        for row in reader:
            txn = {
                "user_id": row.get("user_id", f"uploaded_{count}"),
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "merchant_category": row.get("merchant_category", "Unknown"),
                "amount": float(row.get("amount", 0)),
                "location": row.get("location", "Unknown"),
                "country": row.get("country", "Unknown"),
            }
            producer.send(KAFKA_TOPIC, txn)
            count += 1

        producer.flush()
        return {"status": "success", "transactions_sent": count}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")


@app.get("/api/health")
def health_check():
    """Health check endpoint."""
    status = {"api": "healthy", "database": "unknown", "kafka": "unknown"}

    # Check database
    try:
        conn = get_db_connection()
        conn.close()
        status["database"] = "healthy"
    except Exception:
        status["database"] = "unhealthy"

    # Check Kafka
    try:
        producer = get_kafka_producer()
        status["kafka"] = "healthy" if producer else "unhealthy"
    except Exception:
        status["kafka"] = "unhealthy"

    return status


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
