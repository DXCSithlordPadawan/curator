-- =============================================================================
-- Sentinel Curator -- Migration 003: Military Organisation
-- PostgreSQL 15+
--
-- Adds an ORGANISATION table to represent military organisations such as
-- CENTCOM, 7th Fleet, NATO, etc.
--
-- Rules:
--   - An organisation has an owning country (owner_country FK → country.alpha2).
--   - An organisation may optionally be part of a parent organisation
--     (parent_organisation_id self-referential FK).
--   - An organisation cannot be part of itself (chk_no_self_parent_org).
--   - An individual_platform may optionally be assigned to one organisation
--     (organisation_id FK → organisation.id).
-- =============================================================================

-- ---------------------------------------------------------------------------
-- ORGANISATION
-- Classification: UNCLASSIFIED
-- Military organisation (e.g. CENTCOM, 7th Fleet, NATO).
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS organisation (
    id                     UUID         PRIMARY KEY DEFAULT uuid_generate_v4(),
    name                   VARCHAR(255) NOT NULL UNIQUE,
    abbreviation           VARCHAR(50),
    owner_country          CHAR(2)      NOT NULL REFERENCES country(alpha2) ON DELETE RESTRICT,
    parent_organisation_id UUID                  REFERENCES organisation(id) ON DELETE SET NULL,
    created_at             TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at             TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    CONSTRAINT chk_no_self_parent_org
        CHECK (parent_organisation_id <> id)
);

CREATE INDEX IF NOT EXISTS ix_organisation_owner_country
    ON organisation(owner_country);

CREATE INDEX IF NOT EXISTS ix_organisation_parent
    ON organisation(parent_organisation_id)
    WHERE parent_organisation_id IS NOT NULL;

COMMENT ON TABLE  organisation IS
    'UNCLASSIFIED: Military organisation (e.g. CENTCOM, 7th Fleet, NATO).';
COMMENT ON COLUMN organisation.id IS
    'UUID v4 primary key -- prevents enumeration.';
COMMENT ON COLUMN organisation.name IS
    'Full official name of the military organisation.';
COMMENT ON COLUMN organisation.abbreviation IS
    'Common abbreviation or short name, e.g. CENTCOM, NATO.';
COMMENT ON COLUMN organisation.owner_country IS
    'ISO 3166-1 alpha-2 FK -- nation that owns / sponsors this organisation (REFERENCES country.alpha2).';
COMMENT ON COLUMN organisation.parent_organisation_id IS
    'Optional FK to the parent ORGANISATION this organisation falls under '
    '(e.g. NAVCENT under CENTCOM). NULL for top-level organisations. '
    'Cannot reference the organisation''s own id (chk_no_self_parent_org).';

-- ---------------------------------------------------------------------------
-- INDIVIDUAL_PLATFORM: add optional organisation membership
-- ---------------------------------------------------------------------------
ALTER TABLE individual_platform
    ADD COLUMN IF NOT EXISTS organisation_id UUID
        REFERENCES organisation(id) ON DELETE SET NULL;

CREATE INDEX IF NOT EXISTS ix_individual_platform_organisation
    ON individual_platform(organisation_id)
    WHERE organisation_id IS NOT NULL;

COMMENT ON COLUMN individual_platform.organisation_id IS
    'Optional FK to the ORGANISATION this platform is assigned to '
    '(e.g. a carrier assigned to 7th Fleet). NULL when not assigned.';

-- ---------------------------------------------------------------------------
-- Least-privilege grant for application service account
-- ---------------------------------------------------------------------------
GRANT SELECT ON organisation TO curator_app;
