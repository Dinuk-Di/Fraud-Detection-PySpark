# Assessment Report: FinTech Fraud Detection System

## 1. Justification of Lambda Architecture

The Lambda Architecture was chosen for this FinTech Fraud Detection System to address the dual requirements of **real-time responsiveness** and **historical accuracy**.

### Speed Layer (Real-time)

- **Role:** The Speed Layer (implemented with Apache Spark Structured Streaming) processes incoming transaction streams from Kafka in real-time.
- **Justification:** In fraud detection, latency is critical. Waiting for batch processing (e.g., end-of-day reconciliation) would mean fraudulent transactions settle before being detected. The Speed Layer enables immediate blocking or flagging of high-value and impossible travel scenarios within seconds.
- **Trade-off:** It prioritizes low latency over perfect consistency or complex historical context.

### Batch Layer (Historical)

- **Role:** The Batch Layer (orchestrated by Apache Airflow) processes the master dataset stored in the Data Lake (Parquet/Postgres) at regular intervals (every 6 hours).
- **Justification:** While the Speed Layer is fast, it may miss context available only after aggregating data over time (e.g., daily spending patterns). The Batch Layer allows for re-processing data with more complex, computationally intensive algorithms and correcting any errors from the Speed Layer. It provides the "source of truth".

### Serving Layer

- **Role:** The Serving Layer (PostgreSQL & React Dashboard) merges views from both layers.
- **Justification:** It provides stakeholders with an up-to-date view (from Speed Layer) while eventually becoming consistent with the Batch Layer's comprehensive reports (Reconciliation).

## 2. Privacy Implications & Ethics

### User Profiling

- **Risk:** The system builds profiles of user spending habits and locations. This "Digital Twin" can be misused for targeted advertising or discrimination (e.g., loan denials based on location history).
- **Mitigation:** The system should strictly limit profiling to fraud indicators. Behavioral data must be pseudo-anonymized where possible.

### Location Tracking

- **Risk:** "Impossible Travel" detection requires continuous location monitoring. This infringes on user privacy if strictly personal movements are tracked outside of transaction contexts.
- **Mitigation:** Location data should only be captured at the point of transaction. Continuous background tracking should be avoided. Data retention policies must ensure location logs are purged after the fraud detection window (e.g., 30 days).

## 3. Data Governance

### Policies for financial Data

1.  **Encryption:** All Personally Identifiable Information (PII) like `user_id` and transaction details must be encrypted both in transit (TLS for Kafka/HTTPs) and at rest (PostgreSQL TDE).
2.  **Access Control:** Role-Based Access Control (RBAC) must be enforced. Only authorized Fraud Analysts should view raw transaction details in the dashboard.
3.  **Audit Trails:** Every access to the `reconciliation_reports` or `fraud_alerts` tables must be logged.
4.  **Data Quality:** The Batch Layer acts as a quality gate, ensuring that data ingested meets the schema requirements before being permanently added to the historical ledger.

## 4. Conclusion

This architecture provides a robust, scalable solution for modern fraud detection, balancing the need for speed with the necessity of accurate execution and reporting, while strictly adhering to ethical data handling practices.
