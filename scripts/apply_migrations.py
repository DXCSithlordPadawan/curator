"""
apply_migrations.py

Applies all SQL migration files in db/migrations/ in filename order
against the configured PostgreSQL database.

Usage:
    python scripts/apply_migrations.py

The script is idempotent — all DDL statements use CREATE IF NOT EXISTS.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import psycopg2
from psycopg2 import sql as pgsql

# Ensure the src package is importable when run from the project root.
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from sentinel_curator.utils.config import get_settings  # noqa: E402
from sentinel_curator.utils.logging import configure_logging, get_logger  # noqa: E402

configure_logging()
logger = get_logger(__name__)

MIGRATIONS_DIR = Path(__file__).resolve().parents[1] / "db" / "migrations"


def apply_migrations() -> None:
    """Apply all .sql files in db/migrations/ in sorted order."""
    settings = get_settings()

    migration_files = sorted(MIGRATIONS_DIR.glob("*.sql"))
    if not migration_files:
        logger.warning("apply_migrations.no_files", directory=str(MIGRATIONS_DIR))
        return

    logger.info(
        "apply_migrations.start",
        file_count=len(migration_files),
        db=settings.db_name,
        host=settings.db_host,
    )

    conn = psycopg2.connect(
        host=settings.db_host,
        port=settings.db_port,
        dbname=settings.db_name,
        user=settings.db_user,
        password=settings.db_password.get_secret_value(),
    )
    conn.autocommit = False

    try:
        for migration_file in migration_files:
            logger.info("apply_migrations.applying", file=migration_file.name)
            sql_text = migration_file.read_text(encoding="utf-8")
            with conn.cursor() as cur:
                cur.execute(sql_text)
            conn.commit()
            logger.info("apply_migrations.applied", file=migration_file.name)
    except Exception as exc:
        conn.rollback()
        logger.error("apply_migrations.failed", error=str(exc))
        raise
    finally:
        conn.close()

    logger.info("apply_migrations.complete", file_count=len(migration_files))


if __name__ == "__main__":
    apply_migrations()
