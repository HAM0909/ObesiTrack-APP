import sys
from pathlib import Path
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder, StandardScaler
import pickle
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add project root to Python path
PROJECT_ROOT = Path(__file__).parent.parent.resolve()
sys.path.append(str(PROJECT_ROOT))


def load_data():
    """Load the obesity dataset."""
    data_path = PROJECT_ROOT / "data" / "obesity_data.csv"
    if not data_path.exists():
        raise FileNotFoundError(f"Dataset not found at {data_path}")
    df = pd.read_csv(data_path)
    logger.info(f"✅ Loaded data from {data_path}")
    return df


def preprocess_data(df: pd.DataFrame):
    """Preprocess the data for training.
    - One-hot encode categorical features
    - Scale numerical features
    - Label-encode target
    Returns: X (np.ndarray), y (np.ndarray), label_encoder, feature_scaler
    """
    target_col = "NObeyesdad"
    if target_col not in df.columns:
        raise KeyError(f"Target column '{target_col}' not found in dataset")

    # Identify features
    categorical_features = [
        'Gender', 'family_history_with_overweight', 'FAVC', 'FCVC',
        'NCP', 'CAEC', 'SMOKE', 'CH2O', 'SCC', 'FAF', 'TUE', 'CALC', 'MTRANS'
    ]
    numerical_features = ['Age', 'Height', 'Weight']

    missing = [c for c in categorical_features + numerical_features + [target_col] if c not in df.columns]
    if missing:
        raise KeyError(f"Missing expected columns: {missing}")

    # Encode target
    label_encoder = LabelEncoder()
    y = label_encoder.fit_transform(df[target_col])

    # One-hot encode categorical
    X_cat = pd.get_dummies(df[categorical_features], drop_first=False)

    # Scale numerical
    scaler = StandardScaler()
    X_num = scaler.fit_transform(df[numerical_features])

    # Combine
    X = np.hstack([X_num, X_cat.values])
    return X, y, label_encoder, scaler


def train_model(X: np.ndarray, y: np.ndarray) -> RandomForestClassifier:
    """Train the Random Forest model."""
    model = RandomForestClassifier(
        n_estimators=200,
        max_depth=None,
        n_jobs=-1,
        random_state=42,
    )
    model.fit(X, y)
    return model


def save_artifacts(model: RandomForestClassifier, label_encoder: LabelEncoder, scaler: StandardScaler):
    """Save the model and encoders to app/ml directory using pickle protocol 3 for compatibility."""
    ml_dir = PROJECT_ROOT / "app" / "ml"
    ml_dir.mkdir(parents=True, exist_ok=True)

    model_path = ml_dir / "model.pkl"
    with open(model_path, "wb") as f:
        pickle.dump(model, f, protocol=3)
    logger.info(f"✅ Saved model to {model_path}")

    label_path = ml_dir / "label_encoder.pkl"
    with open(label_path, "wb") as f:
        pickle.dump(label_encoder, f, protocol=3)
    logger.info(f"✅ Saved label encoder to {label_path}")

    feature_path = ml_dir / "feature_encoder.pkl"
    with open(feature_path, "wb") as f:
        pickle.dump(scaler, f, protocol=3)
    logger.info(f"✅ Saved feature scaler to {feature_path}")


def main():
    logger.info("🚀 Starting model training")

    # Load data
    df = load_data()

    # Preprocess
    X, y, label_encoder, scaler = preprocess_data(df)

    # Split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    # Train
    model = train_model(X_train, y_train)

    # Evaluate
    train_score = model.score(X_train, y_train)
    test_score = model.score(X_test, y_test)
    logger.info("📊 Model Performance:")
    logger.info(f"Train accuracy: {train_score:.4f}")
    logger.info(f"Test accuracy: {test_score:.4f}")

    # Save
    save_artifacts(model, label_encoder, scaler)

    logger.info("✅ Training complete!")


if __name__ == "__main__":
    main()