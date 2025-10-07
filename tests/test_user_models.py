import unittest
from unittest.mock import Mock, patch
from datetime import datetime
from pathlib import Path
import sys
from pydantic import ValidationError
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Ensure 'ObesiTrack' project root is on sys.path so 'app' package is importable
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.models.user import User
from app.models.base import Base
from app.schemas.user import (
    UserCreate, 
    UserUpdate, 
    UserResponse, 
    UserWithPredictions
)


class TestUserModel(unittest.TestCase):
    """Test User SQLAlchemy model"""
    
    def setUp(self):
        """Set up in-memory SQLite database for testing"""
        self.engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(self.engine)
        self.SessionLocal = sessionmaker(bind=self.engine)
        self.db = self.SessionLocal()
    
    def tearDown(self):
        """Clean up database session"""
        self.db.close()
    
    def test_user_model_field_validation(self):
        """Test User model creates correctly with all fields"""
        user = User(
            email="test@example.com",
            username="testuser",
            hashed_password="hashed_password_123",
            is_active=True,
            is_admin=False
        )
        
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        
        # Verify all fields are set correctly
        self.assertEqual(user.email, "test@example.com")
        self.assertEqual(user.username, "testuser")
        self.assertEqual(user.hashed_password, "hashed_password_123")
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_admin)
        self.assertIsNotNone(user.id)
        self.assertIsNotNone(user.created_at)
    
    def test_user_model_defaults(self):
        """Test User model default values"""
        user = User(
            email="test@example.com",
            username="testuser",
            hashed_password="hashed_password_123"
        )
        
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        
        # Verify default values
        self.assertTrue(user.is_active)  # Default should be True
        self.assertFalse(user.is_admin)  # Default should be False
        self.assertIsNotNone(user.created_at)
        self.assertIsNone(user.updated_at)  # Should be None initially
    
    def test_user_model_unique_constraints(self):
        """Test unique constraints on email and username"""
        # Create first user
        user1 = User(
            email="test@example.com",
            username="testuser",
            hashed_password="hashed1"
        )
        self.db.add(user1)
        self.db.commit()
        
        # Try to create second user with same email
        user2 = User(
            email="test@example.com",
            username="differentuser",
            hashed_password="hashed2"
        )
        self.db.add(user2)
        
        # Should raise integrity error
        with self.assertRaises(Exception):  # SQLAlchemy will raise IntegrityError
            self.db.commit()
            
        # Rollback and try with same username
        self.db.rollback()
        
        user3 = User(
            email="different@example.com",
            username="testuser",
            hashed_password="hashed3"
        )
        self.db.add(user3)
        
        # Should also raise integrity error
        with self.assertRaises(Exception):
            self.db.commit()
    
    def test_user_model_relationship(self):
        """Test relationship with predictions"""
        user = User(
            email="test@example.com",
            username="testuser",
            hashed_password="hashed_password_123"
        )
        
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        
        # Verify predictions relationship exists (should be empty list)
        self.assertEqual(len(user.predictions), 0)
        self.assertIsInstance(user.predictions, list)


class TestUserSchemas(unittest.TestCase):
    """Test Pydantic schemas for User"""
    
    def test_user_create_schema_validation(self):
        """Test UserCreate schema validates correctly"""
        user_data = {
            "email": "test@example.com",
            "username": "testuser",
            "password": "password123"
        }
        
        user = UserCreate(**user_data)
        
        self.assertEqual(user.email, "test@example.com")
        self.assertEqual(user.username, "testuser")
        self.assertEqual(user.password, "password123")
    
    def test_user_create_email_cleaning(self):
        """Test UserCreate schema cleans email correctly"""
        user_data = {
            "email": "  test@example.com  ",
            "username": "testuser",
            "password": "password123"
        }
        
        user = UserCreate(**user_data)
        
        # Email should be cleaned (spaces removed)
        self.assertEqual(user.email, "test@example.com")
    
    def test_user_create_invalid_email(self):
        """Test UserCreate schema validation with invalid email"""
        user_data = {
            "email": "invalid-email",
            "username": "testuser",
            "password": "password123"
        }
        
        with self.assertRaises(ValidationError) as context:
            UserCreate(**user_data)
        
        # Verify validation error mentions email
        error_details = str(context.exception)
        self.assertIn("email", error_details.lower())
    
    def test_user_create_missing_fields(self):
        """Test UserCreate schema validation with missing required fields"""
        # Missing email
        with self.assertRaises(ValidationError):
            UserCreate(username="testuser", password="password123")
        
        # Missing username
        with self.assertRaises(ValidationError):
            UserCreate(email="test@example.com", password="password123")
        
        # Missing password
        with self.assertRaises(ValidationError):
            UserCreate(email="test@example.com", username="testuser")
    
    def test_user_update_schema_validation(self):
        """Test UserUpdate schema validates correctly"""
        # Test with all fields
        update_data = {
            "email": "newemail@example.com",
            "username": "newusername",
            "password": "newpassword123"
        }
        
        user_update = UserUpdate(**update_data)
        
        self.assertEqual(user_update.email, "newemail@example.com")
        self.assertEqual(user_update.username, "newusername")
        self.assertEqual(user_update.password, "newpassword123")
    
    def test_user_update_partial_fields(self):
        """Test UserUpdate schema with partial field updates"""
        # Test with only email
        user_update = UserUpdate(email="newemail@example.com")
        self.assertEqual(user_update.email, "newemail@example.com")
        self.assertIsNone(user_update.username)
        self.assertIsNone(user_update.password)
        
        # Test with only username
        user_update = UserUpdate(username="newusername")
        self.assertIsNone(user_update.email)
        self.assertEqual(user_update.username, "newusername")
        self.assertIsNone(user_update.password)
    
    def test_user_response_schema_validation(self):
        """Test UserResponse schema validation"""
        response_data = {
            "id": 1,
            "email": "test@example.com",
            "username": "testuser",
            "created_at": datetime.now(),
            "updated_at": None,
            "is_active": True,
            "is_admin": False
        }
        
        user_response = UserResponse(**response_data)
        
        self.assertEqual(user_response.id, 1)
        self.assertEqual(user_response.email, "test@example.com")
        self.assertEqual(user_response.username, "testuser")
        self.assertTrue(user_response.is_active)
        self.assertFalse(user_response.is_admin)
        self.assertIsNotNone(user_response.created_at)
    
    def test_user_response_from_orm(self):
        """Test UserResponse schema can be created from ORM model"""
        # Create mock user model
        user_model = Mock()
        user_model.id = 1
        user_model.email = "test@example.com"
        user_model.username = "testuser"
        user_model.created_at = datetime.now()
        user_model.updated_at = None
        user_model.is_active = True
        user_model.is_admin = False
        
        # UserResponse should work with from_attributes=True
        user_response = UserResponse.model_validate(user_model)
        
        self.assertEqual(user_response.id, 1)
        self.assertEqual(user_response.email, "test@example.com")
        self.assertEqual(user_response.username, "testuser")
    
    def test_user_with_predictions_schema(self):
        """Test UserWithPredictions schema"""
        user_data = {
            "id": 1,
            "email": "test@example.com",
            "username": "testuser",
            "created_at": datetime.now(),
            "updated_at": None,
            "is_active": True,
            "is_admin": False,
            "predictions": []
        }
        
        user_with_predictions = UserWithPredictions(**user_data)
        
        self.assertEqual(user_with_predictions.id, 1)
        self.assertEqual(user_with_predictions.email, "test@example.com")
        self.assertIsInstance(user_with_predictions.predictions, list)
        self.assertEqual(len(user_with_predictions.predictions), 0)
    
    def test_user_response_default_values(self):
        """Test UserResponse schema default values"""
        minimal_data = {
            "id": 1,
            "email": "test@example.com",
            "username": "testuser",
            "created_at": datetime.now()
        }
        
        user_response = UserResponse(**minimal_data)
        
        # Test default values
        self.assertTrue(user_response.is_active)  # Default True
        self.assertFalse(user_response.is_admin)  # Default False
        self.assertIsNone(user_response.updated_at)  # Default None


if __name__ == "__main__":
    unittest.main()