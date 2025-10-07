# 🤝 Contributing to ObesiTrack

Thank you for considering contributing to ObesiTrack! We welcome contributions from everyone and appreciate your help in making this project better.

## 📋 Table of Contents

1. [Code of Conduct](#code-of-conduct)
2. [Getting Started](#getting-started)
3. [Development Setup](#development-setup)
4. [Contribution Workflow](#contribution-workflow)
5. [Coding Standards](#coding-standards)
6. [Testing Requirements](#testing-requirements)
7. [Documentation Guidelines](#documentation-guidelines)
8. [Pull Request Process](#pull-request-process)
9. [Issue Reporting](#issue-reporting)
10. [Security Vulnerabilities](#security-vulnerabilities)

---

## 🤝 Code of Conduct

### Our Pledge

We are committed to making participation in our project a harassment-free experience for everyone, regardless of age, body size, disability, ethnicity, sex characteristics, gender identity and expression, level of experience, education, socio-economic status, nationality, personal appearance, race, religion, or sexual identity and orientation.

### Our Standards

**Examples of behavior that contributes to creating a positive environment include:**

- Using welcoming and inclusive language
- Being respectful of differing viewpoints and experiences
- Gracefully accepting constructive criticism
- Focusing on what is best for the community
- Showing empathy towards other community members

**Examples of unacceptable behavior include:**

- The use of sexualized language or imagery
- Trolling, insulting/derogatory comments, and personal or political attacks
- Public or private harassment
- Publishing others' private information without explicit permission
- Other conduct which could reasonably be considered inappropriate

### Enforcement

Project maintainers are responsible for clarifying the standards of acceptable behavior and will take appropriate and fair corrective action in response to any instances of unacceptable behavior.

---

## 🚀 Getting Started

### Ways to Contribute

- **Bug Reports**: Help us identify and fix bugs
- **Feature Requests**: Suggest new features or improvements
- **Code Contributions**: Submit bug fixes or new features
- **Documentation**: Improve or add documentation
- **Testing**: Add or improve test coverage
- **Design**: Improve UI/UX design
- **Performance**: Optimize code and queries

### Before You Start

1. **Check existing issues** to avoid duplicate work
2. **Join discussions** on relevant issues or features
3. **Ask questions** if anything is unclear
4. **Start small** with your first contribution

---

## 🛠️ Development Setup

### Prerequisites

- **Python**: 3.11 or higher
- **Node.js**: 18+ (for Playwright tests)
- **PostgreSQL**: 13+ (or SQLite for local development)
- **Git**: Latest version
- **Docker**: Latest version (optional but recommended)

### Initial Setup

```bash
# 1. Fork the repository on GitHub
# 2. Clone your fork
git clone https://github.com/YOUR-USERNAME/ObesiTrack-APP.git
cd ObesiTrack-APP/ObesiTrack

# 3. Add upstream remote
git remote add upstream https://github.com/HAM0909/ObesiTrack-APP.git

# 4. Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 5. Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt  # Development dependencies
npm install  # For Playwright tests

# 6. Copy environment template
cp .env.example .env
# Edit .env with your local configuration

# 7. Initialize database
python scripts/init_db.py

# 8. Create demo users (optional)
python create_demo_users.py

# 9. Start the development server
uvicorn main:app --reload --port 8000

# 10. Verify setup
curl http://localhost:8000/health
```

### Development Dependencies

Create `requirements-dev.txt` if it doesn't exist:

```txt
# Testing
pytest>=7.4.0
pytest-asyncio>=0.21.0
pytest-cov>=4.1.0
httpx>=0.24.0
fakeredis>=2.18.0

# Code Quality
black>=23.0.0
isort>=5.12.0
flake8>=6.0.0
mypy>=1.5.0
pre-commit>=3.3.0

# Documentation
mkdocs>=1.5.0
mkdocs-material>=9.2.0

# Development
watchdog>=3.0.0
python-dotenv>=1.0.0
```

### Pre-commit Hooks

```bash
# Install pre-commit hooks
pip install pre-commit
pre-commit install

# Run hooks manually
pre-commit run --all-files
```

Create `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files

  - repo: https://github.com/psf/black
    rev: 23.7.0
    hooks:
      - id: black

  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort

  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8
```

---

## 🔄 Contribution Workflow

### 1. Choose an Issue

- Browse [open issues](https://github.com/HAM0909/ObesiTrack-APP/issues)
- Look for issues labeled `good first issue` or `help wanted`
- Comment on the issue to indicate you're working on it

### 2. Create a Branch

```bash
# Update your main branch
git checkout main
git pull upstream main

# Create a new branch
git checkout -b feature/your-feature-name
# or
git checkout -b fix/bug-description
```

### Branch Naming Convention

- **Features**: `feature/feature-name`
- **Bug fixes**: `fix/bug-description`
- **Documentation**: `docs/doc-improvement`
- **Tests**: `test/test-improvement`
- **Refactoring**: `refactor/component-name`

### 3. Make Changes

- Write clear, focused commits
- Follow coding standards
- Add or update tests
- Update documentation if needed

### 4. Test Your Changes

```bash
# Run unit tests
python -m pytest tests/ -v

# Run specific test
python -m pytest tests/unit/test_auth.py -v

# Check test coverage
python -m pytest tests/ --cov=app --cov-report=html

# Run E2E tests (ensure server is running)
npm test

# Code quality checks
black app/ tests/
isort app/ tests/
flake8 app/ tests/
mypy app/
```

### 5. Commit Changes

```bash
# Stage changes
git add .

# Commit with descriptive message
git commit -m "feat: add user profile validation

- Add Pydantic model for user profile validation
- Implement email format validation
- Add age range validation (16-100)
- Update tests for new validation rules

Fixes #123"
```

### Commit Message Format

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `test`: Adding or fixing tests
- `refactor`: Code refactoring
- `perf`: Performance improvements
- `chore`: Maintenance tasks

**Examples:**
```
feat(auth): add password strength validation
fix(prediction): handle edge case for BMI calculation
docs(api): update authentication endpoint examples
test(e2e): add user registration flow tests
```

### 6. Push Changes

```bash
# Push to your fork
git push origin feature/your-feature-name
```

### 7. Create Pull Request

- Go to your fork on GitHub
- Click "New Pull Request"
- Fill out the PR template completely
- Link to related issues

---

## 📏 Coding Standards

### Python Code Style

We follow **PEP 8** with some project-specific conventions:

#### Formatting
```python
# Use Black formatter (line length: 88)
black app/ tests/

# Import sorting with isort
isort app/ tests/
```

#### Code Structure
```python
"""Module docstring describing purpose."""

import os
import sys
from typing import List, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from app.core.config import settings
from app.models.user import User


class UserCreate(BaseModel):
    """User creation model."""
    
    email: str
    username: str
    password: str
    
    class Config:
        """Pydantic config."""
        schema_extra = {
            "example": {
                "email": "user@example.com",
                "username": "johndoe",
                "password": "securepassword123"
            }
        }


async def create_user(user_data: UserCreate) -> User:
    """
    Create a new user.
    
    Args:
        user_data: User creation data
        
    Returns:
        Created user instance
        
    Raises:
        HTTPException: If user already exists
    """
    # Implementation here
    pass
```

#### Naming Conventions
- **Variables/Functions**: `snake_case`
- **Classes**: `PascalCase`
- **Constants**: `UPPER_SNAKE_CASE`
- **Private methods**: `_leading_underscore`
- **Files/Modules**: `snake_case.py`

#### Type Hints
```python
from typing import List, Dict, Optional, Union

def process_predictions(
    predictions: List[Dict[str, Union[str, float]]],
    user_id: int,
    include_history: bool = False
) -> Optional[Dict[str, any]]:
    """Process user predictions with type hints."""
    pass
```

### JavaScript/TypeScript Code Style

```typescript
// Use ESLint and Prettier
// File: tests/e2e/auth.spec.ts

import { test, expect, Page } from '@playwright/test';

interface LoginCredentials {
  email: string;
  password: string;
}

class AuthPage {
  constructor(private page: Page) {}

  async login(credentials: LoginCredentials): Promise<void> {
    await this.page.goto('/auth/login');
    await this.page.fill('[data-testid="email"]', credentials.email);
    await this.page.fill('[data-testid="password"]', credentials.password);
    await this.page.click('[data-testid="submit"]');
  }

  async isLoggedIn(): Promise<boolean> {
    await this.page.waitForSelector('[data-testid="dashboard"]');
    return await this.page.isVisible('[data-testid="user-menu"]');
  }
}

test.describe('Authentication', () => {
  test('should login successfully with valid credentials', async ({ page }) => {
    const authPage = new AuthPage(page);
    
    await authPage.login({
      email: 'admin@obesittrack.com',
      password: 'admin123'
    });
    
    expect(await authPage.isLoggedIn()).toBe(true);
  });
});
```

### SQL Style

```sql
-- Use uppercase for keywords, snake_case for identifiers
SELECT 
    u.id,
    u.email,
    u.created_at,
    COUNT(p.id) as prediction_count
FROM users u
LEFT JOIN predictions p ON u.id = p.user_id
WHERE 
    u.is_active = true
    AND u.created_at >= '2024-01-01'
GROUP BY u.id, u.email, u.created_at
ORDER BY u.created_at DESC
LIMIT 100;
```

---

## 🧪 Testing Requirements

### Test Coverage Standards

- **Minimum Coverage**: 80% overall
- **Critical Functions**: 95% coverage
- **New Features**: 90% coverage required

### Test Types

#### Unit Tests
```python
# tests/unit/test_auth_service.py
import pytest
from unittest.mock import Mock, patch

from app.services.auth import AuthService
from app.models.user import User
from app.core.security import verify_password


class TestAuthService:
    """Test authentication service."""
    
    @pytest.fixture
    def auth_service(self):
        """Create auth service instance."""
        return AuthService()
    
    @pytest.fixture
    def mock_user(self):
        """Create mock user."""
        return User(
            id=1,
            email="test@example.com",
            username="testuser",
            hashed_password="$2b$12$hashed_password"
        )
    
    async def test_authenticate_user_success(self, auth_service, mock_user):
        """Test successful user authentication."""
        with patch('app.services.auth.get_user_by_email') as mock_get_user, \
             patch('app.core.security.verify_password') as mock_verify:
            
            mock_get_user.return_value = mock_user
            mock_verify.return_value = True
            
            result = await auth_service.authenticate_user(
                "test@example.com", 
                "correct_password"
            )
            
            assert result == mock_user
            mock_get_user.assert_called_once_with("test@example.com")
            mock_verify.assert_called_once()
    
    async def test_authenticate_user_wrong_password(self, auth_service, mock_user):
        """Test authentication with wrong password."""
        with patch('app.services.auth.get_user_by_email') as mock_get_user, \
             patch('app.core.security.verify_password') as mock_verify:
            
            mock_get_user.return_value = mock_user
            mock_verify.return_value = False
            
            result = await auth_service.authenticate_user(
                "test@example.com", 
                "wrong_password"
            )
            
            assert result is None
```

#### Integration Tests
```python
# tests/integration/test_prediction_api.py
import pytest
from httpx import AsyncClient

from app.main import app
from app.core.database import get_db
from tests.conftest import override_get_db


class TestPredictionAPI:
    """Test prediction API endpoints."""
    
    @pytest.mark.asyncio
    async def test_create_prediction(self, client: AsyncClient, user_token: str):
        """Test creating a new prediction."""
        prediction_data = {
            "gender": "male",
            "age": 25,
            "height": 170.0,
            "weight": 70.0,
            # ... other required fields
        }
        
        response = await client.post(
            "/api/prediction/predict",
            json=prediction_data,
            headers={"Authorization": f"Bearer {user_token}"}
        )
        
        assert response.status_code == 200
        result = response.json()
        assert "prediction" in result
        assert "confidence" in result
        assert "bmi" in result
        assert result["bmi"] == pytest.approx(24.2, rel=1e-1)
```

#### E2E Tests
```typescript
// tests/e2e/prediction.spec.ts
import { test, expect } from '@playwright/test';

test.describe('Prediction Flow', () => {
  test.beforeEach(async ({ page }) => {
    // Login before each test
    await page.goto('/auth/login');
    await page.fill('[data-testid="email"]', 'admin@obesittrack.com');
    await page.fill('[data-testid="password"]', 'admin123');
    await page.click('[data-testid="submit"]');
    await expect(page.locator('[data-testid="dashboard"]')).toBeVisible();
  });

  test('should create prediction successfully', async ({ page }) => {
    // Navigate to prediction form
    await page.goto('/prediction/new');
    
    // Fill form
    await page.selectOption('[data-testid="gender"]', 'male');
    await page.fill('[data-testid="age"]', '25');
    await page.fill('[data-testid="height"]', '170');
    await page.fill('[data-testid="weight"]', '70');
    
    // Fill other required fields...
    
    // Submit form
    await page.click('[data-testid="submit-prediction"]');
    
    // Verify result
    await expect(page.locator('[data-testid="prediction-result"]')).toBeVisible();
    await expect(page.locator('[data-testid="prediction-class"]')).toContainText('Normal_Weight');
  });
});
```

### Test Data and Fixtures

```python
# tests/conftest.py
import pytest
import asyncio
from httpx import AsyncClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.core.database import Base, get_db
from app.models.user import User
from app.core.security import get_password_hash, create_access_token


# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
def db_session():
    """Create test database session."""
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


def override_get_db():
    """Override database dependency."""
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture(scope="function")
async def client():
    """Create test client."""
    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest.fixture
def test_user(db_session):
    """Create test user."""
    user = User(
        email="test@example.com",
        username="testuser",
        hashed_password=get_password_hash("testpass123")
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def user_token(test_user):
    """Create user access token."""
    return create_access_token(data={"sub": test_user.email})
```

---

## 📚 Documentation Guidelines

### Code Documentation

#### Docstrings
```python
def calculate_bmi(weight: float, height: float) -> float:
    """
    Calculate Body Mass Index (BMI).
    
    BMI is calculated as weight (kg) divided by height (m) squared.
    
    Args:
        weight: Weight in kilograms (must be positive)
        height: Height in centimeters (must be positive)
        
    Returns:
        BMI value as a float
        
    Raises:
        ValueError: If weight or height is not positive
        
    Example:
        >>> calculate_bmi(70.0, 175.0)
        22.86
    """
    if weight <= 0:
        raise ValueError("Weight must be positive")
    if height <= 0:
        raise ValueError("Height must be positive")
    
    height_m = height / 100  # Convert cm to meters
    return weight / (height_m ** 2)
```

#### API Documentation
```python
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field

router = APIRouter()


class PredictionRequest(BaseModel):
    """
    Request model for obesity prediction.
    
    Contains all required features for the ML model prediction.
    """
    gender: str = Field(..., description="User's gender", example="male")
    age: int = Field(..., ge=16, le=100, description="Age in years", example=25)
    height: float = Field(..., gt=0, description="Height in cm", example=175.0)
    weight: float = Field(..., gt=0, description="Weight in kg", example=70.0)
    # ... other fields


@router.post("/predict", response_model=PredictionResponse)
async def create_prediction(
    prediction_data: PredictionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new obesity prediction.
    
    This endpoint accepts user data and returns an obesity classification
    prediction using the trained ML model.
    
    Args:
        prediction_data: All required features for prediction
        current_user: Currently authenticated user
        db: Database session
        
    Returns:
        Prediction result with classification, confidence, and BMI
        
    Raises:
        HTTPException: 400 if input data is invalid
        HTTPException: 500 if prediction fails
    """
    # Implementation here
    pass
```

### Markdown Documentation

#### Structure
- Use clear headings hierarchy (H1 > H2 > H3)
- Include table of contents for long documents
- Use code blocks with language specification
- Add examples for complex concepts

#### Style Guide
- **Headers**: Use sentence case
- **Code**: Use `backticks` for inline code
- **Lists**: Use `-` for bullet points
- **Links**: Use descriptive text
- **Images**: Include alt text

---

## 🔍 Pull Request Process

### PR Template

Create `.github/pull_request_template.md`:

```markdown
## Description

Brief description of changes made.

## Type of Change

- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update
- [ ] Performance improvement
- [ ] Code refactoring

## Related Issues

Fixes #(issue_number)
Closes #(issue_number)

## Testing

- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] E2E tests pass
- [ ] Manual testing completed

## Checklist

- [ ] My code follows the project's style guidelines
- [ ] I have performed a self-review of my code
- [ ] I have commented my code, particularly in hard-to-understand areas
- [ ] I have made corresponding changes to the documentation
- [ ] My changes generate no new warnings
- [ ] I have added tests that prove my fix is effective or that my feature works
- [ ] New and existing unit tests pass locally with my changes
- [ ] Any dependent changes have been merged and published

## Screenshots (if applicable)

Add screenshots here

## Additional Notes

Any additional information that reviewers should know
```

### Review Process

1. **Automated Checks**
   - CI/CD pipeline must pass
   - All tests must pass
   - Code coverage must meet requirements
   - Code quality checks must pass

2. **Manual Review**
   - At least one maintainer review required
   - Code follows style guidelines
   - Documentation is updated
   - Changes are properly tested

3. **Approval and Merge**
   - All feedback addressed
   - Approved by maintainers
   - Merged with appropriate merge strategy

### Merge Strategies

- **Squash and merge**: For feature branches (preferred)
- **Merge commit**: For complex features with meaningful commit history
- **Rebase and merge**: For simple fixes

---

## 🐛 Issue Reporting

### Bug Reports

Use the bug report template:

```markdown
**Bug Description**
A clear and concise description of what the bug is.

**To Reproduce**
Steps to reproduce the behavior:
1. Go to '...'
2. Click on '....'
3. Scroll down to '....'
4. See error

**Expected Behavior**
A clear description of what you expected to happen.

**Screenshots**
If applicable, add screenshots to help explain your problem.

**Environment:**
- OS: [e.g. Ubuntu 20.04]
- Python Version: [e.g. 3.11.2]
- Browser: [e.g. Chrome 118]
- ObesiTrack Version: [e.g. 1.0.0]

**Additional Context**
Add any other context about the problem here.
```

### Feature Requests

Use the feature request template:

```markdown
**Is your feature request related to a problem? Please describe.**
A clear and concise description of what the problem is.

**Describe the solution you'd like**
A clear and concise description of what you want to happen.

**Describe alternatives you've considered**
A clear and concise description of any alternative solutions or features you've considered.

**Additional context**
Add any other context or screenshots about the feature request here.
```

---

## 🔒 Security Vulnerabilities

### Reporting Security Issues

**DO NOT** create public issues for security vulnerabilities.

Instead:

1. **Email**: Send details to security@obesittrack.com
2. **Include**: 
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if known)

3. **Response**: We will respond within 48 hours
4. **Disclosure**: We follow responsible disclosure practices

### Security Best Practices

- Never commit secrets or credentials
- Use environment variables for sensitive data
- Follow OWASP security guidelines
- Keep dependencies updated
- Use proper input validation
- Implement proper error handling

---

## 🏆 Recognition

### Contributors

We recognize all contributors in:
- README.md contributors section
- Release notes
- GitHub repository insights
- Special recognition for significant contributions

### Contribution Levels

- **First-time contributor**: Merged first PR
- **Regular contributor**: 5+ merged PRs
- **Core contributor**: 20+ merged PRs + ongoing involvement
- **Maintainer**: Trusted with repository access

---

## 📞 Getting Help

### Communication Channels

- **GitHub Issues**: Bug reports and feature requests
- **GitHub Discussions**: General questions and ideas
- **Email**: maintainers@obesittrack.com

### Response Times

- **Bug reports**: 24-48 hours
- **Feature requests**: 1-2 weeks
- **Security issues**: 24 hours
- **PR reviews**: 2-5 business days

---

## 📄 License

By contributing to ObesiTrack, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to ObesiTrack! 🎉

Your contributions help make obesity prediction and management more accessible and effective for everyone.