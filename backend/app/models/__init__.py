from sqlmodel import SQLModel

# Import all models so Alembic detects them
from .user import User
# from .role import Role
# from .other import OtherModel

# ✅ Expose metadata for Alembic
Base = SQLModel.metadata

__all__ = ["User", "Base"]
