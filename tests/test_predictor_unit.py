import unittest
from pathlib import Path
import sys

# Ensure 'ObesiTrack' project root is on sys.path so 'app' package is importable
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.ml.predictor import ObesityPredictor


class DummyModel:
    def predict(self, X):
        return [1]

    def predict_proba(self, X):
        import numpy as np
        return np.array([[0.2, 0.8]])


class TestObesityPredictor(unittest.TestCase):
    def setUp(self):
        self.predictor = ObesityPredictor()
        # Inject dummy components to avoid dependency on serialized assets
        self.predictor.model = DummyModel()
        self.predictor.label_encoder = None
        self.predictor.feature_encoder = None

    def test_preprocess_features_bmi_and_keys(self):
        features = {
            "Gender": "male",
            "Age": 30,
            "Height": 170.0,
            "Weight": 68.0,
            "family_history_with_overweight": "yes",
            "FAVC": "no",
            "FCVC": 2.0,
            "NCP": 3.0,
            "CAEC": "Sometimes",
            "SMOKE": "no",
            "CH2O": 2.0,
            "SCC": "no",
            "FAF": 1.0,
            "TUE": 1.0,
            "CALC": "Sometimes",
            "MTRANS": "Public_Transportation",
        }
        df, bmi = self.predictor.preprocess_features(features)
        self.assertIsNotNone(df)
        self.assertGreater(df.shape[1], 0)
        # BMI 68/(1.7^2) ~ 23.53
        self.assertAlmostEqual(bmi, 68.0 / (1.7 ** 2), places=5)

    def test_predict_returns_expected_keys(self):
        features = {
            "Gender": "Male",
            "Age": 30,
            "Height": 170.0,
            "Weight": 68.0,
            "family_history_with_overweight": "yes",
            "FAVC": "no",
            "FCVC": 2.0,
            "NCP": 3.0,
            "CAEC": "Sometimes",
            "SMOKE": "no",
            "CH2O": 2.0,
            "SCC": "no",
            "FAF": 1.0,
            "TUE": 1.0,
            "CALC": "Sometimes",
            "MTRANS": "Public_Transportation",
        }
        result = self.predictor.predict(features)
        self.assertIsInstance(result, dict)
        for key in [
            "prediction",
            "probability",
            "bmi",
            "risk_level",
            "confidence",
            "recommendations",
        ]:
            self.assertIn(key, result)


if __name__ == "__main__":
    unittest.main()
