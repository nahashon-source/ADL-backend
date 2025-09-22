from pydantic_settings import BaseSettings  # ✅ correct for Pydantic v2
from pydantic import SecretStr, AnyHttpUrl
from typing import List, Optional


class Settings(BaseSettings):
    # === App Metadata ===
    project_name: str = "ADL Backend"
    description: str = "ADL Backend API for Authentication, Admin Panel, and Core Services."
    version: str = "1.0.0"
    debug: bool = True
    environment: str = "development"
    root_path: str = ""

    # === Database ===
    database_url: str = "postgresql+asyncpg://nashon:mwendwa04@localhost:5432/ADL"

    # === Security ===
    secret_key: SecretStr = SecretStr("CHANGE_ME")
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # === CORS ===
    cors_origins: List[AnyHttpUrl] = ["http://localhost:3000"]

    # === API Docs & Contact Info ===
    contact_name: str = "API Support"
    contact_email: str = "support@example.com"
    license_name: str = "MIT"
    license_url: str = "https://opensource.org/licenses/MIT"

    # === Optional external services ===
    smtp_server: Optional[str] = None
    smtp_port: Optional[int] = None
    smtp_username: Optional[str] = None
    smtp_password: Optional[SecretStr] = None

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


settings = Settings()
