from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr
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

    # === SMTP Email Configuration (Optional) ===
    smtp_host: Optional[str] = None
    smtp_port: Optional[int] = None
    smtp_user: Optional[str] = None
    smtp_password: Optional[SecretStr] = None
    smtp_from_email: Optional[str] = None
    smtp_from_name: Optional[str] = None
    
    # === Server Config (not used directly, just for reference) ===
    backend_port: Optional[int] = None
    host: Optional[str] = None

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


settings = Settings()
