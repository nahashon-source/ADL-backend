from pydantic import BaseModel, EmailStr
from typing import Optional

# === Base schema for shared fields ===
class AdminBase(BaseModel):
    username: str
    email: EmailStr

# === Schema for creating a new admin ===
class AdminCreate(AdminBase):
    password: str
    is_superadmin: Optional[bool] = False

# === Schema for reading admin data ===
class AdminRead(AdminBase):
    id: int
    is_active: bool = True
    is_superadmin: bool = False

    class Config:
        orm_mode = True

# === Schema for admin login ===
class AdminLogin(BaseModel):
    username: str
    password: str

# === Token response schema ===
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
