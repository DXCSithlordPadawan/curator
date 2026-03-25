"""
FastAPI application entry point.

Exposes:
  GET  /health        — liveness probe (unauthenticated)
  POST /query         — natural-language query endpoint (role-authenticated)

Authentication: Role is read from the X-Curator-Role header.
In production this header must be set by a trusted upstream gateway / IdP proxy.
Direct client-supplied role headers must be rejected at the ingress layer.

Compliance: OWASP A01 Broken Access Control · NIST AC-3 · CIS Level 2
"""

from __future__ import annotations

import time
from contextlib import asynccontextmanager
from typing import Annotated, Any, AsyncIterator

import uvicorn
from fastapi import Depends, FastAPI, Header, HTTPException, Request, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from sentinel_curator.curator.agent import CuratorAgent, build_agent_from_settings
from sentinel_curator.curator.sql_guard import SqlGuardViolation
from sentinel_curator.utils.config import get_settings
from sentinel_curator.utils.logging import configure_logging, get_logger

logger = get_logger(__name__)

# ---------------------------------------------------------------------------
# Application state — agent is initialised once on startup
# ---------------------------------------------------------------------------
_agent: CuratorAgent | None = None


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Initialise the Curator Agent on startup; clean up on shutdown."""
    global _agent
    configure_logging()
    logger.info("sentinel_curator.startup")
    _agent = build_agent_from_settings()
    yield
    logger.info("sentinel_curator.shutdown")
    _agent = None


# ---------------------------------------------------------------------------
# FastAPI app
# ---------------------------------------------------------------------------
app = FastAPI(
    title="Sentinel Curator API",
    version="0.1.0",
    description=(
        "Secure LLM-curated military asset query interface. "
        "RESTRICTED — authorised users only."
    ),
    docs_url="/docs",   # disable in production via env guard if required
    redoc_url="/redoc",
    lifespan=lifespan,
)


# ---------------------------------------------------------------------------
# Request / Response schemas
# ---------------------------------------------------------------------------
class QueryRequest(BaseModel):
    question: str = Field(
        ...,
        min_length=5,
        max_length=1000,
        description="Natural-language question in English.",
        examples=["Where was the USS Nimitz at 0800 UTC today?"],
    )


class QueryResponse(BaseModel):
    question: str
    sql: str | None
    results: list[dict[str, Any]]
    clearance: str
    duration_ms: float
    message: str | None = None


class HealthResponse(BaseModel):
    status: str
    version: str


# ---------------------------------------------------------------------------
# Dependency: resolve caller role from trusted header
# ---------------------------------------------------------------------------
def get_caller_role(
    x_curator_role: Annotated[str | None, Header()] = None,
) -> str:
    """
    Resolve the caller's RBAC role from the X-Curator-Role header.

    In development, falls back to SC_DEV_DEFAULT_ROLE if the header is absent.
    In production, an absent or unrecognised header results in HTTP 401.
    """
    settings = get_settings()
    if x_curator_role:
        return x_curator_role

    if settings.app_env == "development" and settings.dev_default_role:
        return settings.dev_default_role

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="X-Curator-Role header is required.",
    )


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
@app.get("/health", response_model=HealthResponse, tags=["Operations"])
async def health() -> HealthResponse:
    """Liveness probe — returns 200 if the service is running."""
    return HealthResponse(status="ok", version="0.1.0")


@app.post("/query", response_model=QueryResponse, tags=["Curator"])
async def query(
    request: QueryRequest,
    caller_role: Annotated[str, Depends(get_caller_role)],
) -> QueryResponse:
    """
    Submit a natural-language query to the Sentinel Curator Agent.

    The agent translates the question to SQL, validates it through the SQL Guard,
    executes it, and returns results filtered to the caller's clearance tier.
    """
    if _agent is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Curator agent is not initialised.",
        )

    start = time.perf_counter()

    try:
        result = _agent.query(request.question, caller_role=caller_role)
    except SqlGuardViolation as exc:
        logger.warning(
            "api.query.sql_guard_violation",
            role=caller_role,
            detail=str(exc),
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"SQL Guard violation: {exc}",
        ) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    except Exception as exc:
        logger.error("api.query.unexpected_error", error=str(exc))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred. Check server logs.",
        ) from exc

    duration_ms = (time.perf_counter() - start) * 1000

    return QueryResponse(
        question=request.question,
        sql=result.get("sql"),
        results=result.get("results", []),
        clearance=result.get("clearance", "UNCLASSIFIED"),
        duration_ms=round(duration_ms, 2),
        message=result.get("message"),
    )


# ---------------------------------------------------------------------------
# Entry point for direct execution
# ---------------------------------------------------------------------------
def run() -> None:
    settings = get_settings()
    uvicorn.run(
        "sentinel_curator.api.main:app",
        host=settings.app_host,
        port=settings.app_port,
        reload=(settings.app_env == "development"),
    )


if __name__ == "__main__":
    run()
