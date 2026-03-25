"""
ORM model: STATUS

Master lookup table for operational status codes
(e.g. Active, Decommissioned, In Maintenance, Reserve).
Classification tier: UNCLASSIFIED

Relationships:
  - referenced by zero, one, or many INDIVIDUAL_PLATFORM (status_id)
  - referenced by zero, one, or many WEAPON_MOUNT (status_id)
"""

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from sentinel_curator.models.base import Base

if TYPE_CHECKING:
    from sentinel_curator.models.individual_platform import IndividualPlatform
    from sentinel_curator.models.weapon_mount import WeaponMount


class Status(Base):
    """Master lookup for operational status codes."""

    __tablename__ = "status"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="UUID v4 — prevents enumeration",
    )
    code: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        unique=True,
        comment="Short machine-readable code, e.g. ACTIVE, DECOMMISSIONED, MAINTENANCE, RESERVE",
    )
    label: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Human-readable label for display purposes",
    )
    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Optional description of what this status means operationally",
    )

    # ------------------------------------------------------------------
    # Relationships
    # ------------------------------------------------------------------

    platforms: Mapped[list["IndividualPlatform"]] = relationship(
        "IndividualPlatform",
        back_populates="status",
        lazy="select",
    )

    weapons: Mapped[list["WeaponMount"]] = relationship(
        "WeaponMount",
        back_populates="status",
        lazy="select",
    )
