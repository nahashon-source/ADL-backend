from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from datetime import datetime

from app.core.database import get_db
from app.models.user import User
from app.models.password_reset import PasswordResetToken
from app.services.email_service import email_service
from app.core.security import get_password_hash

router = APIRouter()


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str


@router.post("/forgot-password", status_code=status.HTTP_200_OK)
async def forgot_password(
    request: ForgotPasswordRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Request password reset - sends email with reset token
    
    NOTE: Always returns success message to prevent email enumeration attacks
    """
    # Find user by email
    user = db.query(User).filter(User.email == request.email).first()
    
    # Always return success to prevent email enumeration
    response_message = "If your email is registered, you will receive a password reset link shortly."
    
    if not user:
        return {"message": response_message}
    
    # Check if user is active
    if not user.is_active:
        return {"message": response_message}
    
    # Invalidate any existing tokens for this user
    existing_tokens = db.query(PasswordResetToken).filter(
        PasswordResetToken.user_id == user.id,
        PasswordResetToken.used == False
    ).all()
    
    for token in existing_tokens:
        token.used = True
    
    # Create new reset token
    reset_token = PasswordResetToken(user_id=user.id)
    db.add(reset_token)
    db.commit()
    db.refresh(reset_token)
    
    # Send email in background
    background_tasks.add_task(
        email_service.send_password_reset_email,
        to_email=user.email,
        reset_token=reset_token.token,
        user_name=user.full_name or user.email
    )
    
    return {"message": response_message}


@router.post("/reset-password", status_code=status.HTTP_200_OK)
async def reset_password(
    request: ResetPasswordRequest,
    db: Session = Depends(get_db)
):
    """
    Reset password using token from email
    """
    # Find the reset token
    reset_token = db.query(PasswordResetToken).filter(
        PasswordResetToken.token == request.token
    ).first()
    
    if not reset_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )
    
    # Check if token is valid
    if not reset_token.is_valid():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )
    
    # Get the user
    user = db.query(User).filter(User.id == reset_token.user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    
    # Update password
    user.hashed_password = get_password_hash(request.new_password)
    user.updated_at = datetime.utcnow()
    
    # Mark token as used
    reset_token.used = True
    
    db.commit()
    
    return {
        "message": "Password has been reset successfully. You can now login with your new password."
    }


@router.post("/test-email", status_code=status.HTTP_200_OK)
async def test_email():
    """
    Test endpoint to verify email service is working
    
    NOTE: Change the to_email to your actual email address
    """
    test_result = email_service.send_email(
        to_email="test@example.com",  # ⚠️ CHANGE THIS TO YOUR EMAIL
        subject="Test Email from ADL Backend",
        html_content="""
        <h1>✅ Test Email</h1>
        <p>If you're reading this, your email service is working correctly!</p>
        <p>Your SMTP configuration is properly set up.</p>
        """,
        text_content="Test Email - If you're reading this, your email service is working correctly!"
    )
    
    if test_result:
        return {"message": "Test email sent successfully! Check your inbox."}
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send test email. Check your SMTP configuration and logs."
        )