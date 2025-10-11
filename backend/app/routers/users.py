"""
FILE: backend/app/routers/users.py - UPDATED WITH FIXES
- Fixed datetime.utcnow() deprecation warnings
- Ensured full_name is handled in all responses
"""

from fastapi import APIRouter, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from sqlalchemy.exc import IntegrityError
from datetime import timedelta, datetime, timezone
from typing import Any, Optional
from sqlalchemy import func

from backend.app.db.session import get_session
from backend.app.models.user import User
from backend.app.schemas.user import (
    UserCreate, UserRead, UserLogin, RefreshTokenRequest,
    UserProfileUpdate, ChangePasswordRequest, UserListResponse
)
from backend.app.core.security import hash_password, verify_password, create_access_token
from backend.app.core.deps import get_current_user, get_current_admin
from backend.app.models.admin import Admin
from backend.app.schemas.admin import Token, TokenRefresh
from backend.app.core.exceptions import (
    AuthenticationException,
    DuplicateRecordException,
    EmailAlreadyExistsException,
    UsernameAlreadyExistsException,
    BusinessLogicException,
)
from backend.app.core.logging.config import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/users", tags=["Users"])

ACCESS_TOKEN_EXPIRE_MINUTES = 15
REFRESH_TOKEN_EXPIRE_DAYS = 7


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_in: UserCreate,
    session: AsyncSession = Depends(get_session)
) -> UserRead:
    """
    Register a new user with hashed password.
    Ensures unique username and email.
    """
    logger.info(f"Registering new user: {user_in.username}")

    # Check if username or email already exists
    query = select(User).where(
        (User.username == user_in.username) | (User.email == user_in.email)
    )
    existing_user = (await session.execute(query)).scalar_one_or_none()

    if existing_user:
        if existing_user.username == user_in.username:
            logger.warning(f"Registration failed: Username '{user_in.username}' already exists")
            raise UsernameAlreadyExistsException(user_in.username)
        else:
            logger.warning(f"Registration failed: Email '{user_in.email}' already exists")
            raise EmailAlreadyExistsException(user_in.email)

    # Hash password and create new user
    new_user = User(
        username=user_in.username,
        email=user_in.email,
        full_name=user_in.full_name,
        hashed_password=hash_password(user_in.password),
    )

    try:
        session.add(new_user)
        await session.commit()
        await session.refresh(new_user)
        logger.info(f"✅ User '{user_in.username}' registered successfully (ID: {new_user.id})")
    except IntegrityError:
        await session.rollback()
        logger.error(f"Database integrity error during user registration: {user_in.username}")
        raise DuplicateRecordException(resource="User")
    except Exception as e:
        await session.rollback()
        logger.error(f"Unexpected error during user registration: {str(e)}", exc_info=True)
        raise

    return new_user


@router.post("/login", response_model=Token)
async def login_user(
    user_in: UserLogin,
    session: AsyncSession = Depends(get_session)
) -> dict[str, Any]:
    """Authenticate user and return JWT access + refresh tokens."""
    logger.info(f"Login attempt for user: {user_in.username}")

    result = await session.execute(
        select(User).where(User.username == user_in.username)
    )
    user = result.scalar_one_or_none()

    if not user or not user.is_active or not verify_password(user_in.password, user.hashed_password):
        logger.warning(f"Login failed for user: {user_in.username}")
        raise AuthenticationException("Invalid username or password")

    # Generate JWT tokens
    token_data = {"id": user.id, "role": "superuser" if user.is_superuser else "user"}
    access_token = create_access_token(
        token_data,
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    refresh_token = create_access_token(
        token_data,
        expires_delta=timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    )

    logger.info(f"✅ User '{user_in.username}' logged in successfully")
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


@router.post("/refresh", response_model=TokenRefresh)
async def refresh_token(token_request: RefreshTokenRequest) -> dict[str, Any]:
    """Issue a new access token using a valid refresh token."""
    from backend.app.core.security import validate_refresh_token

    logger.info("Token refresh requested")

    token_data = validate_refresh_token(token_request.refresh_token)
    if not token_data:
        logger.warning("Token refresh failed: Invalid or expired refresh token")
        raise AuthenticationException("Invalid or expired refresh token")

    new_access_token = create_access_token(
        {"id": token_data["id"], "role": token_data["role"]},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    logger.info("✅ Token refreshed successfully")
    return {"access_token": new_access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserRead)
async def get_current_user_profile(
    current_user: User = Depends(get_current_user)
) -> User:
    """Get current authenticated user's profile."""
    logger.info(f"Fetching profile for user: {current_user.username}")
    return current_user


@router.put("/me", response_model=UserRead)
async def update_user_profile(
    user_update: UserProfileUpdate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
) -> User:
    """Update current authenticated user's profile."""
    logger.info(f"Updating profile for user: {current_user.username}")

    # Check if username is being updated
    if user_update.username and user_update.username != current_user.username:
        result = await session.execute(
            select(User).where(User.username == user_update.username)
        )
        existing_user = result.scalar_one_or_none()
        if existing_user:
            logger.warning(f"Profile update failed: Username '{user_update.username}' already exists")
            raise UsernameAlreadyExistsException(user_update.username)
        current_user.username = user_update.username
        logger.info(f"Username updated to: {user_update.username}")

    # Check if email is being updated
    if user_update.email and user_update.email != current_user.email:
        result = await session.execute(
            select(User).where(User.email == user_update.email)
        )
        existing_user = result.scalar_one_or_none()
        if existing_user:
            logger.warning(f"Profile update failed: Email '{user_update.email}' already exists")
            raise EmailAlreadyExistsException(user_update.email)
        current_user.email = user_update.email
        logger.info(f"Email updated to: {user_update.email}")

    # Update full_name if provided
    if user_update.full_name is not None:
        current_user.full_name = user_update.full_name
        logger.info(f"Full name updated to: {user_update.full_name}")

    # Update timestamp with timezone-aware datetime
    current_user.updated_at = datetime.now(timezone.utc)

    # Save changes
    session.add(current_user)
    await session.commit()
    await session.refresh(current_user)

    logger.info(f"✅ Profile updated for user: {current_user.username}")
    return current_user


@router.post("/change-password")
async def change_password(
    password_data: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
) -> dict:
    """Change current authenticated user's password."""
    logger.info(f"Password change requested for user: {current_user.username}")

    # Verify current password
    if not verify_password(password_data.current_password, current_user.hashed_password):
        logger.warning(f"Password change failed: Incorrect current password for {current_user.username}")
        raise AuthenticationException("Current password is incorrect")

    # Check new password is different from current
    if password_data.current_password == password_data.new_password:
        logger.warning(f"Password change failed: New password same as current for {current_user.username}")
        raise BusinessLogicException(
            message="New password must be different from current password"
        )

    # Hash and update password
    current_user.hashed_password = hash_password(password_data.new_password)
    current_user.updated_at = datetime.now(timezone.utc)

    # Save changes
    session.add(current_user)
    await session.commit()

    logger.info(f"✅ Password changed successfully for user: {current_user.username}")
    return {"message": "Password changed successfully"}


@router.get("/", response_model=UserListResponse)
async def list_users(
    page: int = 1,
    page_size: int = 10,
    is_active: Optional[bool] = None,
    current_admin: Admin = Depends(get_current_admin),
    session: AsyncSession = Depends(get_session)
) -> dict:
    """List all users with pagination and optional filtering (Admin only)."""
    logger.info(f"Admin listing users - page: {page}, page_size: {page_size}, is_active: {is_active}")

    # Validate pagination parameters
    if page < 1:
        logger.warning(f"Invalid page number: {page}")
        raise BusinessLogicException(message="Page must be >= 1")
    if page_size < 1 or page_size > 100:
        logger.warning(f"Invalid page size: {page_size}")
        raise BusinessLogicException(message="Page size must be between 1 and 100")

    # Build query
    query = select(User)

    # Apply filters
    if is_active is not None:
        query = query.where(User.is_active == is_active)

    # Get total count
    count_query = select(func.count()).select_from(User)
    if is_active is not None:
        count_query = count_query.where(User.is_active == is_active)
    result = await session.execute(count_query)
    total = result.scalar_one()

    # Apply pagination
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size).order_by(User.id)

    # Execute query
    result = await session.execute(query)
    users = result.scalars().all()

    # Calculate total pages
    total_pages = (total + page_size - 1) // page_size

    logger.info(f"✅ Retrieved {len(users)} users (total: {total})")
    return {
        "users": users,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages
    }