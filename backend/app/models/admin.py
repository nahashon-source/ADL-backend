from sqlmodel import SQLModel, Field, Column, String
from sqlalchemy import Boolean, DateTime
from typing import Optional
from datetime import datetime, timezone


class Admin(SQLModel, table=True):
    """
    Admin model for database table
    """
    __tablename__ = "admins"
    __table_args__ = {"extend_existing": True}
    
    # ---------- Primary Key ----------
    id: Optional[int] = Field(
        default=None, 
        primary_key=True, 
        index=True,
        description="Primary key"
    )
    
    # ---------- Identity ----------
    username: str = Field(
        sa_column=Column(String(50), unique=True, index=True, nullable=False),
        description="Unique admin username"
    )
    email: str = Field(
        sa_column=Column(String(255), unique=True, index=True, nullable=False),
        description="Admin email address"
    )
    hashed_password: str = Field(
        sa_column=Column(String(255), nullable=False),
        description="Hashed password for secure authentication"
    )
    
    # ---------- Profile ----------
    full_name: Optional[str] = Field(
        default=None,
        sa_column=Column(String(255), nullable=True),
        description="Admin full name"
    )
    
    # ---------- Flags ----------
    is_active: bool = Field(
        default=True,
        sa_column=Column(Boolean, nullable=False, server_default="1"),
        description="Indicates whether the admin account is active"
    )
    is_superadmin: bool = Field(
        default=False,
        sa_column=Column(Boolean, nullable=False, server_default="0"),
        description="Indicates full access privileges"
    )
    
    # ---------- Timestamps ----------
    # IMPORTANT: timezone=True tells SQLAlchemy to convert timezone-aware datetimes
    # to naive (remove timezone) when storing in TIMESTAMP WITHOUT TIME ZONE columns
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True), nullable=False, index=True),
        description="Timestamp when admin was created"
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(
            DateTime(timezone=True), 
            nullable=False, 
            index=True, 
            onupdate=lambda: datetime.now(timezone.utc)
        ),
        description="Timestamp when admin was last updated"
    )