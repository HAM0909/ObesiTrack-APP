import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
import pickle
from pathlib import Path

# Define paths
DATA_PATH = Path("data/obesity_data.csv")
MODELS_DIR = Path("app/ml/models")

# Create models directory if it doesn't exist
MODELS_DIR.mkdir(exist_ok=True)

# Load data
data = pd.read_csv(DATA_PATH)

# Define features and target
X = data.drop("NObeyesdad", axis=1)
y = data["NObeyesdad"]

# Identify categorical and numerical features
categorical_features = X.select_dtypes(include=['object']).columns
numerical_features = X.select_dtypes(include=['number']).columns

# Encode categorical features
# For simplicity, we'll use LabelEncoder for all categorical features.
# In a real-world scenario, OneHotEncoder might be more appropriate for some.
preprocessor = ColumnTransformer(
    transformers=[
        ('cat', LabelEncoder(), categorical_features)
    ],
    remainder='passthrough'
)

# Encode target variable
label_encoder = LabelEncoder()
y_encoded = label_encoder.fit_transform(y)

# Split data
X_train, X_test, y_train, y_test = train_test_split(X, y_encoded, test_size=0.2, random_state=42)

# Create a feature encoder for the categorical features
feature_encoder = LabelEncoder()
for col in categorical_features:
    X_train[col] = feature_encoder.fit_transform(X_train[col])
    X_test[col] = feature_encoder.transform(X_test[col])


# Train model
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Save model and encoders
with open(MODELS_DIR / "model.pkl", "wb") as f:
    pickle.dump(model, f)

with open(MODELS_DIR / "feature_encoder.pkl", "wb") as f:
    pickle.dump(feature_encoder, f)

with open(MODELS_DIR / "label_encoder.pkl", "wb") as f:
    pickle.dump(label_encoder, f)

# Model training complete. Model and encoders saved to app/ml/models/