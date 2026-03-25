# Sentinel Curator -- Container Build Guide

**Version:** 0.1.0
**Date:** 2026-03-25

---

## 1. Container Architecture

Two containers are defined:

| Container | Image | Purpose |
|---|---|---|
| sentinel_app | Built from deploy/Containerfile.app | FastAPI application |
| sentinel_db | Built from deploy/Containerfile.db | PostgreSQL 15 + PostGIS 3.4 |

Both run on the curator_internal Podman bridge network with internal: true,
meaning the database has no external network egress.

---

## 2. Building the Application Container

```bash
# From the project root
podman build \
    -f deploy/Containerfile.app \
    -t sentinel-curator-app:0.1.0 \
    .
```

The build uses a two-stage approach:
- Stage deps: installs all Python dependencies
- Stage final: copies only runtime artefacts, drops to non-root user (uid 1001)

---

## 3. Building the Database Container

The database container extends the official postgis/postgis:15-3.4 image.
In most deployments this image is used directly without a custom build.

To build a custom hardened variant:

```bash
podman build \
    -f deploy/Containerfile.db \
    -t sentinel-curator-db:0.1.0 \
    .
```

---

## 4. Security Controls in Containerfile.app

| Control | Implementation |
|---|---|
| Non-root user | useradd curator uid 1001; USER curator directive |
| Minimal base image | python:3.11-slim (no unnecessary OS packages) |
| No secrets in image | All credentials via environment variables at runtime |
| Healthcheck | HTTP GET /health via httpx in the container |
| Read-only src | Source files copied; no write access needed at runtime |

---

## 5. Podman Compose Reference

Start all services:
```bash
podman-compose -f deploy/podman-compose.yml up -d
```

View logs:
```bash
podman-compose -f deploy/podman-compose.yml logs -f app
podman-compose -f deploy/podman-compose.yml logs -f db
```

Stop all services:
```bash
podman-compose -f deploy/podman-compose.yml down
```

Rebuild and restart application only:
```bash
podman-compose -f deploy/podman-compose.yml build app
podman-compose -f deploy/podman-compose.yml up -d --no-deps app
```

---

## 6. Network Verification

Confirm the database container has no external egress:

```bash
# This should fail or time out -- db has no external route
podman exec sentinel_db curl -s --max-time 5 https://example.com
```

Confirm the app container can reach the database:

```bash
podman exec sentinel_app python -c \
    "import psycopg2; psycopg2.connect(host='db', port=5432, dbname='sentinel_curator', user='curator_app', password='YOUR_PASSWORD'); print('OK')"
```

---

## 7. Image Versioning

Tag images with both the version and latest for reproducibility:

```bash
podman tag sentinel-curator-app:0.1.0 sentinel-curator-app:latest
```

For production, always reference the versioned tag (not latest) in
podman-compose.yml to ensure deterministic deployments.
