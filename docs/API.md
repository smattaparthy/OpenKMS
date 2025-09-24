# OpenKMS API Documentation

## Overview

The OpenKMS API provides a comprehensive RESTful interface for managing knowledge management and training administration functions. Built with FastAPI, it offers automatic OpenAPI/Swagger documentation, type validation, and async operations for optimal performance.

### Base URL
- **Development**: `http://localhost:8000/api/v1`
- **Production**: `https://api.yourdomain.com/api/v1`

### API Documentation
- **Interactive Swagger UI**: `/docs`
- **ReDoc**: `/redoc`
- **OpenAPI Schema**: `/openapi.json`

---

## Authentication

The API uses JWT (JSON Web Token) authentication for securing endpoints. All protected endpoints require a valid JWT token in the Authorization header.

### Authentication Flow
1. User authenticates via `/api/v1/auth/login`
2. Server returns `access_token` and `refresh_token`
3. Client includes `access_token` in subsequent requests
4. Use `refresh_token` to obtain new `access_token` when expired

### Authorization Header
```
Authorization: Bearer <access_token>
```

### Token Types
- **Access Token**: Short-lived (15 minutes) token for API requests
- **Refresh Token**: Long-lived (7 days) token for obtaining new access tokens

---

## Response Formats

All API responses follow a consistent JSON format:

### Success Response
```json
{
  "data": {},
  "message": "Success message",
  "status": "success"
}
```

### Error Response
```json
{
  "detail": "Error message",
  "status": "error",
  "code": "ERROR_CODE"
}
```

### HTTP Status Codes
- **200 OK**: Successful request
- **201 Created**: Resource created successfully
- **400 Bad Request**: Invalid request data
- **401 Unauthorized**: Authentication required
- **403 Forbidden**: Insufficient permissions
- **404 Not Found**: Resource not found
- **422 Unprocessable Entity**: Validation error
- **500 Internal Server Error**: Server error

---

## API Endpoints

### 📋 Authentication Endpoints

#### POST /api/v1/auth/login
Authenticate user and return JWT tokens.

**Request Body:**
```json
{
  "username": "string",
  "password": "string"
}
```

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "username": "johndoe",
    "email": "john.doe@example.com",
    "full_name": "John Doe",
    "role": "EMPLOYEE",
    "is_active": true
  }
}
```

**Status Codes:**
- `200 OK`: Authentication successful
- `401 Unauthorized`: Invalid credentials
- `422 Unprocessable Entity`: Validation error

#### POST /api/v1/auth/register
Register a new user.

**Request Body:**
```json
{
  "username": "string (max 50 chars)",
  "email": "valid@email.com",
  "full_name": "string",
  "password": "string (min 8 chars)",
  "office_location": "string (optional)",
  "department": "string (optional)"
}
```

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "user": {
    "id": 2,
    "username": "newuser",
    "email": "newuser@example.com",
    "full_name": "New User",
    "role": "EMPLOYEE",
    "is_active": true
  }
}
```

**Status Codes:**
- `201 Created`: User registered successfully
- `400 Bad Request`: User already exists
- `422 Unprocessable Entity`: Invalid data

#### POST /api/v1/auth/refresh
Refresh access token using refresh token.

**Request Body:**
```json
{
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer"
}
```

**Status Codes:**
- `200 OK`: Token refreshed successfully
- `401 Unauthorized**: Invalid refresh token

#### POST /api/v1/auth/change-password
Change user password.

**Request Body:**
```json
{
  "current_password": "string",
  "new_password": "string (min 8 chars)"
}
```

**Response:**
```json
{
  "message": "Password changed successfully"
}
```

**Status Codes:**
- `200 OK`: Password changed successfully
- `400 Bad Request`: Current password incorrect
- `422 Unprocessable Entity`: Validation error

#### GET /api/v1/auth/me
Get current authenticated user information.

**Response:**
```json
{
  "user": {
    "id": 1,
    "username": "johndoe",
    "email": "john.doe@example.com",
    "full_name": "John Doe",
    "office_location": "Office A",
    "department": "IT",
    "role": "EMPLOYEE",
    "is_active": true
  },
  "message": "User information retrieved successfully"
}
```

**Status Codes:**
- `200 OK`: User information retrieved
- `401 Unauthorized**: Not authenticated

---

### 👥 User Management Endpoints

#### GET /api/v1/users
Get list of users with pagination and filtering.

**Query Parameters:**
- `skip`: Number of users to skip (default: 0)
- `limit`: Number of users to return (default: 100, max: 1000)
- `active_only`: Filter active users (default: true)
- `role`: Filter by role (EMPLOYEE, KNOWLEDGE_MANAGER, ADMIN)

**Response:**
```json
{
  "users": [
    {
      "id": 1,
      "username": "johndoe",
      "email": "john.doe@example.com",
      "full_name": "John Doe",
      "office_location": "Office A",
      "department": "IT",
      "role": "EMPLOYEE",
      "is_active": true,
      "created_at": "2023-12-01T10:00:00Z"
    }
  ],
  "total": 1,
  "skip": 0,
  "limit": 100
}
```

**Status Codes:**
- `200 OK`: Users retrieved successfully
- `401 Unauthorized**: Not authenticated
- `403 Forbidden`: Insufficient permissions

#### GET /api/v1/users/{user_id}
Get specific user by ID.

**Response:**
```json
{
  "user": {
    "id": 1,
    "username": "johndoe",
    "email": "john.doe@example.com",
    "full_name": "John Doe",
    "office_location": "Office A",
    "department": "IT",
    "role": "EMPLOYEE",
    "is_active": true,
    "created_at": "2023-12-01T10:00:00Z",
    "updated_at": "2023-12-01T10:00:00Z"
  }
}
```

**Status Codes:**
- `200 OK`: User retrieved successfully
- `401 Unauthorized`: Not authenticated
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: User not found

#### PUT /api/v1/users/{user_id}
Update user information.

**Request Body:**
```json
{
  "full_name": "string (optional)",
  "email": "string (optional)",
  "office_location": "string (optional)",
  "department": "string (optional)",
  "role": "EMPLOYEE|KNOWLEDGE_MANAGER|ADMIN (optional)",
  "is_active": "boolean (optional)"
}
```

**Response:**
```json
{
  "user": {
    "id": 1,
    "username": "johndoe",
    "email": "john.doe@example.com",
    "full_name": "John Doe",
    "office_location": "Office A",
    "department": "IT",
    "role": "EMPLOYEE",
    "is_active": true,
    "updated_at": "2023-12-01T10:00:00Z"
  },
  "message": "User updated successfully"
}
```

**Status Codes:**
- `200 OK`: User updated successfully
- `401 Unauthorized`: Not authenticated
- `403 Forbidden**: Insufficient permissions
- `404 Not Found`: User not found
- `422 Unprocessable Entity`: Validation error

#### DELETE /api/v1/users/{user_id}
Delete user (soft delete).

**Response:**
```json
{
  "message": "User deactivated successfully"
}
```

**Status Codes:**
- `200 OK`: User deactivated successfully
- `401 Unauthorized`: Not authenticated
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: User not found

---

### 📚 Training Management Endpoints

#### GET /api/v1/trainings
Get list of training programs with filtering and search.

**Query Parameters:**
- `skip`: Number of trainings to skip (default: 0)
- `limit`: Number of trainings to return (default: 100, max: 1000)
- `search`: Search in title and description
- `category`: Filter by category (SECURITY, LEADERSHIP, TECHNICAL, COMPLIANCE)
- `level`: Filter by level (BEGINNER, INTERMEDIATE, ADVANCED)
- `status`: Filter by status (PUBLISHED, DRAFT)
- `instructor_id`: Filter by instructor ID

**Response:**
```json
{
  "trainings": [
    {
      "id": 1,
      "title": "Security Awareness Training",
      "description": "Comprehensive security awareness training",
      "category": "SECURITY",
      "level": "BEGINNER",
      "status": "PUBLISHED",
      "duration_minutes": 120,
      "credits": 2,
      "instructor_id": 1,
      "max_participants": 50,
      "created_at": "2023-12-01T10:00:00Z",
      "updated_at": "2023-12-01T10:00:00Z"
    }
  ],
  "total": 1,
  "skip": 0,
  "limit": 100
}
```

**Status Codes:**
- `200 OK`: Trainings retrieved successfully
- `401 Unauthorized`: Not authenticated

#### GET /api/v1/trainings/{training_id}
Get specific training by ID.

**Response:**
```json
{
  "training": {
    "id": 1,
    "title": "Security Awareness Training",
    "description": "Comprehensive security awareness training",
    "category": "SECURITY",
    "level": "BEGINNER",
    "status": "PUBLISHED",
    "duration_minutes": 120,
    "credits": 2,
    "instructor_id": 1,
    "max_participants": 50,
    "created_at": "2023-12-01T10:00:00Z",
    "updated_at": "2023-12-01T10:00:00Z"
  }
}
```

**Status Codes:**
- `200 OK`: Training retrieved successfully
- `401 Unauthorized`: Not authenticated
- `404 Not Found`: Training not found

#### POST /api/v1/trainings
Create new training program.

**Request Body:**
```json
{
  "title": "string",
  "description": "string",
  "category": "SECURITY|LEADERSHIP|TECHNICAL|COMPLIANCE",
  "level": "BEGINNER|INTERMEDIATE|ADVANCED",
  "status": "PUBLISHED|DRAFT",
  "duration_minutes": "integer",
  "credits": "integer",
  "max_participants": "integer"
}
```

**Response:**
```json
{
  "training": {
    "id": 2,
    "title": "New Training Program",
    "description": "Training description",
    "category": "TECHNICAL",
    "level": "INTERMEDIATE",
    "status": "DRAFT",
    "duration_minutes": 180,
    "credits": 3,
    "instructor_id": 1,
    "max_participants": 30,
    "created_at": "2023-12-01T10:00:00Z"
  },
  "message": "Training created successfully"
}
```

**Status Codes:**
- `201 Created`: Training created successfully
- `401 Unauthorized`: Not authenticated
- `403 Forbidden`: Insufficient permissions
- `422 Unprocessable Entity`: Validation error

#### PUT /api/v1/trainings/{training_id}
Update training program.

**Request Body:**
```json
{
  "title": "string (optional)",
  "description": "string (optional)",
  "category": "SECURITY|LEADERSHIP|TECHNICAL|COMPLIANCE (optional)",
  "level": "BEGINNER|INTERMEDIATE|ADVANCED (optional)",
  "status": "PUBLISHED|DRAFT (optional)",
  "duration_minutes": "integer (optional)",
  "credits": "integer (optional)",
  "max_participants": "integer (optional)"
}
```

**Response:**
```json
{
  "training": {
    "id": 1,
    "title": "Updated Training Program",
    "description": "Updated description",
    "category": "SECURITY",
    "level": "BEGINNER",
    "status": "PUBLISHED",
    "duration_minutes": 120,
    "credits": 2,
    "instructor_id": 1,
    "max_participants": 50,
    "updated_at": "2023-12-01T10:00:00Z"
  },
  "message": "Training updated successfully"
}
```

**Status Codes:**
- `200 OK`: Training updated successfully
- `401 Unauthorized`: Not authenticated
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Training not found
- `422 Unprocessable Entity`: Validation error

#### DELETE /api/v1/trainings/{training_id}
Delete training program.

**Response:**
```json
{
  "message": "Training deleted successfully"
}
```

**Status Codes:**
- `200 OK`: Training deleted successfully
- `401 Unauthorized`: Not authenticated
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Training not found

---

### 📝 Registration Management Endpoints

#### GET /api/v1/registrations
Get training registrations with filtering.

**Query Parameters:**
- `skip`: Number of registrations to skip (default: 0)
- `limit`: Number of registrations to return (default: 100, max: 1000)
- `user_id`: Filter by user ID
- `training_id`: Filter by training ID
- `status`: Filter by status (REGISTERED, ATTENDED, CANCELLED, COMPLETED)

**Response:**
```json
{
  "registrations": [
    {
      "id": 1,
      "user_id": 1,
      "training_id": 1,
      "status": "REGISTERED",
      "registered_at": "2023-12-01T10:00:00Z",
      "attended_at": null,
      "completion_date": null,
      "feedback_score": null
    }
  ],
  "total": 1,
  "skip": 0,
  "limit": 100
}
```

**Status Codes:**
- `200 OK`: Registrations retrieved successfully
- `401 Unauthorized`: Not authenticated

#### GET /api/v1/registrations/{registration_id}
Get specific registration by ID.

**Response:**
```json
{
  "registration": {
    "id": 1,
    "user_id": 1,
    "training_id": 1,
    "status": "REGISTERED",
    "registered_at": "2023-12-01T10:00:00Z",
    "attended_at": null,
    "completion_date": null,
    "feedback_score": null
  }
}
```

**Status Codes:**
- `200 OK`: Registration retrieved successfully
- `401 Unauthorized**: Not authenticated
- `404 Not Found`: Registration not found

#### POST /api/v1/registrations
Register for a training program.

**Request Body:**
```json
{
  "training_id": "integer"
}
```

**Response:**
```json
{
  "registration": {
    "id": 2,
    "user_id": 1,
    "training_id": 2,
    "status": "REGISTERED",
    "registered_at": "2023-12-01T10:00:00Z",
    "attended_at": null,
    "completion_date": null,
    "feedback_score": null
  },
  "message": "Registration successful"
}
```

**Status Codes:**
- `201 Created`: Registration successful
- `400 Bad Request**: Already registered or training full
- `401 Unauthorized`: Not authenticated
- `404 Not Found`: Training not found
- `422 Unprocessable Entity**: Validation error

#### PUT /api/v1/registrations/{registration_id}
Update registration status.

**Request Body:**
```json
{
  "status": "REGISTERED|ATTENDED|CANCELLED|COMPLETED",
  "feedback_score": "integer (optional, 1-5)"
}
```

**Response:**
```json
{
  "registration": {
    "id": 1,
    "user_id": 1,
    "training_id": 1,
    "status": "ATTENDED",
    "registered_at": "2023-12-01T10:00:00Z",
    "attended_at": "2023-12-01T10:00:00Z",
    "completion_date": null,
    "feedback_score": null
  },
  "message": "Registration updated successfully"
}
```

**Status Codes:**
- `200 OK`: Registration updated successfully
- `401 Unauthorized`: Not authenticated
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Registration not found
- `422 Unprocessable Entity`: Validation error

#### DELETE /api/v1/registrations/{registration_id}
Cancel registration.

**Response:**
```json
{
  "message": "Registration cancelled successfully"
}
```

**Status Codes:**
- `200 OK`: Registration cancelled successfully
- `401 Unauthorized`: Not authenticated
- `404 Not Found`: Registration not found

---

## Data Models

### User Roles
```json
{
  "roles": [
    "EMPLOYEE",
    "KNOWLEDGE_MANAGER",
    "ADMIN"
  ]
}
```

### Training Categories
```json
{
  "categories": [
    "SECURITY",
    "LEADERSHIP",
    "TECHNICAL",
    "COMPLIANCE"
  ]
}
```

### Training Levels
```json
{
  "levels": [
    "BEGINNER",
    "INTERMEDIATE",
    "ADVANCED"
  ]
}
```

### Registration Statuses
```json
{
  "statuses": [
    "REGISTERED",
    "ATTENDED",
    "CANCELLED",
    "COMPLETED"
  ]
}
```

---

## Error Handling

The API returns detailed error information for troubleshooting:

### Validation Errors
```json
{
  "detail": [
    {
      "loc": ["body", "password"],
      "msg": "ensure this value has at least 8 characters",
      "type": "value_error.any_str.min_length"
    }
  ]
}
```

### Authentication Errors
```json
{
  "detail": "Could not validate credentials"
}
```

### Authorization Errors
```json
{
  "detail": "Not authorized to perform this action"
}
```

### Resource Not Found
```json
{
  "detail": "User with id 999 not found"
}
```

---

## Rate Limiting

The API implements rate limiting to prevent abuse:

- **Authentication endpoints**: 5 requests per minute
- **User management**: 100 requests per minute
- **Training management**: 200 requests per minute
- **Registration endpoints**: 100 requests per minute

Rate limit headers are included in responses:
- `X-RateLimit-Limit`: Maximum requests allowed
- `X-RateLimit-Remaining`: Remaining requests
- `X-RateLimit-Reset`: Time when limit resets (UTC timestamp)

---

## Pagination

List endpoints support pagination using `skip` and `limit` parameters:

### Example Request
```
GET /api/v1/users?skip=0&limit=10
```

### Response with Pagination Info
```json
{
  "users": [...],
  "total": 150,
  "skip": 0,
  "limit": 10
}
```

### Pagination Best Practices
- Use `skip` and `limit` for large datasets
- Don't request more than 1000 items per request
- Implement client-side pagination for better UX
- Use `total` field to calculate page numbers

---

## Webhooks

The API supports webhooks for real-time notifications:

### Available Events
- `user.registered`: New user registration
- `training.created`: New training program created
- `registration.completed`: Training registration completed

### Webhook Configuration
Configure webhook URLs in the application settings. Webhooks are sent as POST requests with event payload in JSON format.

### Webhook Payload Example
```json
{
  "event": "training.created",
  "timestamp": "2023-12-01T10:00:00Z",
  "data": {
    "training_id": 1,
    "title": "New Training Program",
    "created_by": 1
  }
}
```

---

## SDKs and Libraries

### Python SDK
```python
import requests

class OpenKMSAPI:
    def __init__(self, base_url, api_key):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({"Authorization": f"Bearer {api_key}"})

    def get_users(self):
        response = self.session.get(f"{self.base_url}/api/v1/users")
        return response.json()
```

### JavaScript SDK
```javascript
class OpenKMSAPI {
    constructor(baseUrl, apiKey) {
        this.baseUrl = baseUrl;
        this.headers = { 'Authorization': `Bearer ${apiKey}` };
    }

    async getUsers() {
        const response = await fetch(`${this.baseUrl}/api/v1/users`, {
            headers: this.headers
        });
        return response.json();
    }
}
```

---

## API Changelog

### Version 1.0.0 (2023-12-01)
- Initial API release
- User management endpoints
- Training management endpoints
- Registration management endpoints
- JWT authentication
- OpenAPI documentation

---

## Support

For API support and questions:
- **Documentation**: See `/docs` endpoint for interactive documentation
- **Issues**: Report bugs at [GitHub Issues](https://github.com/your-org/openkms/issues)
- **Email**: support@openkms.com

---

*Last updated: December 1, 2023*