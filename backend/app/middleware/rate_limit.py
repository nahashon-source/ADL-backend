from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request, Response
from fastapi.responses import JSONResponse
import logging

logger = logging.getLogger(__name__)


def get_identifier(request: Request) -> str:
    """
    Get identifier for rate limiting.
    Uses IP address by default, but can be extended to use user_id from JWT.
    """
    # Try to get user from token first
    try:
        if hasattr(request.state, "user_id"):
            return f"user:{request.state.user_id}"
    except Exception:
        pass
    
    # Fallback to IP address
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0]
    return get_remote_address(request)


# Create limiter instance
limiter = Limiter(
    key_func=get_identifier,
    default_limits=["200/hour"],  # Default limit for all routes
    storage_uri="memory://",  # Use memory storage (can be Redis in production)
    headers_enabled=True,  # Add rate limit headers to responses
)


def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded) -> Response:
    """
    Custom handler for rate limit exceeded errors
    """
    logger.warning(
        f"Rate limit exceeded for {get_identifier(request)} on {request.url.path}"
    )
    
    return JSONResponse(
        status_code=429,
        content={
            "error": "Rate limit exceeded",
            "message": "Too many requests. Please try again later.",
            "detail": str(exc.detail)
        },
        headers={"Retry-After": str(exc.detail.split("Retry after ")[1].split(" ")[0]) if "Retry after" in exc.detail else "60"}
    )