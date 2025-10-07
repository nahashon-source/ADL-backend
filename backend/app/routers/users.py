from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from sqlalchemy.exc import IntegrityError
from datetime import timedelta
from typing import Any
from datetime import datetime

from backend.app.db.session import get_session
from backend.app.models.user import User
from backend.app.schemas.user import UserCreate, UserRead, UserLogin
from backend.app.schemas.admin import Token, TokenRefresh, RefreshTokenRequest
from backend.app.core.security import hash_password, verify_password, create_access_token
from backend.app.core.deps import get_current_user
from backend.app.schemas.user import UserCreate, UserRead, UserLogin, RefreshTokenRequest, UserProfileUpdate, ChangePasswordRequest

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

@router.post("/refresh", response_model=TokenRefresh)
async def refresh_token(token_request: RefreshTokenRequest) -> dict[str, Any]:
    """
    Issue a new access token using a valid refresh token.
    """
    from backend.app.core.security import validate_refresh_token

    token_data = validate_refresh_token(token_request.refresh_token)
    if not token_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )

    new_access_token = create_access_token(
        {"id": token_data["id"], "role": token_data["role"]},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    return {"access_token": new_access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserRead)
async def get_current_user_profile(current_user: User = Depends(get_current_user)) -> User:
    """
    Get current authenticated user's profile.
    Requires valid JWT token in Authorization header.
    """
    return current_user


@router.put("/me", response_model=UserRead)
async def update_user_profile(
    user_update: UserProfileUpdate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
) -> User:
    """
    Update current authenticated user's profile.
    Users can only update their username and email.
    Requires valid JWT token in Authorization header.
    """
    # Check if username is being updated and if it's already taken
    if user_update.username and user_update.username != current_user.username:
        result = await session.execute(
            select(User).where(User.username == user_update.username)
        )
        existing_user = result.scalar_one_or_none()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already exists"
            )
        current_user.username = user_update.username
    
    # Check if email is being updated and if it's already taken
    if user_update.email and user_update.email != current_user.email:
        result = await session.execute(
            select(User).where(User.email == user_update.email)
        )
        existing_user = result.scalar_one_or_none()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already exists"
            )
        current_user.email = user_update.email
    
    # Update timestamp
    current_user.updated_at = datetime.utcnow()
    
    # Save changes
    session.add(current_user)
    await session.commit()
    await session.refresh(current_user)
    
    return current_user


@router.post("/change-password")
async def change_password(
    password_data: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
) -> dict:
    """
    Change current authenticated user's password.
    Requires current password verification.
    Requires valid JWT token in Authorization header.
    """
    # Verify current password
    if not verify_password(password_data.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )
    
    # Check new password is different from current
    if password_data.current_password == password_data.new_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password must be different from current password"
        )
    
    # Hash and update password
    current_user.hashed_password = hash_password(password_data.new_password)
    current_user.updated_at = datetime.utcnow()
    
    # Save changes
    session.add(current_user)
    await session.commit()
    
    return {"message": "Password changed successfully"}