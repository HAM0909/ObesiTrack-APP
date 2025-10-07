# ObesiTrack - Complete Documentation & Workflow Guide

## 📑 Table of Contents

1. [Project Overview](#project-overview)
2. [System Architecture](#system-architecture)
3. [Installation & Setup](#installation--setup)
4. [API Documentation](#api-documentation)
5. [User Workflows](#user-workflows)
6. [Development Workflows](#development-workflows)
7. [Testing Framework](#testing-framework)
8. [Deployment Guide](#deployment-guide)
9. [Data Models & ML](#data-models--ml)
10. [Troubleshooting](#troubleshooting)

## 📊 Project Overview

**ObesiTrack** is an advanced obesity tracking and prediction system that combines machine learning with web technologies to provide users with personalized health insights and predictions about obesity risk factors.

### ✨ Key Features

- **🔐 Secure Authentication**: JWT-based user authentication system
- **📊 AI-Powered Predictions**: Machine learning models for obesity classification
- **📈 Data Visualization**: Interactive charts and analytics dashboard
- **👥 User Management**: Comprehensive admin panel for user administration
- **📱 Responsive Web Interface**: Modern, mobile-friendly UI
- **🧪 Comprehensive Testing**: Full E2E test coverage with Playwright
- **🐳 Docker Support**: Complete containerization for easy deployment

### 🎯 Target Users

- **End Users**: Individuals tracking their weight and health metrics
- **Healthcare Professionals**: Medical practitioners monitoring patient progress
- **Researchers**: Data scientists studying obesity patterns and trends
- **Administrators**: System administrators managing users and analytics

---

## 🏗️ System Architecture

### Tech Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Backend** | FastAPI + Uvicorn | High-performance REST API |
| **Database** | PostgreSQL / SQLite | Persistent data storage |
| **Authentication** | JWT + Passlib | Secure user authentication |
| **Machine Learning** | Scikit-learn | Obesity prediction models |
| **Frontend Templates** | Jinja2 + HTML/CSS/JS | Server-side rendered UI |
| **Testing** | Playwright + Pytest | End-to-end and unit testing |
| **Containerization** | Docker + Docker Compose | Development and deployment |

### Project Structure

```
ObesiTrack/
├── 📁 app/                     # Core application package
│   ├── 📁 auth/               # Authentication module
│   │   ├── dependencies.py    # Auth dependencies
│   │   ├── jwt_handler.py     # JWT token handling
│   │   └── __init__.py
│   ├── 📁 ml/                 # Machine Learning module
│   │   ├── 📁 models/         # Pre-trained ML models
│   │   ├── predictor.py       # Prediction engine
│   │   ├── model_trainer.py   # Model training scripts
│   │   └── training_pipeline.py
│   ├── 📁 models/             # Database models
│   │   ├── base.py           # Base model classes
│   │   ├── user.py           # User models
│   │   ├── prediction.py     # Prediction models
│   │   └── __init__.py
│   ├── 📁 routers/            # API route handlers
│   │   ├── auth.py           # Authentication endpoints
│   │   ├── prediction.py     # Prediction endpoints
│   │   ├── admin.py          # Admin panel endpoints
│   │   ├── metrics.py        # Analytics endpoints
│   │   ├── pages.py          # Web page routes
│   │   └── __init__.py
│   ├── 📁 schemas/            # Pydantic data schemas
│   │   ├── auth.py           # Auth schemas
│   │   ├── prediction.py     # Prediction schemas
│   │   ├── user.py           # User schemas
│   │   └── __init__.py
│   ├── 📁 static/             # Static web assets
│   │   ├── 📁 css/           # Stylesheets
│   │   ├── 📁 js/            # JavaScript files
│   │   └── 📁 images/        # Image assets
│   ├── config.py              # Application configuration
│   ├── database.py            # Database connection & setup
│   ├── templating.py          # Template configuration
│   └── main.py                # Alternative FastAPI entry point
├── 📁 templates/              # HTML templates
│   ├── base.html             # Base template
│   ├── login.html            # Login page
│   ├── register.html         # Registration page
│   ├── app_obesity.html      # Main prediction interface
│   ├── admin.html            # Admin dashboard
│   ├── history.html          # User history
│   └── user_history.html     # Detailed user history
├── 📁 tests/                  # Test suites
│   ├── 📁 e2e/               # End-to-end tests (Playwright)
│   ├── test_auth.py          # Authentication tests
│   ├── test_prediction.py    # Prediction tests
│   ├── test_admin.py         # Admin tests
│   └── test_*.py             # Additional unit tests
├── 📁 data/                   # Data and models
│   ├── obesity_data.csv      # Training dataset
│   └── EDA.ipynb            # Exploratory Data Analysis
├── 📁 scripts/                # Utility scripts
│   ├── init_db.py            # Database initialization
│   ├── train_model.py        # Model training
│   └── e2e_api_test.py       # API testing script
├── main.py                    # Primary FastAPI application entry point
├── create_demo_users.py       # Demo user creation script
├── requirements.txt           # Python dependencies
├── package.json              # Node.js dependencies (Playwright)
├── playwright.config.ts       # Playwright configuration
├── docker-compose.yml         # Docker Compose configuration
├── Dockerfile                # Docker container definition
├── .env.example              # Environment variables template
└── README.md                 # Basic project documentation
```

---

## 🚀 Installation & Setup

### Prerequisites

- **Python 3.11+** (Recommended: 3.12)
- **Node.js 18+** (for Playwright tests)
- **PostgreSQL 13+** (or SQLite for development)
- **Docker & Docker Compose** (optional, for containerized deployment)

### 1. Clone & Setup

```bash
# Clone the repository
git clone https://github.com/HAM0909/ObesiTrack-APP.git
cd ObesiTrack-APP/ObesiTrack

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows PowerShell:
.\.venv\Scripts\Activate.ps1
# Windows Command Prompt:
.\.venv\Scripts\activate.bat
# macOS/Linux:
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt

# Install Node.js dependencies (for testing)
npm install
```

### 2. Environment Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit .env file with your configuration
# Key variables:
# - DATABASE_URL: Your database connection string
# - SECRET_KEY: JWT signing key (change in production!)
# - DEBUG: Set to False in production
```

#### Environment Variables Explained

| Variable | Description | Example |
|----------|-------------|---------|
| `DATABASE_URL` | Database connection string | `postgresql://user:pass@localhost:5432/db` |
| `SECRET_KEY` | JWT signing secret (CHANGE IN PRODUCTION!) | Long random string |
| `ALGORITHM` | JWT algorithm | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token expiration time | `30` |
| `APP_NAME` | Application name | `ObesiTrack` |
| `DEBUG` | Debug mode (development only) | `True`/`False` |
| `POSTGRES_DB` | PostgreSQL database name | `obesittrack` |
| `POSTGRES_USER` | PostgreSQL username | `postgres` |
| `POSTGRES_PASSWORD` | PostgreSQL password | `your_password` |

### 3. Database Setup

#### Option A: Using PostgreSQL (Recommended for Production)

```bash
# Install PostgreSQL and create database
createdb obesittrack

# Update DATABASE_URL in .env file
DATABASE_URL=postgresql://username:password@localhost:5432/obesittrack

# Initialize database
python scripts/init_db.py
```

#### Option B: Using SQLite (Development)

```bash
# SQLite database will be created automatically
DATABASE_URL=sqlite:///./obesity_tracker.db

# Initialize database
python scripts/init_db.py
```

### 4. Create Demo Users

```bash
# Start the application first
uvicorn main:app --reload --port 8000

# In another terminal, create demo users
python create_demo_users.py
```

### 5. Start the Application

#### Development Mode

```bash
# Start with auto-reload
uvicorn main:app --reload --port 8000 --host 0.0.0.0

# Or using the alternative entry point
uvicorn app.main:app --reload --port 8000 --host 0.0.0.0
```

#### Production Mode

```bash
# Start with production settings
uvicorn main:app --port 8000 --host 0.0.0.0 --workers 4
```

### 6. Verify Installation

Open your browser and navigate to:
- **Application**: http://localhost:8000
- **Health Check**: http://localhost:8000/health
- **API Documentation**: http://localhost:8000/docs
- **Alternative API Docs**: http://localhost:8000/redoc

---

## 📋 API Documentation

### Authentication Endpoints

#### POST /api/auth/register
Register a new user account.

**Request Body:**
```json
{
  "username": "string",
  "email": "user@example.com",
  "password": "string"
}
```

**Response (201):**
```json
{
  "message": "User created successfully",
  "user_id": 123
}
```

#### POST /api/auth/login
Authenticate user and receive JWT token.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "string"
}
```

**Response (200):**
```json
{
  "access_token": "jwt_token_here",
  "token_type": "bearer",
  "user": {
    "id": 123,
    "username": "string",
    "email": "user@example.com",
    "is_admin": false
  }
}
```

### Prediction Endpoints

#### POST /api/prediction/predict
Make an obesity prediction based on user data.

**Headers:**
```
Authorization: Bearer <jwt_token>
```

**Request Body:**
```json
{
  "gender": "male",
  "age": 25,
  "height": 170.0,
  "weight": 70.0,
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
```

**Response (200):**
```json
{
  "prediction": "Normal_Weight",
  "confidence": 0.85,
  "bmi": 24.2,
  "risk_level": "Low",
  "recommendations": [
    "Maintain current weight",
    "Continue regular exercise"
  ],
  "created_at": "2024-01-01T12:00:00Z"
}
```

#### GET /api/prediction/history
Get user's prediction history.

**Headers:**
```
Authorization: Bearer <jwt_token>
```

**Response (200):**
```json
{
  "predictions": [
    {
      "id": 1,
      "prediction": "Normal_Weight",
      "confidence": 0.85,
      "bmi": 24.2,
      "created_at": "2024-01-01T12:00:00Z"
    }
  ],
  "total": 1
}
```

### Admin Endpoints

#### GET /api/admin/users
Get list of all users (Admin only).

**Headers:**
```
Authorization: Bearer <admin_jwt_token>
```

**Response (200):**
```json
{
  "users": [
    {
      "id": 1,
      "username": "user1",
      "email": "user1@example.com",
      "is_admin": false,
      "created_at": "2024-01-01T12:00:00Z"
    }
  ]
}
```

#### DELETE /api/admin/users/{user_id}
Delete a user account (Admin only).

### Analytics Endpoints

#### GET /api/metrics/dashboard
Get dashboard analytics data.

**Response (200):**
```json
{
  "total_users": 100,
  "total_predictions": 500,
  "predictions_today": 25,
  "prediction_distribution": {
    "Normal_Weight": 40,
    "Overweight_Level_I": 30,
    "Overweight_Level_II": 20,
    "Obesity_Type_I": 10
  }
}
```

---

## 👤 User Workflows

### 1. New User Registration Workflow

```mermaid
graph TD
    A[Visit Homepage] --> B[Click Register]
    B --> C[Fill Registration Form]
    C --> D[Submit Form]
    D --> E{Validation}
    E -->|Success| F[Account Created]
    E -->|Error| G[Show Errors]
    G --> C
    F --> H[Redirect to Login]
    H --> I[Login with Credentials]
    I --> J[Access Main App]
```

**Steps:**
1. Navigate to http://localhost:8000
2. Click "Register" link
3. Fill out the registration form:
   - Username (unique)
   - Email (valid format)
   - Password (minimum requirements)
4. Submit form
5. If successful, redirect to login page
6. Login with new credentials
7. Access the main prediction interface

### 2. Obesity Prediction Workflow

```mermaid
graph TD
    A[Login to System] --> B[Access Prediction Form]
    B --> C[Fill Personal Data]
    C --> D[Fill Lifestyle Data]
    D --> E[Submit for Prediction]
    E --> F[ML Model Processing]
    F --> G[Display Results]
    G --> H[View Recommendations]
    H --> I[Save to History]
    I --> J[Export/Share Results]
```

**Steps:**
1. **Login**: Authenticate with email/password
2. **Navigate to Prediction**: Access main prediction interface
3. **Enter Basic Information**:
   - Gender (Male/Female)
   - Age (years)
   - Height (cm)
   - Weight (kg)
4. **Enter Lifestyle Information**:
   - Family history of overweight
   - Frequent high-calorie food consumption
   - Frequency of vegetable consumption
   - Number of main meals
   - Food consumption between meals
   - Smoking habits
   - Daily water consumption
   - Calorie monitoring habits
   - Physical activity frequency
   - Technology usage time
   - Alcohol consumption
   - Transportation mode
5. **Submit & Review Results**:
   - Obesity classification prediction
   - Confidence score
   - BMI calculation
   - Risk level assessment
   - Personalized recommendations

### 3. Admin User Management Workflow

```mermaid
graph TD
    A[Admin Login] --> B[Access Admin Panel]
    B --> C[View User List]
    C --> D[User Management Actions]
    D --> E[View User Details]
    D --> F[Delete User]
    D --> G[View User Analytics]
    E --> H[View Prediction History]
    F --> I[Confirm Deletion]
    G --> J[Export Reports]
```

**Admin Features:**
- View all registered users
- Delete user accounts
- View user prediction histories
- Generate analytics reports
- Monitor system usage

---

## 💻 Development Workflows

### Setting Up Development Environment

```bash
# 1. Clone and setup (see Installation section)

# 2. Install development dependencies
pip install -r requirements.txt
npm install

# 3. Install Playwright browsers
npx playwright install

# 4. Set up pre-commit hooks (optional)
pip install pre-commit
pre-commit install
```

### Code Organization Best Practices

1. **Follow the established structure**:
   - Models in `app/models/`
   - API routes in `app/routers/`
   - Schemas in `app/schemas/`
   - ML code in `app/ml/`

2. **Database Changes**:
   - Update models in `app/models/`
   - Create migration scripts
   - Test changes thoroughly

3. **API Development**:
   - Add new endpoints to appropriate routers
   - Include proper authentication
   - Document with FastAPI docstrings
   - Add comprehensive tests

4. **ML Model Updates**:
   - Update training pipeline in `app/ml/`
   - Ensure backward compatibility
   - Update predictor class
   - Validate model performance

### Git Workflow

```bash
# 1. Create feature branch
git checkout -b feature/new-feature

# 2. Make changes and commit
git add .
git commit -m "feat: add new feature"

# 3. Run tests before pushing
npm run test:e2e
python -m pytest tests/

# 4. Push and create pull request
git push origin feature/new-feature
```

### Database Migrations

```bash
# 1. Make model changes in app/models/

# 2. Generate migration (if using Alembic)
alembic revision --autogenerate -m "Add new field"

# 3. Apply migration
alembic upgrade head

# 4. Test migration rollback
alembic downgrade -1
alembic upgrade head
```

---

## 🧪 Testing Framework

### Test Structure

The project uses a comprehensive testing approach:

1. **Unit Tests** (pytest): Test individual components
2. **Integration Tests** (pytest): Test component interactions  
3. **End-to-End Tests** (Playwright): Test complete user workflows

### Running Tests

#### Unit & Integration Tests

```bash
# Run all Python tests
python -m pytest tests/

# Run specific test file
python -m pytest tests/test_auth.py

# Run with coverage
python -m pytest tests/ --cov=app --cov-report=html

# Run with verbose output
python -m pytest tests/ -v
```

#### End-to-End Tests

```bash
# Install Playwright browsers (first time only)
npx playwright install

# Run all E2E tests
npx playwright test

# Run tests with UI
npx playwright test --ui

# Run tests in headed mode (see browser)
npx playwright test --headed

# Run specific test file
npx playwright test tests/e2e/auth-credentials-validation.spec.ts

# Generate test report
npx playwright show-report
```

### Test Categories

#### Authentication Tests (`test_auth.py`)
- User registration validation
- Login/logout functionality
- JWT token generation/validation
- Password hashing security

#### Prediction Tests (`test_prediction.py`)
- ML model loading and initialization
- Prediction accuracy validation
- Input data validation
- Error handling for invalid inputs

#### Admin Tests (`test_admin.py`)
- Admin-only endpoint security
- User management operations
- Analytics data accuracy

#### End-to-End Test Suites

1. **Authentication E2E** (`auth-credentials-validation.spec.ts`):
   - Complete registration flow
   - Login with valid/invalid credentials
   - Session management

2. **Prediction Functionality** (`prediction-fix.spec.ts`):
   - Complete prediction workflow
   - Form validation
   - Result display verification

3. **Admin Management** (`admin-user-management.spec.ts`):
   - Admin panel access
   - User list management
   - User deletion workflows

4. **Infrastructure Tests** (`infrastructure-deployment.spec.ts`):
   - System health checks
   - Database connectivity
   - API endpoint availability

### Writing New Tests

#### Unit Test Example

```python
# tests/test_new_feature.py
import pytest
from app.models.user import User
from app.database import get_db

def test_user_creation():
    """Test user model creation."""
    user = User(
        username="testuser",
        email="test@example.com",
        hashed_password="hashed_password"
    )
    assert user.username == "testuser"
    assert user.email == "test@example.com"
    assert not user.is_admin
```

#### E2E Test Example

```typescript
// tests/e2e/new-feature.spec.ts
import { test, expect } from '@playwright/test';

test.describe('New Feature Tests', () => {
  test('should perform new feature workflow', async ({ page }) => {
    // Navigate to application
    await page.goto('/');
    
    // Perform actions
    await page.click('[data-testid="new-feature-button"]');
    
    // Verify results
    await expect(page.locator('[data-testid="result"]')).toBeVisible();
  });
});
```

---

## 🚢 Deployment Guide

### Docker Deployment (Recommended)

#### 1. Using Docker Compose (Development)

```bash
# Build and start all services
docker-compose up --build

# Start in background
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Clean up (including volumes)
docker-compose down -v
```

#### 2. Production Docker Deployment

```bash
# Build production image
docker build -t obesitrack:latest .

# Run with production settings
docker run -d \
  --name obesitrack-app \
  -p 8000:8000 \
  -e DATABASE_URL="postgresql://user:pass@db:5432/obesittrack" \
  -e SECRET_KEY="your-production-secret-key" \
  -e DEBUG=False \
  obesitrack:latest
```

### Manual Deployment

#### 1. Server Setup

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python 3.11+
sudo apt install python3.11 python3.11-venv python3-pip

# Install PostgreSQL
sudo apt install postgresql postgresql-contrib

# Install Node.js (for optional frontend builds)
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs
```

#### 2. Application Deployment

```bash
# Clone repository
git clone https://github.com/HAM0909/ObesiTrack-APP.git
cd ObesiTrack-APP/ObesiTrack

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with production values

# Initialize database
python scripts/init_db.py

# Create demo users (optional)
python create_demo_users.py
```

#### 3. Process Management with systemd

```bash
# Create systemd service file
sudo nano /etc/systemd/system/obesitrack.service
```

```ini
[Unit]
Description=ObesiTrack FastAPI Application
After=network.target

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/path/to/ObesiTrack
Environment=PATH=/path/to/ObesiTrack/venv/bin
EnvironmentFile=/path/to/ObesiTrack/.env
ExecStart=/path/to/ObesiTrack/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start service
sudo systemctl enable obesitrack
sudo systemctl start obesitrack
sudo systemctl status obesitrack
```

#### 4. Nginx Reverse Proxy

```bash
# Install Nginx
sudo apt install nginx

# Create Nginx configuration
sudo nano /etc/nginx/sites-available/obesitrack
```

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Static files (if serving directly)
    location /static/ {
        alias /path/to/ObesiTrack/app/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/obesitrack /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### Environment-Specific Configurations

#### Development
- `DEBUG=True`
- SQLite database
- Detailed logging
- Auto-reload enabled

#### Staging
- `DEBUG=False`
- PostgreSQL database
- Standard logging
- SSL certificates
- Performance monitoring

#### Production
- `DEBUG=False`
- PostgreSQL with connection pooling
- Structured logging
- SSL/TLS encryption
- Load balancing
- Monitoring and alerting
- Backup strategies

---

## 🤖 Data Models & ML

### Database Models

#### User Model (`app/models/user.py`)

```python
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    predictions = relationship("Prediction", back_populates="user")
```

#### Prediction Model (`app/models/prediction.py`)

```python
class Prediction(Base):
    __tablename__ = "predictions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    
    # Input features
    gender = Column(String)
    age = Column(Integer)
    height = Column(Float)
    weight = Column(Float)
    # ... additional features
    
    # Results
    prediction = Column(String)
    confidence = Column(Float)
    bmi = Column(Float)
    risk_level = Column(String)
    
    # Metadata
    input_data = Column(JSON)  # Store complete input for analysis
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="predictions")
```

### Machine Learning Pipeline

#### Model Features

The ML model uses 16 input features to predict obesity levels:

**Demographic Features:**
- Gender (Male/Female)
- Age (years)
- Height (cm)
- Weight (kg)

**Lifestyle Features:**
- Family history of overweight (yes/no)
- Frequent consumption of high caloric food (yes/no)
- Frequency of vegetable consumption (0-3 scale)
- Number of main meals (1-4)
- Food consumption between meals (Always/Frequently/Sometimes/no)
- Smoking habits (yes/no)
- Daily water consumption (1-3 liters)
- Calories consumption monitoring (yes/no)
- Physical activity frequency (0-3 scale)
- Technology usage time (0-2 hours)
- Alcohol consumption (Always/Frequently/Sometimes/no)
- Transportation mode (Walking/Bike/Public_Transportation/Automobile/Motorbike)

#### Prediction Classes

The model predicts one of seven obesity levels:
1. **Insufficient_Weight**: BMI < 18.5
2. **Normal_Weight**: 18.5 ≤ BMI < 25
3. **Overweight_Level_I**: 25 ≤ BMI < 30
4. **Overweight_Level_II**: 30 ≤ BMI < 35
5. **Obesity_Type_I**: 35 ≤ BMI < 40
6. **Obesity_Type_II**: 40 ≤ BMI < 50
7. **Obesity_Type_III**: BMI ≥ 50

#### Model Training Pipeline

```python
# app/ml/training_pipeline.py
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.model_selection import train_test_split

class ObesityTrainingPipeline:
    def __init__(self):
        self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.feature_encoder = StandardScaler()
        self.label_encoder = LabelEncoder()
    
    def train(self, data_path):
        # Load and preprocess data
        data = pd.read_csv(data_path)
        X, y = self.preprocess_data(data)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        # Train model
        X_train_scaled = self.feature_encoder.fit_transform(X_train)
        y_train_encoded = self.label_encoder.fit_transform(y_train)
        
        self.model.fit(X_train_scaled, y_train_encoded)
        
        # Evaluate
        accuracy = self.model.score(
            self.feature_encoder.transform(X_test),
            self.label_encoder.transform(y_test)
        )
        
        return accuracy
```

#### Prediction Service

```python
# app/ml/predictor.py
class ObesityPredictor:
    def predict(self, features: Dict[str, Any]) -> Dict[str, Any]:
        # Preprocess features
        processed_features = self._preprocess_features(features)
        
        # Make prediction
        prediction_encoded = self.model.predict([processed_features])[0]
        prediction = self.label_encoder.inverse_transform([prediction_encoded])[0]
        
        # Get confidence scores
        probabilities = self.model.predict_proba([processed_features])[0]
        confidence = max(probabilities)
        
        # Calculate BMI
        bmi = features['weight'] / (features['height'] / 100) ** 2
        
        # Determine risk level
        risk_level = self._calculate_risk_level(prediction, bmi)
        
        return {
            'prediction': prediction,
            'confidence': confidence,
            'bmi': round(bmi, 1),
            'risk_level': risk_level,
            'recommendations': self._generate_recommendations(prediction, bmi)
        }
```

### Data Analysis & Insights

The system provides analytics on:
- **Prediction Distribution**: Breakdown of obesity classifications
- **User Demographics**: Age, gender distribution
- **Lifestyle Patterns**: Common risk factors
- **Temporal Trends**: Changes in predictions over time
- **Regional Analysis**: Geographic patterns (if location data available)

---

## 🔧 Troubleshooting

### Common Issues & Solutions

#### 1. Database Connection Issues

**Problem**: `psycopg2.OperationalError: could not connect to server`

**Solutions:**
```bash
# Check if PostgreSQL is running
sudo systemctl status postgresql

# Start PostgreSQL if stopped
sudo systemctl start postgresql

# Verify connection parameters in .env
DATABASE_URL=postgresql://username:password@localhost:5432/database_name

# Test connection manually
psql -h localhost -U username -d database_name
```

#### 2. Model Loading Errors

**Problem**: `FileNotFoundError: Model files not found`

**Solutions:**
```bash
# Ensure model files exist
ls app/ml/models/
# Should contain: model.pkl, feature_encoder.pkl, label_encoder.pkl

# Retrain models if missing
python scripts/train_model.py

# Check file permissions
chmod 644 app/ml/models/*.pkl
```

#### 3. JWT Token Issues

**Problem**: `Invalid token` or `Token expired`

**Solutions:**
```bash
# Check SECRET_KEY in .env (must be consistent)
SECRET_KEY=your-super-secret-key-change-this-in-production

# Verify token expiration time
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Clear browser cookies and re-login
# Or extend token expiration for development
```

#### 4. Playwright Test Failures

**Problem**: Tests failing with timeout errors

**Solutions:**
```bash
# Install/update browsers
npx playwright install

# Run tests with higher timeout
npx playwright test --timeout 60000

# Check if application is running
curl http://localhost:8000/health

# Run tests in headed mode to debug
npx playwright test --headed
```

#### 5. Port Already in Use

**Problem**: `OSError: [Errno 98] Address already in use`

**Solutions:**
```bash
# Find process using port 8000
lsof -i :8000
# or
netstat -tulpn | grep :8000

# Kill process
kill -9 <PID>

# Or use different port
uvicorn main:app --port 8001
```

#### 6. Static Files Not Loading

**Problem**: CSS/JS files not loading (404 errors)

**Solutions:**
```bash
# Verify static files directory structure
ls -la app/static/

# Check FastAPI static files mounting in main.py
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Ensure correct paths in templates
<link rel="stylesheet" href="{{ url_for('static', path='css/style.css') }}">
```

### Performance Optimization

#### 1. Database Query Optimization

```python
# Use indexes on frequently queried columns
class User(Base):
    email = Column(String, unique=True, index=True)  # ✅ Indexed
    created_at = Column(DateTime, index=True)        # ✅ For date queries

# Use eager loading for relationships
from sqlalchemy.orm import selectinload
users = session.query(User).options(selectinload(User.predictions)).all()
```

#### 2. Caching Strategies

```python
# Redis caching for frequent predictions
import redis
from functools import wraps

redis_client = redis.Redis(host='localhost', port=6379, db=0)

def cache_prediction(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        cache_key = f"prediction:{hash(str(kwargs))}"
        cached_result = redis_client.get(cache_key)
        
        if cached_result:
            return json.loads(cached_result)
        
        result = func(*args, **kwargs)
        redis_client.setex(cache_key, 3600, json.dumps(result))  # 1 hour cache
        return result
    
    return wrapper
```

#### 3. Application Monitoring

```python
# Add monitoring middleware
import time
from fastapi import Request

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response
```

### Security Best Practices

#### 1. Environment Variables Security

```bash
# Never commit .env files
echo ".env" >> .gitignore

# Use strong secrets in production
SECRET_KEY=$(openssl rand -hex 32)

# Rotate secrets regularly
# Update SECRET_KEY and restart application
```

#### 2. Database Security

```python
# Use parameterized queries (SQLAlchemy handles this automatically)
# ✅ Safe
user = session.query(User).filter(User.email == email).first()

# ❌ Vulnerable to SQL injection (avoid raw SQL)
# session.execute(f"SELECT * FROM users WHERE email = '{email}'")
```

#### 3. Input Validation

```python
# Use Pydantic for input validation
class PredictionRequest(BaseModel):
    age: int = Field(..., ge=1, le=120)  # Age between 1-120
    height: float = Field(..., ge=50, le=250)  # Height in cm
    weight: float = Field(..., ge=10, le=500)  # Weight in kg
    
    @validator('email')
    def validate_email(cls, v):
        if '@' not in v:
            raise ValueError('Invalid email format')
        return v.lower()
```

### Monitoring & Logging

#### 1. Structured Logging

```python
import logging
import json
from datetime import datetime

class JSONFormatter(logging.Formatter):
    def format(self, record):
        return json.dumps({
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        })

# Configure logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
handler.setFormatter(JSONFormatter())
logger.addHandler(handler)
```

#### 2. Health Check Endpoints

```python
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "database": check_database_health(),
        "ml_model": check_model_health(),
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/metrics")
async def get_metrics():
    return {
        "total_users": get_user_count(),
        "predictions_today": get_predictions_today(),
        "average_response_time": get_avg_response_time(),
        "uptime": get_uptime()
    }
```

---

## 📚 Additional Resources

### API Documentation
- **Interactive API Docs**: http://localhost:8000/docs
- **Alternative API Docs**: http://localhost:8000/redoc

### External Documentation
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Playwright Documentation](https://playwright.dev/)
- [scikit-learn Documentation](https://scikit-learn.org/)

### Development Tools
- [Postman Collection](./docs/postman_collection.json) - API testing
- [Database ERD](./docs/database_diagram.png) - Database schema
- [Architecture Diagram](./docs/architecture.png) - System overview

### Support & Contributing

#### Reporting Issues
1. Check existing issues on GitHub
2. Provide detailed error logs
3. Include steps to reproduce
4. Specify environment details

#### Contributing Guidelines
1. Fork the repository
2. Create feature branch
3. Add comprehensive tests
4. Update documentation
5. Submit pull request

---

**Last Updated**: October 2025
**Version**: 1.0.0
**Maintainer**: HAM0909

For additional support or questions, please refer to the [GitHub repository](https://github.com/HAM0909/ObesiTrack-APP) or open an issue.