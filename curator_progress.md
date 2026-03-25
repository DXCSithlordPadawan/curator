# Sentinel Curator — Progress Log

**Project:** Sentinel Curator  
**PRD Version:** 1.0  
**Log Started:** 2026-03-25  
**Author:** Iain Reid

---

## Status Legend

| Symbol | Meaning |
|--------|---------|
| ✅ | Complete |
| 🔄 | In Progress |
| ⏳ | Pending |
| ❌ | Blocked |
| 🔍 | Under Review |

---

## Phase Overview

| Phase | Description | Status |
|-------|-------------|--------|
| Phase 0 | Repository scaffold & documentation | ✅ Complete |
| Phase 1 | SQL DDL & Podman Compose environment | ⏳ Pending |
| Phase 2 | Python Curator Agent (LangChain RAG) | ⏳ Pending |
| Phase 3 | RBAC filtering on LLM output layer | ⏳ Pending |
| Phase 4 | Stress test, seed data, performance tuning | ⏳ Pending |

---

## Phase 0 — Repository Scaffold & Documentation

**Started:** 2026-03-25  
**Completed:** 2026-03-25  
**Status:** ✅ Complete

### Tasks

| Task | Status | Notes |
|------|--------|-------|
| Create repository directory structure | ✅ | `src/`, `tests/`, `db/`, `deploy/`, `docs/`, `scripts/` |
| Write `.gitignore` | ✅ | Python, Podman, secrets, logs |
| Write `README.md` | ✅ | Architecture summary, quick-start, doc index |
| Write `pyproject.toml` | ✅ | Python 3.11+, SQLAlchemy, Pydantic, FastAPI, LangChain |
| Write `.env.example` | ✅ | All required env vars, no live secrets |
| Scaffold Python package `__init__.py` files | ✅ | All sub-packages initialised |
| Stub ORM models | ✅ | `platform_class`, `individual_platform`, `platform_mount`, `weapon_mount`, `rwr_system`, `geolocation_log` |
| Stub Curator Agent | ✅ | LangChain RAG agent skeleton |
| Stub SQL Guard middleware | ✅ | Write/Delete/Grant intercept |
| Stub RBAC roles | ✅ | `UNCLASSIFIED`, `RESTRICTED`, `CONFIDENTIAL` |
| Stub FastAPI routes | ✅ | `/query`, `/health` |
| Write initial DDL migration | ✅ | `001_initial_schema.sql` with PostGIS |
| Write seed data | ✅ | Representative non-live platforms |
| Write Podman Compose | ✅ | `db` + `app` services, isolated bridge network |
| Write Containerfiles | ✅ | `Containerfile.app`, `Containerfile.db` |
| Write all documentation stubs | ✅ | Architecture, Security, RBAC, RACI, API, User, Deployment, Container, Maintenance, UI |
| Write `apply_migrations.py` script | ✅ | |

### Gaps Identified in Phase 0

| Gap | Severity | Resolution |
|-----|----------|-----------|
| LLM provider not specified (LangChain vs LlamaIndex) | Medium | Deferred to Phase 2 — LangChain chosen as default, swappable via config |
| FIPS 140-3 cryptography library selection | High | `cryptography` >= 41.x with OpenSSL 3.x FIPS module — to be validated in Phase 1 |
| PostGIS version pinning for air-gapped build | Medium | Pinned to `postgis/postgis:15-3.4` — verify offline availability |
| Alembic vs raw SQL migrations | Low | Raw SQL chosen for Phase 1 simplicity; Alembic to be added in Phase 2 |
| No integration tests yet | Medium | Addressed in Phase 2 with pytest-asyncio + testcontainers |

---

## Phase 1 — SQL DDL & Podman Compose Environment

**Started:** —  
**Completed:** —  
**Status:** ⏳ Pending

### Tasks

| Task | Status | Notes |
|------|--------|-------|
| Validate DDL against PostgreSQL 15 + PostGIS 3.4 | ⏳ | |
| Test rootless Podman Compose bring-up | ⏳ | |
| Validate UUID extension enabled | ⏳ | |
| Test PostGIS `GEOGRAPHY(POINT, 4326)` column creation | ⏳ | |
| Verify encrypted bridge network — no external egress | ⏳ | |
| Apply seed data and validate FK constraints | ⏳ | |
| Run CIS Level 2 PostgreSQL hardening checklist | ⏳ | |

---

## Phase 2 — Python Curator Agent

**Started:** —  
**Completed:** —  
**Status:** ⏳ Pending

### Tasks

| Task | Status | Notes |
|------|--------|-------|
| Implement LangChain SQL agent with schema DDL context | ⏳ | |
| Implement SQL Guard — full write/delete/grant blocking | ⏳ | |
| Unit tests for SQL Guard | ⏳ | |
| Integration test: NL query → SQL → result | ⏳ | |
| Implement RBAC output filter | ⏳ | |

---

## Phase 3 — RBAC Filtering

**Started:** —  
**Completed:** —  
**Status:** ⏳ Pending

---

## Phase 4 — Stress Test & Performance Tuning

**Started:** —  
**Completed:** —  
**Status:** ⏳ Pending

---

## Decision Log

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-03-25 | LangChain chosen over LlamaIndex | Wider SQL agent tooling; easier swap via abstraction layer |
| 2026-03-25 | Raw SQL DDL for Phase 1 migrations | Simplicity; Alembic adds value in Phase 2 when models stabilise |
| 2026-03-25 | Rootless Podman over Docker | Organisational security standard; FIPS alignment |
| 2026-03-25 | UUID v4 PKs throughout | Prevent enumeration attacks per PRD §3.1 |
| 2026-03-25 | FastAPI for API layer | Async-native, OpenAPI auto-docs, Pydantic integration |

---

## Sources & References

| Reference | URL / Location |
|-----------|---------------|
| PRD v1.0 | `Sentinel_Curator.md` (uploaded) |
| FIPS 140-3 | https://csrc.nist.gov/publications/detail/fips/140/3/final |
| NIST SP 800-53 Rev 5 | https://csrc.nist.gov/publications/detail/sp/800-53/rev-5/final |
| CIS PostgreSQL Benchmark | https://www.cisecurity.org/benchmark/postgresql |
| OWASP Top 10 | https://owasp.org/www-project-top-ten/ |
| PostGIS docs | https://postgis.net/documentation/ |
| LangChain SQL Agents | https://python.langchain.com/docs/use_cases/sql/ |
| Podman rootless | https://github.com/containers/podman/blob/main/docs/tutorials/rootless_tutorial.md |
