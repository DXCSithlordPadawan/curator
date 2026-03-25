"""
ORM model: INDIVIDUAL_PLATFORM

A specific physical asset (e.g. USS Nimitz, CVN-68).
Classification tier: RESTRICTED (location/telemetry data)
"""

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from sentinel_curator.models.base import Base

if TYPE_CHECKING:
    from sentinel_curator.models.platform_class import PlatformClass
    from sentinel_curator.models.platform_mount import PlatformMount
    from sentinel_curator.models.geolocation_log import GeolocationLog


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
        String(100),
        nullable=False,
        comment="ISO 3166-1 alpha-2 country code of operating nation",
    )
    owner_country: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="ISO 3166-1 alpha-2 country code of owning nation",
    )

    # Relationships
    platform_class: Mapped["PlatformClass"] = relationship(
        "PlatformClass",
        back_populates="platforms",
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
