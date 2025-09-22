from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from backend.app.db.session import get_session
from backend.app.models.user import User
from backend.app.models.admin import Admin
from backend.app.schemas.auth import LoginRequest, Token
from backend.app.core.security import verify_password, create_access_token

router = APIRouter(tags=["Authentication"])

@router.post("/login", response_model=Token)
async def login(form_data: LoginRequest, session: AsyncSession = Depends(get_session)):
    """
    Authenticate user or admin and return a JWT token.
    """
    # Check Admin first
    result = await session.exec(select(Admin).where(Admin.username == form_data.username))
    admin = result.first()
    if admin:
        if not verify_password(form_data.password, admin.hashed_password):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
        token_data = {"sub": admin.username, "role": "admin"}
        access_token = create_access_token(token_data)
        return {"access_token": access_token, "token_type": "bearer"}

    # Check regular User
    result = await session.exec(select(User).where(User.username == form_data.username))
    user = result.first()
    if user:
        if not verify_password(form_data.password, user.hashed_password):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
        token_data = {"sub": user.username, "role": "user"}
        access_token = create_access_token(token_data)
        return {"access_token": access_token, "token_type": "bearer"}

    # If neither found
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
