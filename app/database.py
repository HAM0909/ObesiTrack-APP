from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.base import Base
from app.config import settings
import os

# Determine if we're running in Docker
IN_DOCKER = os.getenv('IN_DOCKER', '').lower() in {'1', 'true', 'yes'}

# Use the appropriate host
# Prefer DATABASE_URL as-is; if host.docker.internal appears, normalize based on IN_DOCKER
host = "host.docker.internal" if IN_DOCKER else "localhost"
DATABASE_URL = settings.database_url.replace("host.docker.internal", host)

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# This is synchronous; define as sync to avoid blocking the event loop when awaited implicitly
async def init_db():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()