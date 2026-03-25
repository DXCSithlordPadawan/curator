-- =============================================================================
-- Sentinel Curator -- Representative Seed Data
-- FOR DEVELOPMENT / TESTING ONLY -- NOT LIVE OPERATIONAL DATA
-- All hull numbers, names, and positions are illustrative / fictitious.
-- =============================================================================

-- ---------------------------------------------------------------------------
-- Countries (UNCLASSIFIED) -- ISO 3166-1 alpha-2 reference data
-- Only the codes required by the seed platforms are listed here.
-- Add further rows as needed; the country table is the canonical source.
-- ---------------------------------------------------------------------------
INSERT INTO country (alpha2, name)
VALUES
    ('GB', 'United Kingdom of Great Britain and Northern Ireland'),
    ('US', 'United States of America')
ON CONFLICT (alpha2) DO NOTHING;

-- ---------------------------------------------------------------------------
-- Platform Classes (UNCLASSIFIED)
-- ---------------------------------------------------------------------------
INSERT INTO platform_class (id, class_name, manufacturer_country, description)
VALUES
    ('a1000000-0000-4000-8000-000000000001', 'Nimitz-class',        'US', 'Nuclear-powered supercarrier class, 10 hulls commissioned.'),
    ('a1000000-0000-4000-8000-000000000002', 'Ford-class',          'US', 'Next-generation nuclear carrier class.'),
    ('a1000000-0000-4000-8000-000000000003', 'Type 45 Destroyer',   'GB', 'Royal Navy air-defence destroyer.'),
    ('a1000000-0000-4000-8000-000000000004', 'Arleigh Burke-class', 'US', 'Multi-mission guided-missile destroyer.')
ON CONFLICT (class_name) DO NOTHING;

-- ---------------------------------------------------------------------------
-- Individual Platforms (RESTRICTED)
-- ---------------------------------------------------------------------------
INSERT INTO individual_platform (id, hull_serial_id, name, class_id, operator_country, owner_country)
VALUES
    ('b2000000-0000-4000-8000-000000000001', 'CVN-68', 'USS Nimitz',          'a1000000-0000-4000-8000-000000000001', 'US', 'US'),
    ('b2000000-0000-4000-8000-000000000002', 'CVN-78', 'USS Gerald R. Ford',  'a1000000-0000-4000-8000-000000000002', 'US', 'US'),
    ('b2000000-0000-4000-8000-000000000003', 'D32',    'HMS Daring',          'a1000000-0000-4000-8000-000000000003', 'GB', 'GB'),
    ('b2000000-0000-4000-8000-000000000004', 'DDG-51', 'USS Arleigh Burke',   'a1000000-0000-4000-8000-000000000004', 'US', 'US')
ON CONFLICT (hull_serial_id) DO NOTHING;

-- ---------------------------------------------------------------------------
-- Platform Mounts (CONFIDENTIAL)
-- ---------------------------------------------------------------------------
INSERT INTO platform_mount (id, mount_designation, platform_id, operator_country, owner_country)
VALUES
    ('c3000000-0000-4000-8000-000000000001', 'CIWS-FWD', 'b2000000-0000-4000-8000-000000000001', 'US', 'US'),
    ('c3000000-0000-4000-8000-000000000002', 'CIWS-AFT', 'b2000000-0000-4000-8000-000000000001', 'US', 'US'),
    ('c3000000-0000-4000-8000-000000000003', 'VLS-FWD',  'b2000000-0000-4000-8000-000000000004', 'US', 'US')
ON CONFLICT DO NOTHING;

-- ---------------------------------------------------------------------------
-- Weapon Mounts (CONFIDENTIAL)
-- ---------------------------------------------------------------------------
INSERT INTO weapon_mount (id, weapon_designation, mount_id, operator_country, owner_country, notes)
VALUES
    ('d4000000-0000-4000-8000-000000000001', 'Phalanx CIWS Block 1B', 'c3000000-0000-4000-8000-000000000001', 'US', 'US', 'Forward CIWS position'),
    ('d4000000-0000-4000-8000-000000000002', 'Phalanx CIWS Block 1B', 'c3000000-0000-4000-8000-000000000002', 'US', 'US', 'Aft CIWS position'),
    ('d4000000-0000-4000-8000-000000000003', 'Mk 41 VLS (SM-2)',      'c3000000-0000-4000-8000-000000000003', 'US', 'US', 'Forward VLS battery')
ON CONFLICT DO NOTHING;

-- ---------------------------------------------------------------------------
-- RWR Systems (CONFIDENTIAL)
-- NOTE: Emitter IDs and system details are FICTITIOUS for testing only.
-- ---------------------------------------------------------------------------
INSERT INTO rwr_system (id, model_name, sensitivity_range, exclusion_emitter_ids, notes)
VALUES
    (
        'e5000000-0000-4000-8000-000000000001',
        'AN/ALQ-214 IDECM',
        '0.5-18 GHz',
        ARRAY['EMITTER-ALPHA-001', 'EMITTER-BRAVO-042'],
        'FICTITIOUS TEST DATA'
    ),
    (
        'e5000000-0000-4000-8000-000000000002',
        'UAT Mk 9 (Type 45)',
        '2-18 GHz',
        ARRAY['EMITTER-DELTA-007'],
        'FICTITIOUS TEST DATA'
    )
ON CONFLICT (model_name) DO NOTHING;

-- ---------------------------------------------------------------------------
-- Platform RWR Associations (CONFIDENTIAL)
-- Links platforms to the RWR system(s) they carry.
-- USS Nimitz carries AN/ALQ-214 IDECM.
-- USS Arleigh Burke carries AN/ALQ-214 IDECM (same model, different platform).
-- HMS Daring carries UAT Mk 9.
-- USS Gerald R. Ford has no RWR system recorded (zero case -- valid).
-- ---------------------------------------------------------------------------
INSERT INTO platform_rwr (id, platform_id, rwr_system_id)
VALUES
    (
        'g7000000-0000-4000-8000-000000000001',
        'b2000000-0000-4000-8000-000000000001',   -- USS Nimitz
        'e5000000-0000-4000-8000-000000000001'    -- AN/ALQ-214 IDECM
    ),
    (
        'g7000000-0000-4000-8000-000000000002',
        'b2000000-0000-4000-8000-000000000003',   -- HMS Daring
        'e5000000-0000-4000-8000-000000000002'    -- UAT Mk 9
    ),
    (
        'g7000000-0000-4000-8000-000000000003',
        'b2000000-0000-4000-8000-000000000004',   -- USS Arleigh Burke
        'e5000000-0000-4000-8000-000000000001'    -- AN/ALQ-214 IDECM (same model as Nimitz)
    )
ON CONFLICT ON CONSTRAINT uq_platform_rwr DO NOTHING;

-- ---------------------------------------------------------------------------
-- Geolocation Log (RESTRICTED) -- fictitious positions
-- ---------------------------------------------------------------------------
INSERT INTO geolocation_log (id, platform_id, coordinates, timestamp_utc)
VALUES
    (
        'f6000000-0000-4000-8000-000000000001',
        'b2000000-0000-4000-8000-000000000001',
        ST_GeogFromText('POINT(-118.2437 33.9416)'),
        '2026-03-25 08:00:00+00'
    ),
    (
        'f6000000-0000-4000-8000-000000000002',
        'b2000000-0000-4000-8000-000000000003',
        ST_GeogFromText('POINT(-1.0980 50.7984)'),
        '2026-03-25 08:00:00+00'
    )
ON CONFLICT DO NOTHING;
