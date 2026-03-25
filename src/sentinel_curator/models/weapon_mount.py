"""
ORM model: WEAPON_MOUNT

Specific weapon fitted to a platform mount (e.g. 20mm Cannon on Pylon-3).
Classification tier: CONFIDENTIAL

  - operator_country FK → COUNTRY
  - owner_country    FK → COUNTRY
  - status_id        FK → STATUS (optional)
"""

import uuid
from typing import TYPE_CHECKING, Optional

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from sentinel_curator.models.base import Base

if TYPE_CHECKING:
    from sentinel_curator.models.country import Country
    from sentinel_curator.models.platform_mount import PlatformMount
    from sentinel_curator.models.status import Status


class WeaponMount(Base):
    """A specific weapon fitted to a platform mount position."""

    __tablename__ = "weapon_mount"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    weapon_designation: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Weapon designation, e.g. 'Phalanx CIWS Block 1B', 'Mk 41 VLS'",
    )
    mount_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("platform_mount.id", ondelete="CASCADE"),
        nullable=False,
    )
    operator_country: Mapped[str] = mapped_column(
        String(2),
        ForeignKey("country.alpha2", ondelete="RESTRICT"),
        nullable=False,
        comment="ISO 3166-1 alpha-2 FK — nation operating this weapon",
    )
    owner_country: Mapped[str] = mapped_column(
        String(2),
        ForeignKey("country.alpha2", ondelete="RESTRICT"),
        nullable=False,
        comment="ISO 3166-1 alpha-2 FK — nation owning this weapon",
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    status_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("status.id", ondelete="SET NULL"),
        nullable=True,
        default=None,
        comment=(
            "Optional FK to the STATUS master table indicating the current "
            "operational status of this weapon (e.g. Active, In Maintenance). "
            "NULL when not set."
        ),
    )

    # ------------------------------------------------------------------
    # Relationships
    # ------------------------------------------------------------------

    mount: Mapped["PlatformMount"] = relationship(
        "PlatformMount",
        back_populates="weapons",
    )

    operator: Mapped["Country"] = relationship(
        "Country",
        foreign_keys=[operator_country],
        lazy="select",
    )

    owner: Mapped["Country"] = relationship(
        "Country",
        foreign_keys=[owner_country],
        lazy="select",
    )

    # Operational status of this weapon (e.g. Active, In Maintenance).
    status: Mapped[Optional["Status"]] = relationship(
        "Status",
        back_populates="weapons",
        lazy="select",
    )
