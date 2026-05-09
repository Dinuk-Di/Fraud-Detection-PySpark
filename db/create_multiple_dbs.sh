#!/bin/bash
set -e

# Create the Airflow metadb
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" <<-EOSQL
    CREATE DATABASE airflow;
    CREATE USER airflow WITH PASSWORD 'airflow';
    GRANT ALL PRIVILEGES ON DATABASE airflow TO airflow;
EOSQL

# Grant schema permissions for airflow user
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" -d airflow <<-EOSQL
    ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO airflow;
    ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO airflow;
    GRANT ALL PRIVILEGES ON SCHEMA public TO airflow;
EOSQL

# Create the Fraud Detection app db with appuser
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" <<-EOSQL
    CREATE DATABASE frauddb;
    CREATE USER appuser WITH PASSWORD 'apppassword';
    GRANT ALL PRIVILEGES ON DATABASE frauddb TO appuser;
EOSQL

# Grant schema permissions for appuser
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" -d frauddb <<-EOSQL
    ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO appuser;
    ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO appuser;
    GRANT ALL PRIVILEGES ON SCHEMA public TO appuser;
EOSQL

echo "✓ Databases and users created successfully"
