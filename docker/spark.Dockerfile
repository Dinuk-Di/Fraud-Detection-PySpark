FROM apache/spark:3.5.0-python3

USER root

WORKDIR /app

# Disable Python output buffering for real-time logs
ENV PYTHONUNBUFFERED=1
ENV PYSPARK_PYTHON=/usr/bin/python3
ENV PYSPARK_DRIVER_PYTHON=/usr/bin/python3

# Install Python dependencies
COPY src/spark_jobs/requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy Spark jobs
COPY src/spark_jobs/ .

# Download Kafka and Postgres connectors
RUN mkdir -p /opt/spark/jars && \
    wget -q -P /opt/spark/jars https://repo1.maven.org/maven2/org/apache/spark/spark-sql-kafka-0-10_2.12/3.5.0/spark-sql-kafka-0-10_2.12-3.5.0.jar && \
    wget -q -P /opt/spark/jars https://repo1.maven.org/maven2/org/apache/kafka/kafka-clients/3.5.0/kafka-clients-3.5.0.jar && \
    wget -q -P /opt/spark/jars https://repo1.maven.org/maven2/org/apache/spark/spark-token-provider-kafka-0-10_2.12/3.5.0/spark-token-provider-kafka-0-10_2.12-3.5.0.jar && \
    wget -q -P /opt/spark/jars https://repo1.maven.org/maven2/org/apache/commons/commons-pool2/2.11.1/commons-pool2-2.11.1.jar && \
    wget -q -P /opt/spark/jars https://repo1.maven.org/maven2/org/postgresql/postgresql/42.7.1/postgresql-42.7.1.jar

CMD ["/usr/bin/python3", "streaming_fraud_detection.py"]
