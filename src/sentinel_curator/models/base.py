"""
SQLAlchemy declarative base and shared column conventions.

All tables use UUID v4 primary keys to prevent enumeration attacks.
Timestamps are stored in UTC.
"""

import uuid

from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase, mapped_column
from sqlalchemy.dialects.postgresql import UUID


# Naming convention keeps FK/index names deterministic across migrations.
_NAMING_CONVENTION: dict[str, str] = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class Base(DeclarativeBase):
    """Shared declarative base for all Sentinel Curator ORM models."""

    metadata = MetaData(naming_convention=_NAMING_CONVENTION)

    def __repr__(self) -> str:  # pragma: no cover
        cols = ", ".join(
            f"{c.name}={getattr(self, c.name)!r}"
            for c in self.__table__.columns
        )
        return f"<{self.__class__.__name__}({cols})>"
