FROM python:3.10-slim

WORKDIR /app

# Disable Python output buffering for real-time logs
ENV PYTHONUNBUFFERED=1

COPY src/producer/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/producer/producer.py .

CMD ["python", "producer.py"]
