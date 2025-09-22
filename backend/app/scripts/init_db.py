
import asyncio
from backend.app.db.session import init_db  # ✅ absolute import works from project root

async def main():
    await init_db()
    print("✅ Database tables created successfully!")

if __name__ == "__main__":
    asyncio.run(main())