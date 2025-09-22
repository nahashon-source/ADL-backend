from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.core.config import settings  # ✅ consistent import


# Create FastAPI instance
app = FastAPI(
    title=getattr(settings, "project_name", "ADL Backend"),
    debug=getattr(settings, "debug", False),
    version=getattr(settings, "version", "1.0.0"),
    description=getattr(
        settings,
        "description",
        "ADL Backend API for Authentication, Admin Panel, and Core Services."
    ),
    contact={
        "name": getattr(settings, "contact_name", "API Support"),
        "email": getattr(settings, "contact_email", "support@example.com"),  # 🔴 update later
    },
    license_info={
        "name": getattr(settings, "license_name", "MIT"),
        "url": getattr(settings, "license_url", "https://opensource.org/licenses/MIT"),
    },
    root_path=getattr(settings, "root_path", ""),  # useful for reverse proxy setups
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=getattr(settings, "cors_origins", ["*"]),  # 🔴 restrict in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check endpoint
@app.get("/health", tags=["System"])
async def health_check():
    """Return minimal system health info (safe for public exposure)."""
    return {
        "status": "ok",
        "project": getattr(settings, "project_name", "ADL Backend"),
        "version": getattr(settings, "version", "1.0.0"),
        "debug": getattr(settings, "debug", False),
        "environment": getattr(settings, "environment", "development"),
    }
