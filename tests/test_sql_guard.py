"""
Unit tests for the SQL Guard middleware.

Tests cover:
  - SELECT passthrough
  - All blocked statement types (INSERT, UPDATE, DELETE, DROP, etc.)
  - Write-permitted role bypass
  - Empty/null SQL handling
  - SQL with leading comments
"""

import pytest

from sentinel_curator.curator.sql_guard import SqlGuardViolation, guard_sql


class TestGuardSqlPassthrough:
    """SELECT statements should always pass through."""

    def test_simple_select(self) -> None:
        sql = "SELECT id, class_name FROM platform_class"
        assert guard_sql(sql, "UNCLASSIFIED") == sql

    def test_select_with_where(self) -> None:
        sql = "SELECT name FROM individual_platform WHERE operator_country = 'US'"
        assert guard_sql(sql, "RESTRICTED") == sql

    def test_select_with_leading_whitespace(self) -> None:
        sql = "   \n  SELECT id FROM platform_class"
        assert guard_sql(sql, "UNCLASSIFIED") == sql

    def test_select_with_line_comment(self) -> None:
        sql = "-- find all platforms\nSELECT id FROM individual_platform"
        assert guard_sql(sql, "UNCLASSIFIED") == sql

    def test_select_with_block_comment(self) -> None:
        sql = "/* analyst query */\nSELECT id FROM platform_class"
        assert guard_sql(sql, "UNCLASSIFIED") == sql


class TestGuardSqlBlocked:
    """Destructive / mutating statements must raise SqlGuardViolation."""

    @pytest.mark.parametrize(
        "sql",
        [
            "INSERT INTO platform_class (class_name) VALUES ('Evil')",
            "UPDATE individual_platform SET name = 'Hacked'",
            "DELETE FROM geolocation_log",
            "DROP TABLE platform_class",
            "TRUNCATE geolocation_log",
            "CREATE TABLE malicious (id INT)",
            "ALTER TABLE platform_class ADD COLUMN x TEXT",
            "GRANT SELECT ON platform_class TO attacker",
            "REVOKE SELECT ON platform_class FROM curator_app",
            "COPY platform_class TO '/tmp/data.csv'",
        ],
    )
    def test_blocked_statement(self, sql: str) -> None:
        with pytest.raises(SqlGuardViolation):
            guard_sql(sql, caller_role="UNCLASSIFIED")

    def test_blocked_for_restricted_role(self) -> None:
        with pytest.raises(SqlGuardViolation):
            guard_sql("DELETE FROM geolocation_log", caller_role="RESTRICTED")

    def test_blocked_for_intel_officer(self) -> None:
        """INTEL_OFFICER has high clearance but is not a write-permitted role."""
        with pytest.raises(SqlGuardViolation):
            guard_sql("INSERT INTO rwr_system (model_name) VALUES ('X')", caller_role="INTEL_OFFICER")


class TestGuardSqlWritePermitted:
    """SYSTEM_ADMIN may execute write statements."""

    def test_insert_allowed_for_system_admin(self) -> None:
        sql = "INSERT INTO platform_class (class_name, manufacturer_country) VALUES ('Test', 'US')"
        result = guard_sql(sql, caller_role="SYSTEM_ADMIN")
        assert result == sql

    def test_delete_allowed_for_system_admin(self) -> None:
        sql = "DELETE FROM geolocation_log WHERE timestamp_utc < NOW() - INTERVAL '1 year'"
        result = guard_sql(sql, caller_role="SYSTEM_ADMIN")
        assert result == sql


class TestGuardSqlEdgeCases:
    """Edge case handling."""

    def test_empty_sql_raises_value_error(self) -> None:
        with pytest.raises(ValueError):
            guard_sql("", caller_role="UNCLASSIFIED")

    def test_whitespace_only_raises_value_error(self) -> None:
        with pytest.raises(ValueError):
            guard_sql("   \n\t  ", caller_role="UNCLASSIFIED")

    def test_case_insensitive_blocking(self) -> None:
        """Lowercase / mixed-case blocked keywords must also be caught."""
        with pytest.raises(SqlGuardViolation):
            guard_sql("delete from geolocation_log", caller_role="UNCLASSIFIED")

        with pytest.raises(SqlGuardViolation):
            guard_sql("Delete From platform_class", caller_role="UNCLASSIFIED")
