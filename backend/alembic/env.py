"""
Alembic env.py — Configuración de migraciones async.
Importa todos los modelos SQLModel para que autogenerate los detecte.
"""

import asyncio
from logging.config import fileConfig

from alembic import context
from dotenv import load_dotenv
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import async_engine_from_config
from sqlmodel import SQLModel

# Cargar variables de entorno ANTES de importar modelos
load_dotenv()

# ── Importar TODOS los modelos para que SQLModel.metadata los registre ──
import app.modules.categorias.model  # noqa: F401, E402
import app.modules.direcciones.model  # noqa: F401, E402
import app.modules.pagos.model  # noqa: F401, E402
import app.modules.pedidos.model  # noqa: F401, E402
import app.modules.productos.model  # noqa: F401, E402
import app.modules.refreshtokens.model  # noqa: F401, E402
import app.modules.usuarios.model  # noqa: F401, E402

from app.core.config import get_settings  # noqa: E402

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Cargar DATABASE_URL desde settings
settings = get_settings()

# Reemplazar asyncpg por psycopg2 para migraciones sync offline,
# o usar la URL async para modo online
database_url = settings.DATABASE_URL
config.set_main_option("sqlalchemy.url", database_url)

# add your model's MetaData object here
# for 'autogenerate' support
target_metadata = SQLModel.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection) -> None:
    """Helper to configure context and run migrations."""
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """Run migrations in 'online' mode using async engine."""
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
