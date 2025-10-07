from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlmodel import select
from datetime import timedelta
from typing import Any

from backend.app.db.session import get_session
from backend.app.models.admin import Admin
from backend.app.schemas.admin import AdminCreate, AdminRead, AdminLogin, Token, TokenRefresh, RefreshTokenRequest
from backend.app.core.security import hash_password, verify_password, create_access_token

router = APIRouter(prefix="/admins", tags=["Admins"])

ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7


@router.post("/register", response_model=AdminRead, status_code=status.HTTP_201_CREATED)
async def register_admin(admin_in: AdminCreate, session: AsyncSession = Depends(get_session)) -> Admin:
    """
    Register a new admin with hashed password.
    Ensures unique username/email.
    """
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
    except IntegrityError:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username or email already exists."
        )
    except Exception as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error: {str(e)}"
        )

    return new_admin


@router.post("/login", response_model=Token)
async def login_admin(admin_in: AdminLogin, session: AsyncSession = Depends(get_session)) -> dict[str, Any]:
    """
    Authenticate admin and return JWT access + refresh tokens.
    """
    result = await session.execute(select(Admin).where(Admin.username == admin_in.username))
    admin = result.scalar_one_or_none()

    if not admin or not admin.is_active or not verify_password(admin_in.password, admin.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Generate JWT tokens
    token_data = {"id": admin.id, "role": "superadmin" if admin.is_superadmin else "admin"}
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