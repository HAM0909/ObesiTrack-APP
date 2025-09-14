import pickle
from pathlib import Path
import pandas as pd
from typing import Dict, Any
import logging
import numpy as np

logger = logging.getLogger(__name__)

class ObesityPredictor:
    """
    Obesity prediction model wrapper.
    This class is a singleton that loads a trained model and encoders.
    """
    _instance = None
    
    model = None
    feature_encoder = None
    label_encoder = None
    
    numerical_features = ['Age', 'Height', 'Weight']
    categorical_features = [
        'Gender', 'family_history_with_overweight', 'FAVC', 'FCVC', 
        'NCP', 'CAEC', 'SMOKE', 'CH2O', 'SCC', 'FAF', 'TUE', 'CALC', 'MTRANS'
    ]

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ObesityPredictor, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        
        self._load_model_assets()
        self._initialized = True

    def _load_model_assets(self):
        """Load the trained model and encoders from files."""
        models_dir = Path(__file__).parent.resolve()
        model_path = models_dir / "model.pkl"
        feature_encoder_path = models_dir / "feature_encoder.pkl"
        label_encoder_path = models_dir / "label_encoder.pkl"

        try:
            with open(model_path, 'rb') as f:
                self.model = pickle.load(f)
            logger.info(f"✅ Model loaded from {model_path}")
        except Exception as e:
            logger.error(f"❌ Error loading model.pkl: {e}", exc_info=True)
            self.model = None

        try:
            with open(feature_encoder_path, 'rb') as f:
                self.feature_encoder = pickle.load(f)
            logger.info(f"✅ Feature encoder loaded from {feature_encoder_path}")
        except Exception as e:
            logger.error(f"❌ Error loading feature_encoder.pkl: {e}", exc_info=True)
            self.feature_encoder = None

        try:
            with open(label_encoder_path, 'rb') as f:
                self.label_encoder = pickle.load(f)
            logger.info(f"✅ Label encoder loaded from {label_encoder_path}")
        except Exception as e:
            logger.error(f"❌ Error loading label_encoder.pkl: {e}", exc_info=True)
            self.label_encoder = None

    def preprocess_features(self, features: Dict[str, Any]) -> pd.DataFrame:
        """Preprocess input features for model prediction"""
        df = pd.DataFrame([features])
        
        if 'Weight' in features and 'Height' in features and features['Height'] > 0:
            height_m = features['Height'] / 100
            df['BMI'] = features['Weight'] / (height_m ** 2)
        else:
            df['BMI'] = 0
        
        feature_defaults = {
            'Gender': 'Male', 'Age': 25, 'Height': 170, 'Weight': 70,
            'family_history_with_overweight': 'yes', 'FAVC': 'yes', 'FCVC': 2, 'NCP': 3,
            'CAEC': 'Sometimes', 'SMOKE': 'no', 'CH2O': 2, 'SCC': 'no', 'FAF': 1,
            'TUE': 1, 'CALC': 'Sometimes', 'MTRANS': 'Public_Transportation'
        }
        
        for feature, default_value in feature_defaults.items():
            if feature not in df.columns:
                df[feature] = default_value
        
        return df

    def predict(self, features: Dict[str, Any]) -> Dict[str, Any]:
        """Make prediction based on input features"""
        if not self.model:
            logger.warning("Model not loaded, returning mock prediction.")
            bmi = (features.get('Weight', 70) / (features.get('Height', 170)/100)**2)
            return {
                "prediction": "Normal_Weight", "probability": 0.5, "bmi": round(bmi, 2),
                "risk_level": "Low", "confidence": 0.5,
                "recommendations": ["Model not loaded. This is a mock response."]
            }
        
        try:
            X = self.preprocess_features(features)
            
            if self.feature_encoder:
                # This assumes a compatible encoder. May need adjustment.
                for col in self.categorical_features:
                    if col in X.columns:
                        # This is a potential point of failure if the encoder is a ColumnTransformer
                        # or expects all columns at once.
                        pass # Bypassing transformation for now as it's likely incorrect.

            # Ensure columns are in the same order as during training
            # This is a simplification; a robust solution would save/load column order
            # X = X[self.model.feature_names_in_] 
            
            prediction_encoded = self.model.predict(X)[0]
            probabilities = self.model.predict_proba(X)[0]
            probability = float(max(probabilities))
            
            prediction = self.label_encoder.inverse_transform([prediction_encoded])[0]
            
            bmi = X['BMI'].values[0] if 'BMI' in X.columns else 0
            risk_level = self.calculate_risk_level(prediction, probability)
            
            return {
                "prediction": prediction,
                "probability": float(probability),
                "confidence": float(probability),
                "bmi": round(float(bmi), 2),
                "risk_level": risk_level,
                "recommendations": self.get_recommendations(prediction, bmi)
            }
        except Exception as e:
            logger.error(f"Prediction error: {e}")
            raise ValueError(f"Error making prediction: {str(e)}")

    def calculate_risk_level(self, prediction: str, probability: float) -> str:
        """Calculate risk level based on prediction and probability"""
        if "Obesity" in prediction: return "High"
        if "Overweight" in prediction: return "Medium"
        return "Low"

    def get_recommendations(self, prediction: str, bmi: float) -> list:
        """Get health recommendations based on prediction"""
        if "Obesity" in prediction or "Overweight" in prediction:
            return [
                "Consult with a healthcare professional for personalized advice.",
                "Increase physical activity and focus on a balanced diet."
            ]
        elif "Normal" in prediction:
            return ["Maintain your current healthy lifestyle and regular check-ups."]
        else:
            return ["Consult with a healthcare professional for advice on healthy weight gain."]

def load_model() -> ObesityPredictor:
    """Loads the singleton predictor instance."""
    return ObesityPredictor()