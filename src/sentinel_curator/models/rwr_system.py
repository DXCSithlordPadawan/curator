"""
ORM model: RWR_SYSTEM

Radar Warning Receiver system model, including its Emitter-ID exclusion list
(frequencies / IDs the system is physically or logically incapable of detecting).

Classification tier: CONFIDENTIAL (Emitter-ID exclusions are sensitive)
"""

import uuid

from sqlalchemy import String, Text
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.orm import Mapped, mapped_column

from sentinel_curator.models.base import Base


class RwrSystem(Base):
    """
    An RWR model and its known detection limitations.

    The `exclusion_emitter_ids` field contains the list of emitter IDs
    (radar frequencies / platform signatures) that this RWR variant
    cannot detect. This is the operationally critical 'blind spot' data.
    """

    __tablename__ = "rwr_system"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    model_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True,
        comment="RWR model designation, e.g. 'AN/ALR-67(V)3'",
    )
    sensitivity_range: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        comment="Frequency sensitivity range, e.g. '2–18 GHz'",
    )
    # Stored as a PostgreSQL text array; each element is an emitter ID string.
    # Access to this column must be restricted to CONFIDENTIAL-cleared roles.
    exclusion_emitter_ids: Mapped[list[str] | None] = mapped_column(
        ARRAY(String),
        nullable=True,
        comment="CONFIDENTIAL: Emitter IDs this RWR cannot detect",
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
