from typing import AsyncGenerator

from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from backend.app.core.config import settings

# --- Async Engine ---
engine = create_async_engine(
    settings.database_url,
    echo=True,   # 🔹 Set False in production
    future=True,
)

# --- Async Session Maker ---
async_session_maker = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# --- Dependency for FastAPI routes ---
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Async generator for database sessions.
    Use in FastAPI with: Depends(get_session)
    """
    async with async_session_maker() as session:
        yield session

# --- Initialize DB ---
async def init_db() -> None:
    """
    Create all tables defined in SQLModel metadata.
    """
    try:
        async with engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.create_all)
        print("✅ Database tables created successfully!")
    except Exception as e:
        print(f"❌ Failed to initialize database: {e}")
        raise
