import asyncio
from logging.config import fileConfig
import sys
from pathlib import Path

from alembic import context
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.future import Connection

# Handle both local development and Docker container paths
if str(Path(__file__).parent.parent.parent) not in sys.path:
    sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Use relative imports that work in both environments
try:
    from core.settings import get_settings
    from db.meta import meta
    from db.models import load_all_models
except ImportError:
    # Fallback for local development
    from src.core.settings import get_settings
    from src.db.meta import meta
    from src.db.models import load_all_models

# load models BEFORE metadata
load_all_models()

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = meta


def run_migrations_offline() -> None:
    settings = get_settings()

    context.configure(
        url=settings.postgres_url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    settings = get_settings()

    engine = create_async_engine(settings.postgres_url)

    async with engine.connect() as connection:
        await connection.run_sync(do_run_migrations)


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())