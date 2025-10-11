from pydantic import BaseModel, EmailStr, StringConstraints, ConfigDict, Field
from typing import Annotated, Optional
from datetime import datetime


# ---------- Base ----------
class UserBase(BaseModel):
    username: str
    email: EmailStr
    full_name: Optional[str] = None
    is_active: bool = True
    is_superuser: bool = False


# ---------- Create ----------
class UserCreate(BaseModel):
    username: Annotated[str, StringConstraints(min_length=3, max_length=50)]
    email: EmailStr
    password: Annotated[str, StringConstraints(min_length=8)]
    full_name: Optional[str] = Field(default=None, description="User's full name")


# ---------- Login ----------
class UserLogin(BaseModel):
    username: str
    password: str


# ---------- Refresh Token ----------
class RefreshTokenRequest(BaseModel):
    refresh_token: str


# ---------- Read ----------
class UserRead(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ---------- Update ----------
class UserUpdate(BaseModel):
    username: Annotated[str, StringConstraints(min_length=3, max_length=50)] | None = None
    email: EmailStr | None = None
    full_name: Optional[str] = None
    password: Annotated[str, StringConstraints(min_length=8)] | None = None
    is_active: bool | None = None
    is_superuser: bool | None = None


class UserProfileUpdate(BaseModel):
    username: Annotated[str, StringConstraints(min_length=3, max_length=50)] | None = None
    email: EmailStr | None = None
    full_name: Optional[str] = None


# ---------- Change Password ----------
class ChangePasswordRequest(BaseModel):
    """Schema for changing user password"""
    current_password: Annotated[str, StringConstraints(min_length=8)]
    new_password: Annotated[str, StringConstraints(min_length=8)]


# ---------- User List (Paginated) ----------
class UserListResponse(BaseModel):
    """Schema for paginated user list response"""
    users: list[UserRead]
    total: int
    page: int
    page_size: int
    total_pages: int

    model_config = ConfigDict(from_attributes=True)