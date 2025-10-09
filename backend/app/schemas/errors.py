"""
Error Response Schemas

Standardized error response formats for consistent API responses.
"""

from typing import Any, Optional, List, Dict
from pydantic import BaseModel, Field
from datetime import datetime


class ErrorDetail(BaseModel):
    """Individual error detail"""
    field: Optional[str] = Field(None, description="Field that caused the error")
    message: str = Field(..., description="Error message")
    type: Optional[str] = Field(None, description="Error type")


class ErrorResponse(BaseModel):
    """
    Standardized error response format
    
    This ensures all API errors follow the same structure
    for easier client-side handling.
    """
    error: str = Field(..., description="Error type/category")
    message: str = Field(..., description="Human-readable error message")
    status_code: int = Field(..., description="HTTP status code")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="When the error occurred")
    path: Optional[str] = Field(None, description="API endpoint path")
    request_id: Optional[str] = Field(None, description="Unique request identifier for tracing")
    details: Optional[Any] = Field(None, description="Additional error details")
    
    class Config:
        json_schema_extra = {
            "example": {
                "error": "ValidationError",
                "message": "Invalid input data",
                "status_code": 422,
                "timestamp": "2024-10-08T12:00:00.000000",
                "path": "/api/users/register",
                "request_id": "abc-123-def-456",
                "details": {
                    "errors": [
                        {
                            "field": "email",
                            "message": "Invalid email format",
                            "type": "value_error"
                        }
                    ]
                }
            }
        }


class ValidationErrorResponse(ErrorResponse):
    """Validation error with detailed field errors"""
    error: str = Field(default="ValidationError", description="Error type")
    details: Dict[str, List[ErrorDetail]] = Field(
        ..., 
        description="Detailed validation errors by field"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "error": "ValidationError",
                "message": "Request validation failed",
                "status_code": 422,
                "timestamp": "2024-10-08T12:00:00.000000",
                "path": "/api/users/register",
                "details": {
                    "errors": [
                        {
                            "field": "email",
                            "message": "value is not a valid email address",
                            "type": "value_error.email"
                        },
                        {
                            "field": "password",
                            "message": "ensure this value has at least 8 characters",
                            "type": "value_error.any_str.min_length"
                        }
                    ]
                }
            }
        }


class DatabaseErrorResponse(ErrorResponse):
    """Database operation error"""
    error: str = Field(default="DatabaseError", description="Error type")
    
    class Config:
        json_schema_extra = {
            "example": {
                "error": "DatabaseError",
                "message": "Database operation failed",
                "status_code": 500,
                "timestamp": "2024-10-08T12:00:00.000000",
                "path": "/api/users/1"
            }
        }


class AuthenticationErrorResponse(ErrorResponse):
    """Authentication error"""
    error: str = Field(default="AuthenticationError", description="Error type")
    
    class Config:
        json_schema_extra = {
            "example": {
                "error": "AuthenticationError",
                "message": "Invalid credentials",
                "status_code": 401,
                "timestamp": "2024-10-08T12:00:00.000000",
                "path": "/api/users/login"
            }
        }
