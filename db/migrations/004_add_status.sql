-- =============================================================================
-- Sentinel Curator -- Migration 004: Status master table
-- PostgreSQL 15+
--
-- Adds a STATUS lookup table as the single source of truth for operational
-- status values (e.g. Active, Decommissioned, In Maintenance, Reserve).
--
-- Adds a status_id FK to:
--   - individual_platform (operational status of the platform asset)
--   - weapon_mount        (operational status of the fitted weapon)
--
-- status_id is nullable: existing rows carry NULL until explicitly set.
-- =============================================================================

-- ---------------------------------------------------------------------------
-- STATUS
-- Classification: UNCLASSIFIED
-- Master lookup table for operational status codes.
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS status (
    id          UUID         PRIMARY KEY DEFAULT uuid_generate_v4(),
    code        VARCHAR(50)  NOT NULL UNIQUE,
    label       VARCHAR(255) NOT NULL,
    description TEXT,
    created_at  TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE  status IS
    'UNCLASSIFIED: Master lookup table for operational status codes.';
COMMENT ON COLUMN status.id IS
    'UUID v4 primary key -- prevents enumeration.';
COMMENT ON COLUMN status.code IS
    'Short machine-readable code, e.g. ACTIVE, DECOMMISSIONED, MAINTENANCE, RESERVE.';
COMMENT ON COLUMN status.label IS
    'Human-readable label for display purposes.';
COMMENT ON COLUMN status.description IS
    'Optional description of what this status means operationally.';

-- Seed standard status codes.
INSERT INTO status (code, label, description)
VALUES
    ('ACTIVE',          'Active',          'Asset is fully operational and in active service.'),
    ('RESERVE',         'Reserve',         'Asset is operational but held in reserve / reduced readiness.'),
    ('MAINTENANCE',     'In Maintenance',  'Asset is temporarily unavailable due to scheduled or unscheduled maintenance.'),
    ('DECOMMISSIONED',  'Decommissioned',  'Asset has been permanently withdrawn from service.')
ON CONFLICT (code) DO NOTHING;

-- ---------------------------------------------------------------------------
-- INDIVIDUAL_PLATFORM: add optional status FK
-- ---------------------------------------------------------------------------
ALTER TABLE individual_platform
    ADD COLUMN IF NOT EXISTS status_id UUID
        REFERENCES status(id) ON DELETE SET NULL;

CREATE INDEX IF NOT EXISTS ix_individual_platform_status
    ON individual_platform(status_id)
    WHERE status_id IS NOT NULL;

COMMENT ON COLUMN individual_platform.status_id IS
    'Optional FK to the STATUS master table indicating the current operational '
    'status of this platform (e.g. Active, Decommissioned). NULL when not set.';

-- ---------------------------------------------------------------------------
-- WEAPON_MOUNT: add optional status FK
-- ---------------------------------------------------------------------------
ALTER TABLE weapon_mount
    ADD COLUMN IF NOT EXISTS status_id UUID
        REFERENCES status(id) ON DELETE SET NULL;

CREATE INDEX IF NOT EXISTS ix_weapon_mount_status
    ON weapon_mount(status_id)
    WHERE status_id IS NOT NULL;

COMMENT ON COLUMN weapon_mount.status_id IS
    'Optional FK to the STATUS master table indicating the current operational '
    'status of this weapon (e.g. Active, In Maintenance). NULL when not set.';

-- ---------------------------------------------------------------------------
-- Least-privilege grant for application service account
-- ---------------------------------------------------------------------------
GRANT SELECT ON status TO curator_app;
