"""
Custom Exception Classes for FastAPI Application

This module defines custom exceptions that provide better error handling
and more informative error messages throughout the application.

CRITICAL FIX: Changed AppException to inherit from Exception (not HTTPException)
This ensures our custom exception handlers are called instead of FastAPI's default handler.
"""

from typing import Any, Optional
from fastapi import status


class AppException(Exception):
    """
    Base exception class for application-specific exceptions.
    All custom exceptions should inherit from this class.
    
    IMPORTANT: Inherits from Exception (NOT HTTPException) to ensure
    FastAPI routes all exceptions through our custom handlers.
    """
    def __init__(
        self,
        message: str,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        details: Optional[Any] = None,
    ):
        self.message = message
        self.status_code = status_code
        self.details = details
        super().__init__(self.message)


# ============================================================================
# Authentication & Authorization Exceptions
# ============================================================================

class AuthenticationException(AppException):
    """Base class for authentication-related exceptions"""
    def __init__(self, message: str = "Authentication failed", details: Optional[Any] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_401_UNAUTHORIZED,
            details=details
        )


class InvalidCredentialsException(AuthenticationException):
    """Raised when login credentials are invalid"""
    def __init__(self, message: str = "Invalid username or password"):
        super().__init__(message=message)


class TokenExpiredException(AuthenticationException):
    """Raised when JWT token has expired"""
    def __init__(self, message: str = "Token has expired"):
        super().__init__(message=message)


class InvalidTokenException(AuthenticationException):
    """Raised when JWT token is invalid or malformed"""
    def __init__(self, message: str = "Invalid or malformed token"):
        super().__init__(message=message)


class AuthorizationException(AppException):
    """Raised when user doesn't have permission to access resource"""
    def __init__(self, message: str = "You don't have permission to access this resource"):
        super().__init__(
            message=message,
            status_code=status.HTTP_403_FORBIDDEN
        )


class InactiveUserException(AuthenticationException):
    """Raised when user account is inactive/disabled"""
    def __init__(self, message: str = "User account is inactive or disabled"):
        super().__init__(message=message)


# ============================================================================
# Database Exceptions
# ============================================================================

class DatabaseException(AppException):
    """Base class for database-related exceptions"""
    def __init__(self, message: str = "Database operation failed", details: Optional[Any] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details=details
        )


class RecordNotFoundException(AppException):
    """Raised when a database record is not found"""
    def __init__(self, resource: str = "Record", resource_id: Optional[Any] = None):
        message = f"{resource} not found"
        if resource_id:
            message += f" (ID: {resource_id})"
        super().__init__(
            message=message,
            status_code=status.HTTP_404_NOT_FOUND,
            details={"resource": resource, "id": resource_id}
        )


class DuplicateRecordException(AppException):
    """Raised when attempting to create a duplicate record"""
    def __init__(self, resource: str = "Record", field: Optional[str] = None):
        message = f"{resource} already exists"
        if field:
            message += f" (duplicate {field})"
        super().__init__(
            message=message,
            status_code=status.HTTP_409_CONFLICT,
            details={"resource": resource, "field": field}
        )


class DatabaseConnectionException(DatabaseException):
    """Raised when database connection fails"""
    def __init__(self, message: str = "Failed to connect to database"):
        super().__init__(message=message)


# ============================================================================
# Validation Exceptions
# ============================================================================

class ValidationException(AppException):
    """Raised when data validation fails"""
    def __init__(self, message: str = "Validation failed", errors: Optional[list] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            details={"errors": errors} if errors else None
        )


class InvalidInputException(ValidationException):
    """Raised when input data is invalid"""
    def __init__(self, field: str, message: str):
        super().__init__(
            message=f"Invalid {field}: {message}",
            errors=[{"field": field, "message": message}]
        )


# ============================================================================
# Business Logic Exceptions
# ============================================================================

class BusinessLogicException(AppException):
    """Base class for business logic exceptions"""
    def __init__(self, message: str, status_code: int = status.HTTP_400_BAD_REQUEST):
        super().__init__(message=message, status_code=status_code)


class PasswordMismatchException(BusinessLogicException):
    """Raised when password confirmation doesn't match"""
    def __init__(self, message: str = "Passwords do not match"):
        super().__init__(message=message)


class WeakPasswordException(BusinessLogicException):
    """Raised when password doesn't meet security requirements"""
    def __init__(self, message: str = "Password does not meet security requirements"):
        super().__init__(message=message)


class InvalidPasswordResetTokenException(BusinessLogicException):
    """Raised when password reset token is invalid or expired"""
    def __init__(self, message: str = "Invalid or expired password reset token"):
        super().__init__(message=message)


class EmailAlreadyExistsException(DuplicateRecordException):
    """Raised when email already exists in database"""
    def __init__(self, email: str):
        super().__init__(resource="User", field="email")
        self.message = f"Email '{email}' is already registered"


class UsernameAlreadyExistsException(DuplicateRecordException):
    """Raised when username already exists in database"""
    def __init__(self, username: str):
        super().__init__(resource="User", field="username")
        self.message = f"Username '{username}' is already taken"


# ============================================================================
# Rate Limiting Exceptions
# ============================================================================

class RateLimitException(AppException):
    """Raised when rate limit is exceeded"""
    def __init__(self, message: str = "Rate limit exceeded. Please try again later."):
        super().__init__(
            message=message,
            status_code=status.HTTP_429_TOO_MANY_REQUESTS
        )


# ============================================================================
# Email Service Exceptions
# ============================================================================

class EmailServiceException(AppException):
    """Raised when email service fails"""
    def __init__(self, message: str = "Failed to send email"):
        super().__init__(
            message=message,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


class EmailNotConfiguredException(EmailServiceException):
    """Raised when email service is not configured"""
    def __init__(self, message: str = "Email service is not configured"):
        super().__init__(message=message)