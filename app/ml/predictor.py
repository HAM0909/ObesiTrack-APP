import logging

logger = logging.getLogger(__name__)

class ObesityPredictor:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ObesityPredictor, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self.model = "mock_model"
        self.feature_names = ["Age", "Height", "Weight", "FCVC", "NCP", "CAEC", "FAF", "TUE", "CALC", "MTRANS"]
        self.target_classes = ["Insufficient_Weight", "Normal_Weight", "Overweight_Level_I", "Overweight_Level_II", "Obesity_Type_I", "Obesity_Type_II", "Obesity_Type_III"]
        self.label_encoders = {}
        self.is_loaded = True
        self._initialized = True
        logger.info("✅ Mock ML model initialized.")

    def predict(self, input_data):
        logger.info(f"Predicting with input: {input_data}")
        return {
            "prediction": "Normal_Weight",
            "probability": 0.85,
            "confidence": 0.85,
            "bmi": 24.0,
            "risk_level": "Low",
            "recommendations": ["Keep up the good work!"]
        }

def load_model():
    """Loads the singleton predictor instance."""
    return ObesityPredictor()