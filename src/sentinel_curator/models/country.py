"""
ORM model: COUNTRY

ISO 3166-1 alpha-2 country reference table.
Classification tier: UNCLASSIFIED (public reference data)

This table is the single source of truth for all country codes used
throughout the data model. All operator_country, owner_country, and
manufacturer_country columns in other tables are foreign keys to this table.

Standard:  ISO 3166-1 alpha-2
Reference: https://www.iso.org/iso-3166-country-codes.html
           https://www.iban.com/country-codes (verification source)
"""

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from sentinel_curator.models.base import Base


class Country(Base):
    """
    ISO 3166-1 alpha-2 country reference entry.

    The two-character alpha-2 code is used as the natural primary key.
    It is immutable by international standard and human-readable in queries,
    making it preferable to a surrogate UUID for a stable reference table.

    Examples:
        alpha2='US', name='United States of America'
        alpha2='GB', name='United Kingdom of Great Britain and Northern Ireland'
        alpha2='FR', name='France'
    """

    __tablename__ = "country"

    alpha2: Mapped[str] = mapped_column(
        String(2),
        primary_key=True,
        comment="ISO 3166-1 alpha-2 code, e.g. 'GB', 'US', 'FR'",
    )
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="ISO 3166-1 official English short name",
    )
