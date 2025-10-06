import sys
import pathlib
from logging.config import fileConfig

from alembic import context
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import pool
from sqlmodel import SQLModel

# -------------------------------------------------------------------------
# 1. Ensure backend/app is in sys.path
# -------------------------------------------------------------------------
BASE_DIR = pathlib.Path(__file__).resolve().parents[1]  # ~/ADL-backend
APP_DIR = BASE_DIR / "backend" / "app"
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

# -------------------------------------------------------------------------
# 2. Import settings and models
# -------------------------------------------------------------------------
from core.config import settings
import models  # noqa: F401  # ensure models are imported so Alembic detects them
from models.base import metadata  # ✅ SQLModel.metadata exposed in base.py

# -------------------------------------------------------------------------
# 3. Alembic config object & logging
# -------------------------------------------------------------------------
config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Metadata used for autogeneration
target_metadata = metadata

# -------------------------------------------------------------------------
# 4. Helper: resolve DB URL
# -------------------------------------------------------------------------
def get_url() -> str:
    url = getattr(settings, "database_url", None) or getattr(settings, "DATABASE_URL", None)
    if not url:
        raise RuntimeError("❌ DATABASE_URL is not set in settings or .env file")
    return url

# -------------------------------------------------------------------------
# 5. Offline migrations
# -------------------------------------------------------------------------
def run_migrations_offline():
    """Run migrations without a DB connection (generates SQL only)."""
    context.configure(
        url=get_url(),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,            # detect column type changes
        compare_server_default=True,  # detect default value changes
        render_as_batch=True,         # safer for SQLite
    )

    with context.begin_transaction():
        context.run_migrations()

# -------------------------------------------------------------------------
# 6. Online migrations (async engine)
# -------------------------------------------------------------------------
async def run_migrations_online():
    """Run migrations with a live DB connection."""
    connectable = create_async_engine(
        get_url(),
        poolclass=pool.NullPool,
        future=True,
    )

    async with connectable.connect() as connection:
        def do_migrations(conn):
            context.configure(
                connection=conn,
                target_metadata=target_metadata,
                compare_type=True,
                compare_server_default=True,
                render_as_batch=True,
            )
            with context.begin_transaction():
                context.run_migrations()

        await connection.run_sync(do_migrations)

# -------------------------------------------------------------------------
# 7. Entrypoint
# -------------------------------------------------------------------------
if context.is_offline_mode():
    run_migrations_offline()
else:
    import asyncio
    asyncio.run(run_migrations_online())
