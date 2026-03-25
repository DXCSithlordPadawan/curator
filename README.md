# Sentinel Curator

**Version:** 0.1.0 (Phase 1 — Scaffold)  
**Status:** In Development  
**Classification Handling:** UNCLASSIFIED // FOR DEVELOPMENT USE ONLY  
**Compliance Targets:** FIPS 140-3 · CIS Level 2 · OWASP Top 10 · NIST SP 800-53 · DISA STIG

---

## Overview

Sentinel Curator is a secure, LLM-curated database system for tracking and managing global military assets. It provides a natural-language interface over a PostgreSQL/PostGIS relational database, with a Python-based AI agent (RAG architecture) translating analyst queries into validated, role-filtered SQL.

The system enforces strict Role-Based Access Control (RBAC) tiering to ensure data visibility is proportionate to clearance level — from public platform class descriptions through to classified RWR Emitter-ID exclusion data.

---

## Architecture Summary

```
Analyst / Intel Officer
        │
        ▼
  FastAPI REST Layer  ←──── RBAC Filter (role-aware output masking)
        │
        ▼
  Curator Agent (LangChain RAG)
        │  ── schema DDL context only (no raw data)
        ▼
  SQL Guard Middleware  ←── blocks Write / Delete / Grant unless authorised
        │
        ▼
  PostgreSQL 15 + PostGIS  (isolated Podman network, no external egress)
```

Full architecture detail: [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md)

---

## Repository Structure

```
sentinel-curator/
├── src/
│   └── sentinel_curator/
│       ├── models/          # SQLAlchemy ORM models
│       ├── curator/         # LLM RAG agent + SQL Guard middleware
│       ├── api/             # FastAPI routes
│       ├── rbac/            # RBAC roles, decorators, output filters
│       └── utils/           # Logging, config, crypto helpers
├── tests/                   # pytest test suite
├── db/
│   ├── migrations/          # Alembic / raw SQL DDL migrations
│   └── seeds/               # Representative (non-live) seed data
├── deploy/                  # Podman Compose + Containerfiles
├── docs/                    # Full documentation set
├── scripts/                 # Operational helper scripts
├── .env.example             # Environment variable template
├── pyproject.toml           # Project metadata and tooling config
└── curator_progress.md      # Sprint-by-sprint progress log
```

---

## Quick Start (Development)

### Prerequisites

- Python 3.11+
- Podman 4.x (rootless)
- `podman-compose` (`pip install podman-compose`)

### 1. Clone and configure environment

```bash
git clone <repo-url> sentinel-curator
cd sentinel-curator
cp .env.example .env
# Edit .env — set DB password, LLM API key, etc.
```

### 2. Start infrastructure (PostgreSQL + PostGIS)

```bash
podman-compose -f deploy/podman-compose.yml up -d db
```

### 3. Apply database schema

```bash
podman-compose -f deploy/podman-compose.yml run --rm app python scripts/apply_migrations.py
```

### 4. Install Python dependencies

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
```

### 5. Run the API

```bash
uvicorn sentinel_curator.api.main:app --reload --host 127.0.0.1 --port 8000
```

---

## Security Notes

- **No secrets in source control.** All credentials are loaded from environment variables or a secrets manager.
- **Database container has no external egress** — isolated Podman bridge network only.
- **SQL Guard middleware** intercepts all LLM-generated SQL and rejects `INSERT`, `UPDATE`, `DELETE`, `DROP`, `GRANT`, `TRUNCATE` unless the caller holds an authorised write role.
- **RBAC tiers:** UNCLASSIFIED → RESTRICTED → CONFIDENTIAL. Each API response is filtered to the caller's maximum classification level.
- **UUID v4** primary keys throughout — no sequential integer IDs that enable enumeration.

---

## Documentation Index

| Document | Path |
|---|---|
| Architecture | `docs/ARCHITECTURE.md` |
| Security & Compliance | `docs/SECURITY_COMPLIANCE.md` |
| RBAC Roles | `docs/RBAC.md` |
| RACI Matrix | `docs/RACI.md` |
| API Guide | `docs/API_GUIDE.md` |
| User Guide | `docs/USER_GUIDE.md` |
| Deployment Guide | `docs/DEPLOYMENT_GUIDE.md` |
| Container Build Guide | `docs/CONTAINER_BUILD_GUIDE.md` |
| Maintenance Guide | `docs/MAINTENANCE_GUIDE.md` |
| UI Guide | `docs/UI_GUIDE.md` |

---

## Licence

RESTRICTED — Internal use only. Not for public distribution.  
© 2026 Iain Reid / Project Sentinel. All rights reserved.
