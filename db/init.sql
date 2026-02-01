-- 1. Real-Time Fraud Alerts (Speed Layer Sink)
CREATE TABLE IF NOT EXISTS fraud_alerts (
    alert_id SERIAL PRIMARY KEY,
    user_id VARCHAR(50),
    transaction_time TIMESTAMP,
    amount DECIMAL(10, 2),
    location VARCHAR(100),
    merchant_category VARCHAR(100),
    fraud_type VARCHAR(50), -- 'High Value', 'Impossible Travel'
    detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index for efficient lookups
CREATE INDEX IF NOT EXISTS idx_fraud_alerts_user_time 
    ON fraud_alerts(user_id, transaction_time);

-- 2. Reconciliation Reports (Batch Layer Output)
CREATE TABLE IF NOT EXISTS reconciliation_reports (
    report_id SERIAL PRIMARY KEY,
    report_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    total_ingress_amount DECIMAL(15, 2),
    validated_amount DECIMAL(15, 2),
    difference_amount DECIMAL(15, 2)
);

-- 3. Merchant Fraud Report (Analytical Layer)
CREATE TABLE IF NOT EXISTS merchant_fraud_report (
    report_id SERIAL PRIMARY KEY,
    report_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    merchant_category VARCHAR(100),
    fraud_count INTEGER,
    total_fraud_amount DECIMAL(15, 2),
    UNIQUE (report_date, merchant_category)
);

-- Note: Airflow uses the same fraud_detection database (configured in docker-compose.yml)
