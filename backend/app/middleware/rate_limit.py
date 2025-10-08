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
    try:
        if hasattr(request.state, "user_id"):
            return f"user:{request.state.user_id}"
    except Exception:
        pass
    
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0]
    return get_remote_address(request)


limiter = Limiter(
    key_func=get_identifier,
    default_limits=["200/hour"],
    storage_uri="memory://",
    headers_enabled=True,
)


def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded) -> Response:
    """Custom handler for rate limit exceeded errors"""
    logger.warning(f"Rate limit exceeded for {get_identifier(request)} on {request.url.path}")
    
    return JSONResponse(
        status_code=429,
        content={
            "error": "Rate limit exceeded",
            "message": "Too many requests. Please try again later.",
            "detail": str(exc.detail)
        },
        headers={"Retry-After": "60"}
    )
