import pickle
import os
from pathlib import Path
import numpy as np
import pandas as pd
from typing import Optional, Dict, Any, Tuple
import logging

logger = logging.getLogger(__name__)

class ObesityPredictor:
    """Obesity prediction model wrapper for Random Forest with encoders"""
    
    def __init__(self, model=None, feature_encoder=None, label_encoder=None):
        self.model = model
        self.feature_encoder = feature_encoder
        self.label_encoder = label_encoder
        
        # Define expected features based on your dataset
        self.numerical_features = ['Age', 'Height', 'Weight']
        self.categorical_features = [
            'Gender', 'family_history_with_overweight', 'FAVC', 'FCVC', 
            'NCP', 'CAEC', 'SMOKE', 'CH2O', 'SCC', 'FAF', 'TUE', 'CALC', 'MTRANS'
        ]
        
    def preprocess_features(self, features: Dict[str, Any]) -> pd.DataFrame:
        """Preprocess input features for model prediction"""
        # Create DataFrame from features
        df = pd.DataFrame([features])
        
        # Calculate BMI if weight and height are provided
        if 'Weight' in features and 'Height' in features:
            # Assuming height is in cm, convert to meters for BMI calculation
            height_m = features['Height'] / 100
            df['BMI'] = features['Weight'] / (height_m ** 2)
        
        # Handle missing features with default values
        feature_defaults = {
            'Gender': 'Male',
            'Age': 25,
            'Height': 170,
            'Weight': 70,
            'family_history_with_overweight': 'yes',
            'FAVC': 'yes',  # Frequent consumption of high caloric food
            'FCVC': 2,  # Frequency of consumption of vegetables
            'NCP': 3,  # Number of main meals
            'CAEC': 'Sometimes',  # Consumption of food between meals
            'SMOKE': 'no',
            'CH2O': 2,  # Consumption of water daily (liters)
            'SCC': 'no',  # Calories consumption monitoring
            'FAF': 1,  # Physical activity frequency (times per week)
            'TUE': 1,  # Time using technology devices (hours)
            'CALC': 'Sometimes',  # Consumption of alcohol
            'MTRANS': 'Public_Transportation'  # Transportation used
        }
        
        for feature, default_value in feature_defaults.items():
            if feature not in df.columns:
                df[feature] = default_value
        
        return df
    
    def predict(self, features: Dict[str, Any]) -> Dict[str, Any]:
        """Make prediction based on input features"""
        
        # If no model is loaded, return mock prediction based on BMI
        if not self.model:
            weight = features.get('Weight', 70)
            height = features.get('Height', 170)
            bmi = weight / ((height / 100) ** 2)
            
            if bmi < 18.5:
                category = "Insufficient_Weight"
                risk = 0.1
            elif bmi < 25:
                category = "Normal_Weight"
                risk = 0.2
            elif bmi < 30:
                category = "Overweight_Level_I"
                risk = 0.5
            elif bmi < 35:
                category = "Overweight_Level_II"
                risk = 0.65
            elif bmi < 40:
                category = "Obesity_Type_I"
                risk = 0.75
            elif bmi < 45:
                category = "Obesity_Type_II"
                risk = 0.85
            else:
                category = "Obesity_Type_III"
                risk = 0.95
            
            return {
                "prediction": category,
                "probability": risk,
                "bmi": round(bmi, 2),
                "risk_level": "High" if risk > 0.6 else "Medium" if risk > 0.3 else "Low",
                "confidence": 0.85,  # Mock confidence
                "recommendations": self.get_recommendations(category, bmi)
            }
        
        # Use actual model if available
        try:
            # Preprocess features
            X = self.preprocess_features(features)
            
            # Apply feature encoding if encoder is available
            if self.feature_encoder:
                # Assuming feature_encoder is fitted on categorical features
                for col in self.categorical_features:
                    if col in X.columns and col in self.feature_encoder.get_params():
                        X[col] = self.feature_encoder.transform(X[[col]])
            
            # Make prediction
            prediction_encoded = self.model.predict(X)[0]
            
            # Get prediction probabilities if available
            if hasattr(self.model, 'predict_proba'):
                probabilities = self.model.predict_proba(X)[0]
                probability = float(max(probabilities))
                confidence = float(probability)
            else:
                probability = 0.85  # Default confidence
                confidence = 0.85
            
            # Decode prediction if label encoder is available
            if self.label_encoder:
                prediction = self.label_encoder.inverse_transform([prediction_encoded])[0]
            else:
                prediction = prediction_encoded
            
            # Calculate BMI
            bmi = X['BMI'].values[0] if 'BMI' in X.columns else 0
            
            # Determine risk level
            risk_level = self.calculate_risk_level(prediction, probability)
            
            return {
                "prediction": prediction,
                "probability": float(probability),
                "confidence": float(confidence),
                "bmi": round(float(bmi), 2),
                "risk_level": risk_level,
                "recommendations": self.get_recommendations(prediction, bmi)
            }
            
        except Exception as e:
            logger.error(f"Prediction error: {e}")
            raise ValueError(f"Error making prediction: {str(e)}")
    
    def calculate_risk_level(self, prediction: str, probability: float) -> str:
        """Calculate risk level based on prediction and probability"""
        high_risk_categories = [
            "Obesity_Type_I", "Obesity_Type_II", "Obesity_Type_III"
        ]
        medium_risk_categories = [
            "Overweight_Level_I", "Overweight_Level_II"
        ]
        
        if prediction in high_risk_categories:
            return "High"
        elif prediction in medium_risk_categories:
            return "Medium"
        else:
            return "Low"
    
    def get_recommendations(self, prediction: str, bmi: float) -> list:
        """Get health recommendations based on prediction"""
        recommendations = []
        
        if "Obesity" in prediction or "Overweight" in prediction:
            recommendations.extend([
                "Consult with a healthcare professional for personalized advice",
                "Consider increasing physical activity to at least 150 minutes per week",
                "Focus on a balanced diet with plenty of fruits and vegetables",
                "Monitor caloric intake and portion sizes",
                "Stay hydrated with at least 8 glasses of water daily"
            ])
        elif "Normal" in prediction:
            recommendations.extend([
                "Maintain your current healthy lifestyle",
                "Continue regular physical activity",
                "Keep a balanced and varied diet",
                "Regular health check-ups are recommended"
            ])
        else:  # Insufficient weight
            recommendations.extend([
                "Consult with a healthcare professional",
                "Ensure adequate caloric intake",
                "Focus on nutrient-dense foods",
                "Consider strength training exercises"
            ])
        
        return recommendations

def load_model() -> Optional[ObesityPredictor]:
    """Load the trained Random Forest model and encoders from files"""
    models_dir = Path("models")
    
    # Define file paths
    model_path = models_dir / "random_forest_model.pkl"
    feature_encoder_path = models_dir / "feature_encoder.pkl"
    label_encoder_path = models_dir / "label_encoder.pkl"
    
    model = None
    feature_encoder = None
    label_encoder = None
    
    # Load Random Forest model
    if model_path.exists():
        try:
            with open(model_path, 'rb') as f:
                model = pickle.load(f)
            logger.info(f"✅ Random Forest model loaded from {model_path}")
        except Exception as e:
            logger.error(f"❌ Error loading Random Forest model: {e}")
    else:
        logger.warning(f"⚠️ Model file not found at {model_path}")
    
    # Load feature encoder
    if feature_encoder_path.exists():
        try:
            with open(feature_encoder_path, 'rb') as f:
                feature_encoder = pickle.load(f)
            logger.info(f"✅ Feature encoder loaded from {feature_encoder_path}")
        except Exception as e:
            logger.error(f"❌ Error loading feature encoder: {e}")
    else:
        logger.warning(f"⚠️ Feature encoder not found at {feature_encoder_path}")
    
    # Load label encoder
    if label_encoder_path.exists():
        try:
            with open(label_encoder_path, 'rb') as f:
                label_encoder = pickle.load(f)
            logger.info(f"✅ Label encoder loaded from {label_encoder_path}")
        except Exception as e:
            logger.error(f"❌ Error loading label encoder: {e}")
    else:
        logger.warning(f"⚠️ Label encoder not found at {label_encoder_path}")
    
    # Return predictor with whatever was loaded
    return ObesityPredictor(
        model=model,
        feature_encoder=feature_encoder,
        label_encoder=label_encoder
    )

def train_model():
    """Train a new model (placeholder for actual training code)"""
    logger.info("Training new model...")
    # Add your actual training code here
    # This should:
    # 1. Load your training data
    # 2. Preprocess features
    # 3. Train Random Forest model
    # 4. Save model and encoders
    return ObesityPredictor()

# Optional: Function to validate model files
def validate_model_files() -> Tuple[bool, list]:
    """Validate that all required model files exist"""
    models_dir = Path("models")
    required_files = [
        "random_forest_model.pkl",
        "feature_encoder.pkl",
        "label_encoder.pkl"
    ]
    
    missing_files = []
    for file in required_files:
        if not (models_dir / file).exists():
            missing_files.append(file)
    
    is_valid = len(missing_files) == 0
    
    if not is_valid:
        logger.warning(f"⚠️ Missing model files: {', '.join(missing_files)}")
    else:
        logger.info("✅ All model files present")
    
    return is_valid, missing_files