from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.base import Base  # Corrected import
from os import getenv

<<<<<<< HEAD
DATABASE_URL = "sqlite:////tmp/obesittrack.db"
engine = create_engine(DATABASE_URL, pool_pre_ping=True, connect_args={"check_same_thread": False})
=======
DATABASE_URL = getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL, pool_pre_ping=True)
>>>>>>> 34b8ed696e9e4848bf9e161c4623c97fb5af4e57
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
def init_db():
 Base.metadata.create_all(bind=engine)
def get_db():
  db = SessionLocal()
  try:
     yield db
  finally:
   db.close()