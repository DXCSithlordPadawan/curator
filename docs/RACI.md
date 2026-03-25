# Sentinel Curator -- RACI Matrix

**Version:** 0.1.0
**Date:** 2026-03-25

---

## Role Definitions

| Role | Description |
|---|---|
| Project Architect | System design, security architecture, final technical decisions |
| Developer | Code implementation, unit testing, migration authorship |
| DBA | Database schema, performance tuning, CIS hardening |
| Security Officer | Compliance verification, threat modelling, audit review |
| Platform Admin | Podman/container infrastructure, network isolation |
| Analyst | End-user querying the system via natural language |
| Intel Officer | Clearance-level user accessing CONFIDENTIAL data |

---

## RACI Key

- R = Responsible (does the work)
- A = Accountable (owns the outcome)
- C = Consulted (provides input)
- I = Informed (kept up to date)

---

## Phase 0 -- Scaffold and Documentation

| Task | Architect | Developer | DBA | Security | Platform Admin |
|---|---|---|---|---|---|
| Repository structure | A/R | C | I | I | I |
| ORM model design | A/R | C | C | I | I |
| DDL schema authorship | A | R | C | I | I |
| Security compliance doc | A/R | I | C | C | I |
| RBAC design | A/R | C | I | C | I |

---

## Phase 1 -- DDL and Podman Environment

| Task | Architect | Developer | DBA | Security | Platform Admin |
|---|---|---|---|---|---|
| PostgreSQL container config | C | I | A/R | C | R |
| CIS Level 2 hardening | C | I | R | A | C |
| Network isolation verification | I | I | I | A | R |
| Migration script execution | C | A/R | C | I | I |
| Seed data loading | I | A/R | C | I | I |

---

## Phase 2 -- Curator Agent

| Task | Architect | Developer | DBA | Security | Platform Admin |
|---|---|---|---|---|---|
| LangChain agent implementation | A | R | I | C | I |
| SQL Guard middleware | A | R | I | C | I |
| SQL Guard unit tests | C | A/R | I | C | I |
| Integration testing | C | A/R | C | C | I |
| RBAC output filter | A | R | I | C | I |

---

## Phase 3 -- RBAC Filtering

| Task | Architect | Developer | DBA | Security | Platform Admin |
|---|---|---|---|---|---|
| Column-level masking | A | R | I | C | I |
| Role-header validation | A | R | I | C | I |
| Compliance sign-off | C | I | I | A/R | I |

---

## Ongoing Operations

| Task | Architect | Developer | DBA | Security | Platform Admin |
|---|---|---|---|---|---|
| Security gap analysis review | A/R | C | C | C | I |
| Database backup and restore | I | I | A/R | C | C |
| Container image updates | C | C | I | C | A/R |
| User access provisioning | A | I | I | C | R |
| Audit log review | I | I | I | A/R | I |
| Incident response | A | R | R | A | R |
