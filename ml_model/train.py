import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import pickle
import os

# Create dummy data for training
def generate_training_data(n_samples=1000):
    np.random.seed(42)
    
    # Features
    amounts = np.random.exponential(scale=100, size=n_samples)
    locations = np.random.choice(['New York', 'London', 'Paris', 'Tokyo', 'Sydney'], size=n_samples)
    merchant_categories = np.random.choice(['Retail', 'Food', 'Travel', 'Electronics'], size=n_samples)
    
    # Generate labels (Simple logic for demonstration: High amount or specific location patterns = Fraud)
    labels = []
    for i in range(n_samples):
        is_fraud = 0
        if amounts[i] > 500:
            is_fraud = 1 if np.random.random() > 0.3 else 0
        
        labels.append(is_fraud)
    
    df = pd.DataFrame({
        'amount': amounts,
        'location': locations,
        'merchant_category': merchant_categories,
        'is_fraud': labels
    })
    
    return df

def train_model():
    print("Generating training data...")
    df = generate_training_data()
    
    # Preprocessing
    le_loc = LabelEncoder()
    le_cat = LabelEncoder()
    
    df['location_encoded'] = le_loc.fit_transform(df['location'])
    df['category_encoded'] = le_cat.fit_transform(df['merchant_category'])
    
    X = df[['amount', 'location_encoded', 'category_encoded']]
    y = df['is_fraud']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    print("Training Random Forest model...")
    clf = RandomForestClassifier(n_estimators=100, random_state=42)
    clf.fit(X_train, y_train)
    
    print(f"Model Accuracy: {clf.score(X_test, y_test)}")
    
    # Save model and encoders
    if not os.path.exists('ml_model'):
        os.makedirs('ml_model')
        
    with open('ml_model/model.pkl', 'wb') as f:
        pickle.dump({
            'model': clf,
            'le_loc': le_loc,
            'le_cat': le_cat
        }, f)
    
    print("Model saved to ml_model/model.pkl")

if __name__ == "__main__":
    train_model()
