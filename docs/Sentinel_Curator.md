# Product Requirements Document (PRD): Project Sentinel Curator

**Version:** 1.1  
**Status:** Active — Phase 0 Complete  
**Date:** 2026-03-25  
**Compliance Target:** FIPS 140-3, CIS Level 2, RBAC  
**Author:** Iain Reid (Project Architect)

> **Revision History**
> | Version | Date | Change Summary |
> | :--- | :--- | :--- |
> | 1.0 | 2026-03-25 | Initial draft |
> | 1.1 | 2026-03-25 | Updated to reflect all Phase 0 implementations: COUNTRY reference table, PLATFORM_RWR association table, expanded tech stack (FastAPI, structlog, Pydantic Settings, GeoAlchemy2), finalised LLM choice (LangChain), expanded RBAC roles and SQL Guard, Row-Level Security, roadmap Phase 0 marked complete |

---

## 1. Executive Summary
The goal of **Project Sentinel** is to develop a secure, LLM-curated database system for tracking and managing global military assets. The system must handle complex relationships between platform designs (Classes), physical assets (Individual Platforms), weapon systems, and electronic warfare signatures—specifically Radar Warning Receiver (RWR) models and the "blind spots" (Emitter-IDs) they are incapable of detecting.

---

## 2. Functional Requirements

### 2.1 Data Schema & Relationships
The database utilises a normalised relational structure to ensure data integrity and minimise redundancy across high-value military assets.

* **Country:** ISO 3166-1 alpha-2 reference table. Single source of truth for all `manufacturer_country`, `operator_country`, and `owner_country` foreign keys throughout the schema. Classification: UNCLASSIFIED.
* **Platform Class:** The master template for ship/vehicle designs (e.g., Nimitz-class). Includes Country of Manufacture. Classification: UNCLASSIFIED.
* **Individual Platform:** Specific physical instances (e.g., USS Nimitz). Includes a common name, hull/serial ID (`hull_serial_id`), Country of Operation, and Country of Ownership. Classification: RESTRICTED (telemetry data).
* **Platform Mounts:** Physical hardpoints or pylons on an individual platform (`mount_designation`). Classification: CONFIDENTIAL.
* **Weapon Mounts:** Specific weapon fitted to a platform mount (`weapon_designation`). Classification: CONFIDENTIAL.
* **Electronic Warfare (RWR):** Tracks RWR models (`model_name`, `sensitivity_range`) and their specific **Emitter-ID Exclusions** (`exclusion_emitter_ids` — a PostgreSQL text array of IDs the system is physically or logically incapable of detecting). Classification: CONFIDENTIAL for exclusion data; `model_name` is UNCLASSIFIED.
* **Platform RWR (Association Table):** Many-to-many join table linking `individual_platform` to `rwr_system`. A platform may carry zero, one, or many RWR systems; an RWR model may be fitted to zero, one, or many platforms. The zero case is explicitly supported (a platform with no row in this table carries no tracked RWR system). Classification: CONFIDENTIAL.
* **Spatiotemporal Tracking:** A time-series log of PostGIS `GEOGRAPHY(POINT, 4326)` coordinates with UTC timestamps (`timestamp_utc`) for every individual platform. Classification: RESTRICTED.

### 2.2 LLM Curator (The AI Layer)
The system employs a **Retrieval-Augmented Generation (RAG)** architecture to allow users to query the database using natural language.
* **SQL Generation:** The LLM (LangChain agent) translates English queries into valid PostgreSQL SELECT statements. The LLM is provided with schema DDL context only — it never sees live data rows.
* **Validation Middleware (SQL Guard):** A Python layer (`curator/sql_guard.py`) intercepts LLM-generated SQL and blocks any statement whose leading keyword matches a blocked set: `INSERT`, `UPDATE`, `DELETE`, `DROP`, `TRUNCATE`, `CREATE`, `ALTER`, `GRANT`, `REVOKE`, `COPY`, `EXECUTE`, `CALL`, `DO`, `VACUUM`, `REINDEX`, `CLUSTER`, `COMMENT`, `SECURITY`. Blocked statements raise `SqlGuardViolation` and return HTTP 403. Write-permitted roles (`SYSTEM_ADMIN`, `DATA_CURATOR`) may bypass this guard.
* **CANNOT_ANSWER Sentinel:** If the LLM cannot answer from the schema, it returns the literal string `CANNOT_ANSWER`, which the agent converts into an empty result with an explanatory message rather than attempting SQL execution.
* **Context Awareness:** The LLM is provided with `SQLDatabase.get_table_info()` schema metadata (table and column definitions) but has no direct connection to the database. All execution is mediated by the `CuratorAgent`.

---

## 3. Technical Specifications

### 3.1 Tech Stack
* **Database:** PostgreSQL 15+ with **PostGIS 3.4** extension (`GEOGRAPHY(POINT, 4326)` for WGS-84 telemetry). UUID v4 generated via `uuid-ossp` extension.
* **Language:** Python 3.11+ with **SQLAlchemy 2.0** ORM (declarative mapped columns), **GeoAlchemy2** for PostGIS type support, **Pydantic v2 + pydantic-settings** for data validation and typed config management.
* **Web API:** **FastAPI 0.110+** with **Uvicorn** (async ASGI server). Exposes `GET /health` and `POST /query` endpoints. OpenAPI/Swagger docs served in development; must be disabled in production.
* **Containerisation:** **Podman (Rootless)** via `podman-compose`. Database container has no external egress. Application container runs as non-root `curator` user.
* **Identity:** UUID v4 for all Primary Keys to prevent enumeration attacks.
* **LLM / RAG Orchestration:** **LangChain** (`langchain`, `langchain-community`, `langchain-openai`). LLM provider is swappable via `SC_LLM_PROVIDER` environment variable; currently supports `openai` (ChatOpenAI) and `azure` (AzureChatOpenAI). Default model: `gpt-4-turbo`.
* **Cryptography:** `cryptography >= 42.x` aligned with OpenSSL 3.x FIPS module (to be validated in Phase 1).
* **Logging:** **structlog** — emits structured JSON in production, human-readable console output in development. Controlled via `SC_LOG_FORMAT`.
* **Database Drivers:** `psycopg2-binary` (sync, migrations/scripts), `asyncpg` (async, application runtime).
* **Security Tooling (dev):** `bandit` (SAST), `pip-audit` (dependency audit), `ruff` (lint/style), `mypy` (strict type checking), `black` (formatting).

### 3.2 Core Data Model (Implemented)

| Entity | Key Fields | Classification |
| :--- | :--- | :--- |
| **COUNTRY** | `alpha2 (PK, CHAR(2))`, `name` | UNCLASSIFIED |
| **PLATFORM_CLASS** | `id (UUID PK)`, `class_name`, `manufacturer_country (FK→country)`, `description`, `created_at`, `updated_at` | UNCLASSIFIED |
| **INDIVIDUAL_PLATFORM** | `id (UUID PK)`, `hull_serial_id`, `name`, `class_id (FK→platform_class)`, `operator_country (FK→country)`, `owner_country (FK→country)`, `created_at`, `updated_at` | RESTRICTED |
| **PLATFORM_MOUNT** | `id (UUID PK)`, `mount_designation`, `platform_id (FK→individual_platform)`, `operator_country (FK→country)`, `owner_country (FK→country)`, `created_at` | CONFIDENTIAL |
| **WEAPON_MOUNT** | `id (UUID PK)`, `weapon_designation`, `mount_id (FK→platform_mount)`, `operator_country (FK→country)`, `owner_country (FK→country)`, `notes`, `created_at` | CONFIDENTIAL |
| **RWR_SYSTEM** | `id (UUID PK)`, `model_name`, `sensitivity_range`, `exclusion_emitter_ids (TEXT[])`, `notes`, `created_at` | CONFIDENTIAL (`exclusion_emitter_ids`); `model_name` UNCLASSIFIED |
| **PLATFORM_RWR** | `id (UUID PK)`, `platform_id (FK→individual_platform)`, `rwr_system_id (FK→rwr_system)` | CONFIDENTIAL |
| **GEOLOCATION_LOG** | `id (UUID PK)`, `platform_id (FK→individual_platform)`, `coordinates (GEOGRAPHY POINT 4326)`, `timestamp_utc (TIMESTAMPTZ)` | RESTRICTED |

> All country references (`manufacturer_country`, `operator_country`, `owner_country`) are foreign keys into the `COUNTRY` table (ISO 3166-1 alpha-2).  
> Cardinality: `INDIVIDUAL_PLATFORM → PLATFORM_RWR` is zero-or-many (optional participation — a platform may carry no RWR system).

---

## 4. Security & Compliance

### 4.1 Access Control (RBAC)
To maintain operational security (OPSEC), data visibility is tiered. Roles are resolved from the `X-Curator-Role` HTTP header, which must be set by a trusted upstream gateway or IdP proxy (never accepted directly from the client in production).

| Role | Clearance | Visible Data |
| :--- | :--- | :--- |
| `UNCLASSIFIED`, `ANALYST`, `LOGISTICS_MANAGER` | UNCLASSIFIED | Platform class descriptions, country of manufacture |
| `RESTRICTED` | RESTRICTED | All UNCLASSIFIED data + individual platform locations (telemetry) |
| `INTEL_OFFICER`, `CONFIDENTIAL`, `SYSTEM_ADMIN` | CONFIDENTIAL | All RESTRICTED data + weapon mount specifics + RWR `exclusion_emitter_ids` |
| `DATA_CURATOR` | Write-permitted | Reserved for Phase 2 write agent; may bypass SQL Guard for approved mutations |

Column-level visibility is enforced by the RBAC output filter (`_filter_results`) as a belt-and-braces layer after SQL Guard. Columns restricted at the CONFIDENTIAL tier: `weapon_mount.weapon_designation`, `weapon_mount.notes`, `rwr_system.exclusion_emitter_ids`, `platform_mount.mount_designation`. Columns restricted at the RESTRICTED tier: `geolocation_log.coordinates`, `geolocation_log.timestamp_utc`.

> Note: `rwr_system.model_name` (the RWR designation itself) is treated as UNCLASSIFIED — knowing a model exists is not operationally sensitive. Only the blind-spot list (`exclusion_emitter_ids`) is classified CONFIDENTIAL.

### 4.2 Security Standards
* **FIPS 140-3:** Requirement for all data-at-rest encryption. `cryptography >= 42.x` + OpenSSL 3.x FIPS module — validation deferred to Phase 1.
* **CIS Level 2:** Database hardening and "Least Privilege" service accounts. The `curator_app` PostgreSQL service account is `SELECT`-only on all tables; write operations are performed by a separate migration account.
* **Row-Level Security (RLS):** PostgreSQL RLS is enabled on all RESTRICTED and CONFIDENTIAL tables (`platform_mount`, `weapon_mount`, `rwr_system`, `platform_rwr`, `geolocation_log`). A permissive `curator_app_all` policy grants access to the `curator_app` account. Fine-grained per-role RLS policies are planned for Phase 3.
* **SQL Guard Middleware:** Blocks any LLM-generated statement whose leading keyword is in the blocked set: `INSERT`, `UPDATE`, `DELETE`, `DROP`, `TRUNCATE`, `CREATE`, `ALTER`, `GRANT`, `REVOKE`, `COPY`, `EXECUTE`, `CALL`, `DO`, `VACUUM`, `REINDEX`, `CLUSTER`, `COMMENT`, `SECURITY`. SQL comments are stripped before keyword extraction to prevent evasion. Violations return HTTP 403.
* **Network Isolation:** Podman containers communicate over an internal encrypted bridge (`curator_net`). The database container has no external egress.
* **API Authentication:** Role conveyed via `X-Curator-Role` header. In development, falls back to `SC_DEV_DEFAULT_ROLE`. In production, an absent or unrecognised header returns HTTP 401.

---

## 5. User Stories
* **As an Analyst,** I want to ask "Where was the USS Nimitz at 0800 UTC today?" and receive a map coordinate.
* **As an Intel Officer,** I want to know which Emitter-IDs are invisible to the Type 45 Destroyer's current RWR suite to assess vulnerability.
* **As a Logistics Manager,** I want to see a list of all platforms manufactured in the UK but operated by allied nations.

---

## 6. Implementation Roadmap

1. **Phase 0 ✅ Complete:** Repository scaffold, ORM models, SQL DDL, seed data, Podman Compose, FastAPI stub, RBAC, SQL Guard, structured logging, unit tests, and full documentation suite.
2. **Phase 1 (TBD):** Validate DDL against live PostgreSQL 15 + PostGIS 3.4; test rootless Podman Compose bring-up; verify UUID/PostGIS extensions, internal bridge isolation, seed data constraints, PLATFORM_RWR zero-case, and CIS Level 2 hardening.
3. **Phase 2 (TBD):** Develop and integrate the full LangChain Curator Agent; add integration tests (pytest-asyncio + testcontainers); implement `DATA_CURATOR` write agent; consider Alembic for schema migrations.
4. **Phase 3 (TBD):** Implement fine-grained per-role Row-Level Security policies on the LLM output layer; replace permissive `curator_app_all` RLS policies with role-specific policies.
5. **Phase 4 (TBD):** Stress test with representational data, performance tuning, and air-gapped deployment validation.

---
