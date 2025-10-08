from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded

from backend.app.core.config import settings
from backend.app.routers import users, admins
from backend.app.api.endpoints import test_email, password_reset
from backend.app.middleware.rate_limit import limiter, rate_limit_exceeded_handler
from backend.app.middleware.security_headers import SecurityHeadersMiddleware
from backend.app.core.logging.config import setup_logging, get_logger

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
    Log important configuration and system status
    """
    logger.info("=" * 60)
    logger.info(f"🚀 Starting {settings.project_name} v{settings.version}")
    logger.info("=" * 60)
    logger.info(f"📊 Environment: {settings.environment}")
    logger.info(f"🐛 Debug mode: {settings.debug}")
    logger.info(f"📝 Log level: {settings.log_level}")
    logger.info(f"📁 Log directory: {settings.log_dir}")
    logger.info(f"�� Rate limiting: ENABLED")
    logger.info(f"🛡️  Security headers: ENABLED")
    logger.info(f"🌐 CORS origins: {', '.join(settings.cors_origins_list)}")
    
    # Check email configuration
    if settings.email_enabled:
        logger.info(f"📧 Email service: CONFIGURED ({settings.smtp_host})")
    else:
        logger.warning("⚠️  Email service: NOT CONFIGURED - email features disabled")
    
    # Check database
    logger.info(f"🗄️  Database: PostgreSQL (configured)")
    
    logger.info("=" * 60)
    logger.info("✅ Application started successfully!")
    logger.info(f"📚 API Documentation: http://localhost:{settings.backend_port or 8006}/docs")
    logger.info("=" * 60)


@app.on_event("shutdown")
async def shutdown_event():
    """
    Application shutdown event
    """
    logger.info("=" * 60)
    logger.info(f"🛑 Shutting down {settings.project_name}")
    logger.info("=" * 60)


# === Custom Exception Handlers ===

@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    """
    Custom 404 handler
    """
    logger.warning(f"404 Not Found: {request.url.path} - Method: {request.method}")
    return JSONResponse(
        status_code=404,
        content={
            "error": "Not Found",
            "message": f"The requested resource {request.url.path} was not found",
            "path": str(request.url.path),
        }
    )


@app.exception_handler(500)
async def internal_error_handler(request: Request, exc):
    """
    Custom 500 handler
    """
    logger.error(f"Internal server error on {request.url.path}: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": "An unexpected error occurred. Please try again later.",
        }
    )
