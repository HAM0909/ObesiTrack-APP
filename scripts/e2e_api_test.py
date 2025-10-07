import os
import random
import string
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Use SQLite for local e2e test
os.environ['DATABASE_URL'] = 'sqlite:///./obesity_tracker.db'
os.environ['DEBUG'] = 'true'

from fastapi.testclient import TestClient
from main import app
from app.ml.predictor import ObesityPredictor
from app.database import init_db
import asyncio

# Inject a dummy model to bypass loading external pickled assets
class DummyModel:
    def predict(self, X):
        return [1]
    def predict_proba(self, X):
        import numpy as np
        return np.array([[0.2, 0.8]])

predictor = ObesityPredictor()
predictor.model = DummyModel()
predictor.label_encoder = None
predictor.feature_encoder = None
app.state.model = predictor

# Initialize database tables (run async init_db synchronously)
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
loop.run_until_complete(init_db())

client = TestClient(app)

suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=7))
email = f"e2e_{suffix}@example.com"
username = f"user_{suffix}"

# 1) Register
reg = client.post('/api/auth/register', json={
    'email': email,
    'username': username,
    'password': 'secret123'
})
print('Register:', reg.status_code, reg.text)
assert reg.status_code == 201, f"Register failed: {reg.text}"

# 2) Login
login = client.post('/api/auth/login', json={'email': email, 'password': 'secret123'})
print('Login:', login.status_code, login.text)
assert login.status_code == 200, f"Login failed: {login.text}"

token = login.json()['access_token']
headers = {'Authorization': f'Bearer {token}'}

# 3) Predict
payload = {
    "Gender": "Male",
    "Age": 30,
    "Height": 175.0,
    "Weight": 75.0,
    "family_history_with_overweight": "yes",
    "FAVC": "no",
    "FCVC": 2.0,
    "NCP": 3.0,
    "CAEC": "Sometimes",
    "SMOKE": "no",
    "CH2O": 2.0,
    "SCC": "no",
    "FAF": 1.0,
    "TUE": 1.0,
    "CALC": "Sometimes",
    "MTRANS": "Public_Transportation"
}

pred = client.post('/api/prediction/predict', headers=headers, json=payload)
print('Predict:', pred.status_code, pred.text)
assert pred.status_code == 200, f"Predict failed: {pred.text}"

print('\nE2E test passed successfully.')
