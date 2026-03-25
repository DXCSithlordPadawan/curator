"""
ORM model: ORGANISATION

A military organisation such as CENTCOM, 7th Fleet, or NATO.
Classification tier: UNCLASSIFIED

Relationships:
  - owner_country FK → COUNTRY (the nation that owns / sponsors this organisation)
  - optionally part of one parent ORGANISATION (parent_organisation_id)
  - may contain zero, one, or many child ORGANISATION entries (child_organisations)
  - an organisation cannot be its own parent (DB enforces chk_no_self_parent_org)
  - has zero, one, or many INDIVIDUAL_PLATFORM members (platforms)
"""

import uuid
from typing import TYPE_CHECKING, Optional

from sqlalchemy import CheckConstraint, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from sentinel_curator.models.base import Base

if TYPE_CHECKING:
    from sentinel_curator.models.country import Country
    from sentinel_curator.models.individual_platform import IndividualPlatform


class Organisation(Base):
    """A military organisation (e.g. CENTCOM, 7th Fleet, NATO)."""

    __tablename__ = "organisation"
    __table_args__ = (
        CheckConstraint(
            "parent_organisation_id <> id",
            name="chk_no_self_parent_org",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="UUID v4 — prevents enumeration",
    )
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True,
        comment="Full official name of the military organisation",
    )
    abbreviation: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        comment="Common abbreviation or short name, e.g. CENTCOM, NATO",
    )
    owner_country: Mapped[str] = mapped_column(
        String(2),
        ForeignKey("country.alpha2", ondelete="RESTRICT"),
        nullable=False,
        comment="ISO 3166-1 alpha-2 FK — nation that owns / sponsors this organisation",
    )
    parent_organisation_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organisation.id", ondelete="SET NULL"),
        nullable=True,
        default=None,
        comment=(
            "Optional FK to the parent ORGANISATION this organisation falls under "
            "(e.g. NAVCENT under CENTCOM). NULL for top-level organisations. "
            "Cannot equal this organisation's own id (chk_no_self_parent_org)."
        ),
    )

    # ------------------------------------------------------------------
    # Relationships
    # ------------------------------------------------------------------

    owning_country: Mapped["Country"] = relationship(
        "Country",
        foreign_keys=[owner_country],
        lazy="select",
    )

    # Self-referential: the parent organisation this organisation sits within.
    parent_organisation: Mapped[Optional["Organisation"]] = relationship(
        "Organisation",
        foreign_keys=[parent_organisation_id],
        back_populates="child_organisations",
        remote_side=[id],
        lazy="select",
    )

    # Self-referential: subordinate organisations within this organisation.
    child_organisations: Mapped[list["Organisation"]] = relationship(
        "Organisation",
        foreign_keys=[parent_organisation_id],
        back_populates="parent_organisation",
        lazy="select",
    )

    # Platforms assigned to this organisation.
    platforms: Mapped[list["IndividualPlatform"]] = relationship(
        "IndividualPlatform",
        back_populates="organisation",
        lazy="select",
    )
