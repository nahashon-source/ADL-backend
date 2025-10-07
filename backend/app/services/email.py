import aiosmtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from jinja2 import Environment, FileSystemLoader, select_autoescape
from pathlib import Path
from typing import List, Optional
import logging

from backend.app.core.config import settings

logger = logging.getLogger(__name__)


class EmailService:
    """Async email service for sending transactional emails."""
    
    def __init__(self):
        """Initialize email service with SMTP configuration."""
        self.smtp_host = settings.smtp_host
        self.smtp_port = settings.smtp_port
        self.smtp_user = settings.smtp_user
        self.smtp_password = settings.smtp_password.get_secret_value() if settings.smtp_password else None
        self.from_email = settings.smtp_from_email
        self.from_name = settings.smtp_from_name
        self.use_tls = settings.smtp_use_tls
        self.use_ssl = settings.smtp_use_ssl
        
        # Setup Jinja2 template environment
        template_dir = Path(__file__).parent.parent / "templates" / "emails"
        template_dir.mkdir(parents=True, exist_ok=True)
        
        self.jinja_env = Environment(
            loader=FileSystemLoader(str(template_dir)),
            autoescape=select_autoescape(['html', 'xml'])
        )
    
    def _is_configured(self) -> bool:
        """Check if email service is properly configured."""
        return all([
            self.smtp_host,
            self.smtp_port,
            self.smtp_user,
            self.smtp_password,
            self.from_email
        ])
    
    async def send_email(
        self,
        to_email: str,
        subject: str,
        html_body: str,
        text_body: Optional[str] = None,
        cc: Optional[List[str]] = None,
        bcc: Optional[List[str]] = None
    ) -> bool:
        """
        Send an email using SMTP.
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            html_body: HTML version of email body
            text_body: Plain text version (optional, will use HTML if not provided)
            cc: List of CC recipients (optional)
            bcc: List of BCC recipients (optional)
            
        Returns:
            bool: True if email sent successfully, False otherwise
        """
        if not self._is_configured():
            logger.error("Email service not configured. Please set SMTP environment variables.")
            return False
        
        try:
            # Create message
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = f"{self.from_name} <{self.from_email}>"
            message["To"] = to_email
            
            if cc:
                message["Cc"] = ", ".join(cc)
            if bcc:
                message["Bcc"] = ", ".join(bcc)
            
            # Add plain text version (fallback)
            if text_body:
                text_part = MIMEText(text_body, "plain")
                message.attach(text_part)
            
            # Add HTML version
            html_part = MIMEText(html_body, "html")
            message.attach(html_part)
            
            # Send email via SMTP
            if self.use_ssl:
                await aiosmtplib.send(
                    message,
                    hostname=self.smtp_host,
                    port=self.smtp_port,
                    username=self.smtp_user,
                    password=self.smtp_password,
                    use_tls=False,
                    start_tls=False
                )
            else:
                await aiosmtplib.send(
                    message,
                    hostname=self.smtp_host,
                    port=self.smtp_port,
                    username=self.smtp_user,
                    password=self.smtp_password,
                    use_tls=self.use_tls,
                    start_tls=self.use_tls
                )
            
            logger.info(f"Email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {str(e)}")
            return False
    
    def render_template(self, template_name: str, **context) -> str:
        """
        Render an email template with context variables.
        
        Args:
            template_name: Name of template file (e.g., 'password_reset.html')
            **context: Variables to pass to template
            
        Returns:
            str: Rendered HTML content
        """
        try:
            template = self.jinja_env.get_template(template_name)
            return template.render(**context)
        except Exception as e:
            logger.error(f"Failed to render template {template_name}: {str(e)}")
            raise
    
    async def send_password_reset_email(
        self,
        to_email: str,
        reset_token: str,
        user_name: str
    ) -> bool:
        """
        Send password reset email.
        
        Args:
            to_email: User's email address
            reset_token: Password reset token
            user_name: User's name
            
        Returns:
            bool: True if sent successfully
        """
        # For now, use a simple HTML template inline
        # In Task 5.5, we'll create proper template files
        reset_url = f"{settings.cors_origins.split(',')[0]}/reset-password?token={reset_token}"
        
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Password Reset</title>
        </head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; text-align: center; border-radius: 10px 10px 0 0;">
                <h1 style="color: white; margin: 0;">Password Reset Request</h1>
            </div>
            <div style="background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px;">
                <p>Hello {user_name},</p>
                <p>We received a request to reset your password. Click the button below to reset it:</p>
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{reset_url}" 
                       style="background: #667eea; color: white; padding: 14px 28px; text-decoration: none; border-radius: 5px; display: inline-block; font-weight: bold;">
                        Reset Password
                    </a>
                </div>
                <p style="color: #666; font-size: 14px;">
                    This link will expire in 1 hour. If you didn't request a password reset, you can safely ignore this email.
                </p>
                <hr style="border: none; border-top: 1px solid #ddd; margin: 30px 0;">
                <p style="color: #999; font-size: 12px; text-align: center;">
                    {settings.project_name} • {settings.contact_email}
                </p>
            </div>
        </body>
        </html>
        """
        
        text_body = f"""
        Password Reset Request
        
        Hello {user_name},
        
        We received a request to reset your password. Click the link below to reset it:
        
        {reset_url}
        
        This link will expire in 1 hour. If you didn't request a password reset, you can safely ignore this email.
        
        {settings.project_name}
        """
        
        return await self.send_email(
            to_email=to_email,
            subject="Password Reset Request",
            html_body=html_body,
            text_body=text_body
        )
    
    async def send_welcome_email(self, to_email: str, user_name: str) -> bool:
        """
        Send welcome email to new users.
        
        Args:
            to_email: User's email address
            user_name: User's name
            
        Returns:
            bool: True if sent successfully
        """
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Welcome</title>
        </head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; text-align: center; border-radius: 10px 10px 0 0;">
                <h1 style="color: white; margin: 0;">Welcome to {settings.project_name}! 🎉</h1>
            </div>
            <div style="background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px;">
                <p>Hello {user_name},</p>
                <p>Welcome to {settings.project_name}! We're excited to have you on board.</p>
                <p>Your account has been successfully created and you can now start using our services.</p>
                <div style="background: white; padding: 20px; border-radius: 5px; margin: 20px 0;">
                    <h3 style="margin-top: 0; color: #667eea;">Getting Started</h3>
                    <ul style="color: #666;">
                        <li>Complete your profile</li>
                        <li>Explore our features</li>
                        <li>Contact support if you need help</li>
                    </ul>
                </div>
                <p>If you have any questions, feel free to reach out to our support team.</p>
                <hr style="border: none; border-top: 1px solid #ddd; margin: 30px 0;">
                <p style="color: #999; font-size: 12px; text-align: center;">
                    {settings.project_name} • {settings.contact_email}
                </p>
            </div>
        </body>
        </html>
        """
        
        text_body = f"""
        Welcome to {settings.project_name}!
        
        Hello {user_name},
        
        Welcome to {settings.project_name}! We're excited to have you on board.
        
        Your account has been successfully created and you can now start using our services.
        
        If you have any questions, feel free to reach out to our support team.
        
        {settings.project_name}
        """
        
        return await self.send_email(
            to_email=to_email,
            subject=f"Welcome to {settings.project_name}!",
            html_body=html_body,
            text_body=text_body
        )


# Global email service instance
email_service = EmailService()