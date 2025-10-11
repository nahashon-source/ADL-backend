# ADL-backend
# 🔗 Frontend-Backend Integration Progress Tracker

## 📊 Overall Progress: 0% (0/45 tasks complete)

**Project:** ADL Production - React + FastAPI Integration  
**Last Updated:** October 10, 2025  
**Status:** 🚀 Ready to Start!

---

## 🎯 Integration Roadmap Overview

| Phase | Tasks | Status | Priority | Est. Time |
|-------|-------|--------|----------|-----------|
| **Phase 1: Backend Preparation** | 5 | ⬜ Not Started | 🔥 Critical | 1 hour |
| **Phase 2: React Project Setup** | 6 | ⬜ Not Started | 🔥 Critical | 2 hours |
| **Phase 3: Authentication Flow** | 8 | ⬜ Not Started | 🔥 Critical | 3 hours |
| **Phase 4: API Integration Layer** | 6 | ⬜ Not Started | High | 2 hours |
| **Phase 5: User Dashboard** | 5 | ⬜ Not Started | High | 2 hours |
| **Phase 6: Admin Dashboard** | 5 | ⬜ Not Started | Medium | 2 hours |
| **Phase 7: Error Handling** | 4 | ⬜ Not Started | High | 1 hour |
| **Phase 8: Testing & Polish** | 6 | ⬜ Not Started | Medium | 2 hours |
| **TOTAL** | **45** | **0%** | - | **~15 hours** |

---

## Phase 1: Backend Preparation ⬜ (0% Complete - 0/5)

**Purpose:** Ensure backend is ready for frontend connection

| Task | Status | Description | Notes |
|------|--------|-------------|-------|
| 1.1 | ⬜ Pending | Update CORS settings | Add frontend URL to allowed origins |
| 1.2 | ⬜ Pending | Test all API endpoints | Use Postman/Insomnia to verify |
| 1.3 | ⬜ Pending | Document API response formats | Create API contract document |
| 1.4 | ⬜ Pending | Setup backend on accessible URL | localhost:8000 or deploy |
| 1.5 | ⬜ Pending | Create API health check script | Quick connectivity test |

**Acceptance Criteria:**
- ✅ Backend accessible from frontend URL
- ✅ All 17 endpoints returning expected responses
- ✅ CORS allowing frontend requests
- ✅ API documentation available at /docs

---

## Phase 2: React Project Setup ⬜ (0% Complete - 0/6)

**Purpose:** Initialize React project with modern tooling

| Task | Status | Description | Technology Choice |
|------|--------|-------------|-------------------|
| 2.1 | ⬜ Pending | Create React app | Vite (recommended) or Create React App |
| 2.2 | ⬜ Pending | Install core dependencies | axios, react-router-dom, etc. |
| 2.3 | ⬜ Pending | Setup project structure | /components, /pages, /services, /hooks |
| 2.4 | ⬜ Pending | Configure environment variables | .env for API URL |
| 2.5 | ⬜ Pending | Setup CSS framework | Tailwind CSS / Material-UI / Bootstrap |
| 2.6 | ⬜ Pending | Create basic routing | Home, Login, Register, Dashboard |

**Tech Stack Recommendations:**
- **Build Tool:** Vite (fastest) ⭐ or Create React App
- **HTTP Client:** Axios (recommended) or Fetch API
- **Routing:** React Router v6
- **State Management:** Context API (start simple) or Redux Toolkit
- **UI Framework:** Tailwind CSS (flexible) or Material-UI (components)
- **Form Handling:** React Hook Form (recommended)

**Folder Structure:**
```
frontend/
├── src/
│   ├── components/      # Reusable components
│   ├── pages/          # Page components
│   ├── services/       # API calls
│   ├── hooks/          # Custom hooks
│   ├── context/        # Context providers
│   ├── utils/          # Helper functions
│   └── App.jsx
├── public/
└── package.json
```

---

## Phase 3: Authentication Flow ⬜ (0% Complete - 0/8)

**Purpose:** Implement complete user authentication

| Task | Status | Description | Backend Endpoint |
|------|--------|-------------|------------------|
| 3.1 | ⬜ Pending | Create Login page | POST /api/users/login |
| 3.2 | ⬜ Pending | Create Register page | POST /api/users/register |
| 3.3 | ⬜ Pending | Implement JWT token storage | localStorage/sessionStorage |
| 3.4 | ⬜ Pending | Create AuthContext (state mgmt) | Context API |
| 3.5 | ⬜ Pending | Implement token refresh logic | POST /api/users/refresh |
| 3.6 | ⬜ Pending | Create ProtectedRoute component | Check auth before render |
| 3.7 | ⬜ Pending | Implement Logout functionality | Clear tokens + redirect |
| 3.8 | ⬜ Pending | Add "Remember Me" option | Token persistence strategy |

**Key Features:**
- ✅ JWT token stored securely
- ✅ Auto token refresh before expiry
- ✅ Protected routes redirect to login
- ✅ Persistent login sessions
- ✅ Logout clears all auth data

**Security Checklist:**
- 🔒 Access token in memory (state)
- 🔒 Refresh token in httpOnly cookie (if possible) or localStorage
- 🔒 Auto logout on token expiry
- 🔒 HTTPS in production

---

## Phase 4: API Integration Layer ⬜ (0% Complete - 0/6)

**Purpose:** Create organized API communication layer

| Task | Status | Description | Files to Create |
|------|--------|-------------|-----------------|
| 4.1 | ⬜ Pending | Create axios instance with interceptors | services/api.js |
| 4.2 | ⬜ Pending | Create auth service | services/authService.js |
| 4.3 | ⬜ Pending | Create user service | services/userService.js |
| 4.4 | ⬜ Pending | Create admin service | services/adminService.js |
| 4.5 | ⬜ Pending | Add request/response interceptors | Auto add JWT, handle errors |
| 4.6 | ⬜ Pending | Create API error handler | Centralized error messages |

**API Services Structure:**
```javascript
// services/api.js - Axios instance with interceptors
// services/authService.js - login, register, logout, refresh
// services/userService.js - getProfile, updateProfile, changePassword
// services/adminService.js - listUsers, manageUsers
```

**Interceptor Features:**
- ✅ Auto-attach JWT to requests
- ✅ Auto-refresh expired tokens
- ✅ Centralized error handling
- ✅ Request/Response logging (dev mode)

---

## Phase 5: User Dashboard ⬜ (0% Complete - 0/5)

**Purpose:** Build user-facing pages and features

| Task | Status | Description | Backend Endpoint |
|------|--------|-------------|------------------|
| 5.1 | ⬜ Pending | Create User Profile page | GET /api/users/me |
| 5.2 | ⬜ Pending | Create Edit Profile form | PUT /api/users/me |
| 5.3 | ⬜ Pending | Create Change Password form | POST /api/users/change-password |
| 5.4 | ⬜ Pending | Create User Dashboard home | Display user stats |
| 5.5 | ⬜ Pending | Add Password Reset flow | POST /api/password/forgot-password |

**User Features:**
- ✅ View profile information
- ✅ Edit username, email
- ✅ Change password
- ✅ Dashboard with user stats
- ✅ Forgot/Reset password

---

## Phase 6: Admin Dashboard ⬜ (0% Complete - 0/5)

**Purpose:** Build admin management interface

| Task | Status | Description | Backend Endpoint |
|------|--------|-------------|------------------|
| 6.1 | ⬜ Pending | Create Admin Login page | POST /api/admins/login |
| 6.2 | ⬜ Pending | Create Admin Dashboard | Display admin stats |
| 6.3 | ⬜ Pending | Create User List page | GET /api/admins/users |
| 6.4 | ⬜ Pending | Add pagination to user list | Query params: page, page_size |
| 6.5 | ⬜ Pending | Add user filtering/search | Filter by is_active, search |

**Admin Features:**
- ✅ Separate admin login
- ✅ View all users (paginated)
- ✅ Filter active/inactive users
- ✅ Search users by email/username
- ✅ Admin-only route protection

---

## Phase 7: Error Handling & UX ⬜ (0% Complete - 0/4)

**Purpose:** Polish user experience and error handling

| Task | Status | Description | Implementation |
|------|--------|-------------|----------------|
| 7.1 | ⬜ Pending | Create Loading spinner component | Show during API calls |
| 7.2 | ⬜ Pending | Create Toast/Alert system | Success/Error notifications |
| 7.3 | ⬜ Pending | Handle API errors gracefully | User-friendly error messages |
| 7.4 | ⬜ Pending | Add form validation | Client-side validation |

**UX Improvements:**
- ✅ Loading states for all API calls
- ✅ Toast notifications for success/errors
- ✅ Friendly error messages
- ✅ Form validation before submit
- ✅ Disabled buttons during submission

---

## Phase 8: Testing & Polish ⬜ (0% Complete - 0/6)

**Purpose:** Ensure quality and production readiness

| Task | Status | Description | Tools |
|------|--------|-------------|-------|
| 8.1 | ⬜ Pending | Test all user flows | Manual testing |
| 8.2 | ⬜ Pending | Test all admin flows | Manual testing |
| 8.3 | ⬜ Pending | Test error scenarios | Invalid tokens, network errors |
| 8.4 | ⬜ Pending | Mobile responsiveness | Test on different screens |
| 8.5 | ⬜ Pending | Performance optimization | Lazy loading, code splitting |
| 8.6 | ⬜ Pending | Create deployment guide | Build + deploy instructions |

**Testing Checklist:**
- ✅ Login/Register works
- ✅ Token refresh works
- ✅ Protected routes work
- ✅ Logout works
- ✅ Profile CRUD works
- ✅ Admin features work
- ✅ Error handling works
- ✅ Mobile responsive
- ✅ Fast load times

---

## 🗂️ Project Files Checklist

### Backend Files (Already Complete ✅)
- [x] 17 API endpoints working
- [x] JWT authentication
- [x] CORS configured
- [x] Error handling
- [x] Request ID tracking

### Frontend Files (To Create)
- [ ] `frontend/src/services/api.js` - Axios config
- [ ] `frontend/src/services/authService.js` - Auth API calls
- [ ] `frontend/src/services/userService.js` - User API calls
- [ ] `frontend/src/services/adminService.js` - Admin API calls
- [ ] `frontend/src/context/AuthContext.jsx` - Auth state
- [ ] `frontend/src/components/ProtectedRoute.jsx` - Route guard
- [ ] `frontend/src/pages/Login.jsx` - Login page
- [ ] `frontend/src/pages/Register.jsx` - Register page
- [ ] `frontend/src/pages/Dashboard.jsx` - User dashboard
- [ ] `frontend/src/pages/Profile.jsx` - User profile
- [ ] `frontend/src/pages/admin/AdminDashboard.jsx` - Admin dashboard
- [ ] `frontend/src/pages/admin/UserList.jsx` - User management

---

## 🚀 Quick Start Guide

### Step 1: Backend Preparation (15 minutes)
```bash
# Update CORS in backend/.env
CORS_ORIGINS=http://localhost:3000,http://localhost:5173

# Restart backend
docker-compose restart backend
```

### Step 2: Create React App (5 minutes)
```bash
# Using Vite (recommended - faster)
npm create vite@latest frontend -- --template react
cd frontend
npm install

# OR using Create React App
npx create-react-app frontend
cd frontend
```

### Step 3: Install Dependencies (5 minutes)
```bash
npm install axios react-router-dom
npm install -D tailwindcss postcss autoprefixer  # If using Tailwind
```

### Step 4: Start Development (2 minutes)
```bash
# Terminal 1: Backend (already running)
cd backend
docker-compose up

# Terminal 2: Frontend
cd frontend
npm run dev  # Vite
# or
npm start    # Create React App
```

---

## 📋 Current Status Summary

| Category | Status | Notes |
|----------|--------|-------|
| **Backend API** | ✅ Complete | 17 endpoints, all tested |
| **Backend Auth** | ✅ Complete | JWT with refresh tokens |
| **Backend CORS** | ⚠️ Needs Update | Add frontend URL |
| **React Project** | ⬜ Not Started | Need to create |
| **API Services** | ⬜ Not Started | Need to create |
| **Auth Flow** | ⬜ Not Started | Need to implement |
| **User Pages** | ⬜ Not Started | Need to create |
| **Admin Pages** | ⬜ Not Started | Need to create |

---

## 🎯 Next Immediate Actions

### **TODAY - Phase 1 (1 hour)** ⭐ START HERE
1. ✅ Update CORS settings in backend
2. ✅ Test all API endpoints with Postman
3. ✅ Create API documentation/contract
4. ✅ Verify backend health check

### **THIS WEEK - Phase 2 & 3 (5 hours)**
1. Create React project with Vite
2. Setup project structure
3. Implement authentication flow
4. Create login/register pages

### **NEXT WEEK - Phase 4-6 (6 hours)**
1. Build API integration layer
2. Create user dashboard
3. Create admin dashboard

### **WEEK 3 - Phase 7-8 (3 hours)**
1. Add error handling
2. Test everything
3. Polish and deploy

---

## 💡 Pro Tips

1. **Start Simple** - Get login working first, then add features
2. **Use Postman** - Test backend endpoints before frontend integration
3. **Console.log Everything** - Debug API responses in browser console
4. **Check Network Tab** - Inspect requests/responses in browser DevTools
5. **Version Control** - Commit after each working feature
6. **Environment Variables** - Never hardcode API URLs

---

## 🆘 Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| CORS errors | Add frontend URL to backend CORS_ORIGINS |
| 401 Unauthorized | Check JWT token is being sent in headers |
| Token expired | Implement token refresh logic |
| Network error | Verify backend is running and accessible |
| Can't connect | Check API URL in frontend .env file |

---

## 📞 Support Checklist

Before asking for help, verify:
- [ ] Backend is running (`docker-compose ps`)
- [ ] Backend health check works (`curl http://localhost:8000/health`)
- [ ] Frontend is running (`npm run dev`)
- [ ] Check browser console for errors (F12)
- [ ] Check Network tab for failed requests
- [ ] Verify environment variables are correct

---

**Ready to start?** Let's begin with Phase 1! 🚀





















- ✅ User registration and authentication
- ✅ Admin management system
- ✅ JWT tokens (access + refresh)
- ✅ Email service with password reset
- ✅ Pagination and filtering
- ✅ Comprehensive error handling
- ✅ Request ID tracking
- ✅ Rate limiting
- ✅ Security headers
- ✅ Production logging

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Python 3.12+ (for local development)
- Git

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd ADL-backend





# ADL Backend - FastAPI Production Application

[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-00a393.svg)](https://fastapi.tiangolo.com)
[![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://www.python.org)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-blue.svg)](https://www.postgresql.org)
[![Docker](https://img.shields.io/badge/Docker-24.0+-2496ED.svg)](https://www.docker.com)
[![Tests](https://img.shields.io/badge/Tests-54%2F54-success.svg)](tests/)
[![Coverage](https://img.shields.io/badge/Coverage-68%25-yellow.svg)](tests/)

A production-ready FastAPI backend with PostgreSQL, JWT authentication, email service, and comprehensive testing.

## 📋 Table of Contents

- [Features](#-features)
- [Architecture](#-architecture)
- [Quick Start](#-quick-start)
- [Environment Setup](#-environment-setup)
- [API Documentation](#-api-documentation)
- [Development](#-development)
- [Testing](#-testing)
- [Deployment](#-deployment)
- [Security](#-security)
- [Troubleshooting](#-troubleshooting)

## ✨ Features

### Core Functionality
- 🔐 **JWT Authentication** - Secure token-based auth with refresh tokens
- 👥 **User Management** - Complete CRUD operations with profile management
- 👨‍💼 **Admin System** - Separate admin authentication and user management
- 📧 **Email Service** - Password reset with HTML templates
- 🔒 **Security Headers** - HSTS, CSP, X-Frame-Options, and more
- 🚦 **Rate Limiting** - 200 requests/hour per IP
- 📊 **Health Checks** - Database connectivity monitoring

### Technical Features
- 🐳 **Docker Containerization** - Multi-stage builds, optimized images
- 🗄️ **PostgreSQL** - Async database with connection pooling
- 🔄 **Database Migrations** - Automated Alembic migrations
- 🌐 **HTTPS** - Nginx reverse proxy with SSL
- 📝 **Structured Logging** - Request ID tracking, colored output
- ✅ **Comprehensive Testing** - 54 tests, 68% coverage
- 🎯 **Type Safety** - Full type hints with Pydantic v2

## 🏗️ Architecture

```
ADL-backend/
├── backend/
│   └── app/
│       ├── api/              # API routes
│       │   └── v1/
│       │       └── endpoints/
│       ├── core/             # Core functionality
│       │   ├── config.py
│       │   ├── security.py
│       │   ├── logging/
│       │   └── startup_checks.py
│       ├── models/           # SQLAlchemy models
│       ├── schemas/          # Pydantic schemas
│       ├── services/         # Business logic
│       └── main.py
├── alembic/                  # Database migrations
├── tests/                    # Test suite
├── docker-compose.yml
├── Dockerfile
└── requirements.txt
```

### Technology Stack

| Component | Technology | Version |
|-----------|-----------|---------|
| **Framework** | FastAPI | 0.104+ |
| **Language** | Python | 3.12+ |
| **Database** | PostgreSQL | 15 |
| **ORM** | SQLAlchemy | 2.0+ (async) |
| **Validation** | Pydantic | 2.0+ |
| **Migrations** | Alembic | 1.12+ |
| **Auth** | JWT + bcrypt | - |
| **Web Server** | Nginx | Alpine |
| **Container** | Docker | 24.0+ |

## 🚀 Quick Start

### Prerequisites

- Docker 24.0+ and Docker Compose
- Git

### 1. Clone Repository

```bash
git clone <repository-url>
cd ADL-backend
```

### 2. Environment Setup

```bash
# Copy environment template
cp .env.example .env

# Edit environment variables (see Environment Setup section)
nano .env
```

### 3. Start Services

```bash
# Build and start all services
docker compose up -d

# Wait for health checks (30 seconds)
sleep 30

# Verify services are running
docker compose ps
```

### 4. Verify Installation

```bash
# Check health endpoint
curl -k https://localhost/health

# Expected response:
# {
#   "status": "healthy",
#   "project": "ADL Production",
#   "version": "1.0.0",
#   "environment": "production",
#   "email_configured": true
# }
```

### 5. Access API Documentation

- **Swagger UI**: https://localhost/docs
- **ReDoc**: https://localhost/redoc

## 🔧 Environment Setup

### Required Environment Variables

Create a `.env` file with the following variables:

```bash
# Database Configuration
POSTGRES_USER=adl_user
POSTGRES_PASSWORD=your_secure_password_here
POSTGRES_DB=adl_db
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
DATABASE_URL=postgresql+asyncpg://adl_user:your_secure_password_here@postgres:5432/adl_db

# Application Settings
APP_NAME="ADL Production"
APP_VERSION="1.0.0"
ENVIRONMENT=production
DEBUG=false

# Security
SECRET_KEY=your-secret-key-min-32-chars-very-secure
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7

# CORS (Update for production)
ALLOWED_ORIGINS=["http://localhost:3000","http://localhost:5173"]

# Email Configuration (SMTP)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
FROM_EMAIL=noreply@yourdomain.com
FROM_NAME="ADL Application"

# Rate Limiting
RATE_LIMIT=200/hour
```

### Email Setup (Gmail Example)

1. **Enable 2-Factor Authentication** on your Google account
2. **Generate App Password**:
   - Go to: https://myaccount.google.com/apppasswords
   - Select "Mail" and your device
   - Copy the 16-character password
3. **Update .env**:
   ```bash
   SMTP_USER=your-email@gmail.com
   SMTP_PASSWORD=xxxx-xxxx-xxxx-xxxx  # App password
   ```

### Security Configuration

#### Generate Secure SECRET_KEY

```bash
# Using Python
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Using OpenSSL
openssl rand -base64 32
```

#### SSL Certificate (Production)

For production, replace self-signed certificates:

```bash
# Place your certificates in:
nginx/certs/cert.pem
nginx/certs/key.pem
```

## 📚 API Documentation

### Authentication Flow

```mermaid
sequenceDiagram
    Client->>API: POST /api/users/register
    API->>Database: Create User
    API-->>Client: User Created
    Client->>API: POST /api/users/login
    API->>Database: Verify Credentials
    API-->>Client: Access Token (15m) + Refresh Token (7d)
    Client->>API: GET /api/users/me (with token)
    API-->>Client: User Profile
    Client->>API: POST /api/users/refresh (with refresh token)
    API-->>Client: New Access Token
```

### Available Endpoints

#### User Endpoints (6)

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/users/register` | Register new user | No |
| POST | `/api/users/login` | Login user | No |
| POST | `/api/users/refresh` | Refresh JWT token | Yes (Refresh) |
| GET | `/api/users/me` | Get current user | Yes |
| PUT | `/api/users/me` | Update profile | Yes |
| POST | `/api/users/change-password` | Change password | Yes |

#### Admin Endpoints (5)

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/admins/register` | Register admin | No |
| POST | `/api/admins/login` | Login admin | No |
| POST | `/api/admins/refresh` | Refresh token | Yes (Refresh) |
| GET | `/api/admins/me` | Get admin profile | Yes (Admin) |
| GET | `/api/admins/users` | List all users | Yes (Admin) |

#### Password Reset Endpoints (3)

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/password/forgot-password` | Request reset | No |
| POST | `/api/password/reset-password` | Reset password | No |
| POST | `/api/password/test-email` | Test email config | No |

#### System Endpoints (3)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| GET | `/` | Welcome message |
| GET | `/docs` | Swagger UI |

### Request/Response Examples

#### Register User

```bash
curl -k https://localhost/api/users/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "johndoe",
    "email": "john@example.com",
    "password": "SecurePass123",
    "full_name": "John Doe"
  }'
```

Response:
```json
{
  "id": 1,
  "username": "johndoe",
  "email": "john@example.com",
  "full_name": "John Doe",
  "is_active": true,
  "is_superuser": false,
  "created_at": "2025-10-11T06:41:27.889026",
  "updated_at": "2025-10-11T06:41:27.889039"
}
```

#### Login

```bash
curl -k https://localhost/api/users/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "johndoe",
    "password": "SecurePass123"
  }'
```

Response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}
```

#### Get Current User (Protected)

```bash
curl -k https://localhost/api/users/me \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## 🔨 Development

### Local Development Setup

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt

# Start database only
docker compose up -d postgres

# Run locally (for development)
uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
```

### Database Migrations

```bash
# Create new migration
docker exec -it adl_backend alembic revision --autogenerate -m "description"

# Apply migrations
docker exec -it adl_backend alembic upgrade head

# Rollback one version
docker exec -it adl_backend alembic downgrade -1

# View migration history
docker exec -it adl_backend alembic history
```

### Adding New Endpoints

1. **Create endpoint** in `backend/app/api/v1/endpoints/`
2. **Define schemas** in `backend/app/schemas/`
3. **Add models** if needed in `backend/app/models/`
4. **Register router** in `backend/app/api/v1/api.py`
5. **Write tests** in `tests/`

### Code Style

```bash
# Format code (inside container)
docker exec -it adl_backend black backend/

# Type checking
docker exec -it adl_backend mypy backend/

# Linting
docker exec -it adl_backend flake8 backend/
```

## 🧪 Testing

### Running Tests

```bash
# Run all tests
docker exec -it adl_backend pytest

# Run with coverage
docker exec -it adl_backend pytest --cov=backend --cov-report=html

# Run specific test file
docker exec -it adl_backend pytest tests/test_health.py

# Run with verbose output
docker exec -it adl_backend pytest -v

# Run tests matching pattern
docker exec -it adl_backend pytest -k "test_user"
```

### Test Coverage

Current coverage: **68%** (1401/2067 lines)

| Component | Coverage |
|-----------|----------|
| Models | 100% |
| Schemas | 100% |
| Health Router | 92% |
| Security | 91% |
| Config | 95% |
| Logging | 86% |

### Writing Tests

Tests are located in `tests/` directory:

```python
# tests/test_users.py
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_user_registration(client: AsyncClient):
    response = await client.post(
        "/api/users/register",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "TestPass123"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "testuser"
```

## 🚢 Deployment

### Production Deployment Checklist

- [ ] **Environment Variables**
  - [ ] Change `SECRET_KEY` to strong random value
  - [ ] Update `POSTGRES_PASSWORD`
  - [ ] Configure production `ALLOWED_ORIGINS`
  - [ ] Set `DEBUG=false`
  - [ ] Configure real SMTP credentials
  
- [ ] **SSL Certificates**
  - [ ] Replace self-signed certificates
  - [ ] Configure domain name
  - [ ] Set up certificate renewal (Let's Encrypt)

- [ ] **Database**
  - [ ] Set up database backups
  - [ ] Configure persistent volumes
  - [ ] Set appropriate connection pool size

- [ ] **Security**
  - [ ] Review CORS settings
  - [ ] Configure rate limiting for production
  - [ ] Set up firewall rules
  - [ ] Enable monitoring/alerting

- [ ] **Performance**
  - [ ] Configure worker processes
  - [ ] Set up CDN for static files
  - [ ] Configure caching
  - [ ] Set up load balancing (if needed)

### Docker Deployment

```bash
# Build production image
docker compose build --no-cache

# Start services
docker compose up -d

# View logs
docker compose logs -f

# Stop services
docker compose down

# Complete cleanup (removes volumes)
docker compose down -v
```

### Health Monitoring

```bash
# Check container health
docker compose ps

# Monitor logs
docker compose logs -f backend

# Database health
curl -k https://localhost/health
```

## 🔒 Security

### Security Features Implemented

1. **Password Security**
   - Bcrypt hashing (cost factor: 12)
   - Minimum 8 characters with complexity requirements
   - Password change requires current password

2. **JWT Tokens**
   - Access tokens: 15 minutes expiry
   - Refresh tokens: 7 days expiry
   - Secure token generation with HS256

3. **HTTP Security Headers**
   - Strict-Transport-Security (HSTS)
   - Content-Security-Policy (CSP)
   - X-Frame-Options: DENY
   - X-Content-Type-Options: nosniff
   - X-XSS-Protection
   - Referrer-Policy: strict-origin-when-cross-origin
   - Permissions-Policy

4. **Rate Limiting**
   - 200 requests per hour per IP
   - Configurable via environment

5. **CORS**
   - Configurable allowed origins
   - Credentials support
   - Secure methods only

### Security Best Practices

- Always use HTTPS in production
- Rotate `SECRET_KEY` regularly
- Use strong database passwords
- Keep dependencies updated
- Review logs regularly
- Implement IP whitelisting for admin endpoints
- Set up automated security scanning

## 🐛 Troubleshooting

### Common Issues

#### 1. Container Won't Start

```bash
# Check logs
docker compose logs backend

# Common fixes:
# - Database not ready: Wait 30 seconds
# - Port conflict: Change ports in docker-compose.yml
# - Permission issues: Check file ownership
```

#### 2. Database Connection Failed

```bash
# Verify database is running
docker compose ps postgres

# Check database logs
docker compose logs postgres

# Test connection
docker exec -it adl_postgres psql -U adl_user -d adl_db -c "SELECT 1;"
```

#### 3. Email Not Sending

```bash
# Test email configuration
curl -k https://localhost/api/password/test-email \
  -H "Content-Type: application/json" \
  -d '{"email": "your-email@example.com"}'

# Common issues:
# - Wrong SMTP credentials
# - 2FA required (use App Password for Gmail)
# - Firewall blocking port 587
```

#### 4. Migrations Failed

```bash
# Reset database (WARNING: Deletes all data)
docker compose down -v
docker compose up -d

# Or manually run migrations
docker exec -it adl_backend alembic upgrade head
```

#### 5. SSL Certificate Errors

```bash
# For development, use -k flag
curl -k https://localhost/health

# For production, install proper certificates
# See: https://letsencrypt.org/
```

### Debug Mode

Enable detailed logging:

```bash
# In .env file
DEBUG=true

# Restart services
docker compose restart backend
```

### Getting Help

1. Check logs: `docker compose logs -f`
2. Review API docs: https://localhost/docs
3. Check health endpoint: `curl -k https://localhost/health`
4. Open an issue on GitHub

## 📝 API Changelog

### Version 1.0.0 (Current)

**Features:**
- Full user authentication system
- Admin management
- Password reset flow
- Email service
- Health monitoring
- Comprehensive testing (54 tests, 68% coverage)

**Breaking Changes:**
- None (initial release)

### Upcoming Features (v1.1.0)

- [ ] User avatar uploads
- [ ] Two-factor authentication (2FA)
- [ ] OAuth integration (Google, GitHub)
- [ ] Advanced user search
- [ ] Activity logging
- [ ] API versioning

## 📄 License

[Your License Here]

## 🤝 Contributing

Contributions welcome! Please read CONTRIBUTING.md first.

---

**Built with ❤️ using FastAPI**