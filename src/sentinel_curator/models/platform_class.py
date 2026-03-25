"""
ORM model: PLATFORM_CLASS

Represents the master template for a ship/vehicle design (e.g. Nimitz-class).
Classification tier: UNCLASSIFIED
"""

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from sentinel_curator.models.base import Base

if TYPE_CHECKING:
    from sentinel_curator.models.individual_platform import IndividualPlatform


class PlatformClass(Base):
    """Master design template — e.g. 'Nimitz-class', 'Type 45 Destroyer'."""

    __tablename__ = "platform_class"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="UUID v4 — prevents enumeration",
    )
    class_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True,
        comment="Common design designation, e.g. 'Nimitz-class'",
    )
    manufacturer_country: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="ISO 3166-1 alpha-2 country code of manufacturer",
    )
    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Unclassified public description",
    )

    # Relationships
    platforms: Mapped[list["IndividualPlatform"]] = relationship(
        "IndividualPlatform",
        back_populates="platform_class",
        cascade="all, delete-orphan",
    )
