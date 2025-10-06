from sqlmodel import SQLModel

# Import your models so Alembic can detect them
from .user import User
from .admin import Admin
# from .item import Item
# from .contact_message import ContactMessage

# Expose metadata for Alembic
metadata = SQLModel.metadata


def init_models(engine):
    """
    Create all tables defined in SQLModel.
    Call this only for local development or testing,
    not in production where migrations should be used.
    """
    SQLModel.metadata.create_all(engine)
