from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr, field_validator
from typing import List, Optional


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    Compatible with Pydantic v2.
    """
    
    # === App Metadata ===
    project_name: str = "ADL Backend"
    description: str = "ADL Backend API for Authentication, Admin Panel, and Core Services."
    version: str = "1.0.0"
    debug: bool = True
    environment: str = "development"
    root_path: str = ""

    # === Contact Info (for FastAPI docs) ===
    contact_name: str = "API Support"
    contact_email: str = "support@example.com"
    license_name: str = "MIT"
    license_url: str = "https://opensource.org/licenses/MIT"

    # === Database ===
    database_url: str = "postgresql+asyncpg://adl_user:changeme@postgres:5432/adl_db"
    
    # PostgreSQL variables (not used directly, just for docker-compose)
    postgres_user: Optional[str] = None
    postgres_password: Optional[str] = None
    postgres_db: Optional[str] = None
    postgres_port: Optional[int] = None

    # === Security ===
    secret_key: SecretStr = SecretStr("CHANGE_ME")
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    # === CORS (stored as comma-separated string) ===
    cors_origins: str = "http://localhost:3000"

    # === SMTP Email Configuration ===
    smtp_host: Optional[str] = None
    smtp_port: int = 587  # Default to TLS port
    smtp_user: Optional[str] = None
    smtp_password: Optional[SecretStr] = None
    smtp_from_email: Optional[str] = None
    smtp_from_name: str = "ADL Backend"  # Default sender name
    smtp_use_tls: bool = True
    smtp_use_ssl: bool = False
    
    # === Frontend URL for Email Links ===
    frontend_url: str = "http://localhost:3000"
    
    # === Password Reset Token Settings ===
    reset_token_expire_minutes: int = 60  # 1 hour
    
    # === Server Config (not used directly, just for reference) ===
    backend_port: Optional[int] = None
    host: Optional[str] = None

    # === Logging Configuration ===
    log_level: str = "INFO"
    log_dir: str = "logs"
    enable_json_logs: bool = False  # Enable in production for structured logs
    enable_console_logs: bool = True

    # === Pydantic v2 Configuration ===
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="allow",
    )
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS origins from comma-separated string."""
        if isinstance(self.cors_origins, str):
            return [origin.strip() for origin in self.cors_origins.split(",")]
        return [self.cors_origins]
    
    @property
    def email_enabled(self) -> bool:
        """Check if email service is properly configured."""
        return all([
            self.smtp_host,
            self.smtp_port,
            self.smtp_user,
            self.smtp_password,
            self.smtp_from_email
        ])
    
    @property
    def smtp_server(self) -> Optional[str]:
        """Alias for smtp_host for compatibility."""
        return self.smtp_host
    
    @property
    def smtp_username(self) -> Optional[str]:
        """Alias for smtp_user for compatibility."""
        return self.smtp_user
    
    @property
    def from_email(self) -> Optional[str]:
        """Alias for smtp_from_email for compatibility."""
        return self.smtp_from_email
    
    @property
    def from_name(self) -> str:
        """Alias for smtp_from_name for compatibility."""
        return self.smtp_from_name
    
    def get_smtp_password(self) -> Optional[str]:
        """Get the SMTP password as a plain string."""
        if self.smtp_password:
            return self.smtp_password.get_secret_value()
        return None


settings = Settings()
