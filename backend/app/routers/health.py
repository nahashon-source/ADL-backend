from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from datetime import datetime, timezone

from backend.app.db.session import get_session
from backend.app.core.config import settings
from backend.app.core.logging.config import get_logger

logger = get_logger(__name__)

router = APIRouter(tags=["Health"])


@router.get("/health", status_code=status.HTTP_200_OK)
async def health_check(session: AsyncSession = Depends(get_session)) -> dict:
    """
    Health check endpoint that verifies system status.
    
    Returns:
        dict: System health information including:
            - status: "healthy" or "degraded"
            - timestamp: Current UTC timestamp
            - version: Application version
            - environment: Current environment (dev/prod)
            - project: Project name
            - database: Database connectivity info
            - email_configured: Whether email service is available
    """
    logger.info("Health check requested")
    
    # Check database connection
    db_connected = False
    db_error = None
    try:
        await session.execute(text("SELECT 1"))
        db_connected = True
        logger.info("✅ Database connection healthy")
    except Exception as e:
        db_error = str(e)
        logger.error(f"❌ Database connection failed: {db_error}")
    
    # Check email configuration
    email_configured = bool(settings.smtp_server and settings.smtp_port)
    
    health_data = {
        "status": "healthy" if db_connected else "degraded",
        "timestamp": datetime.now(timezone.utc).isoformat() + "Z",
        "version": "1.0.2",
        "environment": settings.environment,
        "project": "ADL Production",
        "database": {
            "connected": db_connected,
            "error": db_error
        },
        "email_configured": email_configured
    }
    
    logger.info(f"Health check completed - status: {health_data['status']}")
    return health_data