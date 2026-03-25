"""
Unit tests for RBAC roles and clearance-level resolution.
"""

import pytest

from sentinel_curator.rbac.roles import (
    ClearanceLevel,
    get_clearance,
    is_column_visible,
)


class TestGetClearance:
    def test_unclassified_role(self) -> None:
        assert get_clearance("UNCLASSIFIED") == ClearanceLevel.UNCLASSIFIED

    def test_analyst_role(self) -> None:
        assert get_clearance("ANALYST") == ClearanceLevel.UNCLASSIFIED

    def test_logistics_manager(self) -> None:
        assert get_clearance("LOGISTICS_MANAGER") == ClearanceLevel.UNCLASSIFIED

    def test_restricted_role(self) -> None:
        assert get_clearance("RESTRICTED") == ClearanceLevel.RESTRICTED

    def test_intel_officer(self) -> None:
        assert get_clearance("INTEL_OFFICER") == ClearanceLevel.CONFIDENTIAL

    def test_system_admin(self) -> None:
        assert get_clearance("SYSTEM_ADMIN") == ClearanceLevel.CONFIDENTIAL

    def test_unknown_role_defaults_to_unclassified(self) -> None:
        assert get_clearance("UNKNOWN_ROLE") == ClearanceLevel.UNCLASSIFIED

    def test_case_insensitive(self) -> None:
        assert get_clearance("intel_officer") == ClearanceLevel.CONFIDENTIAL
        assert get_clearance("Analyst") == ClearanceLevel.UNCLASSIFIED


class TestIsColumnVisible:
    def test_public_column_always_visible(self) -> None:
        for level in ClearanceLevel:
            assert is_column_visible("platform_class.class_name", level) is True

    def test_restricted_column_hidden_at_unclassified(self) -> None:
        assert (
            is_column_visible(
                "geolocation_log.coordinates", ClearanceLevel.UNCLASSIFIED
            )
            is False
        )

    def test_restricted_column_visible_at_restricted(self) -> None:
        assert (
            is_column_visible(
                "geolocation_log.coordinates", ClearanceLevel.RESTRICTED
            )
            is True
        )

    def test_confidential_column_hidden_at_unclassified(self) -> None:
        assert (
            is_column_visible(
                "rwr_system.exclusion_emitter_ids", ClearanceLevel.UNCLASSIFIED
            )
            is False
        )

    def test_confidential_column_hidden_at_restricted(self) -> None:
        assert (
            is_column_visible(
                "rwr_system.exclusion_emitter_ids", ClearanceLevel.RESTRICTED
            )
            is False
        )

    def test_confidential_column_visible_at_confidential(self) -> None:
        assert (
            is_column_visible(
                "rwr_system.exclusion_emitter_ids", ClearanceLevel.CONFIDENTIAL
            )
            is True
        )

    def test_weapon_mount_hidden_below_confidential(self) -> None:
        assert (
            is_column_visible(
                "weapon_mount.weapon_designation", ClearanceLevel.RESTRICTED
            )
            is False
        )
