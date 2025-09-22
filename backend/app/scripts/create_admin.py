import asyncio
from sqlmodel import SQLModel
from app.db.session import engine

async def init_admin():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    print("Admin seeder placeholder")

if __name__ == "__main__":
    asyncio.run(init_admin())
