from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.base import Base  # Corrected import
from os import getenv

DATABASE_URL = getenv("DATABASE_URL", "sqlite:///./obesittrack.db")
engine = create_engine(DATABASE_URL, pool_pre_ping=True, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
def init_db():
 Base.metadata.create_all(bind=engine)
def get_db():
  db = SessionLocal()
  try:
     yield db
  finally:
   db.close()