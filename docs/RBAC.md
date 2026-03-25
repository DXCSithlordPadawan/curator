# Sentinel Curator -- RBAC Document

**Version:** 0.1.0
**Date:** 2026-03-25

---

## 1. Clearance Tiers

| Tier | Level | Data Visible |
|---|---|---|
| UNCLASSIFIED | 0 | Platform class names, descriptions, manufacturer country |
| RESTRICTED | 1 | Above plus individual platform telemetry and locations |
| CONFIDENTIAL | 2 | Above plus weapon mounts and RWR Emitter-ID exclusion lists |

---

## 2. Role to Clearance Mapping

| Role Name | Clearance | Description |
|---|---|---|
| UNCLASSIFIED | 0 | Default read-only public access |
| ANALYST | 0 | General platform analyst |
| LOGISTICS_MANAGER | 0 | Supply chain and logistics queries |
| RESTRICTED | 1 | Telemetry access granted |
| INTEL_OFFICER | 2 | Full access including RWR blind spots |
| CONFIDENTIAL | 2 | Full classified access |
| SYSTEM_ADMIN | 2 | Full access plus write-permitted role |
| DATA_CURATOR | 2 | Write-permitted data loading role (Phase 2) |

---

## 3. Column Visibility Matrix

| Column | Level 0 | Level 1 | Level 2 |
|---|---|---|---|
| platform_class.class_name | Yes | Yes | Yes |
| platform_class.manufacturer_country | Yes | Yes | Yes |
| platform_class.description | Yes | Yes | Yes |
| individual_platform.name | Yes | Yes | Yes |
| individual_platform.hull_serial_id | Yes | Yes | Yes |
| individual_platform.operator_country | Yes | Yes | Yes |
| individual_platform.owner_country | Yes | Yes | Yes |
| geolocation_log.coordinates | No | Yes | Yes |
| geolocation_log.timestamp_utc | No | Yes | Yes |
| platform_mount.mount_designation | No | No | Yes |
| weapon_mount.weapon_designation | No | No | Yes |
| weapon_mount.notes | No | No | Yes |
| rwr_system.model_name | Yes | Yes | Yes |
| rwr_system.sensitivity_range | Yes | Yes | Yes |
| rwr_system.exclusion_emitter_ids | No | No | Yes |
| platform_rwr (association existence) | No | No | Yes |

Note: rwr_system.model_name and sensitivity_range are treated as UNCLASSIFIED
(knowing an RWR model exists is not sensitive; knowing its blind spots is).

---

## 4. Write Permission

Only two roles may execute write (INSERT/UPDATE/DELETE/DROP) operations:

| Role | Rationale |
|---|---|
| SYSTEM_ADMIN | Platform administration and emergency data correction |
| DATA_CURATOR | Automated data loading pipeline (Phase 2) |

All other roles receive HTTP 403 if the SQL Guard detects a write-type statement.

---

## 5. User Story to Role Mapping

| User Story | Required Role |
|---|---|
| Where was the USS Nimitz at 0800 UTC? | RESTRICTED or above |
| Which Emitter-IDs are invisible to the Type 45 RWR suite? | INTEL_OFFICER or CONFIDENTIAL |
| List all platforms manufactured in the UK but operated by allies | UNCLASSIFIED (ANALYST or LOGISTICS_MANAGER) |

---

## 6. Implementation References

- Role resolution: src/sentinel_curator/rbac/roles.py
- SQL Guard write check: src/sentinel_curator/curator/sql_guard.py
- Output filter: src/sentinel_curator/curator/agent.py
- Unit tests: tests/test_rbac.py
