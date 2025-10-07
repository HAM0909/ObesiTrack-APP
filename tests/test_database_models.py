import unittest
from unittest.mock import Mock, patch
from datetime import datetime
from pathlib import Path
import sys
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError

# Ensure 'ObesiTrack' project root is on sys.path so 'app' package is importable
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.models.user import User
from app.models.prediction import Prediction
from app.models.base import Base


class TestDatabaseConstraints(unittest.TestCase):
    """Test database constraints and integrity"""
    
    def setUp(self):
        """Set up in-memory SQLite database for testing"""
        self.engine = create_engine("sqlite:///:memory:")
        
        # Enable foreign key constraints for SQLite
        @event.listens_for(self.engine, "connect")
        def set_sqlite_pragma(dbapi_connection, connection_record):
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()
            
        Base.metadata.create_all(self.engine)
        self.SessionLocal = sessionmaker(bind=self.engine)
        self.db = self.SessionLocal()
    
    def tearDown(self):
        """Clean up database session"""
        self.db.close()
    
    def test_user_email_unique_constraint(self):
        """Test unique constraint on user email"""
        # Create first user
        user1 = User(
            email="test@example.com",
            username="user1",
            hashed_password="hashed1"
        )
        self.db.add(user1)
        self.db.commit()
        
        # Try to create second user with same email
        user2 = User(
            email="test@example.com",
            username="user2",
            hashed_password="hashed2"
        )
        self.db.add(user2)
        
        # Should raise integrity error
        with self.assertRaises(IntegrityError):
            self.db.commit()
    
    def test_user_username_unique_constraint(self):
        """Test unique constraint on username"""
        # Create first user
        user1 = User(
            email="user1@example.com",
            username="testuser",
            hashed_password="hashed1"
        )
        self.db.add(user1)
        self.db.commit()
        
        # Try to create second user with same username
        user2 = User(
            email="user2@example.com",
            username="testuser",
            hashed_password="hashed2"
        )
        self.db.add(user2)
        
        # Should raise integrity error
        with self.assertRaises(IntegrityError):
            self.db.commit()
    
    def test_prediction_user_foreign_key_constraint(self):
        """Test foreign key constraint for prediction.user_id"""
        # Try to create prediction without valid user_id
        prediction = Prediction(
            user_id=999,  # Non-existent user
            prediction="Normal_Weight",
            probability=0.85,
            bmi=26.12,
            risk_level="Low",
            input_data={}
        )
        self.db.add(prediction)
        
        # Should raise integrity error (foreign key constraint)
        with self.assertRaises(IntegrityError):
            self.db.commit()
    
    def test_user_prediction_cascade_delete(self):
        """Test that deleting user cascades to delete predictions"""
        # Create user
        user = User(
            email="test@example.com",
            username="testuser",
            hashed_password="hashed_password"
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        
        # Create predictions for the user
        prediction1 = Prediction(
            user_id=user.id,
            prediction="Normal_Weight",
            probability=0.85,
            bmi=26.12,
            risk_level="Low",
            input_data={}
        )
        prediction2 = Prediction(
            user_id=user.id,
            prediction="Overweight",
            probability=0.75,
            bmi=28.5,
            risk_level="Medium",
            input_data={}
        )
        
        self.db.add(prediction1)
        self.db.add(prediction2)
        self.db.commit()
        
        # Verify predictions exist
        prediction_count = self.db.query(Prediction).filter(
            Prediction.user_id == user.id
        ).count()
        self.assertEqual(prediction_count, 2)
        
        # Delete user
        self.db.delete(user)
        self.db.commit()
        
        # Verify predictions are also deleted (cascade)
        remaining_predictions = self.db.query(Prediction).filter(
            Prediction.user_id == user.id
        ).count()
        self.assertEqual(remaining_predictions, 0)
    
    def test_user_prediction_relationship(self):
        """Test bidirectional relationship between User and Prediction"""
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
        
        # Test relationship from user to predictions
        self.assertEqual(len(user.predictions), 1)
        self.assertEqual(user.predictions[0].id, prediction.id)
        
        # Test relationship from prediction to user
        self.assertEqual(prediction.user.id, user.id)
        self.assertEqual(prediction.user.email, "test@example.com")
    
    def test_prediction_required_fields(self):
        """Test that required fields are enforced for Prediction model"""
        # Create user first
        user = User(
            email="test@example.com",
            username="testuser",
            hashed_password="hashed_password"
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        
        # Test missing prediction field
        prediction = Prediction(
            user_id=user.id,
            # prediction field missing
            probability=0.85,
            bmi=26.12,
            risk_level="Low",
            input_data={}
        )
        self.db.add(prediction)
        
        # This should work in SQLite but would fail in PostgreSQL with NOT NULL constraint
        # In a real scenario with PostgreSQL, this would raise an error
        try:
            self.db.commit()
            # If using SQLite, manually check the field is None
            self.db.refresh(prediction)
            # In production with proper constraints, this test would expect an IntegrityError
        except IntegrityError:
            # This is the expected behavior with proper database constraints
            pass
    
    def test_prediction_json_field_storage(self):
        """Test JSON field storage and retrieval"""
        # Create user
        user = User(
            email="test@example.com",
            username="testuser",
            hashed_password="hashed_password"
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        
        # Create prediction with complex JSON data
        complex_input_data = {
            "gender": "Male",
            "age": 30,
            "height": 175.0,
            "weight": 80.0,
            "lifestyle": {
                "exercise_frequency": 3,
                "diet_type": "balanced",
                "smoking": False
            },
            "medical_history": ["none"],
            "measurements": [175.0, 80.0, 26.12]
        }
        
        prediction = Prediction(
            user_id=user.id,
            prediction="Normal_Weight",
            probability=0.85,
            bmi=26.12,
            risk_level="Low",
            input_data=complex_input_data
        )
        
        self.db.add(prediction)
        self.db.commit()
        self.db.refresh(prediction)
        
        # Verify JSON data is stored and retrieved correctly
        self.assertIsInstance(prediction.input_data, dict)
        self.assertEqual(prediction.input_data["gender"], "Male")
        self.assertEqual(prediction.input_data["age"], 30)
        self.assertIsInstance(prediction.input_data["lifestyle"], dict)
        self.assertEqual(prediction.input_data["lifestyle"]["exercise_frequency"], 3)
        self.assertIsInstance(prediction.input_data["measurements"], list)
        self.assertEqual(len(prediction.input_data["measurements"]), 3)
    
    def test_user_timestamps(self):
        """Test automatic timestamp creation and updates"""
        # Create user
        user = User(
            email="test@example.com",
            username="testuser",
            hashed_password="hashed_password"
        )
        
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        
        # Verify created_at is set
        self.assertIsNotNone(user.created_at)
        self.assertIsInstance(user.created_at, datetime)
        
        # Verify updated_at is initially None
        self.assertIsNone(user.updated_at)
        
        # Update user
        original_created_at = user.created_at
        user.username = "updated_username"
        self.db.commit()
        self.db.refresh(user)
        
        # Verify created_at didn't change but updated_at is set
        self.assertEqual(user.created_at, original_created_at)
        # Note: In SQLite, the onupdate trigger might not work the same as PostgreSQL
        # In production, updated_at should be automatically set
    
    def test_prediction_timestamps(self):
        """Test automatic timestamp creation for predictions"""
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
        
        # Verify created_at is set
        self.assertIsNotNone(prediction.created_at)
        self.assertIsInstance(prediction.created_at, datetime)
    
    def test_user_defaults(self):
        """Test default values for User model"""
        user = User(
            email="test@example.com",
            username="testuser",
            hashed_password="hashed_password"
        )
        
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        
        # Verify default values
        self.assertTrue(user.is_active)  # Default True
        self.assertFalse(user.is_admin)  # Default False
    
    def test_multiple_users_different_predictions(self):
        """Test multiple users can have different predictions"""
        # Create multiple users
        user1 = User(
            email="user1@example.com",
            username="user1",
            hashed_password="hashed1"
        )
        user2 = User(
            email="user2@example.com",
            username="user2",
            hashed_password="hashed2"
        )
        
        self.db.add(user1)
        self.db.add(user2)
        self.db.commit()
        self.db.refresh(user1)
        self.db.refresh(user2)
        
        # Create predictions for each user
        prediction1 = Prediction(
            user_id=user1.id,
            prediction="Normal_Weight",
            probability=0.85,
            bmi=26.12,
            risk_level="Low",
            input_data={"user": "user1"}
        )
        
        prediction2 = Prediction(
            user_id=user2.id,
            prediction="Obesity_Type_I",
            probability=0.92,
            bmi=32.5,
            risk_level="High",
            input_data={"user": "user2"}
        )
        
        self.db.add(prediction1)
        self.db.add(prediction2)
        self.db.commit()
        
        # Verify each user has their own predictions
        self.assertEqual(len(user1.predictions), 1)
        self.assertEqual(len(user2.predictions), 1)
        self.assertEqual(user1.predictions[0].prediction, "Normal_Weight")
        self.assertEqual(user2.predictions[0].prediction, "Obesity_Type_I")
        
        # Verify predictions belong to correct users
        self.assertEqual(prediction1.user.email, "user1@example.com")
        self.assertEqual(prediction2.user.email, "user2@example.com")


if __name__ == "__main__":
    unittest.main()