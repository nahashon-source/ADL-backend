from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from jose import JWTError
from datetime import datetime, timezone  # ✅ Added timezone
from typing import Union
from fastapi import Request, status, HTTPException

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
from backend.app.core.logging.config import get_logger, get_request_id

logger = get_logger(__name__)

def create_error_response(
    request: Request,
    error_type: str,
    message: str,
    status_code: int,
    details: any = None,
) -> JSONResponse:
    """
    Create a standardized error response with request ID
    
    Args:
        request: FastAPI request object
        error_type: Type/category of error
        message: Human-readable error message
        status_code: HTTP status code
        details: Additional error details (optional)
    
    Returns:
        JSONResponse with standardized error format including request_id
    """
    error_response = {
        "error": error_type,
        "message": message,
        "status_code": status_code,
        "timestamp": datetime.now(timezone.utc).isoformat(),  # ✅ Fixed: timezone-aware
        "path": str(request.url.path),
    }
    
    # Get request_id from either request.state or logging context
    request_id = getattr(request.state, "request_id", None) or get_request_id()
    if request_id:
        error_response["request_id"] = request_id
    
    # Add details if provided
    if details is not None:
        error_response["details"] = details
    
    return JSONResponse(
        status_code=status_code,
        content=error_response
    )

# ============================================================================
# Custom Application Exception Handlers
# ============================================================================

async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    """
    Handle all custom AppException instances
    """
    logger.warning(
        f"{exc.__class__.__name__}: {exc.message} - Path: {request.url.path}",
        extra={"status_code": exc.status_code}
    )
    
    return create_error_response(
        request=request,
        error_type=exc.__class__.__name__.replace("Exception", "Error"),
        message=exc.message,
        status_code=exc.status_code,
        details=exc.details,
    )

# ============================================================================
# Authentication & Authorization Exception Handlers
# ============================================================================

async def authentication_exception_handler(
    request: Request, exc: Union[AuthenticationException, JWTError]
) -> JSONResponse:
    """
    Handle authentication-related exceptions
    """
    if isinstance(exc, JWTError):
        message = "Invalid or expired token"
        logger.warning(f"JWT Error: {str(exc)} - Path: {request.url.path}")
    else:
        message = exc.message
        logger.warning(f"Authentication failed: {message} - Path: {request.url.path}")
    
    return create_error_response(
        request=request,
        error_type="AuthenticationError",
        message=message,
        status_code=status.HTTP_401_UNAUTHORIZED,
    )

async def authorization_exception_handler(
    request: Request, exc: AuthorizationException
) -> JSONResponse:
    """
    Handle authorization (permission) exceptions
    """
    logger.warning(f"Authorization denied: {exc.message} - Path: {request.url.path}")
    
    return create_error_response(
        request=request,
        error_type="AuthorizationError",
        message=exc.message,
        status_code=status.HTTP_403_FORBIDDEN,
    )

# ============================================================================
# Database Exception Handlers
# ============================================================================

async def database_exception_handler(
    request: Request, exc: Union[DatabaseException, SQLAlchemyError]
) -> JSONResponse:
    """
    Handle database-related exceptions
    """
    if isinstance(exc, IntegrityError):
        # Handle unique constraint violations
        logger.warning(f"Database integrity error: {str(exc)} - Path: {request.url.path}")
        return create_error_response(
            request=request,
            error_type="DuplicateRecordError",
            message="A record with this information already exists",
            status_code=status.HTTP_409_CONFLICT,
        )
    
    elif isinstance(exc, DatabaseException):
        logger.error(f"Database error: {exc.message} - Path: {request.url.path}")
        return create_error_response(
            request=request,
            error_type="DatabaseError",
            message=exc.message,
            status_code=exc.status_code,
            details=exc.details,
        )
    
    else:
        # Generic SQLAlchemy error
        logger.error(
            f"Database operation failed: {str(exc)} - Path: {request.url.path}",
            exc_info=True
        )
        return create_error_response(
            request=request,
            error_type="DatabaseError",
            message="A database error occurred",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

async def record_not_found_handler(
    request: Request, exc: RecordNotFoundException
) -> JSONResponse:
    """
    Handle record not found exceptions
    """
    logger.info(f"Record not found: {exc.message} - Path: {request.url.path}")
    
    return create_error_response(
        request=request,
        error_type="NotFoundError",
        message=exc.message,
        status_code=status.HTTP_404_NOT_FOUND,
        details=exc.details,
    )
    
    
async def duplicate_record_handler(
    request: Request, exc: DuplicateRecordException
) -> JSONResponse:
    """
    Handle duplicate record exceptions (409 Conflict)
    """
    logger.warning(f"Duplicate record: {exc.message} - Path: {request.url.path}")
    
    return create_error_response(
        request=request,
        error_type="DuplicateRecordError",
        message=exc.message,
        status_code=status.HTTP_409_CONFLICT,
        details=exc.details,
    )

# ============================================================================
# Validation Exception Handlers
# ============================================================================

async def validation_exception_handler(
    request: Request, exc: Union[ValidationException, RequestValidationError]
) -> JSONResponse:
    """
    Handle validation errors (from Pydantic and custom validation)
    """
    if isinstance(exc, RequestValidationError):
        # FastAPI/Pydantic validation error
        errors = []
        for error in exc.errors():
            field = ".".join(str(loc) for loc in error["loc"] if loc != "body")
            errors.append({
                "field": field,
                "message": error["msg"],
                "type": error["type"],
            })
        
        logger.warning(
            f"Validation error: {len(errors)} field(s) invalid - Path: {request.url.path}",
            extra={"errors": errors}
        )
        
        return create_error_response(
            request=request,
            error_type="ValidationError",
            message="Request validation failed",
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            details={"errors": errors},
        )
    
    else:
        # Custom validation exception
        logger.warning(f"Validation error: {exc.message} - Path: {request.url.path}")
        return create_error_response(
            request=request,
            error_type="ValidationError",
            message=exc.message,
            status_code=exc.status_code,
            details=exc.details,
        )

# ============================================================================
# HTTP Exception Handlers
# ============================================================================

async def not_found_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Handle 404 Not Found errors
    """
    logger.info(f"404 Not Found: {request.url.path} - Method: {request.method}")
    
    return create_error_response(
        request=request,
        error_type="NotFoundError",
        message=f"The requested resource '{request.url.path}' was not found",
        status_code=status.HTTP_404_NOT_FOUND,
    )

async def method_not_allowed_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Handle 405 Method Not Allowed errors
    """
    logger.warning(f"405 Method Not Allowed: {request.method} {request.url.path}")
    
    return create_error_response(
        request=request,
        error_type="MethodNotAllowedError",
        message=f"Method '{request.method}' is not allowed for this endpoint",
        status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
    )

async def internal_server_error_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Handle 500 Internal Server Error
    Catches any unhandled exceptions
    """
    logger.error(
        f"Internal server error: {str(exc)} - Path: {request.url.path}",
        exc_info=True
    )
    
    return create_error_response(
        request=request,
        error_type="InternalServerError",
        message="An unexpected error occurred. Please try again later.",
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )

# ============================================================================
# Rate Limiting Exception Handler
# ============================================================================

async def rate_limit_exception_handler(
    request: Request, exc: RateLimitException
) -> JSONResponse:
    """
    Handle rate limit exceeded exceptions
    """
    logger.warning(f"Rate limit exceeded - Path: {request.url.path}")
    
    return create_error_response(
        request=request,
        error_type="RateLimitError",
        message=exc.message,
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
    )

# ============================================================================
# Email Service Exception Handler
# ============================================================================

async def email_service_exception_handler(
    request: Request, exc: EmailServiceException
) -> JSONResponse:
    """
    Handle email service exceptions
    """
    logger.error(f"Email service error: {exc.message} - Path: {request.url.path}")
    
    return create_error_response(
        request=request,
        error_type="EmailServiceError",
        message=exc.message,
        status_code=exc.status_code,
    )

# ============================================================================
# Additional HTTP Exception Handlers
# ============================================================================

async def bad_request_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Handle 400 Bad Request errors
    """
    logger.warning(f"400 Bad Request: {request.url.path} - {str(exc)}")
    
    return create_error_response(
        request=request,
        error_type="BadRequestError",
        message="The request could not be understood by the server",
        status_code=status.HTTP_400_BAD_REQUEST,
    )

async def unprocessable_entity_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Handle 422 Unprocessable Entity errors
    """
    logger.warning(f"422 Unprocessable Entity: {request.url.path}")
    
    return create_error_response(
        request=request,
        error_type="UnprocessableEntityError",
        message="The request was well-formed but contains semantic errors",
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
    )

async def service_unavailable_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Handle 503 Service Unavailable errors
    """
    logger.error(f"503 Service Unavailable: {request.url.path}")
    
    return create_error_response(
        request=request,
        error_type="ServiceUnavailableError",
        message="The service is temporarily unavailable. Please try again later.",
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
    )

async def timeout_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Handle request timeout errors
    """
    logger.warning(f"Request timeout: {request.url.path}")
    
    return create_error_response(
        request=request,
        error_type="TimeoutError",
        message="The request took too long to process. Please try again.",
        status_code=status.HTTP_504_GATEWAY_TIMEOUT,
    )

# ============================================================================
# FastAPI HTTPException Handler (catches all FastAPI HTTP exceptions)
# ============================================================================

async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """
    Handle FastAPI HTTPException to provide consistent error format
    This catches all FastAPI raised HTTP exceptions (401, 403, etc.)
    """
    # Map common status codes to error types
    error_type_map = {
        400: "BadRequestError",
        401: "AuthenticationError",
        403: "AuthorizationError",
        404: "NotFoundError",
        405: "MethodNotAllowedError",
        409: "ConflictError",
        422: "ValidationError",
        429: "RateLimitError",
        500: "InternalServerError",
        503: "ServiceUnavailableError",
        504: "TimeoutError",
    }
    
    error_type = error_type_map.get(exc.status_code, "HTTPError")
    
    logger.warning(f"HTTP {exc.status_code}: {exc.detail} - Path: {request.url.path}")
    
    return create_error_response(
        request=request,
        error_type=error_type,
        message=str(exc.detail),
        status_code=exc.status_code,
    )

# ============================================================================
# Generic Exception Handler
# ============================================================================

async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Catch-all handler for any unhandled exceptions
    This ensures no exception goes unhandled and provides a consistent response
    """
    logger.error(
        f"Unhandled exception: {exc.__class__.__name__} - {str(exc)} - Path: {request.url.path}",
        exc_info=True,
        extra={"exception_type": exc.__class__.__name__}
    )
    
    return create_error_response(
        request=request,
        error_type="UnexpectedError",
        message="An unexpected error occurred. Our team has been notified.",
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )