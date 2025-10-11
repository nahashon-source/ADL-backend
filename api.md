# ADL Backend API - Quick Reference Guide

**Base URL:** `https://localhost`  
**Version:** 1.0.2  
**Environment:** Production  
**Last Updated:** October 11, 2025

---

## 🔐 Important Notes

1. **Always use HTTPS:** `https://localhost` (NOT `http://` or `:8000`)
2. **Self-signed certificate:** Add `-k` flag to curl or accept browser warning
3. **Authentication:** Include `Authorization: Bearer <token>` header for protected endpoints
4. **Content-Type:** Always send `Content-Type: application/json` for POST/PUT requests

---

## 📚 Table of Contents

- [System Endpoints](#system-endpoints)
- [User Endpoints](#user-endpoints)
- [Admin Endpoints](#admin-endpoints)
- [Password Reset Endpoints](#password-reset-endpoints)
- [Response Format](#response-format)
- [Error Codes](#error-codes)

---

## 🏥 System Endpoints

### Health Check
**GET** `/health`

Returns system health status with database connectivity.

**Example:**
```bash
curl https://localhost/health -k
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-10-11T07:43:07.955769+00:00Z",
  "version": "1.0.2",
  "environment": "production",
  "project": "ADL Production",
  "database": {
    "connected": true,
    "error": null
  },
  "email_configured": true
}
```

---

### Metrics
**GET** `/metrics`

Returns Prometheus-compatible metrics for monitoring.

**Example:**
```bash
curl https://localhost/metrics -k
```

---

### API Documentation
**GET** `/docs` - Swagger UI (Interactive)  
**GET** `/redoc` - ReDoc (Alternative)

Access in browser: `https://localhost/docs`

---

## 👤 User Endpoints

### 1. Register New User
**POST** `/api/users/register`

**Request Body:**
```json
{
  "email": "user@example.com",
  "username": "username123",
  "password": "SecurePass123!",
  "full_name": "John Doe"
}
```

**Example:**
```bash
curl -X POST https://localhost/api/users/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "username": "username123",
    "password": "SecurePass123!",
    "full_name": "John Doe"
  }' \
  -k
```

**Response (201 Created):**
```json
{
  "id": 3,
  "username": "username123",
  "email": "user@example.com",
  "full_name": "John Doe",
  "is_active": true,
  "is_superuser": false,
  "created_at": "2025-10-11T07:42:37.391931",
  "updated_at": "2025-10-11T07:42:37.391947"
}
```

---

### 2. Login
**POST** `/api/users/login`

**Request Body:**
```json
{
  "username": "username123",
  "password": "SecurePass123!"
}
```

**Example:**
```bash
curl -X POST https://localhost/api/users/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "username123",
    "password": "SecurePass123!"
  }' \
  -k
```

**Response (200 OK):**
```json
{
  "access_token": "eyJhbGc...",
  "refresh_token": "eyJhbGc...",
  "token_type": "bearer"
}
```

**Token Expiry:**
- Access Token: 15 minutes
- Refresh Token: 7 days

---

### 3. Refresh Token
**POST** `/api/users/refresh`

**Request Body:**
```json
{
  "refresh_token": "eyJhbGc..."
}
```

**Example:**
```bash
curl -X POST https://localhost/api/users/refresh \
  -H "Content-Type: application/json" \
  -d '{
    "refresh_token": "your_refresh_token_here"
  }' \
  -k
```

**Response (200 OK):**
```json
{
  "access_token": "new_eyJhbGc...",
  "refresh_token": "new_eyJhbGc...",
  "token_type": "bearer"
}
```

---

### 4. Get Current User Profile 🔒
**GET** `/api/users/me`

**Protected:** Requires valid JWT access token

**Example:**
```bash
TOKEN="your_access_token_here"

curl -X GET https://localhost/api/users/me \
  -H "Authorization: Bearer $TOKEN" \
  -k
```

**Response (200 OK):**
```json
{
  "id": 3,
  "username": "username123",
  "email": "user@example.com",
  "full_name": "John Doe",
  "is_active": true,
  "is_superuser": false,
  "created_at": "2025-10-11T07:42:37.391931",
  "updated_at": "2025-10-11T07:42:37.391947"
}
```

---

### 5. Update User Profile 🔒
**PUT** `/api/users/me`

**Protected:** Requires valid JWT access token

**Request Body (all fields optional):**
```json
{
  "email": "newemail@example.com",
  "username": "newusername",
  "full_name": "Jane Doe"
}
```

**Example:**
```bash
TOKEN="your_access_token_here"

curl -X PUT https://localhost/api/users/me \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "Jane Doe"
  }' \
  -k
```

**Response (200 OK):**
```json
{
  "id": 3,
  "username": "username123",
  "email": "user@example.com",
  "full_name": "Jane Doe",
  "is_active": true,
  "is_superuser": false,
  "created_at": "2025-10-11T07:42:37.391931",
  "updated_at": "2025-10-11T08:00:00.000000"
}
```

---

### 6. Change Password 🔒
**POST** `/api/users/change-password`

**Protected:** Requires valid JWT access token

**Request Body:**
```json
{
  "old_password": "SecurePass123!",
  "new_password": "NewSecurePass456!"
}
```

**Example:**
```bash
TOKEN="your_access_token_here"

curl -X POST https://localhost/api/users/change-password \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "old_password": "SecurePass123!",
    "new_password": "NewSecurePass456!"
  }' \
  -k
```

**Response (200 OK):**
```json
{
  "message": "Password changed successfully"
}
```

---

## 👨‍💼 Admin Endpoints

### 1. Register New Admin
**POST** `/api/admins/register`

**Request Body:**
```json
{
  "email": "admin@example.com",
  "username": "admin123",
  "password": "AdminPass123!",
  "full_name": "Admin User"
}
```

**Example:**
```bash
curl -X POST https://localhost/api/admins/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@example.com",
    "username": "admin123",
    "password": "AdminPass123!",
    "full_name": "Admin User"
  }' \
  -k
```

---

### 2. Admin Login
**POST** `/api/admins/login`

**Request Body:**
```json
{
  "username": "admin123",
  "password": "AdminPass123!"
}
```

**Example:**
```bash
curl -X POST https://localhost/api/admins/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin123",
    "password": "AdminPass123!"
  }' \
  -k
```

**Response (200 OK):**
```json
{
  "access_token": "eyJhbGc...",
  "refresh_token": "eyJhbGc...",
  "token_type": "bearer"
}
```

---

### 3. Admin Refresh Token
**POST** `/api/admins/refresh`

Same format as user refresh token.

---

### 4. Get Current Admin Profile 🔒
**GET** `/api/admins/me`

**Protected:** Requires valid admin JWT access token

**Example:**
```bash
ADMIN_TOKEN="your_admin_access_token_here"

curl -X GET https://localhost/api/admins/me \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -k
```

---

### 5. List All Users 🔒 (Admin Only)
**GET** `/api/admins/users`

**Protected:** Requires valid admin JWT access token

**Query Parameters:**
- `page` (optional): Page number (default: 1)
- `page_size` (optional): Items per page (default: 10, max: 100)
- `is_active` (optional): Filter by active status (true/false)

**Example:**
```bash
ADMIN_TOKEN="your_admin_access_token_here"

# Get all users (paginated)
curl -X GET "https://localhost/api/admins/users?page=1&page_size=10" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -k

# Filter active users only
curl -X GET "https://localhost/api/admins/users?is_active=true&page=1&page_size=20" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -k
```

**Response (200 OK):**
```json
{
  "users": [
    {
      "id": 1,
      "username": "user1",
      "email": "user1@example.com",
      "full_name": "User One",
      "is_active": true,
      "is_superuser": false,
      "created_at": "2025-10-10T10:00:00",
      "updated_at": "2025-10-10T10:00:00"
    }
  ],
  "total": 1,
  "page": 1,
  "page_size": 10,
  "total_pages": 1
}
```

---

## 🔑 Password Reset Endpoints

### 1. Forgot Password
**POST** `/api/password/forgot-password`

Sends password reset email with token.

**Request Body:**
```json
{
  "email": "user@example.com"
}
```

**Example:**
```bash
curl -X POST https://localhost/api/password/forgot-password \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com"
  }' \
  -k
```

**Response (200 OK):**
```json
{
  "message": "If the email exists, a password reset link has been sent"
}
```

---

### 2. Reset Password
**POST** `/api/password/reset-password`

Reset password using token from email.

**Request Body:**
```json
{
  "token": "reset_token_from_email",
  "new_password": "NewSecurePass456!"
}
```

**Example:**
```bash
curl -X POST https://localhost/api/password/reset-password \
  -H "Content-Type: application/json" \
  -d '{
    "token": "your_reset_token",
    "new_password": "NewSecurePass456!"
  }' \
  -k
```

**Response (200 OK):**
```json
{
  "message": "Password has been reset successfully"
}
```

---

### 3. Test Email Configuration
**POST** `/api/password/test-email`

Sends a test email to verify SMTP configuration.

**Request Body:**
```json
{
  "recipient": "test@example.com"
}
```

**Example:**
```bash
curl -X POST https://localhost/api/password/test-email \
  -H "Content-Type: application/json" \
  -d '{
    "recipient": "test@example.com"
  }' \
  -k
```

---

## 📋 Response Format

### Success Response
All successful responses follow this format:
```json
{
  "field1": "value1",
  "field2": "value2"
}
```

### Error Response
All error responses follow this standardized format:
```json
{
  "error": "ErrorType",
  "message": "Human-readable error message",
  "status_code": 400,
  "timestamp": "2025-10-11T07:00:00.000000+00:00",
  "path": "/api/users/register",
  "request_id": "uuid-here",
  "details": {
    "additional": "context"
  }
}
```

---

## ⚠️ Error Codes

| Status Code | Error Type | Description |
|-------------|------------|-------------|
| 400 | ValidationError | Invalid request data |
| 401 | AuthenticationError | Invalid or missing credentials |
| 403 | AuthorizationError | Insufficient permissions |
| 404 | NotFoundError | Resource not found |
| 409 | DuplicateRecordError | Resource already exists |
| 422 | ValidationError | Pydantic validation failed |
| 429 | RateLimitExceeded | Too many requests (200/hour limit) |
| 500 | InternalServerError | Server error |
| 503 | ServiceUnavailable | Database or service unavailable |

---

## 🔒 Authentication Flow

### Step-by-step guide:

1. **Register a new user:**
```bash
curl -X POST https://localhost/api/users/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "username": "myuser",
    "password": "SecurePass123!",
    "full_name": "My Name"
  }' \
  -k
```

2. **Login to get tokens:**
```bash
curl -X POST https://localhost/api/users/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "myuser",
    "password": "SecurePass123!"
  }' \
  -k
```

3. **Save the access_token from response:**
```bash
TOKEN="eyJhbGc..."
```

4. **Use token for protected endpoints:**
```bash
curl -X GET https://localhost/api/users/me \
  -H "Authorization: Bearer $TOKEN" \
  -k
```

5. **Refresh token when expired (after 15 minutes):**
```bash
curl -X POST https://localhost/api/users/refresh \
  -H "Content-Type: application/json" \
  -d '{
    "refresh_token": "your_refresh_token"
  }' \
  -k
```

---

## 🛠️ Testing with Postman

### Setup:
1. **Base URL:** `https://localhost`
2. **Disable SSL verification:** Settings → General → SSL certificate verification OFF
3. **Environment variables:**
   - `base_url`: `https://localhost`
   - `access_token`: (set after login)

### Test Collection:
1. Register User → Save user credentials
2. Login User → Save `access_token` to environment
3. Get Profile → Use `{{access_token}}` in Authorization header
4. Update Profile
5. Change Password

---

## 📊 Rate Limiting

- **Limit:** 200 requests per hour per IP address
- **Header:** `X-RateLimit-*` headers in response
- **Exceeded:** Returns 429 with retry-after header

---

## 🔐 Security Headers

All responses include these security headers:
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `X-XSS-Protection: 1; mode=block`
- `Strict-Transport-Security: max-age=31536000; includeSubDomains`
- `Content-Security-Policy: default-src 'self'`
- `Referrer-Policy: strict-origin-when-cross-origin`
- `Permissions-Policy: geolocation=(), microphone=(), camera=()`

---

## 📝 Notes for Frontend Developers

### CORS Configuration:
Current allowed origins:
- `http://localhost:3000` (React dev server)
- `http://localhost:5173` (Vite dev server)
- `https://localhost:3000`
- `https://localhost:5173`

### Credentials:
Always include credentials in fetch requests:
```javascript
fetch('https://localhost/api/users/me', {
  credentials: 'include',
  headers: {
    'Authorization': `Bearer ${token}`
  }
})
```

### Token Storage:
- Store `access_token` in memory or sessionStorage (short-lived)
- Store `refresh_token` in httpOnly cookie (recommended) or localStorage
- Never expose tokens in URLs or logs

---

## 🐛 Troubleshooting

### Issue: Certificate Error
**Solution:** Add `-k` flag to curl or accept certificate in browser

### Issue: 404 Not Found
**Solution:** Make sure you're using `https://localhost` (not `:8000`)

### Issue: 401 Unauthorized
**Solution:** Check if token is expired (15min) or invalid format

### Issue: 429 Rate Limited
**Solution:** Wait for rate limit reset or check `Retry-After` header

### Issue: CORS Error
**Solution:** Check if your origin is in allowed origins list

---

**For more details, visit the interactive documentation at `https://localhost/docs`**