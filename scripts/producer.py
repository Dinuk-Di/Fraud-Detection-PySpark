import time
import json
import random
import argparse
from datetime import datetime, timedelta
# from kafka import KafkaProducer # relying on run_command to install kafka-python

# Mock data configuration
CITIES = {
    'New York': {'lat': 40.7128, 'lon': -74.0060, 'country': 'USA'},
    'London': {'lat': 51.5074, 'lon': -0.1278, 'country': 'UK'},
    'Paris': {'lat': 48.8566, 'lon': 2.3522, 'country': 'France'},
    'Tokyo': {'lat': 35.6762, 'lon': 139.6503, 'country': 'Japan'},
    'Sydney': {'lat': -33.8688, 'lon': 151.2093, 'country': 'Australia'}
}

MERCHANT_CATEGORIES = ['Retail', 'Food', 'Travel', 'Electronics']
USERS = [f'user_{i}' for i in range(1, 101)]

def generate_transaction(user_id=None, force_high_value=False, location=None):
    if user_id is None:
        user_id = random.choice(USERS)
    
    city_name = location if location else random.choice(list(CITIES.keys()))
    
    amount = random.expovariate(1/100) # Average $100
    if force_high_value:
        amount = random.uniform(5000, 10000)
    
    transaction = {
        'user_id': user_id,
        'timestamp': datetime.utcnow().isoformat(),
        'merchant_category': random.choice(MERCHANT_CATEGORIES),
        'amount': round(amount, 2),
        'location': city_name
    }
    return transaction

def run_producer(bootstrap_servers=None):
    if bootstrap_servers is None:
        import os
        bootstrap_servers = os.environ.get('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')(
        bootstrap_servers=bootstrap_servers,
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )
    
    print(f"Producer connected to {bootstrap_servers}")
    
    try:
        while True:
            # Normal transaction
            txn = generate_transaction()
            producer.send('transactions', txn)
            print(f"Sent: {txn}")
            
            # 5% chance of High Value Transaction
            if random.random() < 0.05:
                high_val_txn = generate_transaction(force_high_value=True)
                producer.send('transactions', high_val_txn)
                print(f"Sent [High Value]: {high_val_txn}")
            
            # 2% chance of Impossible Travel
            if random.random() < 0.02:
                user = random.choice(USERS)
                # First transaction
                cities = list(CITIES.keys())
                loc1 = cities[0]
                loc2 = cities[1] # Different city
                
                txn1 = generate_transaction(user_id=user, location=loc1)
                producer.send('transactions', txn1)
                print(f"Sent [Imp Travel 1]: {txn1}")
                
                # Immediate second transaction from far away
                txn2 = generate_transaction(user_id=user, location=loc2)
                # Modify timestamp to be within 10 mins (though processing is real-time, this is for record)
                # Note: Spark processing time will catch the close arrival of messages
                producer.send('transactions', txn2)
                print(f"Sent [Imp Travel 2]: {txn2}")
            
            time.sleep(1) # Rate limit
            
    except KeyboardInterrupt:
        print("Stopping producer...")
    finally:
        producer.close()

if __name__ == "__main__":
    import sys
    # Install kafka-python if needed inside the script execution for simplicity in this env
    # subprocess.check_call([sys.executable, "-m", "pip", "install", "kafka-python"])
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--bootstrap-servers', default='localhost:9092')
    args = parser.parse_args()
    
    run_producer(args.bootstrap_servers)
