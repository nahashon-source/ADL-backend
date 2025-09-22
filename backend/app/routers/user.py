from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from backend.app.db.session import get_session
from backend.app.models.user import User
from backend.app.schemas.user import UserCreate, UserRead
from backend.app.core.security import hash_password

router = APIRouter(prefix="/users", tags=["Users"])

@router.post("/register", response_model=UserRead)
async def register_user(user_in: UserCreate, session: AsyncSession = Depends(get_session)):
    """
    Register a new user with hashed password.
    """
    # Check if username or email exists
    result = await session.execute(select(User).where((User.username == user_in.username) | (User.email == user_in.email)))
    existing_user = result.scalar_one_or_none()
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username or email already exists.")

    # Create new user
    new_user = User(
        username=user_in.username,
        email=user_in.email,
        hashed_password=hash_password(user_in.password)
    )
    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)
    return new_user
