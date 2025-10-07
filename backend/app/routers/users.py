from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from sqlalchemy.exc import IntegrityError
from datetime import timedelta
from typing import Any

from backend.app.db.session import get_session
from backend.app.models.user import User
from backend.app.schemas.user import UserCreate, UserRead, UserLogin
from backend.app.schemas.admin import Token
from backend.app.core.security import hash_password, verify_password, create_access_token

router = APIRouter(prefix="/users", tags=["Users"])

ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def register_user(user_in: UserCreate, session: AsyncSession = Depends(get_session)) -> UserRead:
    """
    Register a new user with hashed password.
    Ensures unique username/email.
    """

    # ✅ Check if username or email already exists before insert
    query = select(User).where(
        (User.username == user_in.username) | (User.email == user_in.email)
    )
    existing_user = (await session.execute(query)).scalar_one_or_none()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username or email already exists."
        )

    # ✅ Hash password before saving
    new_user = User(
        username=user_in.username,
        email=user_in.email,
        hashed_password=hash_password(user_in.password),
    )

    try:
        session.add(new_user)
        await session.commit()
        await session.refresh(new_user)
    except IntegrityError:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Could not create user due to integrity constraint."
        )
    except Exception as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while creating the user."
        )

    return new_user


@router.post("/login", response_model=Token)
async def login_user(user_in: UserLogin, session: AsyncSession = Depends(get_session)) -> dict[str, Any]:
    """
    Authenticate user and return JWT access + refresh tokens.
    """
    result = await session.execute(select(User).where(User.username == user_in.username))
    user = result.scalar_one_or_none()

    if not user or not user.is_active or not verify_password(user_in.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Generate JWT tokens
    token_data = {"id": user.id, "role": "superuser" if user.is_superuser else "user"}
    access_token = create_access_token(token_data, expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    refresh_token = create_access_token(token_data, expires_delta=timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS))

    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}