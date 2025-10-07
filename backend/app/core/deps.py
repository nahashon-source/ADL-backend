from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from backend.app.core.security import decode_access_token
from backend.app.db.session import get_session
from backend.app.models.user import User
from backend.app.models.admin import Admin

# Security scheme for extracting Bearer tokens from headers
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    session: AsyncSession = Depends(get_session)
) -> User:
    """
    Dependency to get the current authenticated user.
    Validates JWT token and returns the User object.
    
    Usage:
        @router.get("/me")
        async def get_me(current_user: User = Depends(get_current_user)):
            return current_user
    """
    token = credentials.credentials
    
    # Decode and validate token
    payload = decode_access_token(token)
    user_id: Optional[int] = payload.get("id")
    role: Optional[str] = payload.get("role")
    
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verify role is user or superuser
    if role not in ["user", "superuser"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions - User role required",
        )
    
    # Fetch user from database
    result = await session.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive",
        )
    
    return user


async def get_current_admin(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    session: AsyncSession = Depends(get_session)
) -> Admin:
    """
    Dependency to get the current authenticated admin.
    Validates JWT token and returns the Admin object.
    
    Usage:
        @router.get("/admin-only")
        async def admin_endpoint(current_admin: Admin = Depends(get_current_admin)):
            return {"admin": current_admin.username}
    """
    token = credentials.credentials
    
    # Decode and validate token
    payload = decode_access_token(token)
    admin_id: Optional[int] = payload.get("id")
    role: Optional[str] = payload.get("role")
    
    if admin_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verify role is admin or superadmin
    if role not in ["admin", "superadmin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions - Admin role required",
        )
    
    # Fetch admin from database
    result = await session.execute(select(Admin).where(Admin.id == admin_id))
    admin = result.scalar_one_or_none()
    
    if admin is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Admin not found",
        )
    
    if not admin.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin account is inactive",
        )
    
    return admin


async def get_current_superuser(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Dependency to require superuser permissions.
    Must be used after get_current_user.
    
    Usage:
        @router.delete("/users/{user_id}")
        async def delete_user(
            user_id: int,
            current_user: User = Depends(get_current_superuser)
        ):
            # Only superusers can access this
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions - Superuser role required",
        )
    return current_user


async def get_current_superadmin(
    current_admin: Admin = Depends(get_current_admin)
) -> Admin:
    """
    Dependency to require superadmin permissions.
    Must be used after get_current_admin.
    
    Usage:
        @router.delete("/admins/{admin_id}")
        async def delete_admin(
            admin_id: int,
            current_admin: Admin = Depends(get_current_superadmin)
        ):
            # Only superadmins can access this
    """
    if not current_admin.is_superadmin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions - Superadmin role required",
        )
    return current_admin
