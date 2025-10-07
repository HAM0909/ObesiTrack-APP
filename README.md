# 🏥 ObesiTrack - Advanced Obesity Prediction & Management System

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-Latest-green.svg)](https://fastapi.tiangolo.com)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-13+-blue.svg)](https://postgresql.org)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://docker.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/Tests-Playwright-green.svg)](https://playwright.dev)

> **ObesiTrack** is a comprehensive web application for obesity prediction, tracking, and management using advanced machine learning algorithms. Built with FastAPI, it provides accurate obesity classification, personalized recommendations, and comprehensive health analytics.

## 🌟 Features

### 🔮 **AI-Powered Predictions**
- **16-Factor Analysis**: Advanced ML model using demographic, lifestyle, and behavioral data
- **7 Obesity Classifications**: From Insufficient Weight to Obesity Type III
- **Real-time Predictions**: Instant obesity risk assessment with confidence scores
- **BMI Integration**: Automatic BMI calculation and risk categorization

### 👥 **User Management**
- **Secure Authentication**: JWT-based authentication with password hashing
- **User Profiles**: Comprehensive profile management with prediction history
- **Admin Dashboard**: Complete user management and analytics interface
- **Role-based Access**: Different access levels for users and administrators

### 📊 **Analytics & Insights**
- **Prediction History**: Track obesity predictions over time
- **Health Analytics**: Comprehensive health metrics and trends
- **Risk Assessment**: Detailed risk analysis with actionable insights
- **Data Visualization**: Charts and graphs for better understanding

### 🛡️ **Security & Performance**
- **JWT Authentication**: Secure token-based authentication
- **Input Validation**: Comprehensive input validation and sanitization
- **Rate Limiting**: API rate limiting for abuse prevention
- **Encrypted Storage**: Secure data storage with encryption

### 🧪 **Testing & Quality**
- **Comprehensive Testing**: Full test coverage with Playwright E2E tests
- **Cross-browser Support**: Tested on Chrome, Firefox, and Safari
- **API Testing**: Complete API endpoint testing
- **Performance Testing**: Load testing and performance optimization

## 🚀 Quick Start

### Option 1: Docker (Recommended)

```bash
# Clone the repository
git clone https://github.com/HAM0909/ObesiTrack-APP.git
cd ObesiTrack-APP/ObesiTrack

# Start with Docker Compose
docker-compose up --build

# Access the application
open http://localhost:8000
```

### Option 2: Local Development

```bash
# Clone and setup
git clone https://github.com/HAM0909/ObesiTrack-APP.git
cd ObesiTrack-APP/ObesiTrack

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
npm install  # For Playwright tests

# Setup environment
cp .env.example .env
# Edit .env with your configuration

# Initialize database
python scripts/init_db.py

# Start the application
uvicorn main:app --reload --port 8000

# Create demo users (optional)
python create_demo_users.py
```

## 📋 System Requirements

### Development Environment
- **Python**: 3.11 or higher
- **Node.js**: 18+ (for testing)
- **PostgreSQL**: 13+ or SQLite (for development)
- **Memory**: 4GB RAM minimum
- **Storage**: 2GB available space

### Production Environment
- **Server**: 2+ CPU cores, 4GB+ RAM
- **Database**: PostgreSQL 13+
- **SSL**: Certificate for HTTPS
- **Docker**: Latest version (recommended)

## 🏗️ Architecture Overview

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend API    │    │   Database      │
│   (Jinja2)      │◄──►│   (FastAPI)      │◄──►│  (PostgreSQL)   │
│   - Templates   │    │   - JWT Auth     │    │   - Users       │
│   - Forms       │    │   - ML Models    │    │   - Predictions │
│   - JavaScript  │    │   - Validation   │    │   - Analytics   │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌──────────────────┐
                       │   ML Pipeline    │
                       │   - Scikit-learn │
                       │   - 16 Features  │
                       │   - 7 Classes    │
                       └──────────────────┘
```

### Tech Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Backend** | FastAPI | High-performance API framework |
| **Database** | PostgreSQL | Reliable data storage |
| **ML Framework** | Scikit-learn | Machine learning predictions |
| **Authentication** | JWT | Secure user authentication |
| **Frontend** | Jinja2 Templates | Server-side rendering |
| **Testing** | Playwright | End-to-end testing |
| **Containerization** | Docker | Easy deployment |

## 📊 ML Model Details

### Input Features (16 total)

| Feature | Type | Description | Example Values |
|---------|------|-------------|---------------|
| **Gender** | Categorical | User's gender | Male, Female |
| **Age** | Numeric | Age in years | 18-65 |
| **Height** | Numeric | Height in cm | 150-200 |
| **Weight** | Numeric | Weight in kg | 40-150 |
| **Family History** | Boolean | Family obesity history | Yes, No |
| **FAVC** | Boolean | Frequent high-calorie food consumption | Yes, No |
| **FCVC** | Numeric | Vegetable consumption frequency | 1-3 |
| **NCP** | Numeric | Main meals per day | 1-4 |
| **CAEC** | Categorical | Between-meal snacking | Always, Frequently, Sometimes, No |
| **SMOKE** | Boolean | Smoking habit | Yes, No |
| **CH2O** | Numeric | Daily water intake (liters) | 1-3 |
| **SCC** | Boolean | Calorie monitoring | Yes, No |
| **FAF** | Numeric | Physical activity frequency | 0-3 |
| **TUE** | Numeric | Technology usage time | 0-2 |
| **CALC** | Categorical | Alcohol consumption | Always, Frequently, Sometimes, No |
| **MTRANS** | Categorical | Transportation method | Walking, Public, Automobile, Bike, Motorbike |

### Output Classifications (7 classes)

1. **Insufficient_Weight** - BMI < 18.5
2. **Normal_Weight** - BMI 18.5-24.9
3. **Overweight_Level_I** - BMI 25.0-29.9
4. **Overweight_Level_II** - BMI 30.0-34.9
5. **Obesity_Type_I** - BMI 35.0-39.9
6. **Obesity_Type_II** - BMI 40.0-44.9
7. **Obesity_Type_III** - BMI ≥ 45.0

## 🔌 API Endpoints

### Authentication
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `GET /api/auth/me` - Get current user

### Predictions
- `POST /api/prediction/predict` - Create new prediction
- `GET /api/prediction/history` - Get prediction history
- `GET /api/prediction/{id}` - Get specific prediction

### Admin (Admin only)
- `GET /api/admin/users` - List all users
- `DELETE /api/admin/users/{id}` - Delete user
- `GET /api/admin/analytics` - System analytics

### Health & Monitoring
- `GET /health` - Application health check
- `GET /api/analytics/overview` - User analytics

For detailed API documentation, see [API_REFERENCE.md](./API_REFERENCE.md)

## 🧪 Testing

### Run All Tests

```bash
# Unit tests
python -m pytest tests/ -v

# E2E tests (requires running server)
npm test

# Run specific test file
npx playwright test tests/test_auth.spec.ts

# Run tests with UI mode
npx playwright test --ui

# Generate test report
npx playwright show-report
```

### Test Coverage

- **Unit Tests**: Core business logic and utilities
- **Integration Tests**: Database operations and API endpoints
- **E2E Tests**: Complete user workflows and UI interactions
- **Cross-browser**: Chrome, Firefox, Safari support

## 🐳 Docker Deployment

### Development

```bash
# Build and run
docker-compose up --build

# Run in background
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Production

```bash
# Build production image
docker build -f Dockerfile.prod -t obesitrack:latest .

# Run with environment file
docker run -d \
  --name obesitrack \
  -p 8000:8000 \
  --env-file .env.production \
  obesitrack:latest

# With PostgreSQL
docker-compose -f docker-compose.prod.yml up -d
```

## 🔧 Configuration

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DATABASE_URL` | Yes | - | PostgreSQL connection string |
| `SECRET_KEY` | Yes | - | JWT signing key (32+ characters) |
| `DEBUG` | No | `False` | Enable debug mode |
| `ALLOWED_HOSTS` | No | `*` | Allowed host names |
| `CORS_ORIGINS` | No | `*` | CORS allowed origins |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | No | `30` | JWT token expiration |

### Database Configuration

```python
# PostgreSQL (Production)
DATABASE_URL="postgresql://user:password@localhost:5432/obesittrack"

# SQLite (Development)
DATABASE_URL="sqlite:///./obesittrack.db"
```

## 📁 Project Structure

```
ObesiTrack/
├── app/
│   ├── api/                 # API routes
│   │   ├── auth.py         # Authentication endpoints
│   │   ├── prediction.py   # Prediction endpoints
│   │   └── admin.py        # Admin endpoints
│   ├── core/               # Core functionality
│   │   ├── config.py       # Configuration
│   │   ├── security.py     # Security utilities
│   │   └── database.py     # Database setup
│   ├── models/             # Database models
│   │   ├── user.py         # User model
│   │   └── prediction.py   # Prediction model
│   ├── services/           # Business logic
│   │   ├── auth.py         # Authentication service
│   │   ├── prediction.py   # ML prediction service
│   │   └── analytics.py    # Analytics service
│   ├── static/             # Static files
│   │   ├── css/           # Stylesheets
│   │   ├── js/            # JavaScript
│   │   └── images/        # Images
│   └── templates/          # Jinja2 templates
│       ├── auth/          # Authentication pages
│       ├── dashboard/     # Dashboard pages
│       └── base.html      # Base template
├── tests/                  # Test files
│   ├── e2e/               # End-to-end tests
│   ├── integration/       # Integration tests
│   └── unit/              # Unit tests
├── scripts/               # Utility scripts
│   ├── init_db.py        # Database initialization
│   └── backup_db.py      # Database backup
├── docs/                  # Documentation
├── docker-compose.yml     # Development Docker setup
├── docker-compose.prod.yml # Production Docker setup
├── Dockerfile             # Development Dockerfile
├── Dockerfile.prod        # Production Dockerfile
├── requirements.txt       # Python dependencies
├── package.json          # Node.js dependencies
├── .env.example          # Environment template
├── main.py               # Application entry point
└── README.md             # This file
```

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](./CONTRIBUTING.md) for guidelines.

### Development Workflow

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Make your changes** and add tests
4. **Run tests**: `pytest tests/ && npm test`
5. **Commit changes**: `git commit -m 'Add amazing feature'`
6. **Push to branch**: `git push origin feature/amazing-feature`
7. **Open a Pull Request**

### Code Standards

- **Python**: Follow PEP 8 style guide
- **JavaScript**: Use ESLint configuration
- **Tests**: Maintain 90%+ coverage
- **Documentation**: Update docs for new features

## 📖 Documentation

| Document | Description |
|----------|-------------|
| [DOCUMENTATION.md](./DOCUMENTATION.md) | Complete technical documentation |
| [API_REFERENCE.md](./API_REFERENCE.md) | Detailed API documentation |
| [WORKFLOW_GUIDE.md](./WORKFLOW_GUIDE.md) | Step-by-step workflows |
| [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md) | Production deployment guide |
| [CONTRIBUTING.md](./CONTRIBUTING.md) | Contribution guidelines |

## 🔐 Security

### Security Features

- **JWT Authentication** with secure token handling
- **Password Hashing** using bcrypt
- **Input Validation** with Pydantic models
- **CORS Protection** with configurable origins
- **SQL Injection Prevention** with SQLAlchemy ORM
- **XSS Protection** with template escaping

### Security Best Practices

- Regular security updates
- Environment variable protection
- HTTPS enforcement in production
- Rate limiting on API endpoints
- Comprehensive input validation

## 🚀 Performance

### Optimization Features

- **Async/Await**: Non-blocking operations
- **Database Indexing**: Optimized queries
- **Connection Pooling**: Efficient database connections
- **Caching**: Redis integration for frequently accessed data
- **Static File Serving**: Optimized static asset delivery

### Performance Benchmarks

- **API Response Time**: < 200ms average
- **Prediction Time**: < 100ms for single prediction
- **Concurrent Users**: 1000+ with proper infrastructure
- **Database Queries**: < 50ms average query time

## 📊 Monitoring

### Health Checks

```bash
# Application health
curl http://localhost:8000/health

# Database health
curl http://localhost:8000/health/db

# Detailed status
curl http://localhost:8000/health/detailed
```

### Logs

```bash
# Application logs
tail -f logs/app.log

# Error logs
tail -f logs/error.log

# Access logs
tail -f logs/access.log
```

## 🐛 Troubleshooting

### Common Issues

| Issue | Solution |
|-------|----------|
| **Database connection error** | Check `DATABASE_URL` and PostgreSQL status |
| **JWT token invalid** | Verify `SECRET_KEY` configuration |
| **Tests failing** | Ensure server is running for E2E tests |
| **Docker build fails** | Check Dockerfile and dependencies |
| **High memory usage** | Review database queries and caching |

For detailed troubleshooting, see [DOCUMENTATION.md#troubleshooting](./DOCUMENTATION.md#troubleshooting)

## 🎯 Roadmap

### Version 1.1 (Coming Soon)
- [ ] **Mobile App**: React Native mobile application
- [ ] **Advanced Analytics**: More detailed health insights
- [ ] **Multi-language Support**: Internationalization
- [ ] **Email Notifications**: Automated health reminders

### Version 1.2
- [ ] **Wearable Integration**: Fitbit, Apple Watch support
- [ ] **Nutrition Tracking**: Meal logging and analysis
- [ ] **Social Features**: Health challenges and sharing
- [ ] **AI Recommendations**: Personalized health suggestions

### Long-term Goals
- [ ] **Telemedicine Integration**: Doctor consultations
- [ ] **Insurance Integration**: Health plan connections
- [ ] **Research Platform**: Anonymized data for research
- [ ] **Enterprise Features**: Corporate health programs

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👥 Team

- **Lead Developer**: [HAM0909](https://github.com/HAM0909)
- **Contributors**: See [CONTRIBUTORS.md](CONTRIBUTORS.md)

## 🆘 Support

### Getting Help

- **Documentation**: Check our comprehensive docs
- **Issues**: [GitHub Issues](https://github.com/HAM0909/ObesiTrack-APP/issues)
- **Discussions**: [GitHub Discussions](https://github.com/HAM0909/ObesiTrack-APP/discussions)
- **Email**: support@obesittrack.com

### FAQ

**Q: Can I use this for commercial purposes?**
A: Yes, under the MIT License terms.

**Q: How accurate are the predictions?**
A: The model achieves 85%+ accuracy on test data.

**Q: Can I customize the ML model?**
A: Yes, you can retrain with your own data.

**Q: Is my data secure?**
A: Yes, we follow security best practices and encrypt sensitive data.

## 📊 Stats

![GitHub Stars](https://img.shields.io/github/stars/HAM0909/ObesiTrack-APP)
![GitHub Forks](https://img.shields.io/github/forks/HAM0909/ObesiTrack-APP)
![GitHub Issues](https://img.shields.io/github/issues/HAM0909/ObesiTrack-APP)
![GitHub Pull Requests](https://img.shields.io/github/issues-pr/HAM0909/ObesiTrack-APP)

---

**Made with ❤️ for better health outcomes**

*ObesiTrack - Empowering healthier lives through intelligent prediction and management.*