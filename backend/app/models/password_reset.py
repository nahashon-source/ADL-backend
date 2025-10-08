from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime, timedelta
from typing import Optional
import secrets
from backend.app.core.config import settings


class PasswordResetToken(SQLModel, table=True):
    __tablename__ = "password_reset_tokens"
    
    id: Optional[str] = Field(
        default_factory=lambda: secrets.token_urlsafe(32),
        primary_key=True
    )
    user_id: str = Field(foreign_key="users.id", nullable=False)
    token: str = Field(unique=True, nullable=False, index=True)
    expires_at: datetime
    used: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    def __init__(self, **kwargs):
        if 'token' not in kwargs:
            kwargs['token'] = secrets.token_urlsafe(32)
        if 'expires_at' not in kwargs:
            kwargs['expires_at'] = datetime.utcnow() + timedelta(
                minutes=settings.reset_token_expire_minutes
            )
        super().__init__(**kwargs)
    
    def is_valid(self) -> bool:
        """Check if token is still valid"""
        return not self.used and datetime.utcnow() < self.expires_at