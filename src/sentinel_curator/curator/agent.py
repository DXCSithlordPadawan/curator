"""
Sentinel Curator Agent

A LangChain-based RAG agent that:
  1. Accepts a natural-language query from an authorised user.
  2. Provides the LLM with schema DDL context only (no live data).
  3. Translates the query into a SQL SELECT statement.
  4. Passes the generated SQL through SqlGuard middleware.
  5. Executes the validated SQL against PostgreSQL.
  6. Returns results filtered to the caller's RBAC clearance tier.

Architecture note:
  The LLM never has direct access to the database connection.
  It only sees the schema DDL (table/column definitions) as context.
  All execution is handled by this agent through the guard layer.

Compliance: OWASP A03 Injection · NIST SI-10 · CIS Level 2
"""

from __future__ import annotations

from typing import Any

import sqlalchemy
from langchain.prompts import ChatPromptTemplate
from langchain_community.utilities import SQLDatabase
from langchain_core.language_models import BaseChatModel
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

from sentinel_curator.curator.sql_guard import SqlGuardViolation, guard_sql
from sentinel_curator.rbac.roles import ClearanceLevel, get_clearance
from sentinel_curator.utils.config import get_settings
from sentinel_curator.utils.logging import get_logger

logger = get_logger(__name__)

# ---------------------------------------------------------------------------
# Prompt template — schema is injected at runtime; no live data is included.
# ---------------------------------------------------------------------------
_SYSTEM_PROMPT = """You are the Sentinel Curator, a read-only database assistant
for a secure military asset tracking system.

You will be given the database schema (DDL) as context.
Your ONLY job is to generate a valid PostgreSQL SELECT query that answers the
user's question. You must NEVER generate INSERT, UPDATE, DELETE, DROP, GRANT,
or any other data-modification statement.

Rules:
- Return ONLY the raw SQL query — no explanation, no markdown, no code fences.
- Use only tables and columns that exist in the schema.
- Always use fully qualified column references (table.column).
- Never use SELECT * — always name the columns explicitly.
- If the question cannot be answered from the schema, respond with exactly:
  CANNOT_ANSWER

Schema:
{schema}
"""

_HUMAN_PROMPT = "Question: {question}"

_PROMPT = ChatPromptTemplate.from_messages(
    [
        ("system", _SYSTEM_PROMPT),
        ("human", _HUMAN_PROMPT),
    ]
)


class CuratorAgent:
    """
    Orchestrates natural-language → SQL → validated result pipeline.

    Usage:
        agent = CuratorAgent(llm=my_llm, db_url=settings.db_url)
        result = agent.query("Where was the USS Nimitz at 0800 UTC today?",
                             caller_role="RESTRICTED")
    """

    def __init__(self, llm: BaseChatModel, db_url: str) -> None:
        self._llm = llm
        self._db = SQLDatabase.from_uri(db_url)
        self._schema: str = self._db.get_table_info()
        self._chain = (
            RunnablePassthrough.assign(schema=lambda _: self._schema)
            | _PROMPT
            | self._llm
            | StrOutputParser()
        )

    def query(
        self,
        question: str,
        caller_role: str = "UNCLASSIFIED",
    ) -> dict[str, Any]:
        """
        Translate a natural-language question into SQL, execute, and return results.

        Args:
            question:    Natural-language query from the user.
            caller_role: RBAC role string — controls SQL Guard and output filtering.

        Returns:
            dict with keys:
              'sql'       — the validated SQL that was executed
              'results'   — list of row dicts (columns filtered by clearance)
              'clearance' — resolved clearance level name

        Raises:
            SqlGuardViolation: If the LLM generates a blocked statement type.
            ValueError:        If the question is empty.
        """
        if not question or not question.strip():
            raise ValueError("Query question must not be empty.")

        clearance = get_clearance(caller_role)
        logger.info(
            "curator.query.start",
            role=caller_role,
            clearance=clearance.name,
            question_preview=question[:100],
        )

        # Step 1 — LLM generates SQL (schema context only, no live data)
        raw_sql: str = self._chain.invoke({"question": question})

        if raw_sql.strip().upper() == "CANNOT_ANSWER":
            logger.info("curator.query.cannot_answer", question_preview=question[:100])
            return {
                "sql": None,
                "results": [],
                "clearance": clearance.name,
                "message": "The question cannot be answered from the available schema.",
            }

        # Step 2 — SQL Guard intercept
        validated_sql = guard_sql(raw_sql, caller_role=caller_role)

        # Step 3 — Execute against database
        logger.info("curator.query.execute", sql_preview=validated_sql[:120])
        raw_results: list[dict[str, Any]] = self._execute_sql(validated_sql)

        # Step 4 — RBAC output filter (strip columns above caller's clearance)
        filtered_results = _filter_results(raw_results, clearance)

        logger.info(
            "curator.query.complete",
            row_count=len(filtered_results),
            clearance=clearance.name,
        )
        return {
            "sql": validated_sql,
            "results": filtered_results,
            "clearance": clearance.name,
        }

    def _execute_sql(self, sql: str) -> list[dict[str, Any]]:
        """Execute a validated SQL string and return rows as dicts."""
        try:
            with self._db._engine.connect() as conn:
                result = conn.execute(sqlalchemy.text(sql))
                columns = list(result.keys())
                return [dict(zip(columns, row)) for row in result.fetchall()]
        except Exception as exc:
            logger.error("curator.query.db_error", error=str(exc))
            raise


def _filter_results(
    rows: list[dict[str, Any]],
    clearance: ClearanceLevel,
) -> list[dict[str, Any]]:
    """
    Remove columns from result rows that exceed the caller's clearance level.

    This is a belt-and-braces output filter — the primary guard is the
    SQL Guard middleware, but this layer ensures no column leaks through
    even if the guard is somehow bypassed.
    """
    from sentinel_curator.rbac.roles import (
        CONFIDENTIAL_COLUMNS,
        RESTRICTED_COLUMNS,
    )

    # Build set of bare column names that are above-clearance
    blocked: set[str] = set()
    if clearance < ClearanceLevel.CONFIDENTIAL:
        for ref in CONFIDENTIAL_COLUMNS:
            blocked.add(ref.split(".")[-1])
    if clearance < ClearanceLevel.RESTRICTED:
        for ref in RESTRICTED_COLUMNS:
            blocked.add(ref.split(".")[-1])

    if not blocked:
        return rows

    return [
        {k: v for k, v in row.items() if k not in blocked}
        for row in rows
    ]


def build_agent_from_settings() -> CuratorAgent:
    """
    Factory: construct a CuratorAgent from application settings.

    The LLM provider is selected based on SC_LLM_PROVIDER in the environment.
    """
    settings = get_settings()

    if settings.llm_provider == "openai":
        from langchain_openai import ChatOpenAI

        llm: BaseChatModel = ChatOpenAI(
            model=settings.llm_model,
            api_key=settings.openai_api_key.get_secret_value()  # type: ignore[union-attr]
            if settings.openai_api_key
            else "",
            temperature=0,
        )
    elif settings.llm_provider == "azure":
        from langchain_openai import AzureChatOpenAI

        llm = AzureChatOpenAI(
            azure_endpoint=settings.azure_openai_endpoint or "",
            azure_deployment=settings.azure_openai_deployment or "",
            api_key=settings.azure_openai_api_key.get_secret_value()  # type: ignore[union-attr]
            if settings.azure_openai_api_key
            else "",
            temperature=0,
        )
    else:
        raise NotImplementedError(
            f"LLM provider '{settings.llm_provider}' is not yet supported. "
            "Supported: openai, azure"
        )

    return CuratorAgent(llm=llm, db_url=settings.db_url)
