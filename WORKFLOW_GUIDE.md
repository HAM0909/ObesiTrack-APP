# ObesiTrack - Detailed Workflow Guide

## 📋 Table of Contents

1. [Quick Start Workflow](#quick-start-workflow)
2. [Development Workflow](#development-workflow)
3. [Testing Workflow](#testing-workflow)
4. [Deployment Workflow](#deployment-workflow)
5. [User Management Workflow](#user-management-workflow)
6. [ML Model Workflow](#ml-model-workflow)
7. [Troubleshooting Workflow](#troubleshooting-workflow)

---

## 🚀 Quick Start Workflow

### For First-Time Setup

```bash
# 1. Clone and navigate to project
git clone https://github.com/HAM0909/ObesiTrack-APP.git
cd ObesiTrack-APP/ObesiTrack

# 2. Set up Python environment
python -m venv venv
# Windows PowerShell:
.\.venv\Scripts\Activate.ps1
# Windows CMD:
.\.venv\Scripts\activate.bat
# macOS/Linux:
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt
npm install

# 4. Configure environment
cp .env.example .env
# Edit .env file with your settings

# 5. Initialize database
python scripts/init_db.py

# 6. Start the application
uvicorn main:app --reload --port 8000

# 7. Verify installation
curl http://localhost:8000/health
```

### For Returning Developers

```bash
# 1. Navigate to project and activate environment
cd ObesiTrack-APP/ObesiTrack
source venv/bin/activate  # or .\.venv\Scripts\Activate.ps1 on Windows

# 2. Pull latest changes
git pull origin main

# 3. Update dependencies if needed
pip install -r requirements.txt

# 4. Start development server
uvicorn main:app --reload --port 8000
```

---

## 💻 Development Workflow

### Feature Development Process

#### 1. Planning Phase
```bash
# Create feature branch
git checkout -b feature/obesity-prediction-enhancement

# Document the feature requirements
# - What problem does it solve?
# - What are the acceptance criteria?
# - What APIs/endpoints are needed?
```

#### 2. Implementation Phase

**Backend Development:**
```bash
# Structure your changes:
# 1. Update/create database models (app/models/)
# 2. Create/update API schemas (app/schemas/)
# 3. Implement business logic (app/routers/)
# 4. Add authentication if needed (app/auth/)
# 5. Update ML components if needed (app/ml/)
```

**Frontend Development:**
```bash
# Update templates and static files:
# 1. HTML templates (templates/)
# 2. CSS styles (app/static/css/)
# 3. JavaScript functionality (app/static/js/)
```

#### 3. Testing Phase
```bash
# Run unit tests
python -m pytest tests/ -v

# Run E2E tests
npx playwright test

# Test specific functionality
npx playwright test tests/e2e/prediction-functionality.spec.ts

# Run tests with coverage
python -m pytest tests/ --cov=app --cov-report=html
```

#### 4. Code Review Phase
```bash
# Check code quality
flake8 app/
black app/  # Format code

# Run all tests
python -m pytest tests/
npx playwright test

# Check for security issues
bandit -r app/

# Create pull request
git push origin feature/obesity-prediction-enhancement
# Open pull request on GitHub
```

### Database Migration Workflow

```bash
# 1. Make changes to models in app/models/
# Example: Add new field to User model

# 2. Create migration script
# If using Alembic:
alembic revision --autogenerate -m "Add profile_picture field to users"

# 3. Review generated migration
cat alembic/versions/xxx_add_profile_picture_field.py

# 4. Apply migration
alembic upgrade head

# 5. Test rollback (in development)
alembic downgrade -1
alembic upgrade head

# 6. Update any affected code
# - API endpoints
# - Schemas
# - Templates
```

### API Development Workflow

#### Adding New Endpoints

**1. Define Schema (app/schemas/)**
```python
# app/schemas/profile.py
from pydantic import BaseModel
from typing import Optional

class ProfileCreate(BaseModel):
    bio: Optional[str] = None
    avatar_url: Optional[str] = None

class ProfileResponse(BaseModel):
    id: int
    bio: Optional[str]
    avatar_url: Optional[str]
    user_id: int
    
    class Config:
        from_attributes = True
```

**2. Update Database Model (app/models/)**
```python
# app/models/user.py
class User(Base):
    # ... existing fields
    bio = Column(String, nullable=True)
    avatar_url = Column(String, nullable=True)
```

**3. Create Router (app/routers/)**
```python
# app/routers/profile.py
from fastapi import APIRouter, Depends
from app.schemas.profile import ProfileCreate, ProfileResponse
from app.auth.dependencies import get_current_user

router = APIRouter()

@router.post("/profile", response_model=ProfileResponse)
async def create_profile(
    profile_data: ProfileCreate,
    current_user = Depends(get_current_user)
):
    # Implementation here
    pass
```

**4. Register Router (main.py)**
```python
from app.routers import profile
app.include_router(profile.router, prefix="/api/profile", tags=["Profile"])
```

**5. Add Tests**
```python
# tests/test_profile.py
def test_create_profile():
    # Test implementation
    pass
```

---

## 🧪 Testing Workflow

### Unit Testing Process

#### 1. Writing Unit Tests
```python
# tests/test_prediction.py
import pytest
from app.ml.predictor import ObesityPredictor

@pytest.fixture
def predictor():
    return ObesityPredictor()

def test_prediction_with_valid_data(predictor):
    """Test prediction with valid input data."""
    test_data = {
        "gender": "male",
        "age": 25,
        "height": 175.0,
        "weight": 70.0,
        # ... other required fields
    }
    
    result = predictor.predict(test_data)
    
    assert "prediction" in result
    assert "confidence" in result
    assert "bmi" in result
    assert 0 <= result["confidence"] <= 1
```

#### 2. Running Tests
```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test file
python -m pytest tests/test_prediction.py -v

# Run tests with coverage
python -m pytest tests/ --cov=app --cov-report=html

# Run tests matching pattern
python -m pytest -k "test_prediction" -v

# Run tests with detailed output
python -m pytest tests/ -v -s
```

### E2E Testing Process

#### 1. Writing E2E Tests
```typescript
// tests/e2e/user-profile.spec.ts
import { test, expect } from '@playwright/test';

test.describe('User Profile Management', () => {
  test.beforeEach(async ({ page }) => {
    // Setup: Login as test user
    await page.goto('/');
    await page.click('[data-testid="login-button"]');
    await page.fill('[name="email"]', 'test@example.com');
    await page.fill('[name="password"]', 'testpassword');
    await page.click('[type="submit"]');
    await expect(page.locator('[data-testid="dashboard"]')).toBeVisible();
  });

  test('should update user profile', async ({ page }) => {
    // Navigate to profile page
    await page.click('[data-testid="profile-link"]');
    
    // Update profile information
    await page.fill('[name="bio"]', 'Updated bio information');
    await page.click('[data-testid="save-profile"]');
    
    // Verify update
    await expect(page.locator('[data-testid="success-message"]')).toBeVisible();
    await expect(page.locator('[name="bio"]')).toHaveValue('Updated bio information');
  });
});
```

#### 2. Running E2E Tests
```bash
# Install browsers (first time only)
npx playwright install

# Run all E2E tests
npx playwright test

# Run tests with UI
npx playwright test --ui

# Run specific test file
npx playwright test tests/e2e/user-profile.spec.ts

# Run tests in headed mode (see browser)
npx playwright test --headed

# Generate and view test report
npx playwright test
npx playwright show-report
```

### Test-Driven Development (TDD) Workflow

#### 1. Red Phase (Write Failing Test)
```python
# tests/test_new_feature.py
def test_calculate_bmi():
    """Test BMI calculation functionality."""
    # This test will fail initially
    from app.utils.health import calculate_bmi
    
    result = calculate_bmi(weight=70, height=175)
    assert result == pytest.approx(22.9, rel=0.1)
```

#### 2. Green Phase (Make Test Pass)
```python
# app/utils/health.py
def calculate_bmi(weight: float, height: float) -> float:
    """Calculate BMI from weight (kg) and height (cm)."""
    height_meters = height / 100
    return weight / (height_meters ** 2)
```

#### 3. Refactor Phase (Improve Code)
```python
# app/utils/health.py
from typing import Union

def calculate_bmi(weight: Union[int, float], height: Union[int, float]) -> float:
    """
    Calculate Body Mass Index (BMI).
    
    Args:
        weight: Weight in kilograms
        height: Height in centimeters
        
    Returns:
        BMI value rounded to 1 decimal place
        
    Raises:
        ValueError: If weight or height are invalid
    """
    if weight <= 0 or height <= 0:
        raise ValueError("Weight and height must be positive values")
    
    height_meters = height / 100
    bmi = weight / (height_meters ** 2)
    return round(bmi, 1)
```

---

## 🚢 Deployment Workflow

### Local Development Deployment

#### 1. Development Environment Setup
```bash
# Create .env for development
DEBUG=True
DATABASE_URL=sqlite:///./obesity_tracker.db
SECRET_KEY=development-secret-key-not-for-production

# Start development server
uvicorn main:app --reload --port 8000 --host 127.0.0.1
```

#### 2. Testing Environment Setup
```bash
# Create .env.testing
DEBUG=False
DATABASE_URL=sqlite:///./test_obesity_tracker.db
SECRET_KEY=testing-secret-key

# Run tests with testing environment
DATABASE_URL=sqlite:///./test_obesity_tracker.db python -m pytest tests/
```

### Docker Development Workflow

#### 1. Docker Development Setup
```bash
# Build development image
docker build -t obesitrack:dev .

# Run with development settings
docker run -d \
  --name obesitrack-dev \
  -p 8000:8000 \
  -v $(pwd):/app \
  -e DEBUG=True \
  obesitrack:dev
```

#### 2. Docker Compose Development
```bash
# Start all services in development mode
docker-compose -f docker-compose.dev.yml up --build

# View logs
docker-compose -f docker-compose.dev.yml logs -f api

# Run tests in container
docker-compose exec api python -m pytest tests/
```

### Production Deployment Workflow

#### 1. Pre-deployment Checklist
```bash
# ✅ All tests passing
python -m pytest tests/
npx playwright test

# ✅ Security scan
bandit -r app/

# ✅ Dependencies updated
pip-audit

# ✅ Environment variables configured
# - SECRET_KEY (strong, unique)
# - DATABASE_URL (production database)
# - DEBUG=False

# ✅ Database migrations applied
alembic upgrade head

# ✅ SSL certificates ready (if applicable)
```

#### 2. Production Deployment Steps

**Using Docker:**
```bash
# 1. Build production image
docker build -t obesitrack:latest .

# 2. Tag for registry
docker tag obesitrack:latest your-registry/obesitrack:latest

# 3. Push to registry
docker push your-registry/obesitrack:latest

# 4. Deploy on production server
docker pull your-registry/obesitrack:latest
docker run -d \
  --name obesitrack-prod \
  -p 8000:8000 \
  --env-file .env.production \
  --restart unless-stopped \
  your-registry/obesitrack:latest
```

**Using systemd:**
```bash
# 1. Deploy code to production server
git clone https://github.com/HAM0909/ObesiTrack-APP.git
cd ObesiTrack-APP/ObesiTrack

# 2. Set up production environment
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env.production
# Edit .env.production with production values

# 4. Set up systemd service
sudo cp deployment/obesitrack.service /etc/systemd/system/
sudo systemctl enable obesitrack
sudo systemctl start obesitrack
```

#### 3. Post-deployment Verification
```bash
# Health check
curl https://your-domain.com/health

# API functionality test
curl -X POST https://your-domain.com/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "testpassword"}'

# Monitor logs
sudo journalctl -u obesitrack -f

# Check performance metrics
curl https://your-domain.com/metrics
```

---

## 👥 User Management Workflow

### Admin User Creation

#### 1. Create First Admin User
```bash
# Method 1: Using demo script (modify create_demo_users.py)
python create_demo_users.py

# Method 2: Direct database insertion
python -c "
from app.database import SessionLocal
from app.models.user import User
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
db = SessionLocal()

admin_user = User(
    username='admin',
    email='admin@yourdomain.com',
    hashed_password=pwd_context.hash('secure_admin_password'),
    is_admin=True
)

db.add(admin_user)
db.commit()
print('Admin user created successfully')
"
```

#### 2. Admin Panel Workflow
```bash
# 1. Login as admin user
# Navigate to: http://localhost:8000/

# 2. Access admin panel
# URL: http://localhost:8000/admin

# 3. Admin capabilities:
# - View all users
# - Delete users
# - View user prediction histories
# - Generate analytics reports
# - Monitor system usage
```

### User Registration Workflow

#### 1. Self-Registration Process
```
User Journey:
1. Visit homepage → Click "Register"
2. Fill registration form (username, email, password)
3. Submit form → Validation checks
4. Account created → Redirect to login
5. Login with new credentials
6. Access main application
```

#### 2. Admin-Managed Registration
```python
# app/routers/admin.py - Admin endpoint for user creation
@router.post("/users", response_model=UserResponse)
async def create_user_as_admin(
    user_data: UserCreate,
    current_admin = Depends(require_admin)
):
    # Create user with admin privileges
    # Send welcome email (optional)
    # Return user details
    pass
```

### User Data Management

#### 1. Data Export Workflow
```python
# app/routers/user.py
@router.get("/export-data")
async def export_user_data(current_user = Depends(get_current_user)):
    """Export all user data for GDPR compliance."""
    return {
        "user_profile": get_user_profile(current_user.id),
        "predictions": get_user_predictions(current_user.id),
        "created_at": current_user.created_at,
        "last_activity": get_last_activity(current_user.id)
    }
```

#### 2. Data Deletion Workflow
```python
# app/routers/user.py
@router.delete("/account")
async def delete_user_account(
    current_user = Depends(get_current_user),
    confirmation: str = Body(...)
):
    """Delete user account and all associated data."""
    if confirmation != "DELETE MY ACCOUNT":
        raise HTTPException(400, "Invalid confirmation")
    
    # Delete user predictions
    # Delete user profile
    # Delete user account
    # Log deletion for audit
    pass
```

---

## 🤖 ML Model Workflow

### Model Training Workflow

#### 1. Data Preparation
```python
# scripts/prepare_training_data.py
import pandas as pd
from app.ml.data_processor import DataProcessor

def prepare_data():
    # Load raw data
    data = pd.read_csv('data/obesity_data.csv')
    
    # Clean and preprocess
    processor = DataProcessor()
    cleaned_data = processor.clean_data(data)
    
    # Feature engineering
    features = processor.engineer_features(cleaned_data)
    
    # Save processed data
    features.to_csv('data/processed_data.csv', index=False)
    print("Data preparation completed")

if __name__ == "__main__":
    prepare_data()
```

#### 2. Model Training Process
```bash
# 1. Prepare training data
python scripts/prepare_training_data.py

# 2. Train models with different algorithms
python scripts/train_model.py --algorithm random_forest
python scripts/train_model.py --algorithm gradient_boosting
python scripts/train_model.py --algorithm svm

# 3. Evaluate models
python scripts/evaluate_models.py

# 4. Select best model
python scripts/select_best_model.py

# 5. Save production model
# Models saved to app/ml/models/
```

#### 3. Model Validation Workflow
```python
# scripts/validate_model.py
from app.ml.predictor import ObesityPredictor
from sklearn.metrics import classification_report
import pandas as pd

def validate_model():
    # Load test data
    test_data = pd.read_csv('data/test_data.csv')
    
    # Initialize predictor
    predictor = ObesityPredictor()
    
    # Make predictions
    predictions = []
    for _, row in test_data.iterrows():
        result = predictor.predict(row.to_dict())
        predictions.append(result['prediction'])
    
    # Evaluate performance
    report = classification_report(test_data['actual'], predictions)
    print("Model Performance Report:")
    print(report)
    
    # Save validation results
    with open('validation_report.txt', 'w') as f:
        f.write(report)

if __name__ == "__main__":
    validate_model()
```

### Model Deployment Workflow

#### 1. Model Update Process
```bash
# 1. Train new model
python scripts/train_model.py

# 2. Validate new model
python scripts/validate_model.py

# 3. Compare with current model
python scripts/compare_models.py --current app/ml/models/model.pkl --new models/new_model.pkl

# 4. If better, backup current model
cp app/ml/models/model.pkl app/ml/models/model_backup.pkl

# 5. Deploy new model
cp models/new_model.pkl app/ml/models/model.pkl
cp models/new_feature_encoder.pkl app/ml/models/feature_encoder.pkl
cp models/new_label_encoder.pkl app/ml/models/label_encoder.pkl

# 6. Restart application
sudo systemctl restart obesitrack

# 7. Test new model
python scripts/test_model_api.py
```

#### 2. Model Rollback Workflow
```bash
# If issues detected with new model:

# 1. Stop application
sudo systemctl stop obesitrack

# 2. Restore backup model
cp app/ml/models/model_backup.pkl app/ml/models/model.pkl

# 3. Restart application
sudo systemctl start obesitrack

# 4. Verify rollback
python scripts/test_model_api.py
```

### Model Monitoring Workflow

#### 1. Performance Monitoring
```python
# app/ml/monitor.py
import logging
from datetime import datetime, timedelta
from app.database import SessionLocal
from app.models.prediction import Prediction

class ModelMonitor:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def check_prediction_drift(self):
        """Check for prediction distribution drift."""
        db = SessionLocal()
        
        # Get recent predictions (last 7 days)
        recent_date = datetime.utcnow() - timedelta(days=7)
        recent_predictions = db.query(Prediction).filter(
            Prediction.created_at >= recent_date
        ).all()
        
        # Analyze distribution
        prediction_counts = {}
        for pred in recent_predictions:
            prediction_counts[pred.prediction] = prediction_counts.get(pred.prediction, 0) + 1
        
        # Log distribution
        self.logger.info(f"Prediction distribution: {prediction_counts}")
        
        # Check for anomalies
        if self._detect_anomaly(prediction_counts):
            self.logger.warning("Prediction drift detected!")
            # Send alert to administrators
            self._send_drift_alert(prediction_counts)
    
    def check_model_accuracy(self):
        """Monitor model accuracy over time."""
        # Implementation for accuracy monitoring
        pass
    
    def _detect_anomaly(self, distribution):
        # Simple anomaly detection logic
        return False
    
    def _send_drift_alert(self, distribution):
        # Send alert to administrators
        pass
```

#### 2. Automated Monitoring Setup
```bash
# Create monitoring script
# scripts/monitor_model.py

# Set up cron job for regular monitoring
crontab -e

# Add line for daily monitoring
0 2 * * * /path/to/venv/bin/python /path/to/scripts/monitor_model.py

# Weekly detailed report
0 9 * * 0 /path/to/venv/bin/python /path/to/scripts/weekly_model_report.py
```

---

## 🔧 Troubleshooting Workflow

### Systematic Debugging Process

#### 1. Issue Identification
```bash
# Step 1: Gather information
# - What is the expected behavior?
# - What is the actual behavior?
# - When did this issue start?
# - What changed recently?

# Step 2: Reproduce the issue
# - Can you consistently reproduce it?
# - What are the exact steps?
# - Does it happen in different environments?

# Step 3: Check logs
tail -f /var/log/obesitrack.log
# or
docker-compose logs -f api

# Step 4: Check system resources
htop
df -h
free -m
```

#### 2. Common Issue Resolution Patterns

**Database Connection Issues:**
```bash
# 1. Check database status
sudo systemctl status postgresql

# 2. Test connection
psql -h localhost -U postgres -d obesittrack

# 3. Check connection string
echo $DATABASE_URL

# 4. Verify credentials
# Check .env file

# 5. Check network connectivity
telnet localhost 5432
```

**Application Not Starting:**
```bash
# 1. Check Python environment
which python
python --version

# 2. Check dependencies
pip check

# 3. Check configuration
python -c "from app.config import settings; print(settings)"

# 4. Check port availability
netstat -tulpn | grep :8000

# 5. Start with debug mode
DEBUG=True uvicorn main:app --reload --log-level debug
```

**ML Model Issues:**
```bash
# 1. Check model files
ls -la app/ml/models/

# 2. Test model loading
python -c "from app.ml.predictor import ObesityPredictor; p = ObesityPredictor()"

# 3. Check model compatibility
python scripts/validate_model_files.py

# 4. Retrain if necessary
python scripts/train_model.py
```

#### 3. Performance Issues Workflow

**Slow Response Times:**
```bash
# 1. Profile the application
pip install py-spy
py-spy record -o profile.svg --pid $(pgrep -f "uvicorn main:app")

# 2. Check database queries
# Enable SQL logging in development
# Add to config.py:
# logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

# 3. Monitor resource usage
htop
iotop

# 4. Check for memory leaks
python -m memory_profiler your_script.py

# 5. Optimize database queries
# Add indexes, use eager loading, etc.
```

**High Memory Usage:**
```bash
# 1. Check memory usage by process
ps aux | grep python | sort -nrk 4

# 2. Profile memory usage
python -m tracemalloc your_script.py

# 3. Check for memory leaks in ML models
# Ensure models are loaded once and reused

# 4. Configure garbage collection
import gc
gc.collect()
```

#### 4. Error Logging and Monitoring

**Set up comprehensive logging:**
```python
# app/logging_config.py
import logging
import sys
from logging.handlers import RotatingFileHandler

def setup_logging():
    # Create logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    
    # File handler with rotation
    file_handler = RotatingFileHandler(
        'logs/obesitrack.log',
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    file_handler.setLevel(logging.INFO)
    
    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)
    
    # Add handlers
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
```

**Error tracking workflow:**
```bash
# 1. Set up error tracking
# Options: Sentry, Rollbar, or custom solution

# 2. Monitor error rates
grep -c "ERROR" /var/log/obesitrack.log

# 3. Analyze error patterns
grep "ERROR" /var/log/obesitrack.log | awk '{print $4}' | sort | uniq -c

# 4. Set up alerts for critical errors
# Use monitoring tools or scripts
```

### Recovery Procedures

#### 1. Database Recovery
```bash
# 1. Stop application
sudo systemctl stop obesitrack

# 2. Backup current state
pg_dump obesittrack > backup_$(date +%Y%m%d_%H%M%S).sql

# 3. Restore from backup (if needed)
dropdb obesittrack
createdb obesittrack
psql obesittrack < backup_20240101_120000.sql

# 4. Restart application
sudo systemctl start obesitrack
```

#### 2. Application Recovery
```bash
# 1. Check system status
sudo systemctl status obesitrack

# 2. Restart application
sudo systemctl restart obesitrack

# 3. If restart fails, check logs
sudo journalctl -u obesitrack -f

# 4. Manual startup (for debugging)
cd /path/to/app
source venv/bin/activate
uvicorn main:app --host 0.0.0.0 --port 8000

# 5. Verify recovery
curl http://localhost:8000/health
```

---

## 📊 Workflow Summary

This workflow guide covers the complete development and operational lifecycle of ObesiTrack:

1. **Quick Start**: Get up and running quickly
2. **Development**: Feature development and code organization
3. **Testing**: Comprehensive testing strategies
4. **Deployment**: From development to production
5. **User Management**: Admin and user workflows
6. **ML Model**: Training, deployment, and monitoring
7. **Troubleshooting**: Systematic problem resolution

Each workflow includes:
- ✅ Step-by-step instructions
- 🔧 Code examples and commands
- 📋 Checklists for quality assurance
- 🚨 Error handling procedures
- 📈 Monitoring and optimization tips

For additional support, refer to the main [DOCUMENTATION.md](./DOCUMENTATION.md) file or the [GitHub repository](https://github.com/HAM0909/ObesiTrack-APP).