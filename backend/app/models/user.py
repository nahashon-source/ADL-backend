from sqlmodel import SQLModel, Field, Column, String
from sqlalchemy import Boolean, DateTime
from typing import Optional
from datetime import datetime, timezone


class User(SQLModel, table=True):
    __tablename__ = "users"
    __table_args__ = {"extend_existing": True}
    
    # ---------- Primary Key ----------
    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    
    # ---------- Identity ----------
    username: str = Field(
        sa_column=Column(String(50), unique=True, index=True, nullable=False)
    )
    email: str = Field(
        sa_column=Column(String(255), unique=True, index=True, nullable=False)
    )
    hashed_password: str = Field(
        sa_column=Column(String(255), nullable=False)
    )
    
    # ---------- Profile ----------
    full_name: Optional[str] = Field(
        default=None,
        sa_column=Column(String(255), nullable=True)
    )
    
    # ---------- Flags ----------
    is_active: bool = Field(
        default=True,
        sa_column=Column(Boolean, nullable=False, server_default="1")
    )
    is_superuser: bool = Field(
        default=False,
        sa_column=Column(Boolean, nullable=False, server_default="0")
    )
    
    # ---------- Timestamps ----------
    # IMPORTANT: timezone=True tells SQLAlchemy to convert timezone-aware datetimes
    # to naive (remove timezone) when storing in TIMESTAMP WITHOUT TIME ZONE columns
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True), nullable=False, index=True)
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(
            DateTime(timezone=True), 
            nullable=False, 
            index=True, 
            onupdate=lambda: datetime.now(timezone.utc)
        )
    )