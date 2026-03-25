# Sentinel Curator -- Deployment Guide

**Version:** 0.1.0
**Date:** 2026-03-25
**Target:** Rootless Podman 4.x on Linux (RHEL 9 / CentOS Stream 9 recommended)

---

## 1. Prerequisites

| Requirement | Minimum Version | Notes |
|---|---|---|
| Podman | 4.0 | Rootless mode required |
| podman-compose | 1.0 | pip install podman-compose |
| Python | 3.11 | For scripts and local dev |
| Git | 2.x | Repository management |
| OpenSSL | 3.x | Required for FIPS 140-3 alignment |

Verify rootless Podman is working:

```bash
podman run --rm hello-world
```

---

## 2. Environment Configuration

Copy the template and populate all values:

```bash
cp .env.example .env
```

Required variables:

| Variable | Description |
|---|---|
| SC_DB_PASSWORD | Strong password (16+ chars, mixed case, symbols) |
| SC_SECRET_KEY | Random 32-byte hex string |
| SC_OPENAI_API_KEY | LLM provider key (or configure Azure alternative) |

Generate a secret key:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

---

## 3. First-Time Deployment

### Step 1 -- Start the database container

```bash
podman-compose -f deploy/podman-compose.yml up -d db
```

Wait for the healthcheck to pass (approximately 15-30 seconds):

```bash
podman-compose -f deploy/podman-compose.yml ps
```

The db service status should show healthy.

### Step 2 -- Apply the database schema

```bash
podman-compose -f deploy/podman-compose.yml run --rm app \
    python scripts/apply_migrations.py
```

### Step 3 -- (Optional) Load seed data for development

```bash
podman-compose -f deploy/podman-compose.yml exec db \
    psql -U curator_app -d sentinel_curator \
    -f /dev/stdin < db/seeds/seed_platforms.sql
```

### Step 4 -- Start the application container

```bash
podman-compose -f deploy/podman-compose.yml up -d app
```

### Step 5 -- Verify the deployment

```bash
curl http://127.0.0.1:8000/health
```

Expected response: {"status":"ok","version":"0.1.0"}

---

## 4. Updating the Application

```bash
# Rebuild the application image
podman-compose -f deploy/podman-compose.yml build app

# Restart the application container only
podman-compose -f deploy/podman-compose.yml up -d --no-deps app
```

---

## 5. Applying New Migrations

Place new SQL files in db/migrations/ with the next sequential prefix
(e.g. 002_add_column.sql). Then run:

```bash
podman-compose -f deploy/podman-compose.yml run --rm app \
    python scripts/apply_migrations.py
```

---

## 6. Stopping the Services

```bash
# Stop without removing volumes
podman-compose -f deploy/podman-compose.yml down

# Stop and remove all data volumes (destructive)
podman-compose -f deploy/podman-compose.yml down -v
```

---

## 7. Production Hardening Checklist

| Item | Action |
|---|---|
| Disable Swagger UI | Set docs_url=None in FastAPI constructor or use SC_APP_ENV=production |
| Remove DEV_DEFAULT_ROLE | Ensure SC_DEV_DEFAULT_ROLE is empty in production .env |
| TLS termination | Place a reverse proxy (nginx/Caddy) in front of the app container |
| PostgreSQL SSL | Enable ssl=require in postgresql.conf and pg_hba.conf |
| Log forwarding | Pipe container stdout to a SIEM-capable log aggregator |
| Secret rotation | Rotate SC_DB_PASSWORD and SC_SECRET_KEY on a defined schedule |
| Image pinning | Pin container image digests in podman-compose.yml for reproducibility |

---

## 8. Air-Gapped Deployment Notes

For air-gapped environments:

1. Pull and save images on a connected machine:
```bash
podman pull docker.io/postgis/postgis:15-3.4
podman pull docker.io/python:3.11-slim
podman save -o postgis-15-3.4.tar postgis/postgis:15-3.4
podman save -o python-3.11-slim.tar python:3.11-slim
```

2. Transfer tar files to the air-gapped host and load:
```bash
podman load -i postgis-15-3.4.tar
podman load -i python-3.11-slim.tar
```

3. Pre-install Python wheels offline:
```bash
pip download -r requirements.txt -d ./wheels/
# Transfer wheels/ directory to air-gapped host
pip install --no-index --find-links=./wheels/ -r requirements.txt
```
