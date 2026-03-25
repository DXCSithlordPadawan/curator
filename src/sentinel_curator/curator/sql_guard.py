"""
SQL Guard Middleware

Intercepts all LLM-generated SQL before execution and blocks any statement
that would mutate or escalate the database unless the caller holds an
explicitly authorised write role.

Security rationale:
  - LLMs can hallucinate or be prompt-injected into generating destructive SQL.
  - This guard is a hard enforcement layer independent of the LLM itself.
  - Approach: parse the first meaningful token(s) of the normalised SQL string.
  - Any statement matching the BLOCKED set raises SqlGuardViolation.

Compliance: OWASP A03:2021 Injection · NIST SP 800-53 SI-10 · CIS Level 2
"""

from __future__ import annotations

import re

from sentinel_curator.utils.logging import get_logger

logger = get_logger(__name__)

# ---------------------------------------------------------------------------
# Blocked statement types (always rejected for read-only callers)
# ---------------------------------------------------------------------------
_BLOCKED_KEYWORDS: frozenset[str] = frozenset(
    {
        "INSERT",
        "UPDATE",
        "DELETE",
        "DROP",
        "TRUNCATE",
        "CREATE",
        "ALTER",
        "GRANT",
        "REVOKE",
        "COPY",
        "EXECUTE",
        "CALL",
        "DO",
        "VACUUM",
        "REINDEX",
        "CLUSTER",
        "COMMENT",
        "SECURITY",
    }
)

# Roles permitted to execute write operations (must match rbac/roles.py)
_WRITE_PERMITTED_ROLES: frozenset[str] = frozenset(
    {
        "SYSTEM_ADMIN",
        "DATA_CURATOR",  # reserved for future Phase 2 write agent
    }
)

# Normalise whitespace / comments before keyword extraction
_COMMENT_RE = re.compile(r"(--[^\n]*|/\*.*?\*/)", re.DOTALL)
_WHITESPACE_RE = re.compile(r"\s+")


class SqlGuardViolation(Exception):
    """
    Raised when a blocked SQL statement type is detected.

    Callers MUST treat this as an unrecoverable security event for the
    current request — log it, return HTTP 403, and do not retry.
    """


def _extract_first_keyword(sql: str) -> str:
    """
    Strip SQL comments and return the first non-whitespace keyword in uppercase.

    Args:
        sql: Raw SQL string from the LLM.

    Returns:
        Upper-cased first token, e.g. 'SELECT', 'INSERT'.
    """
    # Remove SQL comments (-- line and /* block */)
    cleaned = _COMMENT_RE.sub(" ", sql)
    # Collapse whitespace
    cleaned = _WHITESPACE_RE.sub(" ", cleaned).strip()
    if not cleaned:
        return ""
    return cleaned.split()[0].upper().rstrip(";")


def guard_sql(sql: str, caller_role: str = "UNCLASSIFIED") -> str:
    """
    Validate LLM-generated SQL before execution.

    Args:
        sql:         The SQL string produced by the LLM.
        caller_role: The RBAC role of the requesting user.

    Returns:
        The original SQL string if it passes validation.

    Raises:
        SqlGuardViolation: If the statement is blocked and the caller does
                           not hold a write-permitted role.
        ValueError:        If sql is empty or None.
    """
    if not sql or not sql.strip():
        raise ValueError("SQL Guard received an empty SQL string.")

    first_keyword = _extract_first_keyword(sql)
    role_upper = caller_role.upper()

    if first_keyword in _BLOCKED_KEYWORDS:
        if role_upper in _WRITE_PERMITTED_ROLES:
            logger.warning(
                "sql_guard.write_permitted",
                keyword=first_keyword,
                role=role_upper,
                sql_preview=sql[:120],
            )
            return sql

        logger.error(
            "sql_guard.violation_blocked",
            keyword=first_keyword,
            role=role_upper,
            sql_preview=sql[:120],
        )
        raise SqlGuardViolation(
            f"SQL statement type '{first_keyword}' is not permitted "
            f"for role '{role_upper}'. "
            "Only SELECT queries are allowed via the Curator Agent."
        )

    logger.debug(
        "sql_guard.passed",
        keyword=first_keyword,
        role=role_upper,
    )
    return sql
