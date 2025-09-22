from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from backend.app.db.session import get_session
from backend.app.models.admin import Admin
from backend.app.schemas.admin import AdminCreate, AdminRead, AdminLogin, Token
from backend.app.core.security import hash_password, verify_password, create_access_token

router = APIRouter(prefix="/admins", tags=["Admins"])

# === Admin Registration ===
@router.post("/register", response_model=AdminRead)
async def register_admin(admin_in: AdminCreate, session: AsyncSession = Depends(get_session)):
    """
    Register a new admin with hashed password.
    """
    # Check if username or email already exists
    result = await session.execute(
        select(Admin).where((Admin.username == admin_in.username) | (Admin.email == admin_in.email))
    )
    existing_admin = result.scalar_one_or_none()
    if existing_admin:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username or email already exists.")

    # Create new admin
    new_admin = Admin(
        username=admin_in.username,
        email=admin_in.email,
        hashed_password=hash_password(admin_in.password),
        is_superadmin=admin_in.is_superadmin
    )
    session.add(new_admin)
    await session.commit()
    await session.refresh(new_admin)
    return new_admin


# === Admin Login ===
@router.post("/login", response_model=Token)
async def login_admin(admin_in: AdminLogin, session: AsyncSession = Depends(get_session)):
    """
    Authenticate admin and return JWT access token.
    """
    result = await session.execute(select(Admin).where(Admin.username == admin_in.username))
    admin = result.scalar_one_or_none()
    if not admin or not verify_password(admin_in.password, admin.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create JWT token
    token_data = {"sub": str(admin.id), "role": "superadmin" if admin.is_superadmin else "admin"}
    access_token = create_access_token(token_data)
    return {"access_token": access_token, "token_type": "bearer"}
