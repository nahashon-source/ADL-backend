from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, EmailStr

from backend.app.services.email import email_service
from backend.app.core.config import settings

router = APIRouter(prefix="/test", tags=["Testing"])


class TestEmailRequest(BaseModel):
    """Request model for sending test email."""
    to_email: EmailStr
    test_type: str = "welcome"  # Options: "welcome", "password_reset"


class TestEmailResponse(BaseModel):
    """Response model for test email."""
    success: bool
    message: str
    email_configured: bool


@router.post("/send-email", response_model=TestEmailResponse)
async def send_test_email(request: TestEmailRequest):
    """
    Send a test email to verify SMTP configuration.
    
    **Test Types:**
    - `welcome`: Send welcome email template
    - `password_reset`: Send password reset email template
    
    **Example:**
    ```json
    {
        "to_email": "test@example.com",
        "test_type": "welcome"
    }
    ```
    """
    if not settings.email_enabled:
        return TestEmailResponse(
            success=False,
            message="Email service not configured. Please set SMTP environment variables in .env file.",
            email_configured=False
        )
    
    try:
        if request.test_type == "welcome":
            success = await email_service.send_welcome_email(
                to_email=request.to_email,
                user_name="Test User"
            )
        elif request.test_type == "password_reset":
            success = await email_service.send_password_reset_email(
                to_email=request.to_email,
                reset_token="test-token-12345",
                user_name="Test User"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid test_type. Use 'welcome' or 'password_reset'."
            )
        
        if success:
            return TestEmailResponse(
                success=True,
                message=f"Test email sent successfully to {request.to_email}",
                email_configured=True
            )
        else:
            return TestEmailResponse(
                success=False,
                message="Failed to send email. Check server logs for details.",
                email_configured=True
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error sending test email: {str(e)}"
        )


@router.get("/email-config", response_model=dict)
async def check_email_config():
    """
    Check if email service is properly configured.
    
    Returns configuration status without exposing credentials.
    """
    return {
        "email_configured": settings.email_enabled,
        "smtp_host": settings.smtp_host if settings.smtp_host else "Not configured",
        "smtp_port": settings.smtp_port,
        "smtp_from_email": settings.smtp_from_email if settings.smtp_from_email else "Not configured",
        "smtp_from_name": settings.smtp_from_name,
        "smtp_use_tls": settings.smtp_use_tls,
        "smtp_use_ssl": settings.smtp_use_ssl
    }