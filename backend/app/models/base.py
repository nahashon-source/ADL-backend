from sqlmodel import SQLModel

# Import your models here
# from .admin import Admin
# from .item import Item
# from .contact_message import ContactMessage

# This will help Alembic discover models
def init_models():
    SQLModel.metadata.create_all
