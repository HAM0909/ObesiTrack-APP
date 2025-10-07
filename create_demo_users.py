#!/usr/bin/env python3
"""Create demo users for ObesiTrack application"""

import sys
import os
import asyncio
from pathlib import Path

# Add project root to Python path
PROJECT_ROOT = Path(__file__).parent.resolve()
sys.path.insert(0, str(PROJECT_ROOT))

import requests
import json

SERVER_URL = "http://localhost:8000"

def create_demo_users():
    """Create demo users via API"""
    
    # Demo users to create
    demo_users = [
        {
            "email": "admin@obesittrack.com",
            "username": "admin",
            "password": "admin123"
        },
        {
            "email": "test@obesittrack.com", 
            "username": "testuser",
            "password": "test123"
        }
    ]
    
    print("🔨 Creating demo users...")
    
    for user_data in demo_users:
        try:
            # Register user
            response = requests.post(
                f"{SERVER_URL}/api/auth/register",
                json=user_data,
                timeout=10
            )
            
            if response.status_code == 201:
                print(f"✅ Created user: {user_data['email']}")
            elif response.status_code == 400:
                result = response.json()
                if "already exists" in result.get("detail", "").lower():
                    print(f"ℹ️  User already exists: {user_data['email']}")
                else:
                    print(f"⚠️  Error creating {user_data['email']}: {result.get('detail', 'Unknown error')}")
            else:
                print(f"❌ Failed to create {user_data['email']}: Status {response.status_code}")
                print(f"   Response: {response.text}")
                
        except requests.exceptions.ConnectionError:
            print(f"❌ Cannot connect to server at {SERVER_URL}")
            print("   Make sure the server is running: uvicorn main:app --reload --port 8000")
            return False
        except Exception as e:
            print(f"❌ Error creating user {user_data['email']}: {e}")
    
    return True

def test_prediction_api():
    """Test the prediction functionality"""
    
    print("\n🧪 Testing prediction API...")
    
    # Login first
    login_data = {
        "email": "admin@obesittrack.com",
        "password": "admin123"
    }
    
    try:
        # Login
        response = requests.post(
            f"{SERVER_URL}/api/auth/login",
            json=login_data,  # JSON data as expected by the API
            timeout=10
        )
        
        if response.status_code != 200:
            print(f"❌ Login failed: Status {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
        token_data = response.json()
        access_token = token_data["access_token"]
        print(f"✅ Login successful")
        
        # Test prediction
        prediction_data = {
            "gender": "male",
            "age": 25,
            "height": 170.0,
            "weight": 70.0,
            "family_history_with_overweight": "yes",
            "favc": "yes",
            "fcvc": 2.0,
            "ncp": 3.0,
            "caec": "Sometimes",
            "smoke": "no",
            "ch2o": 2.0,
            "scc": "no",
            "faf": 1.0,
            "tue": 1.0,
            "calc": "Sometimes",
            "mtrans": "Public_Transportation"
        }
        
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        response = requests.post(
            f"{SERVER_URL}/api/prediction/predict",
            json=prediction_data,
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Prediction successful!")
            print(f"   Prediction: {result.get('prediction', 'N/A')}")
            print(f"   Confidence: {result.get('confidence', 'N/A'):.1%}")
            print(f"   BMI: {result.get('bmi', 'N/A')}")
            print(f"   Risk Level: {result.get('risk_level', 'N/A')}")
            return True
        else:
            print(f"❌ Prediction failed: Status {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"❌ Cannot connect to server at {SERVER_URL}")
        return False
    except Exception as e:
        print(f"❌ Error testing prediction: {e}")
        return False

if __name__ == "__main__":
    print("=== ObesiTrack Demo Users Setup ===\n")
    
    # Create demo users
    if create_demo_users():
        print("\n✅ Demo users setup complete!")
        
        # Test prediction
        if test_prediction_api():
            print("\n🎉 Everything is working correctly!")
        else:
            print("\n⚠️  Prediction API has issues - check server logs")
    else:
        print("\n❌ Demo users setup failed!")