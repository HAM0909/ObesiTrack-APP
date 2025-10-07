import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.user import User
from app.config import settings

engine = create_engine(settings.database_url)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def delete_user():
    db = TestingSessionLocal()
    try:
        user = db.query(User).filter(User.email == "test@example.com").first()
        if user:
            db.delete(user)
            db.commit()
            print("User 'test@example.com' deleted successfully.")
        else:
            print("User 'test@example.com' not found.")
    finally:
        db.close()

if __name__ == "__main__":
    delete_user()