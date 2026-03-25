# Sentinel Curator — RBAC Document

**Version:** 0.1.0  
**Date:** 2026-03-25

---

## 1. Clearance Tiers

| Tier | Level | Data Visible |
|---|---|---|
| UNCLASSIFIED | 0 | Platform class names, descriptions, manufacturer country |
| RESTRICTED | 1 | Above + individual platform telemetry / locations |
| CONFIDENTIAL | 2 | Above + weapon mounts, RWR Emitter-ID exclusion lists |

---

## 2. Role Mapping

| Role Name | Clearance | Notes |
|---|---|---|
| UNCLASSIFIED | 0 | Default read-only |
| ANALYST | 0 | General platform analyst |
| LOGISTICS_MANAGER | 0 | Supply chain queries |
| RESTRICTED | 1 | Telemetry access |
| INTEL_OFFICER | 2 | Full classified access |
| CONFIDENTIAL | 2 | Full classified access |
| SYSTEM_ADMIN | 2 | Full access + write-permitted |
| DATA_CURATOR | 2 | Write-permitted data loading (Phase 2) |

---

## 3. Column Visibility

| Column | Level 0 | Level 1 | Level 2 |
|---|---|---|---|
| platform_class.class_name | Yes | Yes | Yes |
| platform_class.manufacturer_country | Yes | Yes | Yes |
| individual_platform.name | Yes | Yes | Yes |
| geolocation_log.coordinates | No | Yes | Yes |
| geolocation_log.timestamp_utc | No | Yes | Yes |
| platform_mount.mount_designation | No | No | Yes |
| weapon_mount.weapon_designation | No | No | Yes |
| rwr_system.exclusion_emitter_ids | No | No | Yes |

---

## 4. Write Permission

Write operations (INSERT/UPDATE/DELETE/DROP) are permitted only for:
- SYSTEM_ADMIN
- DATA_CURATOR

All other roles receive HTTP 403 for any write-type statement.

---

## 5. Implementation References

- Role resolution: src/sentinel_curator/rbac/roles.py
- SQL Guard write check: src/sentinel_curator/curator/sql_guard.py
- Output filter: src/sentinel_curator/curator/agent.py
- Tests: tests/test_rbac.py
