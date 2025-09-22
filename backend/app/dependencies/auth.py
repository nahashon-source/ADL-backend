from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from jose import JWTError

from backend.app.core.config import settings
from backend.app.db.session import get_session
from backend.app.models.admin import Admin
from backend.app.core.security import decode_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/admins/login")


async def get_current_admin(token: str = Depends(oauth2_scheme), session: AsyncSession = Depends(get_session)) -> Admin:
    """
    Validate JWT and return the current admin.
    Raises HTTPException if token is invalid or admin not found.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_access_token(token)
        admin_id: int = payload.get("id")
        if admin_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    result = await session.execute(select(Admin).where(Admin.id == admin_id))
    admin = result.scalar_one_or_none()
    if not admin or not admin.is_active:
        raise credentials_exception
    return admin
