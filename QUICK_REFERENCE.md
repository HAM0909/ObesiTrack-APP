# 🚀 ObesiTrack - Quick Reference Guide

## 📋 Table of Contents

1. [Quick Start Commands](#quick-start-commands)
2. [Environment Variables](#environment-variables)
3. [API Endpoints](#api-endpoints)
4. [Database Operations](#database-operations)
5. [Testing Commands](#testing-commands)
6. [Docker Commands](#docker-commands)
7. [Troubleshooting](#troubleshooting)
8. [ML Model Reference](#ml-model-reference)

---

## ⚡ Quick Start Commands

### Local Development

```bash
# Setup
git clone https://github.com/HAM0909/ObesiTrack-APP.git
cd ObesiTrack-APP/ObesiTrack
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt && npm install
cp .env.example .env

# Database
python scripts/init_db.py

# Start server
uvicorn main:app --reload --port 8000

# Create demo users
python create_demo_users.py
```

### Docker (Recommended)

```bash
# Development
docker-compose up --build

# Production
docker-compose -f docker-compose.prod.yml up -d

# Logs
docker-compose logs -f
```

---

## 🔧 Environment Variables

### Required Variables

```bash
# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/obesittrack

# Security
SECRET_KEY=your-super-secure-32-character-key-here
```

### Optional Variables

```bash
# Application
DEBUG=False
ENVIRONMENT=production
ALLOWED_HOSTS=localhost,127.0.0.1

# JWT
ACCESS_TOKEN_EXPIRE_MINUTES=30
ALGORITHM=HS256

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:8000
```

---

## 🌐 API Endpoints

### Authentication

```bash
# Register
POST /api/auth/register
Content-Type: application/json
{
  "email": "user@example.com",
  "username": "user123",
  "password": "securepass123"
}

# Login
POST /api/auth/login
Content-Type: application/json
{
  "email": "user@example.com",
  "password": "securepass123"
}

# Get current user
GET /api/auth/me
Authorization: Bearer <token>
```

### Predictions

```bash
# Make prediction
POST /api/prediction/predict
Authorization: Bearer <token>
Content-Type: application/json
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

# Get history
GET /api/prediction/history?limit=10
Authorization: Bearer <token>

# Get specific prediction
GET /api/prediction/{prediction_id}
Authorization: Bearer <token>
```

### Admin (Admin users only)

```bash
# Get all users
GET /api/admin/users?page=1&size=50
Authorization: Bearer <admin_token>

# Delete user
DELETE /api/admin/users/{user_id}
Authorization: Bearer <admin_token>

# Get analytics
GET /api/admin/analytics
Authorization: Bearer <admin_token>
```

### Health & Monitoring

```bash
# Health check
GET /health

# User analytics
GET /api/analytics/overview
Authorization: Bearer <token>
```

---

## 🗄️ Database Operations

### Manual Database Setup

```bash
# PostgreSQL
sudo -u postgres createdb obesittrack
sudo -u postgres createuser -P obesittrack_user

# Initialize tables
python scripts/init_db.py

# Backup
pg_dump obesittrack > backup.sql

# Restore
psql obesittrack < backup.sql
```

### SQLAlchemy Commands

```python
# In Python shell
from app.core.database import SessionLocal, engine
from app.models import user, prediction

# Create all tables
user.Base.metadata.create_all(bind=engine)

# Get session
db = SessionLocal()

# Query examples
users = db.query(user.User).all()
predictions = db.query(prediction.Prediction).limit(10).all()
```

---

## 🧪 Testing Commands

### Unit Tests

```bash
# All tests
python -m pytest tests/ -v

# Specific test file
python -m pytest tests/unit/test_auth.py -v

# With coverage
python -m pytest tests/ --cov=app --cov-report=html
```

### E2E Tests

```bash
# All E2E tests
npm test

# Specific test
npx playwright test tests/e2e/test_auth.spec.ts

# Debug mode
npx playwright test --debug

# UI mode
npx playwright test --ui

# Generate report
npx playwright show-report
```

### Manual API Testing

```bash
# Health check
curl http://localhost:8000/health

# Register user
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","username":"test","password":"test123"}'

# Login
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","password":"test123"}'

# Make prediction (replace TOKEN)
curl -X POST http://localhost:8000/api/prediction/predict \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"gender":"male","age":25,"height":170,"weight":70,"family_history_with_overweight":"yes","favc":"yes","fcvc":2,"ncp":3,"caec":"Sometimes","smoke":"no","ch2o":2,"scc":"no","faf":1,"tue":1,"calc":"Sometimes","mtrans":"Public_Transportation"}'
```

---

## 🐳 Docker Commands

### Development

```bash
# Build and start
docker-compose up --build

# Start in background
docker-compose up -d

# Stop
docker-compose down

# View logs
docker-compose logs -f api

# Execute commands in container
docker-compose exec api python scripts/init_db.py
```

### Production

```bash
# Build production image
docker build -f Dockerfile.prod -t obesitrack:latest .

# Start production stack
docker-compose -f docker-compose.prod.yml up -d

# Check container status
docker ps

# View container logs
docker logs obesitrack-api
```

### Container Management

```bash
# Remove all containers
docker-compose down --volumes --remove-orphans

# Clean up images
docker image prune -f

# Shell into container
docker-compose exec api /bin/bash

# Database shell
docker-compose exec db psql -U obesittrack_user -d obesittrack
```

---

## 🔧 Troubleshooting

### Common Issues & Solutions

| Issue | Command | Solution |
|-------|---------|----------|
| **Server won't start** | `lsof -i :8000` | Kill process: `kill -9 <PID>` |
| **Database connection** | `pg_isready` | Check PostgreSQL: `sudo systemctl status postgresql` |
| **Module not found** | `pip list` | Install: `pip install -r requirements.txt` |
| **Tests failing** | `curl localhost:8000/health` | Ensure server is running |
| **Docker build fails** | `docker system prune` | Clean Docker cache |

### Log Locations

```bash
# Application logs
tail -f logs/app.log

# Database logs
sudo tail -f /var/log/postgresql/postgresql-13-main.log

# Nginx logs (if using)
sudo tail -f /var/log/nginx/error.log

# Docker logs
docker-compose logs -f
```

### Health Checks

```bash
# Application health
curl -f http://localhost:8000/health || echo "API Down"

# Database health
psql -h localhost -U obesittrack_user -d obesittrack -c "SELECT 1;" || echo "DB Down"

# Memory usage
free -h

# Disk space
df -h

# Process status
ps aux | grep uvicorn
```

---

## 🤖 ML Model Reference

### Input Features (16 total)

| Feature | Type | Values | Description |
|---------|------|--------|-------------|
| `gender` | str | `"male"`, `"female"` | User's gender |
| `age` | int | `16-61` | Age in years |
| `height` | float | `145.0-198.0` | Height in cm |
| `weight` | float | `39.0-173.0` | Weight in kg |
| `family_history_with_overweight` | str | `"yes"`, `"no"` | Family obesity history |
| `favc` | str | `"yes"`, `"no"` | Frequent high-calorie consumption |
| `fcvc` | float | `1.0-3.0` | Vegetable consumption frequency |
| `ncp` | float | `1.0-4.0` | Number of main meals |
| `caec` | str | `"Always"`, `"Frequently"`, `"Sometimes"`, `"no"` | Between-meal eating |
| `smoke` | str | `"yes"`, `"no"` | Smoking habit |
| `ch2o` | float | `1.0-3.0` | Water consumption (liters) |
| `scc` | str | `"yes"`, `"no"` | Calorie consumption monitoring |
| `faf` | float | `0.0-3.0` | Physical activity frequency |
| `tue` | float | `0.0-2.0` | Technology usage time |
| `calc` | str | `"Always"`, `"Frequently"`, `"Sometimes"`, `"no"` | Alcohol consumption |
| `mtrans` | str | `"Automobile"`, `"Bike"`, `"Motorbike"`, `"Public_Transportation"`, `"Walking"` | Transportation mode |

### Output Classes (7 total)

1. **Insufficient_Weight** - BMI < 18.5
2. **Normal_Weight** - BMI 18.5-24.9
3. **Overweight_Level_I** - BMI 25.0-29.9
4. **Overweight_Level_II** - BMI 30.0-34.9
5. **Obesity_Type_I** - BMI 35.0-39.9
6. **Obesity_Type_II** - BMI 40.0-44.9
7. **Obesity_Type_III** - BMI ≥ 45.0

### Example Prediction Request

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

### Example Response

```json
{
  "prediction": "Normal_Weight",
  "confidence": 0.85,
  "bmi": 24.2,
  "risk_level": "Low",
  "recommendations": [
    "Maintain current healthy weight",
    "Continue regular physical activity",
    "Monitor eating habits"
  ],
  "prediction_id": "123e4567-e89b-12d3-a456-426614174000"
}
```

---

## 🔗 Useful URLs

### Local Development
- **Application**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Admin Panel**: http://localhost:8000/admin
- **Health Check**: http://localhost:8000/health

### File Locations
- **Config**: `.env`
- **Logs**: `logs/`
- **Tests**: `tests/`
- **Database**: `app/models/`
- **API Routes**: `app/api/`

### Commands Aliases

```bash
# Add to ~/.bashrc or ~/.zshrc
alias ot-start="uvicorn main:app --reload --port 8000"
alias ot-test="python -m pytest tests/ -v"
alias ot-e2e="npm test"
alias ot-docker="docker-compose up --build"
alias ot-logs="tail -f logs/app.log"
alias ot-db="python scripts/init_db.py"
alias ot-demo="python create_demo_users.py"
```

---

## 📞 Quick Support

### Before Asking for Help

1. Check this quick reference
2. Review logs: `tail -f logs/app.log`
3. Verify server status: `curl localhost:8000/health`
4. Check database: `psql -h localhost -U obesittrack_user -d obesittrack -c "SELECT 1;"`
5. Confirm environment: `cat .env`

### Get Help

- **GitHub Issues**: [Submit Issue](https://github.com/HAM0909/ObesiTrack-APP/issues)
- **Documentation**: [Full Documentation](./DOCUMENTATION.md)
- **API Reference**: [API Docs](./API_REFERENCE.md)

---

**Last Updated**: October 2025 | **Version**: 1.0.0

*Keep this reference handy for quick lookups during development and deployment!*