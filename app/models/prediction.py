from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.models.base import Base

class Prediction(Base):
    __tablename__ = "predictions"
    
    id = Column(Integer, primary_key=True, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)

    # inputs (optional; raw input is stored in JSON field `input_data`)
    gender = Column(Integer, nullable=True)
    age = Column(Integer, nullable=True)
    height = Column(Float, nullable=True)
    weight = Column(Float, nullable=True)
    family_history_with_overweight = Column(String, nullable=True)
    fcvc = Column(Float, nullable=True)
    ncp = Column(Float, nullable=True)
    caec = Column(String, nullable=True)
    faf = Column(Float, nullable=True)
    tue = Column(Float, nullable=True)
    calc = Column(String, nullable=True)
    matrans = Column(String, nullable=True)
    favc = Column(String, nullable=True)
    smoke = Column(String, nullable=True)
    ch2o = Column(Float, nullable=True)
    scc = Column(String, nullable=True)

    # outputs
    prediction = Column(String, nullable=False)
    probability = Column(Float, nullable=False)
    confidence = Column(Float, nullable=True)
    bmi = Column(Float, nullable=False)
    risk_level = Column(String, nullable=False)

    # store raw input payload for auditing
    input_data = Column(JSON, nullable=False, default=dict)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="predictions")
    