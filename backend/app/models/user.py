from sqlmodel import SQLModel, Field, Column, String
from sqlalchemy import Boolean, DateTime
from typing import Optional
from datetime import datetime, timezone


class User(SQLModel, table=True):
    """
    User model representing an application user.
    
    Fields:
        - id: Primary key
        - username: Unique username (max 50 chars)
        - email: Unique email address (max 255 chars)
        - hashed_password: Bcrypt hashed password
        - full_name: Optional display name
        - is_active: Whether user account is active
        - is_superuser: Whether user has superuser privileges
        - created_at: Account creation timestamp (timezone-aware)
        - updated_at: Last update timestamp (timezone-aware)
    """
    __tablename__ = "users"
    __table_args__ = {"extend_existing": True}
    
    # ---------- Primary Key ----------
    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    
    # ---------- Identity ----------
    username: str = Field(
        sa_column=Column(String(50), unique=True, index=True, nullable=False),
        description="Unique username for login"
    )
    email: str = Field(
        sa_column=Column(String(255), unique=True, index=True, nullable=False),
        description="Unique email address"
    )
    hashed_password: str = Field(
        sa_column=Column(String(255), nullable=False),
        description="Bcrypt hashed password"
    )
    
    # ---------- Profile ----------
    full_name: Optional[str] = Field(
        default=None,
        sa_column=Column(String(255), nullable=True),
        description="User's full name (optional)"
    )
    
    # ---------- Status Flags ----------
    is_active: bool = Field(
        default=True,
        sa_column=Column(Boolean, nullable=False, server_default="1"),
        description="Whether user account is active"
    )
    is_superuser: bool = Field(
        default=False,
        sa_column=Column(Boolean, nullable=False, server_default="0"),
        description="Whether user has superuser privileges"
    )
    
    # ---------- Timestamps ----------
    # Using timezone-aware datetimes for proper timezone handling
    # SQLAlchemy converts timezone-aware to naive when storing in TIMESTAMP WITHOUT TIME ZONE
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True), nullable=False, index=True),
        description="Account creation timestamp"
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(
            DateTime(timezone=True), 
            nullable=False, 
            index=True,
            onupdate=lambda: datetime.now(timezone.utc)
        ),
        description="Last profile update timestamp"
    )