from sqlmodel import SQLModel, Field
from typing import Optional

class Admin(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True)
    email: str = Field(index=True, unique=True)
    hashed_password: str
    is_superadmin: bool = False  # Indicates if this admin has full access
    is_active: bool = True