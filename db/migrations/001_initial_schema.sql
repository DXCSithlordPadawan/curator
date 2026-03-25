-- =============================================================================
-- Sentinel Curator — Initial Database Schema (Migration 001)
-- PostgreSQL 15+ with PostGIS 3.4
--
-- Compliance: FIPS 140-3 · CIS Level 2 · NIST SP 800-53
-- UUID v4 primary keys throughout — prevents enumeration attacks.
-- All timestamps stored in UTC (TIMESTAMPTZ).
-- PostGIS GEOGRAPHY(POINT, 4326) for spatial telemetry (WGS-84).
-- =============================================================================

-- ---------------------------------------------------------------------------
-- Extensions
-- ---------------------------------------------------------------------------
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";   -- UUID v4 generation
CREATE EXTENSION IF NOT EXISTS "postgis";     -- Spatial/geographic types

-- ---------------------------------------------------------------------------
-- PLATFORM_CLASS
-- Classification: UNCLASSIFIED
-- Master template for a ship/vehicle design class.
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS platform_class (
    id                   UUID         PRIMARY KEY DEFAULT uuid_generate_v4(),
    class_name           VARCHAR(255) NOT NULL UNIQUE,
    manufacturer_country VARCHAR(100) NOT NULL,
    description          TEXT,
    created_at           TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at           TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE  platform_class                    IS 'UNCLASSIFIED: Master design template for a platform class.';
COMMENT ON COLUMN platform_class.id                 IS 'UUID v4 primary key — prevents enumeration.';
COMMENT ON COLUMN platform_class.manufacturer_country IS 'ISO 3166-1 alpha-2 country code.';

-- ---------------------------------------------------------------------------
-- INDIVIDUAL_PLATFORM
-- Classification: RESTRICTED (location telemetry)
-- A specific physical asset instance.
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS individual_platform (
    id               UUID         PRIMARY KEY DEFAULT uuid_generate_v4(),
    hull_serial_id   VARCHAR(100) NOT NULL UNIQUE,
    name             VARCHAR(255) NOT NULL,
    class_id         UUID         NOT NULL REFERENCES platform_class(id) ON DELETE RESTRICT,
    operator_country VARCHAR(100) NOT NULL,
    owner_country    VARCHAR(100) NOT NULL,
    created_at       TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at       TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_individual_platform_class_id
    ON individual_platform(class_id);

CREATE INDEX IF NOT EXISTS ix_individual_platform_operator
    ON individual_platform(operator_country);

COMMENT ON TABLE individual_platform IS 'RESTRICTED: Specific physical platform instance.';

-- ---------------------------------------------------------------------------
-- PLATFORM_MOUNT (hardpoints / pylons)
-- Classification: CONFIDENTIAL
-- Physical mount positions on an individual platform.
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS platform_mount (
    id                 UUID         PRIMARY KEY DEFAULT uuid_generate_v4(),
    mount_designation  VARCHAR(100) NOT NULL,
    platform_id        UUID         NOT NULL REFERENCES individual_platform(id) ON DELETE CASCADE,
    operator_country   VARCHAR(100) NOT NULL,
    owner_country      VARCHAR(100) NOT NULL,
    created_at         TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_platform_mount_platform_id
    ON platform_mount(platform_id);

COMMENT ON TABLE platform_mount IS 'CONFIDENTIAL: Hardpoint / pylon configuration per platform.';

-- ---------------------------------------------------------------------------
-- WEAPON_MOUNT
-- Classification: CONFIDENTIAL
-- Specific weapon fitted to a platform mount.
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS weapon_mount (
    id                  UUID         PRIMARY KEY DEFAULT uuid_generate_v4(),
    weapon_designation  VARCHAR(255) NOT NULL,
    mount_id            UUID         NOT NULL REFERENCES platform_mount(id) ON DELETE CASCADE,
    operator_country    VARCHAR(100) NOT NULL,
    owner_country       VARCHAR(100) NOT NULL,
    notes               TEXT,
    created_at          TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_weapon_mount_mount_id
    ON weapon_mount(mount_id);

COMMENT ON TABLE weapon_mount IS 'CONFIDENTIAL: Weapon fitted to a specific platform mount.';

-- ---------------------------------------------------------------------------
-- RWR_SYSTEM
-- Classification: CONFIDENTIAL (exclusion_emitter_ids is operationally sensitive)
-- Radar Warning Receiver model + blind spot data.
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS rwr_system (
    id                    UUID         PRIMARY KEY DEFAULT uuid_generate_v4(),
    model_name            VARCHAR(255) NOT NULL UNIQUE,
    sensitivity_range     VARCHAR(100),
    exclusion_emitter_ids TEXT[],           -- CONFIDENTIAL: RWR blind spots
    notes                 TEXT,
    created_at            TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE  rwr_system                        IS 'CONFIDENTIAL: RWR model and detection limitations.';
COMMENT ON COLUMN rwr_system.exclusion_emitter_ids  IS 'CONFIDENTIAL: Emitter IDs this RWR cannot detect (blind spots).';

-- ---------------------------------------------------------------------------
-- GEOLOCATION_LOG
-- Classification: RESTRICTED
-- Time-series GPS telemetry for individual platforms.
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS geolocation_log (
    id             UUID        PRIMARY KEY DEFAULT uuid_generate_v4(),
    platform_id    UUID        NOT NULL REFERENCES individual_platform(id) ON DELETE CASCADE,
    coordinates    GEOGRAPHY(POINT, 4326) NOT NULL,   -- WGS-84
    timestamp_utc  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Spatial index for bounding-box and proximity queries
CREATE INDEX IF NOT EXISTS ix_geolocation_log_coords
    ON geolocation_log USING GIST(coordinates);

-- Time-series index for range queries ("at 0800 UTC today")
CREATE INDEX IF NOT EXISTS ix_geolocation_log_ts
    ON geolocation_log(timestamp_utc DESC);

CREATE INDEX IF NOT EXISTS ix_geolocation_log_platform
    ON geolocation_log(platform_id);

COMMENT ON TABLE  geolocation_log             IS 'RESTRICTED: UTC-timestamped GPS telemetry per platform.';
COMMENT ON COLUMN geolocation_log.coordinates IS 'GEOGRAPHY(POINT,4326) — WGS-84 lat/lon via PostGIS.';

-- ---------------------------------------------------------------------------
-- Row-Level Security policies (to be activated in production)
-- Enables future per-user RLS based on session role variable.
-- ---------------------------------------------------------------------------
ALTER TABLE platform_mount   ENABLE ROW LEVEL SECURITY;
ALTER TABLE weapon_mount     ENABLE ROW LEVEL SECURITY;
ALTER TABLE rwr_system       ENABLE ROW LEVEL SECURITY;
ALTER TABLE geolocation_log  ENABLE ROW LEVEL SECURITY;

-- Permissive policy for application service account (curator_app)
-- Replace with fine-grained per-role policies in Phase 3.
CREATE POLICY curator_app_all ON platform_mount
    FOR ALL TO curator_app USING (true);

CREATE POLICY curator_app_all ON weapon_mount
    FOR ALL TO curator_app USING (true);

CREATE POLICY curator_app_all ON rwr_system
    FOR ALL TO curator_app USING (true);

CREATE POLICY curator_app_all ON geolocation_log
    FOR ALL TO curator_app USING (true);

-- ---------------------------------------------------------------------------
-- Least-privilege grant for application service account
-- ---------------------------------------------------------------------------
GRANT SELECT ON ALL TABLES IN SCHEMA public TO curator_app;
-- Write access is intentionally NOT granted here.
-- Data loading is handled via a separate privileged migration account.
