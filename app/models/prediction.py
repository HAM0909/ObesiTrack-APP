from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.models.base import Base

class Prediction(Base):
    __tablename__ = "predictions"
    
    id = Column(Integer, primary_key=True, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)

    # inputs (names in snake_case to match DB)
    gender = Column(Integer, nullable=False)
    age = Column(Integer, nullable=False)
    height = Column(Float, nullable=False)
    weight = Column(Float, nullable=False)
    family_history_with_overweight = Column(String, nullable=False)
    fcvc = Column(Float, nullable=False)
    ncp = Column(Float, nullable=False)
    caec = Column(String, nullable=False)
    faf = Column(Float, nullable=False)
    tue = Column(Float, nullable=False)
    calc = Column(String, nullable=False)
    matrans = Column(String, nullable=False)
    favc = Column(String, nullable=False)
    smoke = Column(String, nullable=False)
    ch2o = Column(Float, nullable=False)
    scc = Column(String, nullable=False)

    # outputs
    prediction = Column(String, nullable=False)
    probability = Column(Float, nullable=False)
    confidence = Column(Float, nullable=False)
    bmi = Column(Float, nullable=False)
    risk_level = Column(String, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="predictions")