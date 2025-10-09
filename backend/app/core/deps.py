from typing import Optional
from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from jose import JWTError

from backend.app.core.security import decode_access_token
from backend.app.db.session import get_session
from backend.app.models.user import User
from backend.app.models.admin import Admin
from backend.app.core.logging.config import get_logger

# Import custom exceptions instead of HTTPException
from backend.app.core.exceptions import (
    AuthenticationException,
    AuthorizationException,
    RecordNotFoundException,
)

logger = get_logger(__name__)


def _extract_token_from_request(request: Request) -> str:
    """
    Extract Bearer token from Authorization header.
    
    Args:
        request: FastAPI request object
    
    Returns:
        str: Token string
    
    Raises:
        AuthenticationException: If token missing or malformed
    """
    authorization = request.headers.get("Authorization")
    
    if not authorization:
        logger.warning("Authentication failed: Missing Authorization header")
        raise AuthenticationException("Missing authentication token")
    
    # Check if it starts with "Bearer "
    if not authorization.startswith("Bearer "):
        logger.warning(f"Authentication failed: Invalid Authorization header format")
        raise AuthenticationException("Invalid authorization header format")
    
    # Extract token (everything after "Bearer ")
    token = authorization[7:].strip()
    
    if not token:
        logger.warning("Authentication failed: Empty Bearer token")
        raise AuthenticationException("Missing authentication token")
    
    return token


async def get_current_user(
    request: Request,
    session: AsyncSession = Depends(get_session)
) -> User:
    """
    Dependency to get the current authenticated user.
    Validates JWT token and returns the User object.
    
    Args:
        request: FastAPI request object
        session: Database session
    
    Returns:
        User: Authenticated user object
    
    Raises:
        AuthenticationException: If token invalid, expired, or user not found
        AuthorizationException: If user lacks required role or is inactive
    
    Usage:
        @router.get("/me")
        async def get_me(current_user: User = Depends(get_current_user)):
            return current_user
    """
    # Extract token from request
    token = _extract_token_from_request(request)
    
    try:
        # Decode and validate token
        payload = decode_access_token(token)
        user_id: Optional[int] = payload.get("id")
        role: Optional[str] = payload.get("role")
        
        if user_id is None:
            logger.warning("Authentication failed: Invalid token structure (missing user ID)")
            raise AuthenticationException("Invalid authentication credentials")
        
        # Verify role is user or superuser
        if role not in ["user", "superuser"]:
            logger.warning(f"Authorization failed: Invalid role '{role}' for user operation")
            raise AuthorizationException("Not enough permissions - User role required")
    
    except JWTError as e:
        logger.warning(f"JWT validation failed: {str(e)}")
        raise AuthenticationException("Invalid or expired token")
    except AuthenticationException:
        raise
    except AuthorizationException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error during token validation: {str(e)}", exc_info=True)
        raise AuthenticationException("Token validation failed")
    
    # Fetch user from database
    try:
        result = await session.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        
        if user is None:
            logger.warning(f"User not found: ID {user_id}")
            raise RecordNotFoundException(resource="User", resource_id=user_id)
        
        if not user.is_active:
            logger.warning(f"User account is inactive: {user.username}")
            raise AuthenticationException("User account is inactive or disabled")
        
        logger.debug(f"User authenticated successfully: {user.username}")
        return user
    
    except RecordNotFoundException:
        raise
    except AuthenticationException:
        raise
    except Exception as e:
        logger.error(f"Database error during user lookup: {str(e)}", exc_info=True)
        raise


async def get_current_admin(
    request: Request,
    session: AsyncSession = Depends(get_session)
) -> Admin:
    """
    Dependency to get the current authenticated admin.
    Validates JWT token and returns the Admin object.
    
    Args:
        request: FastAPI request object
        session: Database session
    
    Returns:
        Admin: Authenticated admin object
    
    Raises:
        AuthenticationException: If token invalid, expired, or admin not found
        AuthorizationException: If admin lacks required role or is inactive
    
    Usage:
        @router.get("/admin-only")
        async def admin_endpoint(current_admin: Admin = Depends(get_current_admin)):
            return {"admin": current_admin.username}
    """
    # Extract token from request
    token = _extract_token_from_request(request)
    
    try:
        # Decode and validate token
        payload = decode_access_token(token)
        admin_id: Optional[int] = payload.get("id")
        role: Optional[str] = payload.get("role")
        
        if admin_id is None:
            logger.warning("Authentication failed: Invalid token structure (missing admin ID)")
            raise AuthenticationException("Invalid authentication credentials")
        
        # Verify role is admin or superadmin
        if role not in ["admin", "superadmin"]:
            logger.warning(f"Authorization failed: Invalid role '{role}' for admin operation")
            raise AuthorizationException("Not enough permissions - Admin role required")
    
    except JWTError as e:
        logger.warning(f"JWT validation failed: {str(e)}")
        raise AuthenticationException("Invalid or expired token")
    except AuthenticationException:
        raise
    except AuthorizationException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error during token validation: {str(e)}", exc_info=True)
        raise AuthenticationException("Token validation failed")
    
    # Fetch admin from database
    try:
        result = await session.execute(select(Admin).where(Admin.id == admin_id))
        admin = result.scalar_one_or_none()
        
        if admin is None:
            logger.warning(f"Admin not found: ID {admin_id}")
            raise RecordNotFoundException(resource="Admin", resource_id=admin_id)
        
        if not admin.is_active:
            logger.warning(f"Admin account is inactive: {admin.username}")
            raise AuthenticationException("Admin account is inactive or disabled")
        
        logger.debug(f"Admin authenticated successfully: {admin.username}")
        return admin
    
    except RecordNotFoundException:
        raise
    except AuthenticationException:
        raise
    except Exception as e:
        logger.error(f"Database error during admin lookup: {str(e)}", exc_info=True)
        raise


async def get_current_superuser(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Dependency to require superuser permissions.
    Must be used after get_current_user.
    
    Args:
        current_user: Current authenticated user
    
    Returns:
        User: Current user (guaranteed to be superuser)
    
    Raises:
        AuthorizationException: If user is not a superuser
    
    Usage:
        @router.delete("/users/{user_id}")
        async def delete_user(
            user_id: int,
            current_user: User = Depends(get_current_superuser)
        ):
            # Only superusers can access this
    """
    if not current_user.is_superuser:
        logger.warning(f"Superuser permission denied for user: {current_user.username}")
        raise AuthorizationException("Not enough permissions - Superuser role required")
    return current_user


async def get_current_superadmin(
    current_admin: Admin = Depends(get_current_admin)
) -> Admin:
    """
    Dependency to require superadmin permissions.
    Must be used after get_current_admin.
    
    Args:
        current_admin: Current authenticated admin
    
    Returns:
        Admin: Current admin (guaranteed to be superadmin)
    
    Raises:
        AuthorizationException: If admin is not a superadmin
    
    Usage:
        @router.delete("/admins/{admin_id}")
        async def delete_admin(
            admin_id: int,
            current_admin: Admin = Depends(get_current_superadmin)
        ):
            # Only superadmins can access this
    """
    if not current_admin.is_superadmin:
        logger.warning(f"Superadmin permission denied for admin: {current_admin.username}")
        raise AuthorizationException("Not enough permissions - Superadmin role required")
    return current_admin