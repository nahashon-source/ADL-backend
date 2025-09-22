from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from backend.app.core.security import decode_access_token
from backend.app.models.user import User
from backend.app.models.admin import Admin
from backend.app.db.session import get_session
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

async def get_current_user(token: str = Depends(oauth2_scheme), session: AsyncSession = Depends(get_session)):
    """
    Extract current logged-in user/admin from JWT.
    """
    payload = decode_access_token(token)
    username = payload.get("sub")
    role = payload.get("role")

    if role == "admin":
        result = await session.exec(select(Admin).where(Admin.username == username))
        user = result.first()
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Admin not found")
        return user
    else:
        result = await session.exec(select(User).where(User.username == username))
        user = result.first()
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
        return user

async def get_current_admin(current_user: Admin = Depends(get_current_user)):
    """
    Ensure the current user is an admin.
    """
    if not isinstance(current_user, Admin):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    return current_user
