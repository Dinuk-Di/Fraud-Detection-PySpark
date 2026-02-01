# Use the official Spark image with Python support
FROM apache/spark:python3

# Set user to root to install pandas
USER root

# Install pandas as required by your script
RUN pip install --no-cache-dir pandas

# Set the working directory
WORKDIR /opt/spark/work-dir

# Copy your script into the container
COPY app/spark_script.py /opt/spark/work-dir/spark_script.py

# Switch back to the spark user
USER spark