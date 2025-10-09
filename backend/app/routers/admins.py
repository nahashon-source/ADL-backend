from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlmodel import select
from datetime import timedelta
from typing import Any

from backend.app.db.session import get_session
from backend.app.models.admin import Admin
from backend.app.models.user import User
from backend.app.schemas.admin import (
    AdminCreate, AdminRead, AdminLogin, Token, TokenRefresh, RefreshTokenRequest
)
from backend.app.schemas.user import UserRead
from backend.app.core.security import hash_password, verify_password, create_access_token
from backend.app.core.deps import get_current_admin
from backend.app.core.pagination import PaginationParams, PaginatedResponse
from backend.app.core.exceptions import (
    AuthenticationException,
    DuplicateRecordException,
    EmailAlreadyExistsException,
    UsernameAlreadyExistsException,
)
from backend.app.core.logging.config import get_logger
from sqlalchemy import func

logger = get_logger(__name__)

router = APIRouter(prefix="/admins", tags=["Admins"])

ACCESS_TOKEN_EXPIRE_MINUTES = 15
REFRESH_TOKEN_EXPIRE_DAYS = 7


@router.post("/register", response_model=AdminRead, status_code=status.HTTP_201_CREATED)
async def register_admin(
    admin_in: AdminCreate,
    session: AsyncSession = Depends(get_session)
) -> Admin:
    """
    Register a new admin with hashed password.
    Ensures unique username and email.
    
    Args:
        admin_in: AdminCreate schema with username, email, password, is_superadmin
        session: Database session
    
    Returns:
        AdminRead: Created admin object
    
    Raises:
        UsernameAlreadyExistsException: If username already exists
        EmailAlreadyExistsException: If email already registered
    """
    logger.info(f"Registering new admin: {admin_in.username}")

    # Check if username or email already exists
    query = select(Admin).where(
        (Admin.username == admin_in.username) | (Admin.email == admin_in.email)
    )
    existing_admin = (await session.execute(query)).scalar_one_or_none()

    if existing_admin:
        if existing_admin.username == admin_in.username:
            logger.warning(f"Admin registration failed: Username '{admin_in.username}' already exists")
            raise UsernameAlreadyExistsException(admin_in.username)
        else:
            logger.warning(f"Admin registration failed: Email '{admin_in.email}' already exists")
            raise EmailAlreadyExistsException(admin_in.email)

    # Create new admin
    new_admin = Admin(
        username=admin_in.username,
        email=admin_in.email,
        hashed_password=hash_password(admin_in.password),
        is_superadmin=admin_in.is_superadmin,
    )

    try:
        session.add(new_admin)
        await session.commit()
        await session.refresh(new_admin)
        logger.info(f"✅ Admin '{admin_in.username}' registered successfully (ID: {new_admin.id})")
    except IntegrityError:
        await session.rollback()
        logger.error(f"Database integrity error during admin registration: {admin_in.username}")
        raise DuplicateRecordException(resource="Admin")
    except Exception as e:
        await session.rollback()
        logger.error(f"Unexpected error during admin registration: {str(e)}", exc_info=True)
        raise

    return new_admin


@router.post("/login", response_model=Token)
async def login_admin(
    admin_in: AdminLogin,
    session: AsyncSession = Depends(get_session)
) -> dict[str, Any]:
    """
    Authenticate admin and return JWT access + refresh tokens.
    Can login with either username or email.
    
    Args:
        admin_in: AdminLogin schema with username/email and password
        session: Database session
    
    Returns:
        dict with access_token, refresh_token, and token_type
    
    Raises:
        HTTPException 400: If neither username nor email provided
        AuthenticationException: If credentials invalid or admin inactive
    """
    logger.info(f"Admin login attempt - username: {admin_in.username}, email: {admin_in.email}")

    # Build query based on provided credentials
    if admin_in.email:
        query = select(Admin).where(Admin.email == admin_in.email)
    elif admin_in.username:
        query = select(Admin).where(Admin.username == admin_in.username)
    else:
        logger.warning("Admin login failed: Neither username nor email provided")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either username or email must be provided"
        )

    result = await session.execute(query)
    admin = result.scalar_one_or_none()

    if not admin or not admin.is_active or not verify_password(admin_in.password, admin.hashed_password):
        logger.warning(f"Admin login failed - username: {admin_in.username}, email: {admin_in.email}")
        raise AuthenticationException("Invalid username or password")

    # Generate JWT tokens
    token_data = {"id": admin.id, "role": "superadmin" if admin.is_superadmin else "admin"}
    access_token = create_access_token(
        token_data,
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    refresh_token = create_access_token(
        token_data,
        expires_delta=timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    )

    logger.info(f"✅ Admin '{admin_in.username or admin_in.email}' logged in successfully")
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


@router.post("/refresh", response_model=TokenRefresh)
async def refresh_token(token_request: RefreshTokenRequest) -> dict[str, Any]:
    """
    Issue a new access token using a valid refresh token.
    
    Args:
        token_request: RefreshTokenRequest with refresh_token
    
    Returns:
        dict with new access_token and token_type
    
    Raises:
        AuthenticationException: If refresh token invalid or expired
    """
    from backend.app.core.security import validate_refresh_token

    logger.info("Admin token refresh requested")

    token_data = validate_refresh_token(token_request.refresh_token)
    if not token_data:
        logger.warning("Admin token refresh failed: Invalid or expired refresh token")
        raise AuthenticationException("Invalid or expired refresh token")

    new_access_token = create_access_token(
        {"id": token_data["id"], "role": token_data["role"]},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    logger.info("✅ Admin token refreshed successfully")
    return {"access_token": new_access_token, "token_type": "bearer"}


@router.get("/me", response_model=AdminRead)
async def get_current_admin_profile(
    current_admin: Admin = Depends(get_current_admin)
) -> Admin:
    """
    Get current authenticated admin's profile.
    
    Returns:
        Admin: Current admin object with all profile information
    
    Requires:
        Valid JWT token in Authorization header
    """
    logger.info(f"Fetching profile for admin: {current_admin.username}")
    return current_admin


@router.get("/users", response_model=PaginatedResponse[UserRead])
async def list_users(
    page: int = 1,
    page_size: int = 10,
    is_active: bool | None = None,
    current_admin: Admin = Depends(get_current_admin),
    session: AsyncSession = Depends(get_session)
) -> PaginatedResponse[UserRead]:
    """
    List all users with pagination and optional filtering.
    
    **Admin only endpoint.**
    
    Args:
        page: Page number (starts at 1, default: 1)
        page_size: Items per page (1-100, default: 10)
        is_active: Filter by active status (optional)
        current_admin: Current authenticated admin
        session: Database session
    
    Returns:
        PaginatedResponse[UserRead]: Paginated list of users with metadata
    
    Requires:
        Valid admin JWT token in Authorization header
    """
    logger.info(f"Admin listing users - page: {page}, page_size: {page_size}, is_active: {is_active}")

    # Validate pagination params
    pagination = PaginationParams(page=page, page_size=page_size)

    # Build base query
    query = select(User)

    # Apply filters
    if is_active is not None:
        query = query.where(User.is_active == is_active)

    # Order by created_at descending (newest first)
    query = query.order_by(User.created_at.desc())

    # Get total count
    count_query = select(func.count()).select_from(User)
    if is_active is not None:
        count_query = count_query.where(User.is_active == is_active)

    total_result = await session.execute(count_query)
    total = total_result.scalar_one()

    # Apply pagination
    query = query.offset(pagination.offset).limit(pagination.limit)

    # Execute query
    result = await session.execute(query)
    users = result.scalars().all()

    logger.info(f"✅ Retrieved {len(users)} users (total: {total})")

    # Return paginated response
    return PaginatedResponse.create(
        items=users,
        total=total,
        page=pagination.page,
        page_size=pagination.page_size
    )