from sqlmodel import SQLModel, Field, Column
from sqlalchemy import String, Boolean, DateTime, Integer, ForeignKey
from datetime import datetime, timedelta, timezone
from typing import Optional
import secrets
from backend.app.core.config import settings


class PasswordResetToken(SQLModel, table=True):
    """Password reset token model for password recovery flow"""
    __tablename__ = "password_reset_tokens"
    
    # ========== Primary Key ==========
    id: Optional[str] = Field(
        default_factory=lambda: secrets.token_urlsafe(32),
        sa_column=Column(String(255), primary_key=True),
        description="Unique token ID"
    )
    
    # ========== Foreign Key ==========
    # IMPORTANT: Must match User.id type (INTEGER, not VARCHAR)
    user_id: int = Field(
        sa_column=Column(Integer, ForeignKey("users.id"), nullable=False, index=True),
        description="Reference to user requesting password reset"
    )
    
    # ========== Token Data ==========
    token: str = Field(
        default_factory=lambda: secrets.token_urlsafe(32),
        sa_column=Column(String(255), unique=True, nullable=False, index=True),
        description="Actual reset token sent to user"
    )
    
    expires_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), nullable=False),
        description="When this token expires"
    )
    
    # ========== Status ==========
    used: bool = Field(
        default=False,
        sa_column=Column(Boolean, nullable=False, server_default="false"),
        description="Whether this token has been used"
    )
    
    # ========== Timestamps ==========
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True), nullable=False, index=True),
        description="When token was created"
    )
    
    def __init__(self, **kwargs):
        """Initialize with auto-generated token and expiry if not provided"""
        if 'token' not in kwargs:
            kwargs['token'] = secrets.token_urlsafe(32)
        if 'expires_at' not in kwargs:
            kwargs['expires_at'] = datetime.now(timezone.utc) + timedelta(
                minutes=settings.reset_token_expire_minutes
            )
        super().__init__(**kwargs)
    
    def is_valid(self) -> bool:
        """Check if token is still valid (not used and not expired)"""
        current_time = datetime.now(timezone.utc)
        # Ensure expires_at is also timezone-aware for comparison
        expires_at = self.expires_at
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)
        
        return not self.used and current_time < expires_at