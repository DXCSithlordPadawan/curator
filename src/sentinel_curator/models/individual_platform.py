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
"""

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String
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
