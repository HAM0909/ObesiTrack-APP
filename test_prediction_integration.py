#!/usr/bin/env python3
"""
Integration test for the prediction functionality.
This tests the actual ML prediction pipeline end-to-end.
"""

import sys
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from app.ml.predictor import ObesityPredictor


def test_prediction_integration():
    """Test the full prediction pipeline with a realistic example."""
    print("🧪 Testing Prediction Integration...")
    
    # Initialize the predictor
    print("1. Initializing predictor...")
    predictor = ObesityPredictor()
    
    # Check if model is loaded
    assert predictor.model is not None, "Model failed to load - model assets missing"
    print("✅ Model loaded successfully")
    
    # Test with realistic input data
    test_input = {
        "Gender": "Male",
        "Age": 30,
        "Height": 175.0,  # cm
        "Weight": 75.0,   # kg
        "family_history_with_overweight": "yes",
        "FAVC": "yes",    # Frequent consumption of high caloric food
        "FCVC": 2.0,      # Frequency of consumption of vegetables
        "NCP": 3.0,       # Number of main meals
        "CAEC": "Sometimes", # Consumption of food between meals
        "SMOKE": "no",
        "CH2O": 2.0,      # Daily water consumption
        "SCC": "no",      # Calories consumption monitoring
        "FAF": 1.0,       # Physical activity frequency
        "TUE": 1.0,       # Time using technology devices
        "CALC": "Sometimes", # Consumption of alcohol
        "MTRANS": "Public_Transportation"
    }
    
    print("2. Making prediction with test input...")
    result = predictor.predict(test_input)
    
    print("✅ Prediction successful!")
    print(f"📊 Results:")
    print(f"   - Prediction: {result['prediction']}")
    print(f"   - Probability: {result['probability']:.3f}")
    print(f"   - BMI: {result['bmi']:.2f}")
    print(f"   - Risk Level: {result['risk_level']}")
    print(f"   - Confidence: {result['confidence']:.3f}")
    print(f"   - Recommendations: {len(result['recommendations'])} items")
    
    for i, rec in enumerate(result['recommendations'], 1):
        print(f"      {i}. {rec}")
    
    # Verify all expected keys are present
    expected_keys = ['prediction', 'probability', 'bmi', 'risk_level', 'confidence', 'recommendations']
    missing_keys = [key for key in expected_keys if key not in result]
    
    assert not missing_keys, f"Missing keys in result: {missing_keys}"
    print("✅ All expected keys present in result")


def test_feature_preprocessing():
    """Test the feature preprocessing logic."""
    print("\n🔬 Testing Feature Preprocessing...")
    
    predictor = ObesityPredictor()
    
    if not predictor.feature_encoder:
        print("❌ Feature encoder not loaded - testing without encoder")
        
    test_input = {
        "Gender": "Female",  # Test different gender
        "Age": 25,
        "Height": 160.0,
        "Weight": 55.0,
        "family_history_with_overweight": "no",
        "FAVC": "no",
        "FCVC": 3.0,
        "NCP": 2.0,
        "CAEC": "no",
        "SMOKE": "no",
        "CH2O": 3.0,
        "SCC": "yes",
        "FAF": 2.0,
        "TUE": 0.5,
        "CALC": "no",
        "MTRANS": "Walking"
    }
    
    features, bmi = predictor.preprocess_features(test_input)
    
    print(f"✅ Feature preprocessing successful!")
    print(f"   - Features shape: {features.shape}")
    print(f"   - BMI calculated: {bmi:.2f}")
    print(f"   - Expected feature count: 31")
    print(f"   - Actual feature count: {len(features.columns)}")
    
    assert len(features.columns) == 31, f"Feature count mismatch: expected 31, got {len(features.columns)}"
    print("✅ Correct number of features generated")
        
    # Check BMI calculation
    expected_bmi = 55.0 / (1.6 ** 2)  # Weight / (Height in meters)^2
    assert abs(bmi - expected_bmi) < 0.01, f"BMI calculation error: expected {expected_bmi:.2f}, got {bmi:.2f}"
    print("✅ BMI calculation correct")


def test_model_status():
    """Test model status and configuration."""
    print("\n📋 Testing Model Status...")
    
    predictor = ObesityPredictor()
    
    print(f"Model loaded: {predictor.model is not None}")
    print(f"Feature encoder loaded: {predictor.feature_encoder is not None}")
    print(f"Label encoder loaded: {predictor.label_encoder is not None}")
    print(f"Numerical features: {predictor.numerical_features}")
    print(f"Categorical features: {predictor.categorical_features}")
    
    # Verify all model components are loaded
    assert predictor.model is not None, "Model should be loaded"
    assert predictor.feature_encoder is not None, "Feature encoder should be loaded"
    assert predictor.label_encoder is not None, "Label encoder should be loaded"
    assert len(predictor.numerical_features) > 0, "Should have numerical features defined"
    assert len(predictor.categorical_features) > 0, "Should have categorical features defined"
    
    # Test categorical values configuration
    print("\nCategorical value mappings:")
    for feature, values in predictor.categorical_values.items():
        print(f"  {feature}: {values}")
        assert len(values) > 0, f"Feature {feature} should have valid categorical values"


if __name__ == "__main__":
    print("🚀 Starting Prediction Integration Tests\n")
    
    # Run all tests
    tests_passed = 0
    total_tests = 3
    
    try:
        test_model_status()
        tests_passed += 1
        print("✅ test_model_status passed")
    except Exception as e:
        print(f"❌ test_model_status failed: {e}")
        
    try:
        test_feature_preprocessing()
        tests_passed += 1
        print("✅ test_feature_preprocessing passed")
    except Exception as e:
        print(f"❌ test_feature_preprocessing failed: {e}")
        
    try:
        test_prediction_integration()
        tests_passed += 1
        print("✅ test_prediction_integration passed")
    except Exception as e:
        print(f"❌ test_prediction_integration failed: {e}")
    
    print(f"\n📊 Test Results: {tests_passed}/{total_tests} tests passed")
    
    if tests_passed == total_tests:
        print("🎉 All prediction tests passed! The ML pipeline is working correctly.")
    else:
        print("❌ Some tests failed. Please check the model assets and configuration.")
        
    sys.exit(0 if tests_passed == total_tests else 1)