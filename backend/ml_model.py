"""
VoltGuard ML Model
==================
IsolationForest for battery anomaly detection.
"""

import numpy as np
import joblib
import os
from sklearn.ensemble import IsolationForest
from database import get_history

MODEL_PATH = os.path.join(os.path.dirname(__file__), "anomaly_model.pkl")


def train_model():
    """Train IsolationForest on historical data"""
    history = get_history(500)
    
    if len(history) < 30:
        print(f"[ML] Need 30+ readings, have {len(history)}")
        return None
    
    X = np.array([[h["voltage"], h["current"], h["temperature"]] for h in history])
    
    model = IsolationForest(
        contamination=0.1,
        random_state=42,
        n_estimators=100
    )
    model.fit(X)
    
    joblib.dump(model, MODEL_PATH)
    print(f"[ML] Model trained on {len(X)} samples")
    return model


def load_model():
    """Load or train model"""
    if not os.path.exists(MODEL_PATH):
        return train_model()
    return joblib.load(MODEL_PATH)


def predict_risk(voltage, current, temperature):
    """Predict anomaly risk"""
    model = load_model()
    
    if model is None:
        # Fallback rule-based
        risk = 0
        if voltage < 11.8: risk += 40
        if temperature > 40: risk += 35
        if current > 4: risk += 25
        risk = min(risk, 100)
        
        if risk > 70: return "CRITICAL", risk
        elif risk > 40: return "WARNING", risk
        return "NORMAL", risk
    
    X = np.array([[voltage, current, temperature]])
    pred = model.predict(X)[0]
    score = model.score_samples(X)[0]
    
    # Convert to 0-100 risk
    risk = round(min(max((0.3 - score) * 100, 0), 100), 1)
    
    if pred == -1 or risk > 75:
        return "CRITICAL", risk
    elif risk > 50:
        return "WARNING", risk
    return "NORMAL", risk


if __name__ == "__main__":
    train_model()