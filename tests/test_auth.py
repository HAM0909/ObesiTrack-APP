import unittest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
from pathlib import Path
import sys
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import json

# Ensure 'ObesiTrack' project root is on sys.path so 'app' package is importable
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.auth.jwt_handler import (
    verify_password, 
    get_password_hash, 
    create_access_token, 
    verify_token
)
from app.models.user import User
from app.schemas.auth import LoginRequest, RegisterResponse
from app.schemas.user import UserCreate
from app.routers.auth import router
from app.database import get_db


class TestJWTHandler(unittest.TestCase):
    """Test JWT authentication functionality"""
    
    def test_password_hashing_and_verification(self):
        """Test password hashing creates valid hashes and verification works"""
        password = "test_password_123"
        
        # Hash password
        hashed = get_password_hash(password)
        
        # Verify it's not the same as the plain password
        self.assertNotEqual(password, hashed)
        self.assertTrue(hashed.startswith("$2b$"))
        
        # Verify password verification works
        self.assertTrue(verify_password(password, hashed))
        self.assertFalse(verify_password("wrong_password", hashed))
        
    def test_invalid_password_verification(self):
        """Test password verification with invalid inputs"""
        hashed = get_password_hash("correct_password")
        
        # Test wrong password
        self.assertFalse(verify_password("wrong_password", hashed))
        
        # Test empty password
        self.assertFalse(verify_password("", hashed))
        
        # Test None password
        with self.assertRaises(TypeError):
            verify_password(None, hashed)
    
    @patch('app.auth.jwt_handler.settings')
    def test_jwt_token_creation_validation(self, mock_settings):
        """Test JWT token creation with valid data"""
        mock_settings.secret_key = "test_secret_key"
        mock_settings.algorithm = "HS256"
        mock_settings.access_token_expire_minutes = 30
        
        data = {"sub": "test@example.com"}
        token = create_access_token(data)
        
        # Verify token is created and is a string
        self.assertIsInstance(token, str)
        self.assertTrue(len(token) > 10)
        
        # Verify token can be verified
        email = verify_token(token)
        self.assertEqual(email, "test@example.com")
    
    @patch('app.auth.jwt_handler.settings')
    def test_jwt_token_with_custom_expiry(self, mock_settings):
        """Test JWT token creation with custom expiration"""
        mock_settings.secret_key = "test_secret_key"
        mock_settings.algorithm = "HS256"
        
        data = {"sub": "test@example.com"}
        custom_expiry = timedelta(minutes=60)
        token = create_access_token(data, expires_delta=custom_expiry)
        
        # Verify token is created
        self.assertIsInstance(token, str)
        
        # Verify token contains correct email
        email = verify_token(token)
        self.assertEqual(email, "test@example.com")
    
    @patch('app.auth.jwt_handler.settings')
    def test_invalid_jwt_token_handling(self, mock_settings):
        """Test handling of invalid JWT tokens"""
        mock_settings.secret_key = "test_secret_key"
        mock_settings.algorithm = "HS256"
        mock_settings.access_token_expire_minutes = 30
        
        # Test invalid token
        invalid_token = "invalid.token.here"
        result = verify_token(invalid_token)
        self.assertIsNone(result)
        
        # Test empty token
        result = verify_token("")
        self.assertIsNone(result)
        
        # Test token with wrong secret
        mock_settings.secret_key = "wrong_secret"
        valid_token = create_access_token({"sub": "test@example.com"})
        mock_settings.secret_key = "different_secret"
        result = verify_token(valid_token)
        self.assertIsNone(result)


class TestAuthRoutes(unittest.TestCase):
    """Test authentication routes"""
    
    def setUp(self):
        """Set up test client and mock database"""
        from fastapi import FastAPI
        from app.database import get_db
        
        self.app = FastAPI()
        self.app.include_router(router)  # Remove prefix since routes already have paths
        
        # Mock database session
        self.mock_db = Mock(spec=Session)
        
        def get_test_db():
            return self.mock_db
            
        self.app.dependency_overrides[get_db] = get_test_db
        self.client = TestClient(self.app)
    
    def tearDown(self):
        """Clean up after tests"""
        self.app.dependency_overrides.clear()
    
    @patch('app.routers.auth.User')
    @patch('app.routers.auth.get_password_hash')
    def test_user_registration_success(self, mock_hash, mock_user_class):
        """Test successful user registration"""
        mock_hash.return_value = "hashed_password"
        
        # Mock database queries to return no existing users
        self.mock_db.query.return_value.filter.return_value.first.return_value = None
        
        # Mock user creation with all required fields
        now = datetime.now()
        mock_user_instance = Mock()
        mock_user_instance.id = 1
        mock_user_instance.email = "test@example.com"
        mock_user_instance.username = "testuser"
        mock_user_instance.hashed_password = "hashed_password"
        mock_user_instance.created_at = now
        mock_user_instance.updated_at = None
        mock_user_instance.is_active = True
        mock_user_instance.is_admin = False
        
        mock_user_class.return_value = mock_user_instance
        
        self.mock_db.add.return_value = None
        self.mock_db.commit.return_value = None
        
        # Set up refresh to populate the user attributes
        def refresh_user(user):
            user.id = 1
            user.created_at = now
            user.updated_at = None
            user.is_active = True
            user.is_admin = False
            
        self.mock_db.refresh.side_effect = refresh_user
        
        registration_data = {
            "email": "test@example.com",
            "username": "testuser",
            "password": "password123"
        }
        
        response = self.client.post("/register", json=registration_data)
        
        # Verify response
        self.assertEqual(response.status_code, 201)
        response_data = response.json()
        self.assertIn("user", response_data)
        self.assertIn("message", response_data)
        self.assertEqual(response_data["message"], "Registration successful")
    
    def test_user_registration_duplicate_email(self):
        """Test user registration with duplicate email"""
        # Mock existing user with same email
        existing_user = User(
            id=1,
            email="test@example.com",
            username="existinguser",
            hashed_password="hashed"
        )
        self.mock_db.query.return_value.filter.return_value.first.return_value = existing_user
        
        registration_data = {
            "email": "test@example.com",
            "username": "newuser",
            "password": "password123"
        }
        
        response = self.client.post("/register", json=registration_data)
        
        # Verify error response
        self.assertEqual(response.status_code, 400)
        self.assertIn("Email already registered", response.json()["detail"])
    
    def test_user_registration_duplicate_username(self):
        """Test user registration with duplicate username"""
        # Mock no user with email, but user with username
        def mock_filter_side_effect(condition):
            mock_result = Mock()
            if "email" in str(condition):
                mock_result.first.return_value = None
            else:  # username filter
                existing_user = User(
                    id=1,
                    email="other@example.com",
                    username="testuser",
                    hashed_password="hashed"
                )
                mock_result.first.return_value = existing_user
            return mock_result
        
        self.mock_db.query.return_value.filter.side_effect = mock_filter_side_effect
        
        registration_data = {
            "email": "test@example.com",
            "username": "testuser",
            "password": "password123"
        }
        
        response = self.client.post("/register", json=registration_data)
        
        # Verify error response
        self.assertEqual(response.status_code, 400)
        self.assertIn("Username already registered", response.json()["detail"])
    
    @patch('app.routers.auth.verify_password')
    @patch('app.routers.auth.create_access_token')
    def test_user_login_success(self, mock_create_token, mock_verify_password):
        """Test successful user login"""
        mock_verify_password.return_value = True
        mock_create_token.return_value = "test_access_token"
        
        # Mock existing user
        mock_user = User(
            id=1,
            email="test@example.com",
            username="testuser",
            hashed_password="hashed_password",
            created_at=datetime.now(),
            updated_at=None,
            is_active=True,
            is_admin=False
        )
        self.mock_db.query.return_value.filter.return_value.first.return_value = mock_user
        
        login_data = {
            "email": "test@example.com",
            "password": "password123"
        }
        
        response = self.client.post("/login", json=login_data)
        
        # Verify response
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertEqual(response_data["access_token"], "test_access_token")
        self.assertEqual(response_data["token_type"], "bearer")
        self.assertIn("user", response_data)
        self.assertEqual(response_data["message"], "Login successful")
    
    def test_user_login_invalid_email(self):
        """Test login with invalid email"""
        # Mock no user found
        self.mock_db.query.return_value.filter.return_value.first.return_value = None
        
        login_data = {
            "email": "nonexistent@example.com",
            "password": "password123"
        }
        
        response = self.client.post("/login", json=login_data)
        
        # Verify error response
        self.assertEqual(response.status_code, 401)
        self.assertIn("Incorrect email or password", response.json()["detail"])
    
    @patch('app.routers.auth.verify_password')
    def test_user_login_invalid_password(self, mock_verify_password):
        """Test login with invalid password"""
        mock_verify_password.return_value = False
        
        # Mock existing user
        mock_user = User(
            id=1,
            email="test@example.com",
            username="testuser",
            hashed_password="hashed_password",
            is_active=True
        )
        self.mock_db.query.return_value.filter.return_value.first.return_value = mock_user
        
        login_data = {
            "email": "test@example.com",
            "password": "wrong_password"
        }
        
        response = self.client.post("/login", json=login_data)
        
        # Verify error response
        self.assertEqual(response.status_code, 401)
        self.assertIn("Incorrect email or password", response.json()["detail"])
    
    def test_user_login_inactive_user(self):
        """Test login with inactive user"""
        # Mock inactive user
        mock_user = User(
            id=1,
            email="test@example.com",
            username="testuser",
            hashed_password="hashed_password",
            is_active=False
        )
        self.mock_db.query.return_value.filter.return_value.first.return_value = mock_user
        
        with patch('app.routers.auth.verify_password', return_value=True):
            login_data = {
                "email": "test@example.com",
                "password": "password123"
            }
            
            response = self.client.post("/login", json=login_data)
            
            # Verify error response
            self.assertEqual(response.status_code, 400)
            self.assertIn("Inactive user", response.json()["detail"])


if __name__ == "__main__":
    unittest.main()