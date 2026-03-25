"""
ORM model: GEOLOCATION_LOG

Time-series GPS telemetry for individual platforms.
Uses PostGIS GEOGRAPHY(POINT, 4326) for spatial queries.

Classification tier: RESTRICTED
"""

import uuid
from datetime import datetime

from geoalchemy2 import Geography
from sqlalchemy import DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from sentinel_curator.models.base import Base
from sentinel_curator.models.individual_platform import IndividualPlatform


class GeolocationLog(Base):
    """
    UTC-timestamped GPS fix for a specific platform.

    The `coordinates` column stores a PostGIS GEOGRAPHY POINT (WGS-84).
    Use ST_X(coordinates::geometry) / ST_Y(coordinates::geometry)
    to extract longitude / latitude respectively.
    """

    __tablename__ = "geolocation_log"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    platform_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("individual_platform.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="FK to individual platform",
    )
    # PostGIS geography point — SRID 4326 (WGS-84)
    coordinates: Mapped[Geography] = mapped_column(
        Geography(geometry_type="POINT", srid=4326),
        nullable=False,
        comment="GPS fix: GEOGRAPHY(POINT, 4326)",
    )
    timestamp_utc: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        index=True,
        comment="UTC timestamp of the GPS fix",
    )

    # Relationships
    platform: Mapped["IndividualPlatform"] = relationship(
        "IndividualPlatform",
        back_populates="geolocation_logs",
    )
