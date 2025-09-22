from sqlmodel import SQLModel, Field
from typing import Optional
from pydantic import EmailStr

class Admin(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True, description="Primary key")
    username: str = Field(
        index=True,
        unique=True,
        nullable=False,
        description="Unique admin username"
    )
    email: EmailStr = Field(
        index=True,
        unique=True,
        nullable=False,
        description="Admin email address"
    )
    hashed_password: str = Field(
        nullable=False,
        description="Hashed password for secure authentication"
    )
    is_superadmin: bool = Field(
        default=False,
        description="Indicates full access privileges"
    )
    is_active: bool = Field(
        default=True,
        description="Indicates whether the admin account is active"
    )

    class Config:
        orm_mode = True  # Allows ORM models to be converted to Pydantic models easily
