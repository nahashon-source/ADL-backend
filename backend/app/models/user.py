from sqlmodel import SQLModel, Field, Column, String
from sqlalchemy import Boolean
from typing import Optional
from datetime import datetime


class User(SQLModel, table=True):
    __tablename__ = "users"

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
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(nullable=False, index=True)
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(nullable=False, index=True, onupdate=datetime.utcnow)
    )
