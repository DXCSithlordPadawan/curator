# Sentinel Curator -- Progress Log

**Project:** Sentinel Curator
**PRD Version:** 1.0
**Log Started:** 2026-03-25
**Author:** Iain Reid

---

## Status Legend

| Symbol | Meaning |
|--------|---------|
| OK | Complete |
| WIP | In Progress |
| TBD | Pending |
| BLOCKED | Blocked |
| REVIEW | Under Review |

---

## Phase Overview

| Phase | Description | Status |
|-------|-------------|--------|
| Phase 0 | Repository scaffold and documentation | OK |
| Phase 1 | SQL DDL and Podman Compose environment | TBD |
| Phase 2 | Python Curator Agent (LangChain RAG) | TBD |
| Phase 3 | RBAC filtering on LLM output layer | TBD |
| Phase 4 | Stress test, seed data, performance tuning | TBD |

---

## Phase 0 -- Repository Scaffold and Documentation

**Started:** 2026-03-25
**Completed:** 2026-03-25
**Status:** OK

### Tasks

| Task | Status | Notes |
|------|--------|-------|
| Create repository directory structure | OK | src/, tests/, db/, deploy/, docs/, scripts/ |
| Write .gitignore | OK | Python, Podman, secrets, logs |
| Write README.md | OK | Architecture summary, quick-start, doc index |
| Write pyproject.toml | OK | Python 3.11+, full dependency set, tooling config |
| Write .env.example | OK | All required env vars, no live secrets |
| Scaffold Python package __init__.py files | OK | All sub-packages initialised |
| ORM model: base.py | OK | Declarative base, naming conventions |
| ORM model: platform_class.py | OK | UNCLASSIFIED tier |
| ORM model: individual_platform.py | OK | RESTRICTED tier -- corrected with RWR relationship |
| ORM model: platform_mount.py | OK | CONFIDENTIAL tier |
| ORM model: weapon_mount.py | OK | CONFIDENTIAL tier |
| ORM model: rwr_system.py | OK | CONFIDENTIAL tier -- corrected with platforms back-ref |
| ORM model: platform_rwr.py | OK | NEW -- association table for INDIVIDUAL_PLATFORM to RWR_SYSTEM |
| ORM model: geolocation_log.py | OK | RESTRICTED tier, PostGIS GEOGRAPHY |
| utils/config.py | OK | Pydantic-settings typed config, SecretStr for all secrets |
| utils/logging.py | OK | structlog JSON/console structured logging |
| rbac/roles.py | OK | ClearanceLevel enum, role map, column visibility guards |
| curator/sql_guard.py | OK | Write/Delete/Grant intercept middleware, write-role bypass |
| curator/agent.py | OK | LangChain RAG agent stub, _filter_results output masking |
| api/main.py | OK | FastAPI app, /query, /health, lifespan, role dependency |
| db/migrations/001_initial_schema.sql | OK | Full DDL with PostGIS, PLATFORM_RWR, RLS, grants |
| db/seeds/seed_platforms.sql | OK | Platform classes, platforms, mounts, weapons, RWR, associations, telemetry |
| deploy/podman-compose.yml | OK | db + app services, internal bridge, no external DB egress |
| deploy/Containerfile.app | OK | Python 3.11-slim, non-root curator user, healthcheck |
| deploy/Containerfile.db | OK | postgis/postgis:15-3.4 base |
| scripts/apply_migrations.py | OK | Idempotent ordered migration runner |
| tests/conftest.py | OK | Shared role fixtures |
| tests/test_sql_guard.py | OK | Full SQL Guard unit test suite (passthrough, blocked, write-permitted, edge cases) |
| tests/test_rbac.py | OK | RBAC clearance resolution and column visibility matrix tests |
| docs/ARCHITECTURE.md | OK | System diagram, ER diagram, container diagram, component descriptions |
| docs/SECURITY_COMPLIANCE.md | OK | OWASP, NIST SP 800-53, CIS Level 2, FIPS 140-3, threat model |
| docs/RBAC.md | OK | Clearance tiers, role mapping, column visibility matrix, user story mapping |
| docs/RACI.md | OK | All phases and ongoing operations |
| docs/API_GUIDE.md | OK | Endpoints, request/response examples, role filtering table |
| docs/USER_GUIDE.md | OK | Analyst-facing guide, clearance explanation, query tips |
| docs/DEPLOYMENT_GUIDE.md | OK | First-time deploy, updates, air-gapped notes, production hardening |
| docs/CONTAINER_BUILD_GUIDE.md | OK | Build commands, security controls, network verification |
| docs/MAINTENANCE_GUIDE.md | OK | Health checks, backups, secret rotation, log archiving |
| docs/UI_GUIDE.md | OK | Current Swagger UI, planned HTMX frontend, map coordinate notes |

---

## Data Model Correction Log

| Date | Correction | Files Changed |
|------|-----------|---------------|
| 2026-03-25 | Added PLATFORM_RWR association table. INDIVIDUAL_PLATFORM was not linked to RWR_SYSTEM. Cardinality is now zero-to-many in both directions. Zero case validated in seed data (USS Gerald R. Ford has no RWR row). | models/platform_rwr.py (new), models/individual_platform.py, models/rwr_system.py, 001_initial_schema.sql, seed_platforms.sql |
| 2026-03-25 | Corrected ERD diagram cardinality glyph in ARCHITECTURE.md. INDIVIDUAL_PLATFORM→PLATFORM_RWR was `\|\|--o{` (one-or-many, mandatory participation) but must be `\|o--o{` (zero-or-many, optional participation) because a platform may carry no RWR system. All other artefacts (cardinality notes table, ORM code, DDL comments, seed data) were already correct. ARCHITECTURE.md bumped to v0.1.1. | docs/ARCHITECTURE.md |

---

## Gaps Identified in Phase 0

| Gap | Severity | Resolution |
|-----|----------|-----------|
| RWR_SYSTEM had no FK link to INDIVIDUAL_PLATFORM | High | Resolved -- PLATFORM_RWR association table added |
| LLM provider not specified | Medium | LangChain chosen, swappable via SC_LLM_PROVIDER config |
| FIPS 140-3 cryptography library selection | High | cryptography >= 42.x + OpenSSL 3.x FIPS module -- validate in Phase 1 |
| PostGIS version pinning for air-gapped build | Medium | Pinned to postgis/postgis:15-3.4 -- verify offline availability |
| Alembic vs raw SQL migrations | Low | Raw SQL for Phase 1; Alembic considered for Phase 2 |
| No integration tests | Medium | Addressed in Phase 2 with pytest-asyncio + testcontainers |
| Swagger UI exposed in dev | Low | Documented -- must be disabled for production via SC_APP_ENV=production |

---

## Phase 1 -- SQL DDL and Podman Compose Environment

**Started:** --
**Status:** TBD

### Tasks

| Task | Status | Notes |
|------|--------|-------|
| Validate DDL against PostgreSQL 15 + PostGIS 3.4 | TBD | |
| Test rootless Podman Compose bring-up | TBD | |
| Validate UUID extension enabled | TBD | |
| Test PostGIS GEOGRAPHY(POINT, 4326) column creation | TBD | |
| Verify internal bridge -- no external egress on db | TBD | |
| Apply seed data, validate FK and unique constraints | TBD | |
| Validate PLATFORM_RWR zero-case (Ford has no RWR row) | TBD | |
| Run CIS Level 2 PostgreSQL hardening checklist | TBD | |

---

## Phase 2 -- Python Curator Agent

**Status:** TBD

---

## Phase 3 -- RBAC Filtering

**Status:** TBD

---

## Phase 4 -- Stress Test and Performance Tuning

**Status:** TBD

---

## Decision Log

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-03-25 | LangChain chosen over LlamaIndex | Wider SQL agent tooling; easier swap via abstraction layer |
| 2026-03-25 | Raw SQL DDL for Phase 1 migrations | Simplicity; Alembic adds value in Phase 2 when models stabilise |
| 2026-03-25 | Rootless Podman over Docker | Organisational security standard; FIPS alignment |
| 2026-03-25 | UUID v4 PKs throughout | Prevent enumeration attacks per PRD section 3.1 |
| 2026-03-25 | FastAPI for API layer | Async-native, OpenAPI auto-docs, Pydantic integration |
| 2026-03-25 | PLATFORM_RWR many-to-many join table | Correctly models zero-to-many RWR cardinality per platform |
| 2026-03-25 | rwr_system.model_name treated as UNCLASSIFIED | Knowing a model exists is not sensitive; blind spots (exclusion_emitter_ids) are CONFIDENTIAL |

---

## Sources and References

| Reference | URL or Location |
|-----------|----------------|
| PRD v1.0 | Sentinel_Curator.md (uploaded 2026-03-25) |
| FIPS 140-3 | https://csrc.nist.gov/publications/detail/fips/140/3/final |
| NIST SP 800-53 Rev 5 | https://csrc.nist.gov/publications/detail/sp/800-53/rev-5/final |
| CIS PostgreSQL Benchmark | https://www.cisecurity.org/benchmark/postgresql |
| OWASP Top 10 2021 | https://owasp.org/www-project-top-ten/ |
| DISA STIG PostgreSQL | https://www.stigviewer.com/stig/postgresql_9-x/ |
| PostGIS documentation | https://postgis.net/documentation/ |
| LangChain SQL Agents | https://python.langchain.com/docs/use_cases/sql/ |
| Podman rootless tutorial | https://github.com/containers/podman/blob/main/docs/tutorials/rootless_tutorial.md |
| SQLAlchemy 2.0 ORM relationships | https://docs.sqlalchemy.org/en/20/orm/basic_relationships.html |
| Python cryptography library | https://cryptography.io/en/latest/ |
