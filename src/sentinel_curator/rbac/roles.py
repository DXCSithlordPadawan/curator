"""
RBAC role definitions and classification tier enforcement.

Three-tier data visibility model aligned with PRD §4.1:
  UNCLASSIFIED  — Platform class descriptions, country of manufacture
  RESTRICTED    — Individual platform locations / telemetry
  CONFIDENTIAL  — Weapon mounts, RWR Emitter-ID exclusion lists
"""

from enum import IntEnum


class ClearanceLevel(IntEnum):
    """
    Numeric clearance levels allow simple >= comparisons.

    Higher value == higher clearance.
    """

    UNCLASSIFIED = 0
    RESTRICTED = 1
    CONFIDENTIAL = 2


# Map string role names (from JWT / session) to clearance levels.
ROLE_CLEARANCE_MAP: dict[str, ClearanceLevel] = {
    "UNCLASSIFIED": ClearanceLevel.UNCLASSIFIED,
    "ANALYST": ClearanceLevel.UNCLASSIFIED,
    "LOGISTICS_MANAGER": ClearanceLevel.UNCLASSIFIED,
    "RESTRICTED": ClearanceLevel.RESTRICTED,
    "INTEL_OFFICER": ClearanceLevel.CONFIDENTIAL,
    "CONFIDENTIAL": ClearanceLevel.CONFIDENTIAL,
    "SYSTEM_ADMIN": ClearanceLevel.CONFIDENTIAL,
}

# Columns that are suppressed unless the caller holds RESTRICTED or above.
RESTRICTED_COLUMNS: frozenset[str] = frozenset(
    {
        "geolocation_log.coordinates",
        "geolocation_log.timestamp_utc",
    }
)

# Columns that are suppressed unless the caller holds CONFIDENTIAL.
CONFIDENTIAL_COLUMNS: frozenset[str] = frozenset(
    {
        "weapon_mount.weapon_designation",
        "weapon_mount.notes",
        "rwr_system.exclusion_emitter_ids",
        "platform_mount.mount_designation",
    }
)


def get_clearance(role: str) -> ClearanceLevel:
    """
    Resolve a role string to a clearance level.

    Unknown roles are treated as UNCLASSIFIED (deny by default).
    """
    return ROLE_CLEARANCE_MAP.get(role.upper(), ClearanceLevel.UNCLASSIFIED)


def is_column_visible(column_ref: str, clearance: ClearanceLevel) -> bool:
    """
    Return True if the given column is visible at the supplied clearance level.

    Args:
        column_ref: dot-notation reference, e.g. 'rwr_system.exclusion_emitter_ids'
        clearance:  caller's resolved clearance level

    Returns:
        True if the column should be included in the response.
    """
    if column_ref in CONFIDENTIAL_COLUMNS:
        return clearance >= ClearanceLevel.CONFIDENTIAL
    if column_ref in RESTRICTED_COLUMNS:
        return clearance >= ClearanceLevel.RESTRICTED
    return True
