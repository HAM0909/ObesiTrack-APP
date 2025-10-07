import unittest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from pathlib import Path
import sys
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from pydantic import ValidationError

# Ensure 'ObesiTrack' project root is on sys.path so 'app' package is importable
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.schemas.prediction import PredictionInput, PredictionResponse, PredictionHistory
from app.models.prediction import Prediction
from app.models.user import User
from app.routers.prediction import router
from app.database import get_db


class TestPredictionSchemas(unittest.TestCase):
    """Test Pydantic schemas for Prediction"""
    
    def test_prediction_input_schema_validation(self):
        """Test PredictionInput schema validates correctly"""
        input_data = {
            "gender": "Male",
            "age": 30,
            "height": 175.0,
            "weight": 80.0,
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
        
        prediction_input = PredictionInput(**input_data)
        
        self.assertEqual(prediction_input.gender, "Male")
        self.assertEqual(prediction_input.age, 30)
        self.assertEqual(prediction_input.height, 175.0)
        self.assertEqual(prediction_input.weight, 80.0)
        self.assertEqual(prediction_input.fcvc, 2.0)
    
    def test_prediction_input_field_normalization(self):
        """Test PredictionInput schema normalizes field names"""
        input_data = {
            "GENDER": "Male",  # Uppercase
            "AGE": 30,
            "HEIGHT": 175.0,
            "WEIGHT": 80.0,
            "FAMILY_HISTORY_WITH_OVERWEIGHT": "yes",
            "FAVC": "yes",
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
        
        prediction_input = PredictionInput(**input_data)
        
        # Fields should be normalized to lowercase
        self.assertEqual(prediction_input.gender, "Male")
        self.assertEqual(prediction_input.age, 30)
        self.assertEqual(prediction_input.family_history_with_overweight, "yes")
    
    def test_prediction_input_validation_constraints(self):
        """Test PredictionInput schema validation constraints"""
        base_data = {
            "gender": "Male",
            "age": 30,
            "height": 175.0,
            "weight": 80.0,
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
        
        # Test invalid age (too young)
        invalid_data = base_data.copy()
        invalid_data["age"] = 0
        with self.assertRaises(ValidationError):
            PredictionInput(**invalid_data)
        
        # Test invalid age (too old)
        invalid_data = base_data.copy()
        invalid_data["age"] = 150
        with self.assertRaises(ValidationError):
            PredictionInput(**invalid_data)
        
        # Test invalid height (non-positive)
        invalid_data = base_data.copy()
        invalid_data["height"] = 0
        with self.assertRaises(ValidationError):
            PredictionInput(**invalid_data)
        
        # Test invalid weight (non-positive)
        invalid_data = base_data.copy()
        invalid_data["weight"] = 0
        with self.assertRaises(ValidationError):
            PredictionInput(**invalid_data)
        
        # Test invalid fcvc (out of range)
        invalid_data = base_data.copy()
        invalid_data["fcvc"] = 5.0
        with self.assertRaises(ValidationError):
            PredictionInput(**invalid_data)
    
    def test_prediction_input_default_values(self):
        """Test PredictionInput schema default values"""
        minimal_data = {
            "gender": "Female",
            "age": 25,
            "height": 165.0,
            "weight": 60.0
        }
        
        prediction_input = PredictionInput(**minimal_data)
        
        # Test default values
        self.assertEqual(prediction_input.family_history_with_overweight, "yes")
        self.assertEqual(prediction_input.favc, "yes")
        self.assertEqual(prediction_input.fcvc, 2.0)
        self.assertEqual(prediction_input.ncp, 3.0)
        self.assertEqual(prediction_input.caec, "Sometimes")
        self.assertEqual(prediction_input.smoke, "no")
        self.assertEqual(prediction_input.ch2o, 2.0)
        self.assertEqual(prediction_input.scc, "no")
        self.assertEqual(prediction_input.faf, 1.0)
        self.assertEqual(prediction_input.tue, 1.0)
        self.assertEqual(prediction_input.calc, "Sometimes")
        self.assertEqual(prediction_input.mtrans, "Public_Transportation")
    
    def test_prediction_response_schema_validation(self):
        """Test PredictionResponse schema validates correctly"""
        response_data = {
            "prediction": "Normal_Weight",
            "probability": 0.85,
            "confidence": 0.85,
            "bmi": 26.12,
            "risk_level": "Low",
            "recommendations": ["Maintain healthy lifestyle", "Exercise 3x/week"],
            "timestamp": datetime.now()
        }
        
        prediction_response = PredictionResponse(**response_data)
        
        self.assertEqual(prediction_response.prediction, "Normal_Weight")
        self.assertEqual(prediction_response.probability, 0.85)
        self.assertEqual(prediction_response.confidence, 0.85)
        self.assertEqual(prediction_response.bmi, 26.12)
        self.assertEqual(prediction_response.risk_level, "Low")
        self.assertIsInstance(prediction_response.recommendations, list)
        self.assertEqual(len(prediction_response.recommendations), 2)
    
    def test_prediction_response_probability_constraints(self):
        """Test PredictionResponse probability validation constraints"""
        base_data = {
            "prediction": "Normal_Weight",
            "probability": 0.85,
            "confidence": 0.85,
            "bmi": 26.12,
            "risk_level": "Low",
            "recommendations": ["Maintain healthy lifestyle"]
        }
        
        # Test invalid probability (negative)
        invalid_data = base_data.copy()
        invalid_data["probability"] = -0.1
        with self.assertRaises(ValidationError):
            PredictionResponse(**invalid_data)
        
        # Test invalid probability (greater than 1)
        invalid_data = base_data.copy()
        invalid_data["probability"] = 1.5
        with self.assertRaises(ValidationError):
            PredictionResponse(**invalid_data)
        
        # Test invalid confidence (negative)
        invalid_data = base_data.copy()
        invalid_data["confidence"] = -0.1
        with self.assertRaises(ValidationError):
            PredictionResponse(**invalid_data)
        
        # Test invalid confidence (greater than 1)
        invalid_data = base_data.copy()
        invalid_data["confidence"] = 1.5
        with self.assertRaises(ValidationError):
            PredictionResponse(**invalid_data)
    
    def test_prediction_history_schema_validation(self):
        """Test PredictionHistory schema validates correctly"""
        history_data = {
            "id": 1,
            "user_id": 1,
            "prediction": "Normal_Weight",
            "probability": 0.85,
            "bmi": 26.12,
            "risk_level": "Low",
            "input_data": {"gender": "Male", "age": 30},
            "created_at": datetime.now()
        }
        
        prediction_history = PredictionHistory(**history_data)
        
        self.assertEqual(prediction_history.id, 1)
        self.assertEqual(prediction_history.user_id, 1)
        self.assertEqual(prediction_history.prediction, "Normal_Weight")
        self.assertEqual(prediction_history.probability, 0.85)
        self.assertIsInstance(prediction_history.input_data, dict)


class TestPredictionModel(unittest.TestCase):
    """Test Prediction SQLAlchemy model"""
    
    def setUp(self):
        """Set up in-memory SQLite database for testing"""
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        from app.models.base import Base
        
        self.engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(self.engine)
        self.SessionLocal = sessionmaker(bind=self.engine)
        self.db = self.SessionLocal()
    
    def tearDown(self):
        """Clean up database session"""
        self.db.close()
    
    def test_prediction_model_field_validation(self):
        """Test Prediction model creates correctly with all fields"""
        # Create user first (foreign key relationship)
        user = User(
            email="test@example.com",
            username="testuser",
            hashed_password="hashed_password"
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        
        # Create prediction
        prediction = Prediction(
            user_id=user.id,
            gender=1,
            age=30,
            height=175.0,
            weight=80.0,
            family_history_with_overweight="yes",
            fcvc=2.0,
            ncp=3.0,
            caec="Sometimes",
            faf=1.0,
            tue=1.0,
            calc="Sometimes",
            matrans="Public_Transportation",
            favc="yes",
            smoke="no",
            ch2o=2.0,
            scc="no",
            prediction="Normal_Weight",
            probability=0.85,
            confidence=0.85,
            bmi=26.12,
            risk_level="Low",
            input_data={"gender": "Male", "age": 30}
        )
        
        self.db.add(prediction)
        self.db.commit()
        self.db.refresh(prediction)
        
        # Verify all fields are set correctly
        self.assertEqual(prediction.user_id, user.id)
        self.assertEqual(prediction.age, 30)
        self.assertEqual(prediction.height, 175.0)
        self.assertEqual(prediction.weight, 80.0)
        self.assertEqual(prediction.prediction, "Normal_Weight")
        self.assertEqual(prediction.probability, 0.85)
        self.assertEqual(prediction.bmi, 26.12)
        self.assertEqual(prediction.risk_level, "Low")
        self.assertIsInstance(prediction.input_data, dict)
        self.assertIsNotNone(prediction.created_at)
    
    def test_prediction_model_required_fields(self):
        """Test Prediction model with only required fields"""
        # Create user first
        user = User(
            email="test@example.com",
            username="testuser",
            hashed_password="hashed_password"
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        
        # Create prediction with minimal required fields
        prediction = Prediction(
            user_id=user.id,
            prediction="Obesity_Type_I",
            probability=0.90,
            bmi=32.5,
            risk_level="High",
            input_data={"minimal": "data"}
        )
        
        self.db.add(prediction)
        self.db.commit()
        self.db.refresh(prediction)
        
        # Verify required fields
        self.assertEqual(prediction.user_id, user.id)
        self.assertEqual(prediction.prediction, "Obesity_Type_I")
        self.assertEqual(prediction.probability, 0.90)
        self.assertEqual(prediction.bmi, 32.5)
        self.assertEqual(prediction.risk_level, "High")
        self.assertIsNotNone(prediction.id)
        self.assertIsNotNone(prediction.created_at)
    
    def test_prediction_model_user_relationship(self):
        """Test relationship between Prediction and User models"""
        # Create user
        user = User(
            email="test@example.com",
            username="testuser",
            hashed_password="hashed_password"
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        
        # Create prediction
        prediction = Prediction(
            user_id=user.id,
            prediction="Normal_Weight",
            probability=0.85,
            bmi=26.12,
            risk_level="Low",
            input_data={}
        )
        self.db.add(prediction)
        self.db.commit()
        self.db.refresh(prediction)
        
        # Test relationship
        self.assertEqual(prediction.user.id, user.id)
        self.assertEqual(prediction.user.email, "test@example.com")
        self.assertEqual(len(user.predictions), 1)
        self.assertEqual(user.predictions[0].id, prediction.id)


class TestPredictionRoutes(unittest.TestCase):
    """Test prediction API routes"""
    
    def setUp(self):
        """Set up test client and mock dependencies"""
        from fastapi import FastAPI
        from app.auth.dependencies import get_current_user
        
        self.app = FastAPI()
        self.app.include_router(router, prefix="/api/prediction", tags=["predictions"])
        
        # Mock database session
        self.mock_db = Mock(spec=Session)
        
        # Mock current user
        self.mock_user = Mock()
        self.mock_user.id = 1
        self.mock_user.email = "test@example.com"
        self.mock_user.username = "testuser"
        self.mock_user.is_active = True
        
        # Mock model
        self.mock_model = Mock()
        self.app.state.model = self.mock_model
        
        def get_test_db():
            return self.mock_db
            
        def get_test_user():
            return self.mock_user
            
        self.app.dependency_overrides[get_db] = get_test_db
        self.app.dependency_overrides[get_current_user] = get_test_user
        
        self.client = TestClient(self.app)
    
    def tearDown(self):
        """Clean up after tests"""
        self.app.dependency_overrides.clear()
    
    def test_prediction_endpoint_success(self):
        """Test successful prediction endpoint"""
        # Set up mock model prediction result
        self.mock_model.predict.return_value = {
            "prediction": "Normal_Weight",
            "probability": 0.85,
            "confidence": 0.85,
            "bmi": 26.12,
            "risk_level": "Low",
            "recommendations": ["Maintain healthy lifestyle"]
        }
        
        # Mock database operations
        self.mock_db.add.return_value = None
        self.mock_db.commit.return_value = None
        self.mock_db.refresh.return_value = None
        
        prediction_data = {
            "gender": "Male",
            "age": 30,
            "height": 175.0,
            "weight": 80.0,
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
        
        response = self.client.post("/api/prediction/predict", json=prediction_data)
        
        # Verify response
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertEqual(response_data["prediction"], "Normal_Weight")
        self.assertEqual(response_data["probability"], 0.85)
        self.assertEqual(response_data["bmi"], 26.12)
        self.assertEqual(response_data["risk_level"], "Low")
        self.assertIsInstance(response_data["recommendations"], list)
    
    def test_prediction_endpoint_invalid_input(self):
        """Test prediction endpoint with invalid input"""
        invalid_data = {
            "gender": "Male",
            "age": 0,  # Invalid age
            "height": 175.0,
            "weight": 80.0
        }
        
        response = self.client.post("/api/prediction/predict", json=invalid_data)
        
        # Should return validation error
        self.assertEqual(response.status_code, 422)
    
    def test_prediction_endpoint_model_error(self):
        """Test prediction endpoint when model fails"""
        # Mock predictor to raise exception
        self.mock_model.predict.side_effect = Exception("Model prediction failed")
        
        prediction_data = {
            "gender": "Male",
            "age": 30,
            "height": 175.0,
            "weight": 80.0
        }
        
        response = self.client.post("/api/prediction/predict", json=prediction_data)
        
        # Should return internal server error
        self.assertEqual(response.status_code, 500)


if __name__ == "__main__":
    unittest.main()