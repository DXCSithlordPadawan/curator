# =============================================================================
# Containerfile.app — Sentinel Curator FastAPI Application
# Rootless Podman · Python 3.11 slim · Non-root user
# =============================================================================

FROM docker.io/python:3.11-slim AS base

# Security: run as non-root
RUN groupadd --gid 1001 curator \
 && useradd --uid 1001 --gid curator --no-create-home --shell /sbin/nologin curator

WORKDIR /app

# Install OS-level build dependencies (psycopg2, cryptography)
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
        gcc \
        libpq-dev \
 && rm -rf /var/lib/apt/lists/*

# ---------------------------------------------------------------------------
# Dependency layer (cached unless pyproject.toml changes)
# ---------------------------------------------------------------------------
FROM base AS deps

COPY pyproject.toml ./
RUN pip install --no-cache-dir --upgrade pip \
 && pip install --no-cache-dir -e ".[dev]" || true
# Install runtime deps only (no dev extras) for production image
RUN pip install --no-cache-dir \
        fastapi \
        uvicorn[standard] \
        sqlalchemy \
        asyncpg \
        psycopg2-binary \
        geoalchemy2 \
        pydantic \
        pydantic-settings \
        langchain \
        langchain-community \
        langchain-openai \
        cryptography \
        python-dotenv \
        structlog \
        httpx

# ---------------------------------------------------------------------------
# Final image
# ---------------------------------------------------------------------------
FROM base AS final

COPY --from=deps /usr/local/lib/python3.11 /usr/local/lib/python3.11
COPY --from=deps /usr/local/bin /usr/local/bin

COPY src/ ./src/
COPY pyproject.toml ./

RUN pip install --no-cache-dir --no-deps -e .

# Drop to non-root
USER curator

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import httpx; httpx.get('http://localhost:8000/health').raise_for_status()"

CMD ["uvicorn", "sentinel_curator.api.main:app", \
     "--host", "0.0.0.0", "--port", "8000", \
     "--no-access-log"]
