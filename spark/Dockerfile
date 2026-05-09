FROM apache/spark:3.5.3

USER root

# Install system tools needed for curl (if not already present)
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl && \
    rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# Copy the fraud detector script
COPY fraud_detector.py /opt/spark-app/fraud_detector.py

# Download PostgreSQL JDBC driver (42.7.3)
# Ref: official JDBC download page / Maven Central.[web:82][web:90]
RUN curl -L -o /opt/spark/jars/postgresql-42.7.3.jar \
    https://jdbc.postgresql.org/download/postgresql-42.7.3.jar

# Download Kafka connector JARs for Spark 3.5.x
# Using the 0-10 Kafka integration artifacts for Scala 2.12 and Spark 3.5.1.[web:83][web:87]
RUN curl -L -o /opt/spark/jars/spark-sql-kafka-0-10_2.12-3.5.1.jar \
      https://repo1.maven.org/maven2/org/apache/spark/spark-sql-kafka-0-10_2.12/3.5.1/spark-sql-kafka-0-10_2.12-3.5.1.jar && \
    curl -L -o /opt/spark/jars/kafka-clients-3.4.1.jar \
      https://repo1.maven.org/maven2/org/apache/kafka/kafka-clients/3.4.1/kafka-clients-3.4.1.jar && \
    curl -L -o /opt/spark/jars/spark-token-provider-kafka-0-10_2.12-3.5.1.jar \
      https://repo1.maven.org/maven2/org/apache/spark/spark-token-provider-kafka-0-10_2.12/3.5.1/spark-token-provider-kafka-0-10_2.12-3.5.1.jar && \
    curl -L -o /opt/spark/jars/commons-pool2-2.11.1.jar \
      https://repo1.maven.org/maven2/org/apache/commons/commons-pool2/2.11.1/commons-pool2-2.11.1.jar

# Create Ivy cache directory with correct permissions (for dynamic resolution if ever needed)
RUN mkdir -p /home/spark/.ivy2 && chown -R spark:spark /home/spark/.ivy2

USER spark

CMD ["spark-submit", \
  "--master", "local[*]", \
  "--driver-memory", "1g", \
  "/opt/spark-app/fraud_detector.py"]