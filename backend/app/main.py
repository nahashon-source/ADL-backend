from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded

from backend.app.core.config import settings
from backend.app.routers import users, admins
from backend.app.core.startup_checks import perform_startup_checks
from backend.app.api.endpoints import test_email, password_reset
from backend.app.middleware.rate_limit import limiter, rate_limit_exceeded_handler
from backend.app.middleware.security_headers import SecurityHeadersMiddleware
from backend.app.core.logging.config import setup_logging, get_logger
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from jose import JWTError

from backend.app.core.exceptions import (
    AppException,
    AuthenticationException,
    AuthorizationException,
    DatabaseException,
    ValidationException,
    RecordNotFoundException,
    DuplicateRecordException,
    RateLimitException,
    EmailServiceException,
)
from backend.app.core.exception_handlers import (
    app_exception_handler,
    authentication_exception_handler,
    authorization_exception_handler,
    database_exception_handler,
    record_not_found_handler,
    duplicate_record_handler,  # ← ADD THIS LINE
    validation_exception_handler,
    not_found_handler,
    method_not_allowed_handler,
    internal_server_error_handler,
    rate_limit_exception_handler,
    email_service_exception_handler,
    bad_request_handler,
    unprocessable_entity_handler,
    service_unavailable_handler,
    timeout_handler,
    generic_exception_handler,
    http_exception_handler,
)

# Setup enhanced logging
setup_logging(
    log_level=settings.log_level,
    log_dir=settings.log_dir,
    enable_json=settings.enable_json_logs,
    enable_console=settings.enable_console_logs,
)
logger = get_logger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title=settings.project_name,
    debug=settings.debug,
    version=settings.version,
    description=settings.description,
    contact={
        "name": settings.contact_name,
        "email": settings.contact_email,
    },
    license_info={
        "name": settings.license_name,
        "url": settings.license_url,
    },
    root_path=settings.root_path,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# === Add Rate Limiting ===
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)

# === Register Custom Exception Handlers ===
# IMPORTANT: Register specific handlers BEFORE general ones!

# Custom application exceptions (MOST SPECIFIC FIRST)
app.add_exception_handler(AuthenticationException, authentication_exception_handler)
app.add_exception_handler(AuthorizationException, authorization_exception_handler)
app.add_exception_handler(DuplicateRecordException, duplicate_record_handler)
app.add_exception_handler(RecordNotFoundException, record_not_found_handler)
app.add_exception_handler(ValidationException, validation_exception_handler)
app.add_exception_handler(RateLimitException, rate_limit_exception_handler)
app.add_exception_handler(EmailServiceException, email_service_exception_handler)
app.add_exception_handler(DatabaseException, database_exception_handler)
app.add_exception_handler(AppException, app_exception_handler)  # General AppException AFTER specific ones

# SQLAlchemy exceptions
app.add_exception_handler(SQLAlchemyError, database_exception_handler)
app.add_exception_handler(IntegrityError, database_exception_handler)

# JWT exceptions
app.add_exception_handler(JWTError, authentication_exception_handler)

# FastAPI validation exceptions
app.add_exception_handler(RequestValidationError, validation_exception_handler)

# HTTP exceptions (specific codes)
app.add_exception_handler(400, bad_request_handler)
app.add_exception_handler(404, not_found_handler)
app.add_exception_handler(405, method_not_allowed_handler)
app.add_exception_handler(422, unprocessable_entity_handler)
app.add_exception_handler(500, internal_server_error_handler)
app.add_exception_handler(503, service_unavailable_handler)
app.add_exception_handler(504, timeout_handler)

# FastAPI HTTP exceptions 
app.add_exception_handler(HTTPException, http_exception_handler)

# Generic catch-all handler (MUST BE LAST!)
app.add_exception_handler(Exception, generic_exception_handler)

# === Add Security Headers Middleware (FIRST - applies to all responses) ===
app.add_middleware(SecurityHeadersMiddleware)

# === CORS Configuration ===
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# === Include Routers ===
app.include_router(users.router, prefix="/api", tags=["Users"])
app.include_router(admins.router, prefix="/api", tags=["Admins"])
app.include_router(password_reset.router, prefix="/api/password", tags=["Password Reset"])
app.include_router(test_email.router, prefix="/api", tags=["Testing"])

# === System Endpoints ===

@app.get("/health", tags=["System"])
async def health_check():
    """
    Health check endpoint - no rate limit
    Returns minimal system health info.
    """
    return {
        "status": "healthy",
        "project": settings.project_name,
        "version": settings.version,
        "environment": settings.environment,
        "email_configured": settings.email_enabled,
    }

@app.get("/", tags=["System"])
async def root():
    """
    Root endpoint to confirm API is running.
    No rate limit applied to welcome endpoint.
    """
    return {
        "message": f"Welcome to {settings.project_name} API!",
        "version": settings.version,
        "docs": "/docs",
        "redoc": "/redoc",
        "health": "/health",
    }

# === Application Lifecycle Events ===

@app.on_event("startup")
async def startup_event():
    """
    Application startup event
    Perform startup checks and log important configuration
    """
    # Run startup checks first
    await perform_startup_checks(fail_fast=False)  # Set to True in production
    
    logger.info("=" * 60)
    logger.info(f"🚀 Starting {settings.project_name} v{settings.version}")
    logger.info("=" * 60)
    logger.info(f"📊 Environment: {settings.environment}")
    logger.info(f"🐛 Debug mode: {settings.debug}")
    logger.info(f"📝 Log level: {settings.log_level}")
    logger.info(f"📁 Log directory: {settings.log_dir}")
    logger.info(f"📈 Rate limiting: ENABLED")
    logger.info(f"🛡️  Security headers: ENABLED")
    logger.info(f"🌐 CORS origins: {', '.join(settings.cors_origins_list)}")
    
    # Check email configuration
    if settings.email_enabled:
        logger.info(f"📧 Email service: CONFIGURED ({settings.smtp_host})")
    else:
        logger.info("📧 Email service: NOT CONFIGURED")
    
    logger.info("🗄️  Database: PostgreSQL (configured)")
    logger.info("=" * 60)
    logger.info("✅ Application started successfully!")
    logger.info(f"📚 API Documentation: http://localhost:{settings.backend_port}/docs")
    logger.info("=" * 60)

@app.on_event("shutdown")
async def shutdown_event():
    """
    Application shutdown event
    """
    logger.info("=" * 60)
    logger.info(f"🛑 Shutting down {settings.project_name}")
    logger.info("=" * 60)