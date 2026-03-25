# Sentinel Curator -- Maintenance Guide

**Version:** 0.1.0
**Date:** 2026-03-25

---

## 1. Routine Maintenance Tasks

### 1.1 Check Service Health

```bash
# Container status
podman-compose -f deploy/podman-compose.yml ps

# API health probe
curl http://127.0.0.1:8000/health

# Database connectivity
podman exec sentinel_db pg_isready -U curator_app -d sentinel_curator
```

### 1.2 View Application Logs

```bash
# Live log stream
podman-compose -f deploy/podman-compose.yml logs -f app

# Last 100 lines
podman logs --tail 100 sentinel_app
```

### 1.3 View Database Logs

```bash
podman logs --tail 100 sentinel_db
```

---

## 2. Database Maintenance

### 2.1 Manual Backup

```bash
podman exec sentinel_db pg_dump \
    -U curator_app \
    -d sentinel_curator \
    --format=custom \
    > backup_$(date +%Y%m%d_%H%M%S).dump
```

Store backups in an encrypted location. Never store backups in the repository.

### 2.2 Restore from Backup

```bash
podman exec -i sentinel_db pg_restore \
    -U curator_app \
    -d sentinel_curator \
    --clean \
    < backup_20260325_080000.dump
```

### 2.3 Vacuum and Analyse

Run periodically to reclaim storage and update query planner statistics:

```bash
podman exec sentinel_db psql \
    -U curator_app \
    -d sentinel_curator \
    -c "VACUUM ANALYZE;"
```

### 2.4 Check Table Sizes

```bash
podman exec sentinel_db psql \
    -U curator_app \
    -d sentinel_curator \
    -c "SELECT relname, pg_size_pretty(pg_total_relation_size(relid)) FROM pg_catalog.pg_statio_user_tables ORDER BY pg_total_relation_size(relid) DESC;"
```

---

## 3. Security Maintenance

### 3.1 Dependency Auditing

Run monthly and after any dependency update:

```bash
# Audit Python dependencies for known CVEs
pip-audit

# Bandit static security analysis
bandit -r src/
```

### 3.2 Secret Rotation

Rotate SC_DB_PASSWORD and SC_SECRET_KEY on a defined schedule (quarterly minimum):

1. Generate a new password.
2. Update the database user password via psql.
3. Update the .env file (or secrets manager) with the new value.
4. Restart the application container.

```bash
# Update DB password
podman exec sentinel_db psql -U postgres \
    -c "ALTER USER curator_app PASSWORD 'NEW_STRONG_PASSWORD';"
```

### 3.3 Review SQL Guard Violation Logs

Security events are logged at ERROR level with event key sql_guard.violation_blocked.

```bash
# Filter violations from JSON logs
podman logs sentinel_app | python -c \
    "import sys, json; [print(l) for l in sys.stdin if 'sql_guard.violation_blocked' in l]"
```

Investigate any violation immediately -- it may indicate prompt injection attempts.

---

## 4. Applying Schema Updates

1. Create a new migration file in db/migrations/ with the next sequential prefix.
2. Test against a development database first.
3. Apply to production:

```bash
podman-compose -f deploy/podman-compose.yml run --rm app \
    python scripts/apply_migrations.py
```

---

## 5. Updating Container Images

```bash
# Pull updated base images
podman pull docker.io/python:3.11-slim
podman pull docker.io/postgis/postgis:15-3.4

# Rebuild application image
podman-compose -f deploy/podman-compose.yml build app

# Restart with new image
podman-compose -f deploy/podman-compose.yml up -d --no-deps app
```

Always run the test suite after rebuilding:

```bash
python -m pytest tests/ -v
```

---

## 6. Geolocation Log Archiving

The GEOLOCATION_LOG table grows continuously with telemetry. Archive old entries:

```sql
-- Archive entries older than 90 days to a separate table (example pattern)
CREATE TABLE IF NOT EXISTS geolocation_log_archive AS
    SELECT * FROM geolocation_log WHERE timestamp_utc < NOW() - INTERVAL '90 days';

DELETE FROM geolocation_log WHERE timestamp_utc < NOW() - INTERVAL '90 days';
```

Only SYSTEM_ADMIN may run this operation. Coordinate with the DBA before execution.
