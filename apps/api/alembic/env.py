import os
from typing import cast
from logging.config import fileConfig
from sqlalchemy import create_engine, pool
from alembic import context # type: ignore
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv("../../.env")

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

SYNC_DATABASE_URL = os.getenv("SYNC_DATABASE_URL")
if not SYNC_DATABASE_URL:
    raise RuntimeError("SYNC_DATABASE_URL is not set")

# Make Pylance happy: ensure type is str, not Optional[str]
db_url: str = cast(str, SYNC_DATABASE_URL)

target_metadata = None

def run_migrations_offline() -> None:
    context.configure(
        url=db_url,          # use the strictly-typed variable
        literal_binds=True,
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    engine = create_engine(
        db_url,              # use the strictly-typed variable
        poolclass=pool.NullPool,
    )
    with engine.connect() as connection:
        context.configure(
            connection=connection,
            compare_type=True,
        )
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
