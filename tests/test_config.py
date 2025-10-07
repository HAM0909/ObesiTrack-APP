import unittest
from unittest.mock import patch, Mock
from pathlib import Path
import sys
import os

# Ensure 'ObesiTrack' project root is on sys.path so 'app' package is importable
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.config import Settings


class TestConfigSettings(unittest.TestCase):
    """Test application configuration and settings"""
    
    def setUp(self):
        """Set up clean environment for each test"""
        # Store original environment variables
        self.original_env = {}
        env_vars = [
            'DATABASE_URL', 'SECRET_KEY', 'ALGORITHM', 'ACCESS_TOKEN_EXPIRE_MINUTES',
            'APP_NAME', 'APP_VERSION', 'DEBUG', 'POSTGRES_DB', 'POSTGRES_USER', 'POSTGRES_PASSWORD'
        ]
        for var in env_vars:
            self.original_env[var] = os.environ.get(var)
            if var in os.environ:
                del os.environ[var]
    
    def tearDown(self):
        """Restore original environment variables"""
        for var, value in self.original_env.items():
            if value is not None:
                os.environ[var] = value
            elif var in os.environ:
                del os.environ[var]
    
    def test_settings_default_values(self):
        """Test that settings use correct default values"""
        # Set required DATABASE_URL
        os.environ['DATABASE_URL'] = 'postgresql://test:test@localhost/test'
        
        settings = Settings()
        
        # Test values (considering .env file override)
        self.assertEqual(settings.secret_key, "your-super-secret-key-change-this-in-production-very-long-and-random")
        self.assertEqual(settings.algorithm, "HS256")
        self.assertEqual(settings.access_token_expire_minutes, 30)
        self.assertEqual(settings.app_name, "ObesiTrack")
        self.assertEqual(settings.app_version, "1.0.0")
        self.assertFalse(settings.debug)  # .env has DEBUG=False
        self.assertEqual(settings.postgres_db, "obesittrack")
        self.assertEqual(settings.postgres_user, "postgres")
        self.assertEqual(settings.postgres_password, "Chah@15996")
    
    def test_settings_from_environment_variables(self):
        """Test that settings correctly read from environment variables"""
        # Set environment variables
        os.environ['DATABASE_URL'] = 'postgresql://custom:pass@localhost/customdb'
        os.environ['SECRET_KEY'] = 'custom-secret-key'
        os.environ['ALGORITHM'] = 'HS512'
        os.environ['ACCESS_TOKEN_EXPIRE_MINUTES'] = '60'
        os.environ['APP_NAME'] = 'CustomApp'
        os.environ['APP_VERSION'] = '2.0.0'
        os.environ['DEBUG'] = 'false'
        os.environ['POSTGRES_DB'] = 'customdb'
        os.environ['POSTGRES_USER'] = 'customuser'
        os.environ['POSTGRES_PASSWORD'] = 'custompass'
        
        settings = Settings()
        
        # Verify values from environment
        self.assertEqual(settings.database_url, 'postgresql://custom:pass@localhost/customdb')
        self.assertEqual(settings.secret_key, 'custom-secret-key')
        self.assertEqual(settings.algorithm, 'HS512')
        self.assertEqual(settings.access_token_expire_minutes, 60)
        self.assertEqual(settings.app_name, 'CustomApp')
        self.assertEqual(settings.app_version, '2.0.0')
        self.assertFalse(settings.debug)
        self.assertEqual(settings.postgres_db, 'customdb')
        self.assertEqual(settings.postgres_user, 'customuser')
        self.assertEqual(settings.postgres_password, 'custompass')
    
    @patch.dict(os.environ, {}, clear=True)
    def test_settings_database_url_required(self):
        """Test that DATABASE_URL is required"""
        # Create settings without .env file by using a custom class
        class TestSettings(Settings):
            class Config:
                env_file = None  # Don't load .env file
                case_sensitive = False
                extra = "ignore"
        
        # Don't set DATABASE_URL environment variable
        with self.assertRaises(Exception):
            TestSettings()
    
    def test_settings_boolean_conversion(self):
        """Test boolean environment variable conversion"""
        os.environ['DATABASE_URL'] = 'postgresql://test:test@localhost/test'
        
        # Save original DEBUG value
        original_debug = os.environ.get('DEBUG')
        
        # Test various boolean representations
        test_cases = [
            ('true', True),
            ('True', True),
            ('TRUE', True),
            ('1', True),
            ('yes', True),
            ('false', False),
            ('False', False),
            ('FALSE', False),
            ('0', False),
            ('no', False)
        ]
        
        try:
            for env_value, expected in test_cases:
                os.environ['DEBUG'] = env_value
                settings = Settings()
                self.assertEqual(settings.debug, expected, 
                               f"Failed for DEBUG='{env_value}', expected {expected}, got {settings.debug}")
        finally:
            # Restore original DEBUG value
            if original_debug is not None:
                os.environ['DEBUG'] = original_debug
            elif 'DEBUG' in os.environ:
                del os.environ['DEBUG']
    
    def test_settings_integer_conversion(self):
        """Test integer environment variable conversion"""
        os.environ['DATABASE_URL'] = 'postgresql://test:test@localhost/test'
        
        # Test integer conversion
        os.environ['ACCESS_TOKEN_EXPIRE_MINUTES'] = '120'
        settings = Settings()
        self.assertEqual(settings.access_token_expire_minutes, 120)
        self.assertIsInstance(settings.access_token_expire_minutes, int)
        
        # Test invalid integer (should raise error)
        os.environ['ACCESS_TOKEN_EXPIRE_MINUTES'] = 'not-a-number'
        with self.assertRaises(Exception):
            Settings()
    
    def test_settings_string_fields(self):
        """Test string field validation and handling"""
        os.environ['DATABASE_URL'] = 'postgresql://test:test@localhost/test'
        
        # Test empty string handling
        os.environ['SECRET_KEY'] = ''
        settings = Settings()
        self.assertEqual(settings.secret_key, '')
        
        # Test string with spaces
        os.environ['APP_NAME'] = '  Spaced App Name  '
        settings = Settings()
        self.assertEqual(settings.app_name, '  Spaced App Name  ')  # Pydantic doesn't auto-strip
    
    def test_settings_case_sensitivity(self):
        """Test that settings are case insensitive"""
        os.environ['DATABASE_URL'] = 'postgresql://test:test@localhost/test'
        
        # Test lowercase environment variables
        os.environ['secret_key'] = 'lowercase-secret'
        os.environ['app_name'] = 'lowercase-app'
        
        settings = Settings()
        
        # Should work with case insensitive config
        self.assertEqual(settings.secret_key, 'lowercase-secret')
        self.assertEqual(settings.app_name, 'lowercase-app')
    
    @patch.dict(os.environ, {}, clear=True)
    def test_settings_minimal_configuration(self):
        """Test settings with minimal required configuration"""
        # Set only the required DATABASE_URL
        os.environ['DATABASE_URL'] = 'sqlite:///test.db'
        
        # Create settings without .env file by using a custom class
        class TestSettings(Settings):
            class Config:
                env_file = None  # Don't load .env file
                case_sensitive = False
                extra = "ignore"
        
        settings = TestSettings()
        
        # Verify required field is set
        self.assertEqual(settings.database_url, 'sqlite:///test.db')
        
        # Verify all other fields use defaults
        self.assertEqual(settings.secret_key, "your-super-secret-key-change-this-in-production")
        self.assertEqual(settings.algorithm, "HS256")
        self.assertEqual(settings.access_token_expire_minutes, 30)
        self.assertEqual(settings.app_name, "ObesiTrack")
        self.assertEqual(settings.app_version, "1.0.0")
        self.assertTrue(settings.debug)
    
    def test_settings_security_considerations(self):
        """Test security-related configuration aspects"""
        os.environ['DATABASE_URL'] = 'postgresql://test:test@localhost/test'
        
        # Test that default secret key indicates it should be changed
        settings = Settings()
        self.assertIn("change-this-in-production", settings.secret_key)
        
        # Test production-like secret key
        os.environ['SECRET_KEY'] = 'a' * 32  # 32 character key
        settings = Settings()
        self.assertEqual(len(settings.secret_key), 32)
        self.assertNotIn("change-this", settings.secret_key)
    
    def test_settings_database_url_formats(self):
        """Test various database URL formats"""
        # Test PostgreSQL URL
        os.environ['DATABASE_URL'] = 'postgresql://user:pass@localhost:5432/dbname'
        settings = Settings()
        self.assertEqual(settings.database_url, 'postgresql://user:pass@localhost:5432/dbname')
        
        # Test SQLite URL
        os.environ['DATABASE_URL'] = 'sqlite:///./obesity_tracker.db'
        settings = Settings()
        self.assertEqual(settings.database_url, 'sqlite:///./obesity_tracker.db')
        
        # Test PostgreSQL with SSL
        os.environ['DATABASE_URL'] = 'postgresql://user:pass@localhost/db?sslmode=require'
        settings = Settings()
        self.assertIn('sslmode=require', settings.database_url)
    
    def test_settings_jwt_configuration(self):
        """Test JWT-related configuration"""
        os.environ['DATABASE_URL'] = 'postgresql://test:test@localhost/test'
        
        # Test different algorithms
        algorithms = ['HS256', 'HS384', 'HS512', 'RS256']
        for alg in algorithms:
            os.environ['ALGORITHM'] = alg
            settings = Settings()
            self.assertEqual(settings.algorithm, alg)
        
        # Test various token expiration times
        expiration_times = ['15', '30', '60', '120', '1440']  # minutes
        for exp_time in expiration_times:
            os.environ['ACCESS_TOKEN_EXPIRE_MINUTES'] = exp_time
            settings = Settings()
            self.assertEqual(settings.access_token_expire_minutes, int(exp_time))
    
    def test_settings_postgres_configuration(self):
        """Test PostgreSQL-specific configuration"""
        os.environ['DATABASE_URL'] = 'postgresql://test:test@localhost/test'
        
        # Test individual PostgreSQL settings
        os.environ['POSTGRES_DB'] = 'production_db'
        os.environ['POSTGRES_USER'] = 'prod_user'
        os.environ['POSTGRES_PASSWORD'] = 'secure_password_123'
        
        settings = Settings()
        
        self.assertEqual(settings.postgres_db, 'production_db')
        self.assertEqual(settings.postgres_user, 'prod_user')
        self.assertEqual(settings.postgres_password, 'secure_password_123')
    
    def test_settings_extra_fields_ignored(self):
        """Test that extra environment variables are ignored"""
        os.environ['DATABASE_URL'] = 'postgresql://test:test@localhost/test'
        os.environ['UNKNOWN_SETTING'] = 'should_be_ignored'
        os.environ['RANDOM_VAR'] = 'also_ignored'
        
        # Should not raise an error with extra fields due to extra="ignore"
        settings = Settings()
        
        # Verify settings object doesn't have unknown attributes
        self.assertFalse(hasattr(settings, 'unknown_setting'))
        self.assertFalse(hasattr(settings, 'random_var'))
    
    @patch.dict(os.environ, {}, clear=True)
    def test_settings_validation(self):
        """Test settings field validation"""
        # Create settings without .env file by using a custom class
        class TestSettings(Settings):
            class Config:
                env_file = None  # Don't load .env file
                case_sensitive = False
                extra = "ignore"
        
        # Test that missing required field raises appropriate error
        # (DATABASE_URL is required via Field annotation)
        with self.assertRaises(Exception):
            TestSettings()


if __name__ == "__main__":
    unittest.main()