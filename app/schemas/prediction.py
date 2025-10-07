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
   "mtrans": "Public_Transportation"
}
})
    
    gender: str = Field(..., description="Male/Female")
    age: int = Field(..., ge=1, le=120)
    height: float = Field(..., gt=0, description="cm")
    weight: float = Field(..., gt=0, description="kg")
    family_history_with_overweight: str = Field("yes")
    favc: str = Field("yes")
    fcvc: float = Field(2, ge=1, le=3)
    ncp: float = Field(3, ge=1, le=4)
    caec: str = Field("Sometimes")
    smoke: str = Field("no")
    ch2o: float = Field(2, ge=1, le=3)
    scc: str = Field("no")
    faf: float = Field(1, ge=0, le=3)
    tue: float = Field(1, ge=0, le=2)
    calc: str = Field("Sometimes")
    mtrans: str = Field("Public_Transportation")

    @model_validator(mode="before")
    @classmethod
    def normalize_fields(cls, data: dict) -> dict:
        if not isinstance(data, dict):
            return data
            
        # Create a mapping of field names
        field_mapping = {
            'GENDER': 'gender',
            'AGE': 'age',
            'HEIGHT': 'height',
            'WEIGHT': 'weight',
            'FAMILY_HISTORY_WITH_OVERWEIGHT': 'family_history_with_overweight',
            'FAVC': 'favc',
            'FCVC': 'fcvc',
            'NCP': 'ncp',
            'CAEC': 'caec',
            'SMOKE': 'smoke',
            'CH2O': 'ch2o',
            'SCC': 'scc',
            'FAF': 'faf',
            'TUE': 'tue',
            'CALC': 'calc',
            'MTRANS': 'mtrans'
        }
        
        # Normalize all field names to lowercase
        normalized_data = {}
        for key, value in data.items():
            normalized_key = field_mapping.get(key.upper(), key.lower())
            normalized_data[normalized_key] = value
            
        return normalized_data if normalized_data else data

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
    confidence: Optional[float] = None
    bmi: float
    risk_level: str
    input_data: Dict[str, Any]
    created_at: datetime