"""
ORM model: WEAPON_MOUNT

Specific weapon fitted to a platform mount (e.g. 20mm Cannon on Pylon-3).
Classification tier: CONFIDENTIAL
"""

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from sentinel_curator.models.base import Base

if TYPE_CHECKING:
    from sentinel_curator.models.platform_mount import PlatformMount


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
    operator_country: Mapped[str] = mapped_column(String(100), nullable=False)
    owner_country: Mapped[str] = mapped_column(String(100), nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    mount: Mapped["PlatformMount"] = relationship(
        "PlatformMount",
        back_populates="weapons",
    )
