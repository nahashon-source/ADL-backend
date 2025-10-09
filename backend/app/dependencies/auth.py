from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from jose import JWTError

from backend.app.core.config import settings
from backend.app.db.session import get_session
from backend.app.models.admin import Admin
from backend.app.models.user import User
from backend.app.core.security import decode_access_token
from backend.app.core.exceptions import AuthenticationException, AuthorizationException

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/admins/login")


async def get_current_admin(
    token: str = Depends(oauth2_scheme),
    session: AsyncSession = Depends(get_session)
) -> Admin:
    """
    Validate JWT and return the current admin.
    Raises AuthenticationException if token is invalid, expired, or admin not found.
    Raises AuthorizationException if admin is not active.
    """
    try:
        payload = decode_access_token(token)
        admin_id: int = payload.get("id")
        if admin_id is None:
            raise AuthenticationException("Invalid token: missing admin ID")
    except JWTError as e:
        raise AuthenticationException(f"Invalid or expired token: {str(e)}")

    result = await session.execute(select(Admin).where(Admin.id == admin_id))
    admin = result.scalar_one_or_none()
    
    if not admin:
        raise AuthenticationException("Admin not found")
    
    if not admin.is_active:
        raise AuthorizationException("Admin account is inactive")
    
    return admin


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: AsyncSession = Depends(get_session)
) -> User:
    """
    Validate JWT and return the current user.
    Raises AuthenticationException if token is invalid, expired, or user not found.
    Raises AuthorizationException if user is not active.
    """
    try:
        payload = decode_access_token(token)
        user_id: int = payload.get("id")
        if user_id is None:
            raise AuthenticationException("Invalid token: missing user ID")
    except JWTError as e:
        raise AuthenticationException(f"Invalid or expired token: {str(e)}")

    result = await session.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise AuthenticationException("User not found")
    
    if not user.is_active:
        raise AuthorizationException("User account is inactive")
    
    return user