import pickle
from pathlib import Path
import pandas as pd
import numpy as np
from typing import Dict, Any, List
import logging
from fastapi import HTTPException

logger = logging.getLogger(__name__)

class ObesityPredictor:
    """
    Obesity prediction model wrapper.
    This class loads a trained model and encoders.
    """
    def __init__(self):
        logger.info("Initializing ObesityPredictor.")
        self.model = None
        self.feature_encoder = None
        self.label_encoder = None
        # Fixed feature categorization based on actual data analysis
        self.original_numerical_features = ['Age', 'Height', 'Weight']  # These were scaled during training
        self.additional_numerical_features = ['FCVC', 'NCP', 'CH2O', 'FAF', 'TUE']  # These are raw numerical
        self.numerical_features = self.original_numerical_features + self.additional_numerical_features
        self.categorical_features = [
            'Gender', 'family_history_with_overweight', 'FAVC', 'CAEC', 
            'SMOKE', 'SCC', 'CALC', 'MTRANS'
        ]
        # Define all possible categorical values to ensure consistent 31 features
        self.categorical_values = {
            'Gender': ['Female', 'Male'],
            'family_history_with_overweight': ['no', 'yes'],
            'FAVC': ['no', 'yes'],
            'CAEC': ['Always', 'Frequently', 'Sometimes', 'no'],
            'SMOKE': ['no', 'yes'],
            'SCC': ['no', 'yes'],
            'CALC': ['Always', 'Frequently', 'Sometimes', 'no'],
            'MTRANS': ['Automobile', 'Bike', 'Motorbike', 'Public_Transportation', 'Walking']
        }
        self._load_model_assets()
        logger.info("ObesityPredictor initialization complete.")

    def _load_model_assets(self):
        """Loads model assets from disk, with fallbacks for common locations.
        Priority:
        1) app/ml/*.pkl (alongside this file)
        2) repo root *.pkl (for local runs)
        """
        base_path = Path(__file__).parent.resolve()
        repo_root = base_path.parent.parent.resolve()  # ObesiTrack/app/ml -> ObesiTrack

        candidates = [
            {
                "model": base_path / "model.pkl",
                "feature": base_path / "feature_encoder.pkl",
                "label": base_path / "label_encoder.pkl",
                "desc": "app/ml"
            },
            {
                "model": repo_root.parent / "random_forest_model.pkl",
                "feature": repo_root.parent / "feature_encoder.pkl",
                "label": repo_root.parent / "label_encoder.pkl",
                "desc": "repo root"
            },
        ]

        for c in candidates:
            logger.info(f"Attempting to load model assets from {c['desc']}")
            logger.info(f"Model: {c['model']} (exists={c['model'].exists()})")
            logger.info(f"Feature encoder: {c['feature']} (exists={c['feature'].exists()})")
            logger.info(f"Label encoder: {c['label']} (exists={c['label'].exists()})")

            try:
                if c["model"].exists() and c["feature"].exists() and c["label"].exists():
                    with open(c["model"], "rb") as f:
                        self.model = pickle.load(f)
                    with open(c["feature"], "rb") as f:
                        self.feature_encoder = pickle.load(f)
                    with open(c["label"], "rb") as f:
                        self.label_encoder = pickle.load(f)
                    logger.info(f"✅ Model assets loaded from {c['desc']}")
                    return
            except (pickle.UnpicklingError, EOFError) as e:
                logger.error(f"❌ Error deserializing model assets from {c['desc']}: {e}", exc_info=True)
            except Exception as e:
                logger.error(f"❌ Unexpected error loading assets from {c['desc']}: {e}", exc_info=True)

        logger.warning("⚠️ No valid model assets found in any known location.")
        self.model = None
        self.feature_encoder = None
        self.label_encoder = None

    def preprocess_features(self, features: Dict[str, Any]) -> pd.DataFrame:
        """Preprocess input features for model prediction.
        - Accepts keys in any case (lower/upper/title) to be robust with API inputs.
        - Returns a feature DataFrame (combined) and computed BMI.
        """
        def get_value(name: str):
            # Try several key variants
            for key in (name, name.lower(), name.upper(), name.capitalize()):
                if key in features and features[key] is not None:
                    return features[key]
            return None

        # Handle scaled numerical features (original 3 features)
        scaled_numerical_data = {}
        for feature in self.original_numerical_features:
            value = get_value(feature)
            if value is None:
                raise ValueError(f"Missing required numerical feature: {feature}")
            scaled_numerical_data[feature] = float(value)

        # Scale the original 3 numerical features if encoder available
        df_num_scaled = pd.DataFrame([scaled_numerical_data])
        if self.feature_encoder:
            df_num_scaled = pd.DataFrame(
                self.feature_encoder.transform(df_num_scaled),
                columns=self.original_numerical_features,
            )

        # Handle additional numerical features (no scaling)
        additional_numerical_data = {}
        for feature in self.additional_numerical_features:
            value = get_value(feature)
            if value is None:
                raise ValueError(f"Missing required numerical feature: {feature}")
            additional_numerical_data[feature] = float(value)

        df_num_additional = pd.DataFrame([additional_numerical_data])
        
        # Combine all numerical features
        df_num = pd.concat([df_num_scaled.reset_index(drop=True), df_num_additional.reset_index(drop=True)], axis=1)

        # Categorical features
        categorical_data = {}
        for feature in self.categorical_features:
            value = get_value(feature)
            if value is None:
                raise ValueError(f"Missing required categorical feature: {feature}")

            # Normalize Gender capitalization
            if feature.lower() == 'gender' and isinstance(value, str):
                value = value.capitalize()
            categorical_data[feature] = [value]

        # Create DataFrame with consistent categorical encoding
        df_cat = pd.DataFrame(categorical_data)
        
        # Use get_dummies with all possible categories to ensure consistent 31 features
        df_cat_encoded = pd.DataFrame()
        for feature in self.categorical_features:
            # Create a temporary dataframe with all possible values for this feature
            temp_df = pd.DataFrame({feature: self.categorical_values[feature]})
            temp_encoded = pd.get_dummies(temp_df, prefix=feature)
            
            # Create a row for our actual input value
            input_row = pd.DataFrame({feature: [categorical_data[feature][0]]})
            input_encoded = pd.get_dummies(input_row, prefix=feature)
            
            # Reindex input to match all possible columns and fill missing with 0
            input_encoded = input_encoded.reindex(columns=temp_encoded.columns, fill_value=0)
            
            # Concatenate to our final encoded dataframe
            df_cat_encoded = pd.concat([df_cat_encoded, input_encoded], axis=1)

        # BMI from original (unscaled) numerical values
        # Use the original values, not the scaled ones
        original_height = get_value('Height')  
        original_weight = get_value('Weight')
        height_m = float(original_height) / 100.0  # Convert cm to meters
        weight = float(original_weight)
        bmi = weight / (height_m ** 2)

        # Combine numerical and categorical features into a single DataFrame
        df_features = pd.concat([df_num.reset_index(drop=True), df_cat_encoded.reset_index(drop=True)], axis=1)

        logger.debug(f"Preprocessed features columns: {list(df_features.columns)}")
        logger.debug(f"Numerical features: {df_num.to_dict()}")
        logger.debug(f"Categorical features (encoded): {df_cat_encoded.to_dict()}")

        return df_features, bmi

    def predict(self, features: Dict[str, Any]) -> Dict[str, Any]:
        """Make prediction based on input features"""
        if not self.model:
            logger.error("❌ Model not loaded")
            raise RuntimeError("Model not loaded")

        try:
            # Preprocess features
            df_features, bmi = self.preprocess_features(features)

            # Verify we have exactly 31 features as expected by the model
            logger.debug(f"Generated features: {len(df_features.columns)} columns")
            logger.debug(f"Feature columns: {list(df_features.columns)}")
            
            if len(df_features.columns) != 31:
                raise ValueError(f"Feature mismatch: generated {len(df_features.columns)} features, expected 31")

            # Predict class/index
            y_pred = self.model.predict(df_features.values)[0]
            probability = None
            if hasattr(self.model, "predict_proba"):
                probs = self.model.predict_proba(df_features.values)[0]
                probability = float(np.max(probs))

            # Decode class label if label encoder available
            if self.label_encoder is not None:
                prediction_class = self.label_encoder.inverse_transform([y_pred])[0]
            else:
                prediction_class = str(y_pred)

            # Risk mapping
            risk_map = {
                'Normal_Weight': 'Low',
                'Overweight_Level_I': 'Moderate',
                'Overweight_Level_II': 'Moderate',
                'Obesity_Type_I': 'High',
                'Obesity_Type_II': 'Very High',
                'Obesity_Type_III': 'Extreme',
            }
            risk_level = risk_map.get(prediction_class, 'Unknown')

            # Recommendations
            recommendations = self._generate_recommendations(prediction_class, bmi, features)

            result = {
                "prediction": prediction_class,
                "probability": probability if probability is not None else 1.0,
                "bmi": round(float(bmi), 2),
                "risk_level": risk_level,
                "confidence": probability if probability is not None else 1.0,
                "recommendations": recommendations,
            }
            logger.info(f"Prediction result: {result}")
            return result

        except ValueError as e:
            logger.error(f"❌ Invalid input features: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=400,
                detail=f"Invalid input: {str(e)}",
            )
        except Exception as e:
            logger.error(f"❌ Error during prediction: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail="Prediction failed",
            )

    def _generate_recommendations(self, prediction_class: str, bmi: float, features: Dict[str, Any]) -> List[str]:
        """Generate personalized recommendations based on prediction and input features."""
        recommendations = []
        
        # BMI-based recommendations
        if bmi < 18.5:
            recommendations.append("Your BMI indicates you are underweight. Consider consulting a nutritionist for a healthy weight gain plan.")
        elif 18.5 <= bmi < 25:
            recommendations.append("Your BMI is in the healthy range. Maintain your current healthy lifestyle!")
        elif 25 <= bmi < 30:
            recommendations.append("Your BMI indicates you are overweight. Focus on balanced nutrition and regular exercise.")
        else:
            recommendations.append("Your BMI indicates obesity. We recommend consulting a healthcare professional.")

        # Lifestyle recommendations
        if features.get('favc', '').lower() == 'yes':
            recommendations.append("Consider reducing the frequency of high-calorie food consumption.")
        
        if float(features.get('ch2o', 2)) < 2:
            recommendations.append("Increase your daily water intake to at least 2 liters per day.")
        
        if float(features.get('faf', 0)) < 1:
            recommendations.append("Try to incorporate more physical activity into your daily routine.")
        
        if features.get('caec', '').lower() == 'always':
            recommendations.append("Try to reduce eating between meals or choose healthier snacks.")

        return recommendations