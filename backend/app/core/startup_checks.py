"""
Startup validation checks to ensure the application is properly configured
"""
import os
import logging
import smtplib
from typing import Dict, Tuple
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from sqlalchemy import text

from backend.app.core.config import settings
from backend.app.db.session import engine

logger = logging.getLogger(__name__)


def check_database_connection() -> Tuple[bool, str]:
    """
    Check if database connection is working.
    Returns: (success: bool, message: str)
    """
    try:
        # Use sync connection for startup check
        from sqlalchemy import create_engine
        
        # Create sync engine from async URL
        sync_url = settings.database_url.replace('+asyncpg', '')
        sync_engine = create_engine(sync_url)
        
        with sync_engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            result.fetchone()
        
        sync_engine.dispose()
        return True, "Database connection successful"
    except Exception as e:
        return False, f"Database connection failed: {str(e)}"


def check_required_env_vars() -> Tuple[bool, str]:
    """
    Check if all required environment variables are set.
    Returns: (success: bool, message: str)
    """
    required_vars = {
        "DATABASE_URL": settings.database_url,
        "SECRET_KEY": settings.secret_key,
    }
    
    missing_vars = [k for k, v in required_vars.items() if not v]
    
    if missing_vars:
        return False, f"Missing required environment variables: {', '.join(missing_vars)}"
    
    return True, "All required environment variables are set"


def check_security_configuration() -> Tuple[bool, str]:
    """
    Check if security settings are properly configured.
    Returns: (success: bool, message: str)
    """
    issues = []
    
    # Check secret key length
    if len(settings.secret_key) < 32:
        issues.append("SECRET_KEY should be at least 32 characters long")
    
    # Check token expiry
    if settings.access_token_expire_minutes < 1:
        issues.append("ACCESS_TOKEN_EXPIRE_MINUTES must be positive")
    
    if settings.refresh_token_expire_days < 1:
        issues.append("REFRESH_TOKEN_EXPIRE_DAYS must be positive")
    
    if issues:
        return False, "; ".join(issues)
    
    return True, "Security configuration is valid"


def check_email_configuration() -> Tuple[bool, str]:
    """
    Check if email configuration is valid.
    Tests SMTP connection without sending emails.
    Skips actual SMTP connection in test environment.
    """
    # Skip SMTP connection test in test environment
    if os.getenv("ENVIRONMENT") == "test":
        logger.info("Skipping SMTP connection test in test environment")
        return True, "Email check skipped in test environment"
    
    if not settings.smtp_host:
        return True, "Email configuration not set (optional)"
    
    required_email_vars = {
        "SMTP_HOST": settings.smtp_host,
        "SMTP_PORT": settings.smtp_port,
        "SMTP_USER": settings.smtp_user,
        "SMTP_PASSWORD": settings.smtp_password,
        "SMTP_FROM_EMAIL": settings.smtp_from_email,
    }
    
    missing_vars = [k for k, v in required_email_vars.items() if not v]
    if missing_vars:
        return False, f"Incomplete email configuration. Missing: {', '.join(missing_vars)}"
    
    # Test SMTP connection
    try:
        smtp_password = (
            settings.smtp_password.get_secret_value() 
            if hasattr(settings.smtp_password, 'get_secret_value') 
            else settings.smtp_password
        )
        
        if settings.smtp_use_tls:
            server = smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=5)
            server.starttls()
        else:
            server = smtplib.SMTP_SSL(settings.smtp_host, settings.smtp_port, timeout=5)
        
        server.login(settings.smtp_user, smtp_password)
        server.quit()
        
    except smtplib.SMTPAuthenticationError:
        return False, "SMTP authentication failed. Check SMTP_USER and SMTP_PASSWORD"
    except Exception as e:
        # Don't fail startup on email issues - log warning instead
        logger.warning(f"Email configuration test failed: {str(e)}")
        return True, f"Email configured but connection test failed: {str(e)}"
    
    return True, "Email configuration is valid and SMTP connection successful"


async def perform_startup_checks(fail_fast: bool = False) -> Dict[str, Tuple[bool, str]]:
    """
    Perform all startup checks.
    
    Args:
        fail_fast: If True, raise exception on first failure. 
                  If False, continue and log all issues.
    
    Returns:
        Dict of check results: {check_name: (success, message)}
    """
    logger.info("=" * 80)
    logger.info("🚀 PERFORMING STARTUP CHECKS")
    logger.info("=" * 80)
    
    checks = {
        "Environment Variables": check_required_env_vars(),
        "Security Configuration": check_security_configuration(),
        "Database Connection": check_database_connection(),
        "Email Configuration": check_email_configuration(),
    }
    
    all_passed = True
    
    for check_name, (success, message) in checks.items():
        status_icon = "✅" if success else "❌"
        logger.info(f"{status_icon} {check_name}: {message}")
        
        if not success:
            all_passed = False
            if fail_fast:
                raise RuntimeError(f"Startup check failed: {check_name} - {message}")
    
    logger.info("=" * 80)
    
    if all_passed:
        logger.info("✅ ALL STARTUP CHECKS PASSED - Application ready!")
    else:
        logger.warning("⚠️  SOME STARTUP CHECKS FAILED - Application may not work correctly")
    
    logger.info("=" * 80)
    
    return checks
