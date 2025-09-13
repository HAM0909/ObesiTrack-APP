from pydantic import BaseModel, Field, field_validator, model_validator, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime
class PredictionInput(BaseModel):
    model_config = ConfigDict(validate_by_name=True, json_schema_extra={
   "example": {
   "gender": "Male",
   "age": 30,
   "height": 175.0,
   "weight": 80.0,
   "family_history_with_overweight": "yes",
   "favc": "yes",
   "fcvc": 2.0,
   "ncp": 3.0,
   "caec": "Sometimes",
   "smoke": "no",
   "ch2o": 2.0,
   "scc": "no",
   "faf": 1.0,
   "tue": 1.0,
   "calc": "Sometimes",
   "matrans": "Public_Transportation"
}
})
    
gender: str = Field(..., description="Male/Female")
age: int = Field(..., ge=1, le=120)
height: float = Field(..., gt=0, description="cm")
weight: float = Field(..., gt=0, description="kg")

family_history_with_overweight: Optional[str] = Field("yes")
favc: Optional[str] = Field("yes")
fcvc: Optional[float] = Field(2, ge=1, le=3)
ncp: Optional[float] = Field(3, ge=1, le=4)
caec: Optional[str] = Field("Sometimes")

smoke: Optional[str] = Field("no")
ch2o: Optional[float] = Field(2, ge=1, le=3)
scc: Optional[str] = Field("no")
faf: Optional[float] = Field(1, ge=0, le=3)
tue: Optional[float] = Field(1, ge=0, le=2)
calc: Optional[str] = Field("Sometimes")
matrans: Optional[str] = Field("Public_Transportation")

@model_validator(mode="before")
@classmethod
def normalize(cls, data):
    # Accept legacy uppercase keys from old clients
    if not isinstance(data, dict):
        return data
    mapping = {
        "Gender": "gender", "Age": "age", "Height": "height", "Weight": "weight",
        "FAVC": "favc", "FCVC": "fcvc", "NCP": "ncp", "CAEC": "caec",
        "SMOKE": "smoke", "CH2O": "ch2o", "SCC": "scc", "FAF": "faf",
        "TUE": "tue", "CALC": "calc", "MTRANS": "matrans",
    }
    return {mapping.get(k, k): v for k, v in data.items()}

class PredictionResponse(BaseModel):
      model_config = ConfigDict(json_schema_extra={
    "example": {
    "prediction": "Normal_Weight",
    "probability": 0.85,
    "confidence": 0.85,
    "bmi": 26.12,
    "risk_level": "Low",
    "recommendations": ["Maintain healthy lifestyle", "Exercise 3x/week"],
    "timestamp": "2024-01-01T12:00:00"
}
})

prediction: str
probability: float = Field(ge=0, le=1)
confidence: float = Field(ge=0, le=1)
bmi: float
risk_level: str
recommendations: List[str]
timestamp: datetime = Field(default_factory=datetime.now)

class PredictionHistory(BaseModel):
     model_config = ConfigDict(from_attributes=True)
     id: int
     user_id: int
     prediction: str
     probability: float
     bmi: float
     risk_level: str
     input_data: Dict[str, Any]
     created_at: datetime