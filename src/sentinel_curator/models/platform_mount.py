"""
ORM model: PLATFORM_MOUNT (hardpoint / pylon)

Maps physical mount positions on an individual platform.
Classification tier: CONFIDENTIAL

  - operator_country FK → COUNTRY
  - owner_country    FK → COUNTRY
"""

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from sentinel_curator.models.base import Base

if TYPE_CHECKING:
    from sentinel_curator.models.country import Country
    from sentinel_curator.models.individual_platform import IndividualPlatform
    from sentinel_curator.models.weapon_mount import WeaponMount


class PlatformMount(Base):
    """A physical hardpoint or pylon on an individual platform."""

    __tablename__ = "platform_mount"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    mount_designation: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="Mount designation, e.g. 'Pylon-3', 'Turret-A'",
    )
    platform_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("individual_platform.id", ondelete="CASCADE"),
        nullable=False,
    )
    operator_country: Mapped[str] = mapped_column(
        String(2),
        ForeignKey("country.alpha2", ondelete="RESTRICT"),
        nullable=False,
        comment="ISO 3166-1 alpha-2 FK — nation operating this mount",
    )
    owner_country: Mapped[str] = mapped_column(
        String(2),
        ForeignKey("country.alpha2", ondelete="RESTRICT"),
        nullable=False,
        comment="ISO 3166-1 alpha-2 FK — nation owning this mount",
    )

    # ------------------------------------------------------------------
    # Relationships
    # ------------------------------------------------------------------

    platform: Mapped["IndividualPlatform"] = relationship(
        "IndividualPlatform",
        back_populates="mounts",
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

    weapons: Mapped[list["WeaponMount"]] = relationship(
        "WeaponMount",
        back_populates="mount",
        cascade="all, delete-orphan",
    )
