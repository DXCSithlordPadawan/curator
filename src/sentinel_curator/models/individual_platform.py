"""
ORM model: INDIVIDUAL_PLATFORM

A specific physical asset (e.g. USS Nimitz, CVN-68).
Classification tier: RESTRICTED (location/telemetry data)

Relationships:
  - belongs to one PLATFORM_CLASS
  - has zero, one, or many PLATFORM_MOUNT (weapon hardpoints)
  - has zero, one, or many GEOLOCATION_LOG (telemetry)
  - carries zero, one, or many RWR_SYSTEM (via PLATFORM_RWR association table)
  - operator_country FK → COUNTRY
  - owner_country    FK → COUNTRY
  - optionally embarked on one parent INDIVIDUAL_PLATFORM (parent_platform_id)
  - may host zero, one, or many embarked INDIVIDUAL_PLATFORM (embarked_platforms)
  - a platform cannot be its own parent (DB enforces chk_no_self_parent)
"""

import uuid
from typing import TYPE_CHECKING, Optional

from sqlalchemy import CheckConstraint, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from sentinel_curator.models.base import Base

if TYPE_CHECKING:
    from sentinel_curator.models.country import Country
    from sentinel_curator.models.geolocation_log import GeolocationLog
    from sentinel_curator.models.platform_class import PlatformClass
    from sentinel_curator.models.platform_mount import PlatformMount
    from sentinel_curator.models.rwr_system import RwrSystem


class IndividualPlatform(Base):
    """A specific physical instance of a platform class."""

    __tablename__ = "individual_platform"
    __table_args__ = (
        CheckConstraint(
            "parent_platform_id <> id",
            name="chk_no_self_parent",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="UUID v4 — prevents enumeration",
    )
    hull_serial_id: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        unique=True,
        comment="Hull number or serial identifier, e.g. CVN-68",
    )
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Common name, e.g. USS Nimitz",
    )
    class_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("platform_class.id", ondelete="RESTRICT"),
        nullable=False,
        comment="FK to parent platform class",
    )
    operator_country: Mapped[str] = mapped_column(
        String(2),
        ForeignKey("country.alpha2", ondelete="RESTRICT"),
        nullable=False,
        comment="ISO 3166-1 alpha-2 FK — nation currently operating this platform",
    )
    owner_country: Mapped[str] = mapped_column(
        String(2),
        ForeignKey("country.alpha2", ondelete="RESTRICT"),
        nullable=False,
        comment="ISO 3166-1 alpha-2 FK — nation that owns this platform",
    )
    parent_platform_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("individual_platform.id", ondelete="SET NULL"),
        nullable=True,
        default=None,
        comment=(
            "Optional FK to the hosting INDIVIDUAL_PLATFORM "
            "(e.g. aircraft carrier for an embarked aircraft). "
            "NULL when this platform operates independently. "
            "Cannot equal this platform's own id (chk_no_self_parent)."
        ),
    )

    # ------------------------------------------------------------------
    # Relationships
    # ------------------------------------------------------------------

    platform_class: Mapped["PlatformClass"] = relationship(
        "PlatformClass",
        back_populates="platforms",
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

    mounts: Mapped[list["PlatformMount"]] = relationship(
        "PlatformMount",
        back_populates="platform",
        cascade="all, delete-orphan",
    )

    geolocation_logs: Mapped[list["GeolocationLog"]] = relationship(
        "GeolocationLog",
        back_populates="platform",
        cascade="all, delete-orphan",
    )

    # Zero, one, or many RWR systems fitted to this platform.
    # Joined via the PLATFORM_RWR association table.
    rwr_systems: Mapped[list["RwrSystem"]] = relationship(
        "RwrSystem",
        secondary="platform_rwr",
        back_populates="platforms",
        lazy="select",
    )

    # Self-referential: the parent platform that hosts/carries this platform
    # (e.g. the aircraft carrier for an embarked aircraft). NULL if independent.
    parent_platform: Mapped[Optional["IndividualPlatform"]] = relationship(
        "IndividualPlatform",
        foreign_keys=[parent_platform_id],
        back_populates="embarked_platforms",
        remote_side=[id],
        lazy="select",
    )

    # Self-referential: platforms embarked on / hosted by this platform.
    embarked_platforms: Mapped[list["IndividualPlatform"]] = relationship(
        "IndividualPlatform",
        foreign_keys=[parent_platform_id],
        back_populates="parent_platform",
        lazy="select",
    )
