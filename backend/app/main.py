from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.core.config import settings  # consistent import

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
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/health", tags=["System"])
async def health_check():
    """
    Minimal system health info.
    Safe for public exposure.
    """
    return {
        "status": "ok",
        "project": settings.project_name,
        "version": settings.version,
        "debug": settings.debug,
        "environment": settings.environment,
    }
