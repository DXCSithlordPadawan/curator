# Sentinel Curator — Security and Compliance Document

**Version:** 0.1.0  
**Date:** 2026-03-25  
**Standards:** FIPS 140-3 · CIS Level 2 · OWASP Top 10 · NIST SP 800-53 Rev 5 · DISA STIG

---

## 1. Security Architecture Summary

Sentinel Curator applies defence-in-depth across five layers:

1. **Network isolation** — DB container on internal-only Podman bridge (no external egress)
2. **SQL Guard** — hard intercept blocking all LLM write/mutation statements
3. **RBAC output filtering** — column-level masking based on clearance tier
4. **Least-privilege DB account** — `curator_app` has SELECT-only grants
5. **LLM context isolation** — LLM receives schema DDL only, never live data

---

## 2. OWASP Top 10 Mapping

| OWASP Risk | Mitigation |
|---|---|
| A01 Broken Access Control | RBAC clearance tiers; column-level output masking |
| A02 Cryptographic Failures | FIPS 140-3 `cryptography` lib; TLS enforced in production |
| A03 Injection | SQL Guard middleware; parameterised queries via SQLAlchemy |
| A04 Insecure Design | Threat-modelled architecture; LLM never sees live data |
| A05 Security Misconfiguration | CIS Level 2 PostgreSQL hardening; no default passwords |
| A06 Vulnerable Components | `pip-audit` and `bandit` in CI pipeline |
| A07 Auth Failures | Role resolved from trusted upstream header only |
| A08 Data Integrity Failures | DDL migration files hashed and version-controlled |
| A09 Logging Failures | structlog JSON to stdout; all guard violations logged as ERROR |
| A10 SSRF | No user-controlled URL fetch paths in application |

---

## 3. NIST SP 800-53 Rev 5 Controls

| Control | Description | Implementation |
|---|---|---|
| AC-2 | Account Management | RBAC roles defined; least-privilege DB account |
| AC-3 | Access Enforcement | `is_column_visible()` output filter; SQL Guard |
| AC-6 | Least Privilege | `curator_app` SELECT-only; no INSERT/UPDATE grants |
| AU-2 | Event Logging | All SQL Guard violations logged as security events |
| AU-3 | Audit Record Content | structlog includes timestamp, role, SQL preview, event type |
| CM-7 | Least Functionality | Containers have no unnecessary services |
| IA-5 | Authenticator Management | Secrets via env vars; `SecretStr` in Pydantic settings |
| SC-8 | Transmission Confidentiality | TLS required in production (upstream proxy responsibility) |
| SC-28 | Protection at Rest | FIPS 140-3 encryption for data at rest (Phase 1 task) |
| SI-10 | Information Input Validation | SQL Guard validates all LLM-generated SQL |

---

## 4. CIS Level 2 PostgreSQL Hardening Checklist

| Check | Status | Notes |
|---|---|---|
| Use non-default port | Phase 1 | Default 5432 used in dev; change in production |
| Disable superuser remote login | Phase 1 | `pg_hba.conf` to be hardened |
| Enable SSL/TLS for connections | Phase 1 | Internal bridge in dev; TLS in production |
| Use strong password for all accounts | Required | SC_DB_PASSWORD must be 16+ chars |
| Revoke PUBLIC schema privileges | Phase 1 | `REVOKE CREATE ON SCHEMA public FROM PUBLIC` |
| Enable audit logging | Phase 1 | `pgaudit` extension recommended |
| Set `log_connections = on` | Phase 1 | postgresql.conf hardening |
| Set `log_disconnections = on` | Phase 1 | postgresql.conf hardening |
| Row-Level Security enabled | Done | RLS enabled on all sensitive tables in DDL |
| Least-privilege service account | Done | curator_app has SELECT only |

---

## 5. FIPS 140-3 Compliance Notes

- Python `cryptography` library >= 42.0.0 links against OpenSSL 3.x.
- OpenSSL 3.x supports a FIPS 140-3 validated provider module.
- For full FIPS compliance the host OS OpenSSL must have the FIPS module enabled.
- Verify with: `openssl version -a` and `openssl list -providers`
- In air-gapped / UK Gov environments, coordinate with the platform security team.

**Reference:** https://csrc.nist.gov/publications/detail/fips/140/3/final

---

## 6. Secrets Management

- All secrets loaded from environment variables or `.env` file.
- Pydantic `SecretStr` prevents secrets appearing in logs or repr output.
- `.env` is in `.gitignore` — never committed.
- In production, inject secrets via a vault (HashiCorp Vault, AWS Secrets Manager, etc.).

---

## 7. Threat Model Summary

| Threat | Actor | Mitigation |
|---|---|---|
| SQL Injection via LLM prompt | External attacker | SQL Guard blocks all non-SELECT; parameterised queries |
| Data exfiltration via LLM context | Malicious query | LLM receives DDL only; output filtered by clearance |
| Enumeration of platform IDs | Attacker | UUID v4 PKs; no sequential integer IDs |
| Privilege escalation via role header | Attacker | Role header trusted only from upstream IdP proxy |
| Container escape | Attacker | Rootless Podman; non-root app user |
| DB direct access | Attacker | Internal-only network; no exposed DB port |

---

## 8. Sources

| Reference | URL |
|---|---|
| FIPS 140-3 | https://csrc.nist.gov/publications/detail/fips/140/3/final |
| NIST SP 800-53 Rev 5 | https://csrc.nist.gov/publications/detail/sp/800-53/rev-5/final |
| CIS PostgreSQL Benchmark | https://www.cisecurity.org/benchmark/postgresql |
| OWASP Top 10 2021 | https://owasp.org/www-project-top-ten/ |
| DISA STIG PostgreSQL | https://www.stigviewer.com/stig/postgresql_9-x/ |
