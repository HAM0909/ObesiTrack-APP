# ObesiTrack API Reference

## 📚 Table of Contents

1. [API Overview](#api-overview)
2. [Authentication](#authentication)
3. [User Management](#user-management)
4. [Prediction Endpoints](#prediction-endpoints)
5. [Admin Endpoints](#admin-endpoints)
6. [Analytics & Metrics](#analytics--metrics)
7. [Health & System](#health--system)
8. [Error Handling](#error-handling)
9. [Rate Limiting](#rate-limiting)
10. [API Examples](#api-examples)

---

## 🌐 API Overview

### Base URL
- **Development**: `http://localhost:8000`
- **Production**: `https://your-domain.com`

### API Version
- Current Version: `v1`
- All endpoints are prefixed with `/api` except for web pages

### Content Types
- **Request**: `application/json`
- **Response**: `application/json`

### Date Formats
- ISO 8601 format: `YYYY-MM-DDTHH:MM:SSZ`
- Example: `2024-01-15T14:30:00Z`

---

## 🔐 Authentication

All protected endpoints require JWT authentication via the `Authorization` header.

### Headers
```http
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

### Authentication Flow

#### 1. User Registration
```http
POST /api/auth/register
```

**Request Body:**
```json
{
  "username": "string",
  "email": "user@example.com",
  "password": "string"
}
```

**Validation Rules:**
- `username`: 3-50 characters, alphanumeric + underscore
- `email`: Valid email format, unique
- `password`: Minimum 6 characters

**Response (201 Created):**
```json
{
  "message": "User created successfully",
  "user_id": 123
}
```

**Error Responses:**
```json
// 400 Bad Request - Validation Error
{
  "detail": "Email already registered"
}

// 422 Unprocessable Entity - Invalid Data
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

#### 2. User Login
```http
POST /api/auth/login
```

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "string"
}
```

**Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800,
  "user": {
    "id": 123,
    "username": "user123",
    "email": "user@example.com",
    "is_admin": false,
    "created_at": "2024-01-15T10:00:00Z"
  }
}
```

**Error Responses:**
```json
// 401 Unauthorized - Invalid Credentials
{
  "detail": "Invalid email or password"
}

// 400 Bad Request - Missing Fields
{
  "detail": "Email and password are required"
}
```

#### 3. Token Refresh
```http
POST /api/auth/refresh
```

**Headers:**
```http
Authorization: Bearer <current_jwt_token>
```

**Response (200 OK):**
```json
{
  "access_token": "new_jwt_token_here",
  "token_type": "bearer",
  "expires_in": 1800
}
```

---

## 👤 User Management

### Get Current User Profile
```http
GET /api/auth/me
```

**Headers:**
```http
Authorization: Bearer <jwt_token>
```

**Response (200 OK):**
```json
{
  "id": 123,
  "username": "user123",
  "email": "user@example.com",
  "is_admin": false,
  "created_at": "2024-01-15T10:00:00Z",
  "updated_at": "2024-01-15T10:00:00Z",
  "total_predictions": 5,
  "last_prediction_at": "2024-01-15T14:30:00Z"
}
```

### Update User Profile
```http
PUT /api/auth/me
```

**Headers:**
```http
Authorization: Bearer <jwt_token>
```

**Request Body:**
```json
{
  "username": "new_username",
  "email": "newemail@example.com"
}
```

**Response (200 OK):**
```json
{
  "message": "Profile updated successfully",
  "user": {
    "id": 123,
    "username": "new_username",
    "email": "newemail@example.com",
    "updated_at": "2024-01-15T15:00:00Z"
  }
}
```

### Change Password
```http
POST /api/auth/change-password
```

**Headers:**
```http
Authorization: Bearer <jwt_token>
```

**Request Body:**
```json
{
  "current_password": "old_password",
  "new_password": "new_password",
  "confirm_password": "new_password"
}
```

**Response (200 OK):**
```json
{
  "message": "Password changed successfully"
}
```

---

## 🔮 Prediction Endpoints

### Make Prediction
```http
POST /api/prediction/predict
```

**Headers:**
```http
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

**Request Body:**
```json
{
  "gender": "male",
  "age": 25,
  "height": 175.0,
  "weight": 75.0,
  "family_history_with_overweight": "yes",
  "favc": "yes",
  "fcvc": 2.5,
  "ncp": 3.0,
  "caec": "Sometimes",
  "smoke": "no",
  "ch2o": 2.0,
  "scc": "no",
  "faf": 2.0,
  "tue": 1.0,
  "calc": "Sometimes",
  "mtrans": "Public_Transportation"
}
```

**Field Descriptions:**
| Field | Type | Description | Valid Values |
|-------|------|-------------|--------------|
| `gender` | string | Gender | `"male"`, `"female"` |
| `age` | integer | Age in years | 1-120 |
| `height` | float | Height in centimeters | 50.0-250.0 |
| `weight` | float | Weight in kilograms | 10.0-500.0 |
| `family_history_with_overweight` | string | Family history | `"yes"`, `"no"` |
| `favc` | string | Frequent high caloric food | `"yes"`, `"no"` |
| `fcvc` | float | Vegetable consumption frequency | 0.0-3.0 |
| `ncp` | float | Number of main meals | 1.0-4.0 |
| `caec` | string | Food between meals | `"Always"`, `"Frequently"`, `"Sometimes"`, `"no"` |
| `smoke` | string | Smoking habits | `"yes"`, `"no"` |
| `ch2o` | float | Daily water consumption | 1.0-3.0 |
| `scc` | string | Calorie monitoring | `"yes"`, `"no"` |
| `faf` | float | Physical activity frequency | 0.0-3.0 |
| `tue` | float | Technology usage time | 0.0-2.0 |
| `calc` | string | Alcohol consumption | `"Always"`, `"Frequently"`, `"Sometimes"`, `"no"` |
| `mtrans` | string | Transportation mode | `"Walking"`, `"Bike"`, `"Automobile"`, `"Public_Transportation"`, `"Motorbike"` |

**Response (200 OK):**
```json
{
  "id": 456,
  "prediction": "Normal_Weight",
  "confidence": 0.87,
  "bmi": 24.5,
  "bmi_category": "Normal",
  "risk_level": "Low",
  "risk_factors": [
    "family_history_with_overweight"
  ],
  "recommendations": [
    "Maintain your current healthy weight",
    "Continue regular physical activity",
    "Monitor portion sizes during meals"
  ],
  "created_at": "2024-01-15T14:30:00Z",
  "input_data": {
    // Complete input data for reference
  }
}
```

**Prediction Classes:**
- `Insufficient_Weight` - BMI < 18.5
- `Normal_Weight` - 18.5 ≤ BMI < 25
- `Overweight_Level_I` - 25 ≤ BMI < 30
- `Overweight_Level_II` - 30 ≤ BMI < 35
- `Obesity_Type_I` - 35 ≤ BMI < 40
- `Obesity_Type_II` - 40 ≤ BMI < 50
- `Obesity_Type_III` - BMI ≥ 50

### Get Prediction History
```http
GET /api/prediction/history
```

**Headers:**
```http
Authorization: Bearer <jwt_token>
```

**Query Parameters:**
- `limit` (optional): Number of results (default: 10, max: 100)
- `offset` (optional): Pagination offset (default: 0)
- `sort_by` (optional): Sort field (`created_at`, `bmi`, `confidence`)
- `sort_order` (optional): Sort order (`asc`, `desc`, default: `desc`)
- `date_from` (optional): Filter from date (ISO format)
- `date_to` (optional): Filter to date (ISO format)

**Example:**
```http
GET /api/prediction/history?limit=20&sort_by=created_at&sort_order=desc
```

**Response (200 OK):**
```json
{
  "predictions": [
    {
      "id": 456,
      "prediction": "Normal_Weight",
      "confidence": 0.87,
      "bmi": 24.5,
      "risk_level": "Low",
      "created_at": "2024-01-15T14:30:00Z"
    },
    {
      "id": 455,
      "prediction": "Overweight_Level_I",
      "confidence": 0.92,
      "bmi": 26.8,
      "risk_level": "Medium",
      "created_at": "2024-01-14T10:15:00Z"
    }
  ],
  "total": 5,
  "limit": 20,
  "offset": 0,
  "has_more": false
}
```

### Get Specific Prediction
```http
GET /api/prediction/{prediction_id}
```

**Headers:**
```http
Authorization: Bearer <jwt_token>
```

**Response (200 OK):**
```json
{
  "id": 456,
  "prediction": "Normal_Weight",
  "confidence": 0.87,
  "bmi": 24.5,
  "bmi_category": "Normal",
  "risk_level": "Low",
  "risk_factors": ["family_history_with_overweight"],
  "recommendations": ["Maintain your current healthy weight"],
  "input_data": {
    "gender": "male",
    "age": 25,
    // ... complete input data
  },
  "created_at": "2024-01-15T14:30:00Z"
}
```

### Delete Prediction
```http
DELETE /api/prediction/{prediction_id}
```

**Headers:**
```http
Authorization: Bearer <jwt_token>
```

**Response (200 OK):**
```json
{
  "message": "Prediction deleted successfully"
}
```

---

## 👑 Admin Endpoints

All admin endpoints require admin privileges (`is_admin: true`).

### Get All Users
```http
GET /api/admin/users
```

**Headers:**
```http
Authorization: Bearer <admin_jwt_token>
```

**Query Parameters:**
- `limit` (optional): Number of results (default: 50, max: 1000)
- `offset` (optional): Pagination offset (default: 0)
- `search` (optional): Search by username or email
- `is_admin` (optional): Filter by admin status (`true`, `false`)
- `created_after` (optional): Filter users created after date
- `created_before` (optional): Filter users created before date

**Response (200 OK):**
```json
{
  "users": [
    {
      "id": 123,
      "username": "user123",
      "email": "user@example.com",
      "is_admin": false,
      "created_at": "2024-01-15T10:00:00Z",
      "last_login": "2024-01-15T14:00:00Z",
      "total_predictions": 5,
      "last_prediction_at": "2024-01-15T14:30:00Z"
    }
  ],
  "total": 150,
  "limit": 50,
  "offset": 0,
  "has_more": true
}
```

### Get User Details
```http
GET /api/admin/users/{user_id}
```

**Headers:**
```http
Authorization: Bearer <admin_jwt_token>
```

**Response (200 OK):**
```json
{
  "id": 123,
  "username": "user123",
  "email": "user@example.com",
  "is_admin": false,
  "created_at": "2024-01-15T10:00:00Z",
  "updated_at": "2024-01-15T10:00:00Z",
  "last_login": "2024-01-15T14:00:00Z",
  "total_predictions": 5,
  "last_prediction_at": "2024-01-15T14:30:00Z",
  "prediction_summary": {
    "Normal_Weight": 3,
    "Overweight_Level_I": 2
  }
}
```

### Update User
```http
PUT /api/admin/users/{user_id}
```

**Headers:**
```http
Authorization: Bearer <admin_jwt_token>
```

**Request Body:**
```json
{
  "username": "new_username",
  "email": "newemail@example.com",
  "is_admin": true
}
```

**Response (200 OK):**
```json
{
  "message": "User updated successfully",
  "user": {
    "id": 123,
    "username": "new_username",
    "email": "newemail@example.com",
    "is_admin": true,
    "updated_at": "2024-01-15T15:00:00Z"
  }
}
```

### Delete User
```http
DELETE /api/admin/users/{user_id}
```

**Headers:**
```http
Authorization: Bearer <admin_jwt_token>
```

**Query Parameters:**
- `delete_predictions` (optional): Whether to delete user's predictions (`true`, `false`, default: `true`)

**Response (200 OK):**
```json
{
  "message": "User deleted successfully",
  "deleted_predictions": 5
}
```

### Get User Predictions (Admin)
```http
GET /api/admin/users/{user_id}/predictions
```

**Headers:**
```http
Authorization: Bearer <admin_jwt_token>
```

**Query Parameters:** (Same as user prediction history)

**Response (200 OK):**
```json
{
  "user": {
    "id": 123,
    "username": "user123",
    "email": "user@example.com"
  },
  "predictions": [
    {
      "id": 456,
      "prediction": "Normal_Weight",
      "confidence": 0.87,
      "bmi": 24.5,
      "created_at": "2024-01-15T14:30:00Z"
    }
  ],
  "total": 5
}
```

### Bulk User Operations
```http
POST /api/admin/users/bulk
```

**Headers:**
```http
Authorization: Bearer <admin_jwt_token>
```

**Request Body:**
```json
{
  "action": "delete",
  "user_ids": [123, 124, 125],
  "options": {
    "delete_predictions": true,
    "send_notification": false
  }
}
```

**Response (200 OK):**
```json
{
  "message": "Bulk operation completed",
  "action": "delete",
  "success_count": 3,
  "failed_count": 0,
  "results": [
    {
      "user_id": 123,
      "status": "success",
      "message": "User deleted successfully"
    }
  ]
}
```

---

## 📊 Analytics & Metrics

### Dashboard Metrics
```http
GET /api/metrics/dashboard
```

**Headers:**
```http
Authorization: Bearer <jwt_token>
```

**Query Parameters:**
- `period` (optional): Time period (`today`, `week`, `month`, `year`, `all`, default: `month`)
- `user_only` (optional): Show only current user's metrics (`true`, `false`, default: `false`)

**Response (200 OK):**
```json
{
  "period": "month",
  "total_users": 150,
  "total_predictions": 750,
  "predictions_today": 15,
  "predictions_this_week": 85,
  "predictions_this_month": 320,
  "new_users_this_month": 25,
  "prediction_distribution": {
    "Normal_Weight": 285,
    "Overweight_Level_I": 180,
    "Overweight_Level_II": 125,
    "Obesity_Type_I": 85,
    "Obesity_Type_II": 45,
    "Obesity_Type_III": 20,
    "Insufficient_Weight": 10
  },
  "avg_bmi": 26.5,
  "risk_level_distribution": {
    "Low": 320,
    "Medium": 280,
    "High": 150
  },
  "top_risk_factors": [
    {
      "factor": "family_history_with_overweight",
      "count": 450,
      "percentage": 60.0
    },
    {
      "factor": "low_physical_activity",
      "count": 380,
      "percentage": 50.7
    }
  ]
}
```

### Prediction Trends
```http
GET /api/metrics/trends
```

**Headers:**
```http
Authorization: Bearer <jwt_token>
```

**Query Parameters:**
- `period` (optional): `week`, `month`, `quarter`, `year` (default: `month`)
- `group_by` (optional): `day`, `week`, `month` (default: `day`)

**Response (200 OK):**
```json
{
  "period": "month",
  "group_by": "day",
  "data": [
    {
      "date": "2024-01-15",
      "total_predictions": 15,
      "normal_weight": 8,
      "overweight": 4,
      "obesity": 3,
      "avg_bmi": 25.8
    },
    {
      "date": "2024-01-16",
      "total_predictions": 12,
      "normal_weight": 6,
      "overweight": 3,
      "obesity": 3,
      "avg_bmi": 26.2
    }
  ],
  "summary": {
    "total_predictions": 320,
    "avg_predictions_per_day": 10.3,
    "peak_day": "2024-01-20",
    "peak_predictions": 28
  }
}
```

### Export Data
```http
GET /api/metrics/export
```

**Headers:**
```http
Authorization: Bearer <admin_jwt_token>
```

**Query Parameters:**
- `format`: Export format (`csv`, `json`, `xlsx`)
- `data_type`: Type of data (`users`, `predictions`, `analytics`)
- `date_from` (optional): Start date
- `date_to` (optional): End date
- `include_personal_data` (optional): Include personal info (`true`, `false`, default: `false`)

**Response (200 OK):**
Returns file download with appropriate content type.

---

## 🏥 Health & System

### Health Check
```http
GET /health
```

**Response (200 OK):**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T14:30:00Z",
  "version": "1.0.0",
  "environment": "production",
  "database": {
    "status": "healthy",
    "connection_pool": {
      "active": 2,
      "idle": 8,
      "max": 10
    },
    "version": "PostgreSQL 13.11"
  },
  "ml_model": {
    "status": "loaded",
    "version": "1.2.0",
    "last_loaded": "2024-01-15T10:00:00Z",
    "prediction_count": 750
  },
  "cache": {
    "status": "healthy",
    "redis_version": "7.0.11",
    "memory_usage": "15.2MB"
  },
  "disk_space": {
    "available": "85.2GB",
    "used": "14.8GB",
    "percentage": 14.8
  }
}
```

### System Metrics
```http
GET /api/system/metrics
```

**Headers:**
```http
Authorization: Bearer <admin_jwt_token>
```

**Response (200 OK):**
```json
{
  "system": {
    "uptime": 86400,
    "cpu_usage": 15.5,
    "memory_usage": 68.2,
    "disk_usage": 14.8
  },
  "application": {
    "requests_per_minute": 45,
    "avg_response_time": 125,
    "active_users": 23,
    "predictions_per_hour": 12
  },
  "database": {
    "queries_per_second": 5.8,
    "slow_queries": 2,
    "connection_count": 10
  }
}
```

---

## ❌ Error Handling

### Standard Error Response Format

All API endpoints return errors in the following format:

```json
{
  "error": "Error Type",
  "message": "Human-readable error message",
  "details": "Additional error details (optional)",
  "timestamp": "2024-01-15T14:30:00Z",
  "request_id": "req_123456789"
}
```

### HTTP Status Codes

| Code | Status | Description |
|------|--------|-------------|
| 200 | OK | Request successful |
| 201 | Created | Resource created successfully |
| 204 | No Content | Request successful, no content returned |
| 400 | Bad Request | Invalid request data |
| 401 | Unauthorized | Authentication required |
| 403 | Forbidden | Access denied |
| 404 | Not Found | Resource not found |
| 422 | Unprocessable Entity | Validation errors |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Server error |
| 503 | Service Unavailable | Service temporarily unavailable |

### Common Error Responses

#### Validation Error (422)
```json
{
  "error": "Validation Error",
  "message": "Request data validation failed",
  "details": [
    {
      "field": "email",
      "message": "Invalid email format",
      "code": "INVALID_EMAIL"
    },
    {
      "field": "age",
      "message": "Age must be between 1 and 120",
      "code": "VALUE_OUT_OF_RANGE"
    }
  ]
}
```

#### Authentication Error (401)
```json
{
  "error": "Unauthorized",
  "message": "Invalid or expired token",
  "code": "TOKEN_EXPIRED"
}
```

#### Authorization Error (403)
```json
{
  "error": "Forbidden",
  "message": "Admin privileges required",
  "code": "INSUFFICIENT_PRIVILEGES"
}
```

#### Rate Limit Error (429)
```json
{
  "error": "Too Many Requests",
  "message": "Rate limit exceeded. Try again in 60 seconds",
  "retry_after": 60,
  "limit": 100,
  "remaining": 0,
  "reset": "2024-01-15T14:31:00Z"
}
```

---

## 🚦 Rate Limiting

### Rate Limits

| Endpoint Category | Authenticated | Anonymous | Window |
|-------------------|---------------|-----------|---------|
| Authentication | 10 requests | 5 requests | 1 minute |
| Predictions | 100 requests | N/A | 1 hour |
| User Management | 200 requests | N/A | 1 hour |
| Admin Operations | 500 requests | N/A | 1 hour |
| Analytics | 50 requests | N/A | 1 minute |

### Rate Limit Headers

All responses include rate limiting information:

```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1642268400
X-RateLimit-Window: 3600
```

### Rate Limit Exceeded Response

```json
{
  "error": "Too Many Requests",
  "message": "Rate limit exceeded for predictions endpoint",
  "limit": 100,
  "remaining": 0,
  "reset": "2024-01-15T15:00:00Z",
  "retry_after": 300
}
```

---

## 📝 API Examples

### Complete User Registration and Prediction Flow

#### 1. Register New User
```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "email": "john@example.com",
    "password": "secure_password123"
  }'
```

#### 2. Login and Get Token
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com",
    "password": "secure_password123"
  }' | jq -r '.access_token'
```

#### 3. Make Prediction
```bash
TOKEN="your_jwt_token_here"

curl -X POST http://localhost:8000/api/prediction/predict \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "gender": "male",
    "age": 28,
    "height": 178.0,
    "weight": 82.0,
    "family_history_with_overweight": "yes",
    "favc": "no",
    "fcvc": 2.0,
    "ncp": 3.0,
    "caec": "Sometimes",
    "smoke": "no",
    "ch2o": 2.5,
    "scc": "yes",
    "faf": 2.0,
    "tue": 1.0,
    "calc": "no",
    "mtrans": "Walking"
  }'
```

#### 4. Get Prediction History
```bash
curl -X GET "http://localhost:8000/api/prediction/history?limit=10" \
  -H "Authorization: Bearer $TOKEN"
```

### Admin Operations Example

#### 1. Get All Users (Admin)
```bash
ADMIN_TOKEN="admin_jwt_token_here"

curl -X GET "http://localhost:8000/api/admin/users?limit=50&search=john" \
  -H "Authorization: Bearer $ADMIN_TOKEN"
```

#### 2. Delete User (Admin)
```bash
curl -X DELETE "http://localhost:8000/api/admin/users/123?delete_predictions=true" \
  -H "Authorization: Bearer $ADMIN_TOKEN"
```

### Analytics Example

#### 1. Get Dashboard Metrics
```bash
curl -X GET "http://localhost:8000/api/metrics/dashboard?period=month" \
  -H "Authorization: Bearer $TOKEN"
```

#### 2. Export Data (Admin)
```bash
curl -X GET "http://localhost:8000/api/metrics/export?format=csv&data_type=predictions&date_from=2024-01-01" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  --output predictions_export.csv
```

### JavaScript/Fetch Examples

#### Authentication Service Class
```javascript
class ObesiTrackAPI {
  constructor(baseURL = 'http://localhost:8000') {
    this.baseURL = baseURL;
    this.token = localStorage.getItem('access_token');
  }

  async request(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`;
    const config = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers
      },
      ...options
    };

    if (this.token && !config.headers.Authorization) {
      config.headers.Authorization = `Bearer ${this.token}`;
    }

    const response = await fetch(url, config);
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    return response.json();
  }

  // Authentication
  async register(userData) {
    return this.request('/api/auth/register', {
      method: 'POST',
      body: JSON.stringify(userData)
    });
  }

  async login(email, password) {
    const response = await this.request('/api/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password })
    });
    
    this.token = response.access_token;
    localStorage.setItem('access_token', this.token);
    return response;
  }

  // Predictions
  async makePrediction(predictionData) {
    return this.request('/api/prediction/predict', {
      method: 'POST',
      body: JSON.stringify(predictionData)
    });
  }

  async getPredictionHistory(params = {}) {
    const queryString = new URLSearchParams(params).toString();
    return this.request(`/api/prediction/history?${queryString}`);
  }

  // Admin
  async getAllUsers(params = {}) {
    const queryString = new URLSearchParams(params).toString();
    return this.request(`/api/admin/users?${queryString}`);
  }
}

// Usage Example
const api = new ObesiTrackAPI();

// Login and make prediction
api.login('user@example.com', 'password')
  .then(() => api.makePrediction({
    gender: 'male',
    age: 25,
    height: 175,
    weight: 70,
    // ... other fields
  }))
  .then(result => console.log('Prediction:', result))
  .catch(error => console.error('Error:', error));
```

### Python Requests Examples

#### API Client Class
```python
import requests
import json
from typing import Dict, Optional, Any

class ObesiTrackClient:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.token = None
        self.session = requests.Session()
    
    def _request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        url = f"{self.base_url}{endpoint}"
        headers = kwargs.get('headers', {})
        
        if self.token:
            headers['Authorization'] = f"Bearer {self.token}"
        
        kwargs['headers'] = headers
        response = self.session.request(method, url, **kwargs)
        response.raise_for_status()
        return response.json()
    
    def register(self, username: str, email: str, password: str) -> Dict[str, Any]:
        return self._request('POST', '/api/auth/register', json={
            'username': username,
            'email': email,
            'password': password
        })
    
    def login(self, email: str, password: str) -> Dict[str, Any]:
        response = self._request('POST', '/api/auth/login', json={
            'email': email,
            'password': password
        })
        self.token = response['access_token']
        return response
    
    def make_prediction(self, prediction_data: Dict[str, Any]) -> Dict[str, Any]:
        return self._request('POST', '/api/prediction/predict', json=prediction_data)
    
    def get_prediction_history(self, **params) -> Dict[str, Any]:
        return self._request('GET', '/api/prediction/history', params=params)

# Usage Example
client = ObesiTrackClient()

# Register and login
client.register("john_doe", "john@example.com", "password123")
client.login("john@example.com", "password123")

# Make prediction
result = client.make_prediction({
    "gender": "male",
    "age": 28,
    "height": 178.0,
    "weight": 82.0,
    "family_history_with_overweight": "yes",
    "favc": "no",
    "fcvc": 2.0,
    "ncp": 3.0,
    "caec": "Sometimes",
    "smoke": "no",
    "ch2o": 2.5,
    "scc": "yes",
    "faf": 2.0,
    "tue": 1.0,
    "calc": "no",
    "mtrans": "Walking"
})

print(f"Prediction: {result['prediction']}")
print(f"BMI: {result['bmi']}")
print(f"Confidence: {result['confidence']:.2%}")
```

---

## 🔗 Additional Resources

### OpenAPI/Swagger Documentation
- Interactive API documentation: `http://localhost:8000/docs`
- Alternative documentation: `http://localhost:8000/redoc`
- OpenAPI JSON schema: `http://localhost:8000/openapi.json`

### Postman Collection
Import the provided Postman collection for easy API testing:
- Collection file: `docs/postman_collection.json`
- Environment file: `docs/postman_environment.json`

### SDK and Libraries
- **Python SDK**: Available in `client/python/`
- **JavaScript SDK**: Available in `client/javascript/`
- **Postman Collection**: Available in `docs/`

### Support and Issues
- **GitHub Repository**: [ObesiTrack-APP](https://github.com/HAM0909/ObesiTrack-APP)
- **Documentation**: [DOCUMENTATION.md](./DOCUMENTATION.md)
- **Workflow Guide**: [WORKFLOW_GUIDE.md](./WORKFLOW_GUIDE.md)

---

**Last Updated**: October 2025  
**API Version**: 1.0.0  
**Documentation Version**: 1.0.0