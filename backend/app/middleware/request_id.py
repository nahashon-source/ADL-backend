"""
Request ID Middleware
Generates a unique ID for each request to enable request tracing
"""
import uuid
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
import logging

from backend.app.core.logging.config import set_request_id, get_logger

logger = get_logger(__name__)


class RequestIDMiddleware(BaseHTTPMiddleware):
    """
    Middleware that adds a unique request ID to each request.
    
    The request ID:
    - Is generated as a UUID4
    - Is stored in request.state.request_id
    - Is stored in logging context via ContextVar
    - Is added to response headers as X-Request-ID
    - Is included in all log messages automatically
    """
    
    async def dispatch(self, request: Request, call_next):
        # Generate a unique request ID
        request_id = str(uuid.uuid4())
        
        # Store in request state (accessible throughout request lifecycle)
        request.state.request_id = request_id
        
        # Store in logging context (automatically added to all logs)
        set_request_id(request_id)
        
        # Log incoming request
        logger.info(
            f"Incoming request: {request.method} {request.url.path}"
        )
        
        # Process the request
        try:
            response: Response = await call_next(request)
            
            # Log successful completion
            logger.info(
                f"Request completed: {request.method} {request.url.path} - Status: {response.status_code}"
            )
            
        except Exception as e:
            # Log error with full traceback
            logger.error(
                f"Request failed: {request.method} {request.url.path} - Error: {str(e)}",
                exc_info=True
            )
            raise
        
        # Add request ID to response headers
        response.headers["X-Request-ID"] = request_id
        
        return response