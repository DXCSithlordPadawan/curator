-- =============================================================================
-- Sentinel Curator -- Migration 002: Self-referential parent platform
-- PostgreSQL 15+
--
-- Adds an optional parent_platform_id to individual_platform, allowing one
-- platform to be recorded as embarked on (or carried by) another
-- (e.g. a carrier air wing aircraft aboard USS Nimitz).
--
-- Constraint: a platform cannot reference itself as its own parent.
-- =============================================================================

ALTER TABLE individual_platform
    ADD COLUMN IF NOT EXISTS parent_platform_id UUID
        REFERENCES individual_platform(id) ON DELETE SET NULL,
    ADD CONSTRAINT chk_no_self_parent
        CHECK (parent_platform_id <> id);

CREATE INDEX IF NOT EXISTS ix_individual_platform_parent
    ON individual_platform(parent_platform_id)
    WHERE parent_platform_id IS NOT NULL;

COMMENT ON COLUMN individual_platform.parent_platform_id IS
    'Optional FK to another individual_platform that carries or hosts this platform '
    '(e.g. aircraft embarked on a carrier). NULL when the platform is independent. '
    'Cannot reference the platform''s own id (chk_no_self_parent).';
