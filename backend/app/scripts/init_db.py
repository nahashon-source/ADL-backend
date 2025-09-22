import asyncio
from sqlmodel import SQLModel
from backend.app.db.session import engine
from backend.app.models.user import User
from backend.app.models.admin import Admin

async def main():
    """
    Initialize all database tables defined in SQLModel models.
    """
    try:
        async with engine.begin() as conn:
            # Create all tables for registered models
            await conn.run_sync(SQLModel.metadata.create_all)
        print("✅ Database tables created successfully!")
    except Exception as e:
        print(f"❌ Failed to initialize database: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())