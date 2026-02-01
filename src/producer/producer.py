# Fraud Detection Data Producer
"""
Generates synthetic credit card transactions and publishes them to Kafka.
Includes configurable fraud injection for High Value and Impossible Travel scenarios.
"""
import os
import time
import json
import random
import argparse
from datetime import datetime
from kafka import KafkaProducer


# --- Configuration ---
CITIES = {
    'New York': {'lat': 40.7128, 'lon': -74.0060, 'country': 'USA'},
    'London': {'lat': 51.5074, 'lon': -0.1278, 'country': 'UK'},
    'Paris': {'lat': 48.8566, 'lon': 2.3522, 'country': 'France'},
    'Tokyo': {'lat': 35.6762, 'lon': 139.6503, 'country': 'Japan'},
    'Sydney': {'lat': -33.8688, 'lon': 151.2093, 'country': 'Australia'},
}

MERCHANT_CATEGORIES = ['Retail', 'Food', 'Travel', 'Electronics', 'Entertainment']
NUM_USERS = 100


def generate_transaction(
    user_id: str = None,
    force_high_value: bool = False,
    location: str = None
) -> dict:
    """Generates a single synthetic transaction."""
    if user_id is None:
        user_id = f"user_{random.randint(1, NUM_USERS)}"

    city_name = location if location else random.choice(list(CITIES.keys()))

    # Exponential distribution for realistic transaction amounts
    amount = random.expovariate(1 / 100)  # Average $100
    if force_high_value:
        amount = random.uniform(5001, 15000)

    return {
        'user_id': user_id,
        'timestamp': datetime.utcnow().isoformat() + 'Z',
        'merchant_category': random.choice(MERCHANT_CATEGORIES),
        'amount': round(amount, 2),
        'location': city_name,
        'country': CITIES[city_name]['country'],
    }


def run_producer(bootstrap_servers: str, topic: str, rate_limit_sec: float):
    """Main producer loop."""
    producer = KafkaProducer(
        bootstrap_servers=bootstrap_servers,
        value_serializer=lambda v: json.dumps(v).encode('utf-8'),
        acks='all',  # Wait for all replicas to acknowledge
    )

    print(f"[Producer] Connected to Kafka at {bootstrap_servers}")
    print(f"[Producer] Publishing to topic: {topic}")
    print(f"[Producer] Rate Limit: {rate_limit_sec}s per transaction")

    try:
        while True:
            # --- Normal Transaction ---
            txn = generate_transaction()
            producer.send(topic, txn)
            print(f"[Normal] {txn['user_id']} | ${txn['amount']:.2f} | {txn['location']}")

            # --- Fraud Injection: High Value (5% chance) ---
            if random.random() < 0.05:
                high_val_txn = generate_transaction(force_high_value=True)
                producer.send(topic, high_val_txn)
                print(f"[FRAUD:HighValue] {high_val_txn['user_id']} | ${high_val_txn['amount']:.2f}")

            # --- Fraud Injection: Impossible Travel (2% chance) ---
            if random.random() < 0.02:
                user = f"user_{random.randint(1, NUM_USERS)}"
                cities = list(CITIES.keys())
                loc1, loc2 = random.sample(cities, 2)  # Two distinct cities

                txn1 = generate_transaction(user_id=user, location=loc1)
                producer.send(topic, txn1)
                print(f"[FRAUD:ImpTravel-1] {user} | {loc1}")

                # Send second transaction almost immediately from a different location
                txn2 = generate_transaction(user_id=user, location=loc2)
                producer.send(topic, txn2)
                print(f"[FRAUD:ImpTravel-2] {user} | {loc2}")

            producer.flush()
            time.sleep(rate_limit_sec)

    except KeyboardInterrupt:
        print("\n[Producer] Shutting down gracefully...")
    finally:
        producer.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fraud Detection Data Producer")
    parser.add_argument(
        '--bootstrap-servers',
        default=os.environ.get('KAFKA_BOOTSTRAP_SERVERS', 'localhost:29092'),
        help='Kafka broker address (default: localhost:29092 for local dev)',
    )
    parser.add_argument(
        '--topic',
        default='transactions',
        help='Kafka topic to publish to',
    )
    parser.add_argument(
        '--rate',
        type=float,
        default=1.0,
        help='Seconds between transactions (default: 1.0)',
    )
    args = parser.parse_args()

    run_producer(args.bootstrap_servers, args.topic, args.rate)
