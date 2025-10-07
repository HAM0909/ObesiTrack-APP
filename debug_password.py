import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.user import User
from app.auth.jwt_handler import get_password_hash, verify_password
from app.config import settings

# Database setup
# Ensure the DATABASE_URL is loaded from settings
engine = create_engine(settings.database_url)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def debug_password_verification():
    db = TestingSessionLocal()
    try:
        # 1. Get the user from the database
        user = db.query(User).filter(User.email == "test@example.com").first()
        if not user:
            print("User 'test@example.com' not found in the database.")
            return

        stored_hash = user.hashed_password
        print(f"Stored hash from DB: {stored_hash}")

        # 2. The password we are testing
        plain_password = "password"
        print(f"Plain password to test: {plain_password}")

        # 3. Verify the password against the stored hash
        is_valid = verify_password(plain_password, stored_hash)
        print(f"Verification result using app.auth.jwt_handler.verify_password: {is_valid}")

        # 4. Hash the plain password again to see if it's consistent
        # Note: Bcrypt generates a new salt each time, so the new_hash will NOT be the same
        # as the stored_hash. The only way to check is using the verify function.
        new_hash = get_password_hash(plain_password)
        print(f"A newly generated hash for '{plain_password}' for comparison: {new_hash}")
        
        # We can verify the new hash against the same password to prove the functions work
        is_new_hash_valid = verify_password(plain_password, new_hash)
        print(f"Verification of new hash against plain password: {is_new_hash_valid}")


    finally:
        db.close()

if __name__ == "__main__":
    debug_password_verification()