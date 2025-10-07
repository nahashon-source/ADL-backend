from pydantic import BaseModel, EmailStr
from typing import Optional
from pydantic import ConfigDict, field_validator, EmailStr


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

    # class Config:
    #     orm_mode = True
model_config = ConfigDict(from_attributes=True)


# === Schema for admin login ===
class AdminLogin(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: str

    @field_validator('username', 'email')
    @classmethod
    def check_username_or_email(cls, v, info):
        # At least one of username or email must be provided
        if info.field_name == 'email' and not v and not info.data.get('username'):
            raise ValueError('Either username or email must be provided')
        if info.field_name == 'username' and not v and not info.data.get('email'):
            raise ValueError('Either username or email must be provided')
        return v

# === Token response schema ===
class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    
    # === Refresh token response schema (only access token, no refresh) ===
class TokenRefresh(BaseModel):
    access_token: str
    token_type: str = "bearer"

# === Refresh token request schema ===
class RefreshTokenRequest(BaseModel):
    refresh_token: str