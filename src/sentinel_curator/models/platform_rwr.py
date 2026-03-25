"""
ORM model: PLATFORM_RWR (association table)

Links INDIVIDUAL_PLATFORM to RWR_SYSTEM as a many-to-many relationship.

An individual platform may carry zero, one, or many RWR systems.
The same RWR model designation may be fitted to multiple platforms.

Classification tier: CONFIDENTIAL (inherits from RWR_SYSTEM)
"""

import uuid

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from sentinel_curator.models.base import Base


class PlatformRwr(Base):
    """
    Association table between IndividualPlatform and RwrSystem.

    Represents the RWR system(s) currently or historically fitted
    to a specific physical platform. A platform with no row here
    carries no tracked RWR system (zero case).
    """

    __tablename__ = "platform_rwr"

    __table_args__ = (
        # Prevent duplicate associations for the same platform / RWR pair.
        UniqueConstraint(
            "platform_id",
            "rwr_system_id",
            name="uq_platform_rwr_platform_id_rwr_system_id",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="UUID v4 primary key",
    )
    platform_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("individual_platform.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="FK to individual platform carrying this RWR system",
    )
    rwr_system_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("rwr_system.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="FK to the RWR system model fitted to this platform",
    )
