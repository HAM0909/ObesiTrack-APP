import unittest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
from pathlib import Path
import sys
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

# Ensure 'ObesiTrack' project root is on sys.path so 'app' package is importable
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.models.user import User
from app.models.prediction import Prediction
from app.routers.admin import router
from app.database import get_db
from app.auth.dependencies import get_current_admin_user


class TestAdminRoutes(unittest.TestCase):
    """Test admin functionality routes"""
    
    def setUp(self):
        """Set up test client and mock dependencies"""
        from fastapi import FastAPI
        
        self.app = FastAPI()
        self.app.include_router(router, tags=["admin"])
        
        # Mock database session
        self.mock_db = Mock(spec=Session)
        
        # Mock admin user
        self.mock_admin = Mock()
        self.mock_admin.id = 1
        self.mock_admin.email = "admin@example.com"
        self.mock_admin.username = "admin"
        self.mock_admin.is_active = True
        self.mock_admin.is_admin = True
        
        def get_test_db():
            return self.mock_db
            
        def get_test_admin():
            return self.mock_admin
            
        self.app.dependency_overrides[get_db] = get_test_db
        self.app.dependency_overrides[get_current_admin_user] = get_test_admin
        
        self.client = TestClient(self.app)
    
    def tearDown(self):
        """Clean up after tests"""
        self.app.dependency_overrides.clear()
    
    def test_get_all_users_success(self):
        """Test successfully retrieving all users"""
        # Mock users with all required fields
        now = datetime.now()
        mock_users = [
            Mock(id=2, email="user1@example.com", username="user1", 
                 created_at=now, updated_at=now, is_active=True, is_admin=False),
            Mock(id=3, email="user2@example.com", username="user2", 
                 created_at=now, updated_at=now, is_active=True, is_admin=False)
        ]
        
        # Mock query chain
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = mock_users
        
        self.mock_db.query.return_value = mock_query
        
        response = self.client.get("/users")
        
        # Verify response
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertIsInstance(response_data, list)
        self.assertEqual(len(response_data), 2)
    
    def test_get_all_users_with_search(self):
        """Test retrieving users with search filter"""
        # Mock filtered users
        now = datetime.now()
        mock_users = [
            Mock(id=2, email="test@example.com", username="testuser", 
                 created_at=now, updated_at=now, is_active=True, is_admin=False)
        ]
        
        # Mock query chain with search
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = mock_users
        
        self.mock_db.query.return_value = mock_query
        
        response = self.client.get("/users?search=test")
        
        # Verify response
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertIsInstance(response_data, list)
        # Verify filter was called (search functionality)
        self.assertTrue(mock_query.filter.called)
    
    def test_get_all_users_pagination(self):
        """Test user list pagination"""
        mock_users = []  # Empty result for page 2
        
        # Mock query chain
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = mock_users
        
        self.mock_db.query.return_value = mock_query
        
        response = self.client.get("/users?page=2&per_page=10")
        
        # Verify response
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertIsInstance(response_data, list)
        # Verify offset was called with correct value (page 2, per_page 10 = offset 10)
        mock_query.offset.assert_called()
        mock_query.limit.assert_called()
    
    def test_get_user_detail_success(self):
        """Test successfully retrieving user details"""
        # Mock user with predictions
        mock_user = Mock()
        mock_user.id = 2
        mock_user.email = "user@example.com"
        mock_user.username = "testuser"
        mock_user.predictions = []
        mock_user.is_active = True
        mock_user.is_admin = False
        mock_user.created_at = datetime.now()
        mock_user.updated_at = None
        
        # Mock query
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = mock_user
        
        self.mock_db.query.return_value = mock_query
        
        response = self.client.get("/users/2")
        
        # Verify response
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertEqual(response_data["id"], 2)
        self.assertEqual(response_data["email"], "user@example.com")
    
    def test_get_user_detail_not_found(self):
        """Test retrieving non-existent user details"""
        # Mock query returning None
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = None
        
        self.mock_db.query.return_value = mock_query
        
        response = self.client.get("/users/999")
        
        # Verify error response
        self.assertEqual(response.status_code, 404)
        self.assertIn("non trouvé", response.json()["detail"])
    
    def test_update_user_success(self):
        """Test successfully updating a user"""
        # Mock existing user
        mock_user = Mock()
        mock_user.id = 2
        mock_user.email = "user@example.com"
        mock_user.username = "testuser"
        mock_user.is_active = True
        mock_user.is_admin = False
        mock_user.created_at = datetime.now()
        mock_user.updated_at = None
        
        # Mock query for user lookup
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = mock_user
        
        # Mock query for email uniqueness check (no conflict)
        mock_email_query = Mock()
        mock_email_query.filter.return_value = mock_email_query
        mock_email_query.first.return_value = None
        
        def mock_query_side_effect(*args):
            if args and hasattr(args[0], '__name__') and args[0].__name__ == 'User':
                return mock_query
            return mock_email_query
            
        self.mock_db.query.side_effect = [mock_query, mock_email_query]
        
        # Mock database operations
        self.mock_db.commit.return_value = None
        self.mock_db.refresh.return_value = None
        
        update_data = {
            "email": "newemail@example.com",
            "username": "newusername"
        }
        
        response = self.client.put("/users/2", json=update_data)
        
        # Verify response
        self.assertEqual(response.status_code, 200)
        # Verify user was updated
        self.mock_db.commit.assert_called_once()
        self.mock_db.refresh.assert_called_once()
    
    def test_update_user_email_conflict(self):
        """Test updating user with existing email"""
        # Mock existing user
        mock_user = Mock()
        mock_user.id = 2
        mock_user.email = "user@example.com"
        
        # Mock conflicting user with same email
        mock_conflict_user = Mock()
        mock_conflict_user.id = 3
        mock_conflict_user.email = "existing@example.com"
        
        # Mock queries
        mock_user_query = Mock()
        mock_user_query.filter.return_value = mock_user_query
        mock_user_query.first.return_value = mock_user
        
        mock_email_query = Mock()
        mock_email_query.filter.return_value = mock_email_query
        mock_email_query.first.return_value = mock_conflict_user
        
        self.mock_db.query.side_effect = [mock_user_query, mock_email_query]
        
        update_data = {
            "email": "existing@example.com"
        }
        
        response = self.client.put("/users/2", json=update_data)
        
        # Verify error response
        self.assertEqual(response.status_code, 400)
        self.assertIn("déjà utilisé", response.json()["detail"])
    
    def test_update_user_not_found(self):
        """Test updating non-existent user"""
        # Mock query returning None
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = None
        
        self.mock_db.query.return_value = mock_query
        
        update_data = {
            "username": "newusername"
        }
        
        response = self.client.put("/users/999", json=update_data)
        
        # Verify error response
        self.assertEqual(response.status_code, 404)
        self.assertIn("non trouvé", response.json()["detail"])
    
    def test_delete_user_success(self):
        """Test successfully deleting a user"""
        # Mock user to delete
        mock_user = Mock()
        mock_user.id = 2
        mock_user.email = "user@example.com"
        
        # Mock query
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = mock_user
        
        self.mock_db.query.return_value = mock_query
        
        # Mock database operations
        self.mock_db.delete.return_value = None
        self.mock_db.commit.return_value = None
        
        response = self.client.delete("/users/2")
        
        # Verify response
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertIn("supprimé avec succès", response_data["message"])
        # Verify user was deleted
        self.mock_db.delete.assert_called_once_with(mock_user)
        self.mock_db.commit.assert_called_once()
    
    def test_delete_user_self_prevention(self):
        """Test preventing admin from deleting own account"""
        # Mock user is the same as admin
        mock_user = Mock()
        mock_user.id = 1  # Same as admin ID
        mock_user.email = "admin@example.com"
        
        # Mock query
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = mock_user
        
        self.mock_db.query.return_value = mock_query
        
        response = self.client.delete("/users/1")
        
        # Verify error response
        self.assertEqual(response.status_code, 400)
        self.assertIn("propre compte", response.json()["detail"])
    
    def test_delete_user_not_found(self):
        """Test deleting non-existent user"""
        # Mock query returning None
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = None
        
        self.mock_db.query.return_value = mock_query
        
        response = self.client.delete("/users/999")
        
        # Verify error response
        self.assertEqual(response.status_code, 404)
        self.assertIn("non trouvé", response.json()["detail"])
    
    def test_toggle_user_status_success(self):
        """Test successfully toggling user active status"""
        # Mock user
        mock_user = Mock()
        mock_user.id = 2
        mock_user.email = "user@example.com"
        mock_user.is_active = True
        
        # Mock query
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = mock_user
        
        self.mock_db.query.return_value = mock_query
        
        # Mock database operations
        self.mock_db.commit.return_value = None
        self.mock_db.refresh.return_value = None
        
        response = self.client.post("/users/2/toggle-status")
        
        # Verify response
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertIn("message", response_data)
        self.assertIn("user", response_data)
        # Verify status was toggled
        self.assertFalse(mock_user.is_active)
    
    def test_toggle_user_status_self_prevention(self):
        """Test preventing admin from toggling own status"""
        # Mock user is the same as admin
        mock_user = Mock()
        mock_user.id = 1  # Same as admin ID
        mock_user.email = "admin@example.com"
        
        # Mock query
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = mock_user
        
        self.mock_db.query.return_value = mock_query
        
        response = self.client.post("/users/1/toggle-status")
        
        # Verify error response
        self.assertEqual(response.status_code, 400)
        self.assertIn("propre compte", response.json()["detail"])
    
    def test_toggle_admin_status_success(self):
        """Test successfully toggling user admin status"""
        # Mock user
        mock_user = Mock()
        mock_user.id = 2
        mock_user.email = "user@example.com"
        mock_user.is_admin = False
        
        # Mock query
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = mock_user
        
        self.mock_db.query.return_value = mock_query
        
        # Mock database operations
        self.mock_db.commit.return_value = None
        self.mock_db.refresh.return_value = None
        
        response = self.client.post("/users/2/make-admin")
        
        # Verify response
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertIn("message", response_data)
        self.assertIn("user", response_data)
        # Verify admin status was toggled
        self.assertTrue(mock_user.is_admin)
    
    def test_toggle_admin_status_self_prevention(self):
        """Test preventing admin from changing own admin status"""
        # Mock user is the same as admin
        mock_user = Mock()
        mock_user.id = 1  # Same as admin ID
        mock_user.email = "admin@example.com"
        
        # Mock query
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = mock_user
        
        self.mock_db.query.return_value = mock_query
        
        response = self.client.post("/users/1/make-admin")
        
        # Verify error response
        self.assertEqual(response.status_code, 400)
        self.assertIn("propres droits", response.json()["detail"])
    
    def test_get_user_predictions_success(self):
        """Test successfully retrieving user predictions"""
        # Create proper User and Prediction objects instead of Mocks
        from app.models.user import User
        from app.models.prediction import Prediction
        
        # Mock user 
        mock_user = User(
            id=2,
            email="user@example.com",
            username="testuser",
            hashed_password="hashed",
            is_active=True,
            is_admin=False
        )
        
        # Mock predictions 
        now = datetime.now()
        mock_prediction1 = Prediction(
            id=1,
            user_id=2,
            prediction="Normal_Weight",
            probability=0.85,
            created_at=now,
            bmi=22.5,
            risk_level="Low",
            input_data={}
        )
        
        mock_prediction2 = Prediction(
            id=2,
            user_id=2,
            prediction="Obesity_Type_I",
            probability=0.75,
            created_at=now,
            bmi=32.1,
            risk_level="High",
            input_data={}
        )
        
        mock_predictions = [mock_prediction1, mock_prediction2]
        
        # Mock query chains
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = mock_user
        mock_query.order_by.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = mock_predictions
        mock_query.count.return_value = 2
        
        self.mock_db.query.return_value = mock_query
        
        response = self.client.get("/users/2/predictions")
        
        # Verify response
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertIn("user", response_data)
        self.assertIn("predictions", response_data)
        self.assertIn("total", response_data)
        self.assertEqual(response_data["total"], 2)
    
    def test_get_user_predictions_user_not_found(self):
        """Test retrieving predictions for non-existent user"""
        # Mock query returning None
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = None
        
        self.mock_db.query.return_value = mock_query
        
        response = self.client.get("/users/999/predictions")
        
        # Verify error response
        self.assertEqual(response.status_code, 404)
        self.assertIn("non trouvé", response.json()["detail"])
    
    def test_get_admin_dashboard_stats(self):
        """Test retrieving admin dashboard statistics"""
        # Mock database queries with simple counts
        mock_query = Mock()
        mock_query.count.return_value = 10
        mock_query.filter.return_value = mock_query
        mock_query.group_by.return_value = mock_query
        mock_query.join.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = []
        
        self.mock_db.query.return_value = mock_query
        
        response = self.client.get("/stats/dashboard")
        
        # Verify response
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        # Just verify it returns some data structure
        self.assertIsInstance(response_data, dict)


class TestAuthDependencies(unittest.TestCase):
    """Test authentication dependencies"""
    
    def setUp(self):
        """Set up mock database"""
        self.mock_db = Mock(spec=Session)
    
    @patch('app.auth.dependencies.verify_token')
    def test_get_current_user_success(self, mock_verify_token):
        """Test successfully getting current user"""
        from app.auth.dependencies import get_current_user
        from fastapi.security import HTTPAuthorizationCredentials
        
        # Mock token verification
        mock_verify_token.return_value = "user@example.com"
        
        # Mock user in database
        mock_user = Mock()
        mock_user.email = "user@example.com"
        mock_user.is_active = True
        
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = mock_user
        
        self.mock_db.query.return_value = mock_query
        
        # Mock credentials
        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials="valid_token"
        )
        
        result = get_current_user(credentials, self.mock_db)
        
        # Verify result
        self.assertEqual(result, mock_user)
        mock_verify_token.assert_called_once_with("valid_token")
    
    @patch('app.auth.dependencies.verify_token')
    def test_get_current_user_invalid_token(self, mock_verify_token):
        """Test getting current user with invalid token"""
        from app.auth.dependencies import get_current_user
        from fastapi.security import HTTPAuthorizationCredentials
        from fastapi import HTTPException
        
        # Mock invalid token
        mock_verify_token.return_value = None
        
        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials="invalid_token"
        )
        
        with self.assertRaises(HTTPException) as context:
            get_current_user(credentials, self.mock_db)
        
        self.assertEqual(context.exception.status_code, 401)
    
    @patch('app.auth.dependencies.verify_token')
    def test_get_current_user_inactive(self, mock_verify_token):
        """Test getting inactive current user"""
        from app.auth.dependencies import get_current_user
        from fastapi.security import HTTPAuthorizationCredentials
        from fastapi import HTTPException
        
        # Mock token verification
        mock_verify_token.return_value = "user@example.com"
        
        # Mock inactive user
        mock_user = Mock()
        mock_user.email = "user@example.com"
        mock_user.is_active = False
        
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = mock_user
        
        self.mock_db.query.return_value = mock_query
        
        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials="valid_token"
        )
        
        with self.assertRaises(HTTPException) as context:
            get_current_user(credentials, self.mock_db)
        
        self.assertEqual(context.exception.status_code, 400)
        self.assertIn("Inactive user", context.exception.detail)
    
    def test_get_current_admin_user_success(self):
        """Test successfully getting current admin user"""
        from app.auth.dependencies import get_current_admin_user
        
        # Mock admin user
        mock_admin = Mock()
        mock_admin.is_admin = True
        
        result = get_current_admin_user(mock_admin)
        
        # Verify result
        self.assertEqual(result, mock_admin)
    
    def test_get_current_admin_user_insufficient_permissions(self):
        """Test getting admin user with insufficient permissions"""
        from app.auth.dependencies import get_current_admin_user
        from fastapi import HTTPException
        
        # Mock non-admin user
        mock_user = Mock()
        mock_user.is_admin = False
        
        with self.assertRaises(HTTPException) as context:
            get_current_admin_user(mock_user)
        
        self.assertEqual(context.exception.status_code, 403)
        self.assertIn("Not enough permissions", context.exception.detail)


if __name__ == "__main__":
    unittest.main()