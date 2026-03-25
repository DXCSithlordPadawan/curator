# Sentinel Curator -- API Guide

**Version:** 0.1.0
**Date:** 2026-03-25
**Base URL:** http://127.0.0.1:8000

---

## 1. Authentication

All requests must include the X-Curator-Role header set to the caller's RBAC role.

In production this header is injected by a trusted upstream identity proxy.
Direct client-supplied headers are rejected at the ingress layer.

```
X-Curator-Role: ANALYST
```

Valid role values: UNCLASSIFIED, ANALYST, LOGISTICS_MANAGER, RESTRICTED,
INTEL_OFFICER, CONFIDENTIAL, SYSTEM_ADMIN

---

## 2. Endpoints

### GET /health

Liveness probe. No authentication required.

**Response 200:**
```json
{
  "status": "ok",
  "version": "0.1.0"
}
```

---

### POST /query

Submit a natural-language question. The Curator Agent translates it to SQL,
validates it through the SQL Guard, executes it, and returns results filtered
to the caller's clearance tier.

**Request headers:**
```
Content-Type: application/json
X-Curator-Role: RESTRICTED
```

**Request body:**
```json
{
  "question": "Where was the USS Nimitz at 0800 UTC on 2026-03-25?"
}
```

| Field | Type | Required | Constraints |
|---|---|---|---|
| question | string | Yes | 5 to 1000 characters |

**Response 200:**
```json
{
  "question": "Where was the USS Nimitz at 0800 UTC on 2026-03-25?",
  "sql": "SELECT ip.name, gl.coordinates, gl.timestamp_utc FROM individual_platform ip JOIN geolocation_log gl ON gl.platform_id = ip.id WHERE ip.hull_serial_id = 'CVN-68' AND gl.timestamp_utc = '2026-03-25 08:00:00+00'",
  "results": [
    {
      "name": "USS Nimitz",
      "coordinates": "POINT(-118.2437 33.9416)",
      "timestamp_utc": "2026-03-25T08:00:00+00:00"
    }
  ],
  "clearance": "RESTRICTED",
  "duration_ms": 142.5,
  "message": null
}
```

**Response 400 -- Bad request (empty or too-short question):**
```json
{ "detail": "Question must be at least 5 characters." }
```

**Response 401 -- Missing role header (production mode):**
```json
{ "detail": "X-Curator-Role header is required." }
```

**Response 403 -- SQL Guard violation:**
```json
{ "detail": "SQL Guard violation: SQL statement type 'DELETE' is not permitted for role 'ANALYST'." }
```

**Response 503 -- Agent not initialised:**
```json
{ "detail": "Curator agent is not initialised." }
```

---

## 3. Result Filtering by Role

Results are automatically stripped of columns above the caller's clearance.

| Column | ANALYST | RESTRICTED | INTEL_OFFICER |
|---|---|---|---|
| platform name, class, country | Returned | Returned | Returned |
| coordinates, timestamp_utc | Omitted | Returned | Returned |
| weapon_designation | Omitted | Omitted | Returned |
| exclusion_emitter_ids | Omitted | Omitted | Returned |

---

## 4. Example Queries by User Story

### Analyst -- List UK-built platforms operated by allies

```bash
curl -X POST http://127.0.0.1:8000/query \
  -H "Content-Type: application/json" \
  -H "X-Curator-Role: ANALYST" \
  -d '{"question": "List all platforms manufactured in the UK but operated by allied nations"}'
```

### RESTRICTED user -- Platform location

```bash
curl -X POST http://127.0.0.1:8000/query \
  -H "Content-Type: application/json" \
  -H "X-Curator-Role: RESTRICTED" \
  -d '{"question": "Where was USS Nimitz at 0800 UTC today?"}'
```

### Intel Officer -- RWR blind spots

```bash
curl -X POST http://127.0.0.1:8000/query \
  -H "Content-Type: application/json" \
  -H "X-Curator-Role: INTEL_OFFICER" \
  -d '{"question": "Which emitter IDs are invisible to the Type 45 destroyer RWR suite?"}'
```

---

## 5. Interactive Documentation

When running in development mode, OpenAPI docs are available at:

- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc

Disable both in production by setting SC_APP_ENV=production and removing
the docs_url/redoc_url from the FastAPI app constructor.
