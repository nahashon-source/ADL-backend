"""
Startup checks to ensure the application is properly configured.
Fails fast with clear error messages if critical configurations are missing.
"""
import logging
from typing import Dict, Tuple
import smtplib

from sqlalchemy import text
from backend.app.core.config import settings
from backend.app.db.session import engine

logger = logging.getLogger(__name__)


class StartupCheckError(Exception):
    """Raised when a startup check fails"""
    pass


async def check_database_connection() -> Tuple[bool, str]:
    """
    Check if database connection is available.
    
    Returns:
        Tuple[bool, str]: (success, message)
    """
    try:
        async with engine.connect() as conn:
            # FIX: Execute returns a Result object, fetchone() is synchronous
            result = await conn.execute(text("SELECT 1"))
            row = result.fetchone()  # Don't await - fetchone() is synchronous
            if row is None:
                return False, "Database query returned no results"
        return True, "Database connection successful"
    except Exception as e:
        return False, f"Database connection failed: {str(e)}"


def check_required_env_vars() -> Tuple[bool, str]:
    """
    Check if all required environment variables are set.
    
    Returns:
        Tuple[bool, str]: (success, message)
    """
    required_vars = {
        "SECRET_KEY": settings.secret_key,
        "DATABASE_URL": settings.database_url,
        "PROJECT_NAME": settings.project_name,
    }
    
    missing_vars = []
    weak_vars = []
    
    for var_name, var_value in required_vars.items():
        if not var_value or var_value == "":
            missing_vars.append(var_name)
        elif var_name == "SECRET_KEY" and len(str(var_value)) < 32:
            weak_vars.append(f"{var_name} (too short, should be 32+ characters)")
    
    if missing_vars:
        return False, f"Missing required environment variables: {', '.join(missing_vars)}"
    
    if weak_vars:
        logger.warning(f"⚠️  Weak configuration detected: {', '.join(weak_vars)}")
    
    return True, f"All required environment variables present ({len(required_vars)} checked)"


def check_email_configuration() -> Tuple[bool, str]:
    """
    Check if email configuration is valid.
    Tests SMTP connection without sending emails.
    
    Returns:
        Tuple[bool, str]: (success, message)
    """
    if not settings.smtp_host:
        return True, "Email not configured (optional)"
    
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
    
    # Test SMTP connection (with timeout to avoid hanging)
    try:
        # FIX: Extract SecretStr value properly
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
        
        # Use the extracted password string
        server.login(settings.smtp_user, smtp_password)
        server.quit()
        return True, "Email configuration valid (SMTP connection successful)"
    except smtplib.SMTPAuthenticationError:
        return False, "Email authentication failed (check SMTP_USER and SMTP_PASSWORD)"
    except Exception as e:
        # Don't fail startup on email issues - log warning instead
        logger.warning(f"⚠️  Email configuration test failed: {str(e)}")
        return True, f"Email configured but connection test failed: {str(e)}"


def check_security_configuration() -> Tuple[bool, str]:
    """
    Check security-related configurations.
    
    Returns:
        Tuple[bool, str]: (success, message)
    """
    warnings = []
    
    # Check JWT token expiration
    if settings.access_token_expire_minutes < 5:
        warnings.append("ACCESS_TOKEN_EXPIRE_MINUTES is very short (< 5 minutes)")
    elif settings.access_token_expire_minutes > 60:
        warnings.append("ACCESS_TOKEN_EXPIRE_MINUTES is very long (> 60 minutes)")
    
    # Check debug mode in production
    if settings.environment == "production" and settings.debug:
        warnings.append("DEBUG mode is enabled in production environment")
    
    # Check CORS origins
    if "*" in settings.cors_origins_list:
        warnings.append("CORS allows all origins (*) - security risk in production")
    
    if warnings:
        logger.warning(f"⚠️  Security warnings: {'; '.join(warnings)}")
        return True, f"Security check passed with warnings: {len(warnings)} issue(s)"
    
    return True, "Security configuration looks good"


async def run_all_startup_checks() -> Dict[str, Tuple[bool, str]]:
    """
    Run all startup checks and return results.
    
    Returns:
        Dict[str, Tuple[bool, str]]: Dictionary of check results
    """
    logger.info("🔍 Running startup checks...")
    
    checks = {
        "Environment Variables": check_required_env_vars(),
        "Security Configuration": check_security_configuration(),
        "Email Configuration": check_email_configuration(),
        "Database Connection": await check_database_connection(),
    }
    
    return checks


async def perform_startup_checks(fail_fast: bool = False) -> None:
    """
    Perform all startup checks and optionally fail fast.
    
    Args:
        fail_fast: If True, raise exception on first failure
        
    Raises:
        StartupCheckError: If any check fails and fail_fast is True
    """
    logger.info("=" * 60)
    logger.info("🔍 STARTUP CHECKS")
    logger.info("=" * 60)
    
    results = await run_all_startup_checks()
    
    all_passed = True
    failed_checks = []
    
    for check_name, (success, message) in results.items():
        status = "✅" if success else "❌"
        log_func = logger.info if success else logger.error
        log_func(f"{status} {check_name}: {message}")
        
        if not success:
            all_passed = False
            failed_checks.append(check_name)
    
    logger.info("=" * 60)
    
    if not all_passed:
        error_msg = f"Startup checks failed: {', '.join(failed_checks)}"
        logger.error(f"❌ {error_msg}")
        logger.error("=" * 60)
        
        if fail_fast:
            raise StartupCheckError(error_msg)
        else:
            logger.warning("⚠️  Continuing despite failed checks (fail_fast=False)")
    else:
        logger.info("✅ All startup checks passed!")
    
    logger.info("=" * 60)