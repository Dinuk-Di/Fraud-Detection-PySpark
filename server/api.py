from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import psycopg2
from psycopg2.extras import RealDictCursor
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db_connection():
    conn = psycopg2.connect(
        host=os.environ.get("DB_HOST", "localhost"),
        database="fraud_detection",
        user=os.environ.get("DB_USER", "user"),
        password=os.environ.get("DB_PASSWORD", "password"),
        cursor_factory=RealDictCursor
    )
    return conn

@app.get("/api/alerts")
def get_alerts():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM fraud_alerts ORDER BY detected_at DESC LIMIT 50")
        alerts = cur.fetchall()
        cur.close()
        conn.close()
        return alerts
    except Exception as e:
        return {"error": str(e)}

@app.get("/api/stats")
def get_stats():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT merchant_category, COUNT(*) as count 
            FROM fraud_alerts 
            GROUP BY merchant_category
        """)
        stats = cur.fetchall()
        cur.close()
        conn.close()
        return stats
    except Exception as e:
        return {"error": str(e)}

@app.get("/api/reports")
def get_reports():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM reconciliation_reports ORDER BY report_date DESC LIMIT 10")
        reports = cur.fetchall()
        cur.close()
        conn.close()
        return reports
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
