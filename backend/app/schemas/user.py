from pydantic import BaseModel, EmailStr, StringConstraints
from typing import Annotated
from datetime import datetime


# ---------- Base ----------
class UserBase(BaseModel):
    username: str
    email: EmailStr
    is_active: bool = True
    is_superuser: bool = False


# ---------- Create ----------
class UserCreate(BaseModel):
    username: Annotated[str, StringConstraints(min_length=3, max_length=50)]
    email: EmailStr
    password: Annotated[str, StringConstraints(min_length=8)]
    
    # ---------- Login ----------
class UserLogin(BaseModel):
    username: str
    password: str


# ---------- Read ----------
class UserRead(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True  # replaces orm_mode in Pydantic v2


# ---------- Update ----------
class UserUpdate(BaseModel):
    username: Annotated[str, StringConstraints(min_length=3, max_length=50)] | None = None
    email: EmailStr | None = None
    password: Annotated[str, StringConstraints(min_length=8)] | None = None
    is_active: bool | None = None
    is_superuser: bool | None = None
