-- ============================================================================
-- Thirumurai & Devaram Collection Setup
-- ============================================================================
-- This script creates collections to represent:
-- 1. Original authorial works (Sambandar, Appar, Sundarar)
-- 2. Traditional collections (Devaram, Thirumurai)
--
-- Background:
-- - Sambandar's "Thirukkappu" was split into Thirumurai 1-3
-- - Appar's "Devaram" was split into Thirumurai 4-6
-- - Sundarar's "Thirupattu" became Thirumurai 7
-- - "Devaram" now refers to all 7 Thirumurai collectively
-- - "Thirumurai" is the complete collection of 12 Thirumurai
-- ============================================================================

BEGIN;

-- ============================================================================
-- 1. AUTHOR-BASED COLLECTIONS (Original Authorial Works)
-- ============================================================================

-- Sambandar's original work: Thirukkappu (split into Thirumurai 1-3)
INSERT INTO collections (collection_name, collection_name_tamil, collection_type, description, sort_order)
VALUES (
    'Sambandar Devaram (Thirukkappu)',
    'சம்பந்தர் தேவாரம் (திருக்கப்பு)',
    'author',
    'Original work by Thirugnanasambanthar, split into first three Thirumurai (1-3)',
    321
) ON CONFLICT (collection_name) DO NOTHING;

-- Appar's original work: Devaram (split into Thirumurai 4-6)
INSERT INTO collections (collection_name, collection_name_tamil, collection_type, description, sort_order)
VALUES (
    'Appar Devaram',
    'அப்பர் தேவாரம்',
    'author',
    'Original work by Thirunavukkarasar (Appar), split into Thirumurai 4-6',
    322
) ON CONFLICT (collection_name) DO NOTHING;

-- Sundarar's original work: Thirupattu (Thirumurai 7)
INSERT INTO collections (collection_name, collection_name_tamil, collection_type, description, sort_order)
VALUES (
    'Sundarar Devaram (Thirupattu)',
    'சுந்தரர் தேவாரம் (திருப்பாட்டு)',
    'author',
    'Original work by Sundarar, forms the seventh Thirumurai',
    323
) ON CONFLICT (collection_name) DO NOTHING;

-- ============================================================================
-- 2. TRADITIONAL COLLECTIONS
-- ============================================================================

-- Devaram: First 7 Thirumurai (by Sambandar, Appar, Sundarar)
INSERT INTO collections (collection_name, collection_name_tamil, collection_type, description, sort_order)
VALUES (
    'Devaram',
    'தேவாரம்',
    'tradition',
    'First seven Thirumurai by the three great Nayanmars (Sambandar, Appar, Sundarar)',
    320
) ON CONFLICT (collection_name) DO NOTHING;

-- Thirumurai: Complete collection of 12 Shaivite devotional works
INSERT INTO collections (collection_name, collection_name_tamil, collection_type, description, sort_order)
VALUES (
    'Thirumurai',
    'திருமுறை',
    'tradition',
    'Complete collection of twelve Shaivite devotional works',
    300
) ON CONFLICT (collection_name) DO NOTHING;

-- ============================================================================
-- 3. ASSIGN WORKS TO COLLECTIONS
-- ============================================================================

-- Helper: Get collection IDs
DO $$
DECLARE
    sambandar_collection_id INTEGER;
    appar_collection_id INTEGER;
    sundarar_collection_id INTEGER;
    devaram_collection_id INTEGER;
    thirumurai_collection_id INTEGER;
BEGIN
    -- Get collection IDs
    SELECT collection_id INTO sambandar_collection_id FROM collections WHERE collection_name = 'Sambandar Devaram (Thirukkappu)';
    SELECT collection_id INTO appar_collection_id FROM collections WHERE collection_name = 'Appar Devaram';
    SELECT collection_id INTO sundarar_collection_id FROM collections WHERE collection_name = 'Sundarar Devaram (Thirupattu)';
    SELECT collection_id INTO devaram_collection_id FROM collections WHERE collection_name = 'Devaram';
    SELECT collection_id INTO thirumurai_collection_id FROM collections WHERE collection_name = 'Thirumurai';

    -- ========================================================================
    -- Sambandar's works (Thirumurai 1-3)
    -- ========================================================================
    -- Assign to Sambandar collection
    INSERT INTO work_collections (work_id, collection_id, position_in_collection, is_primary, notes)
    SELECT
        work_id,
        sambandar_collection_id,
        work_id - 43,  -- Position 1, 2, 3
        FALSE,
        'Part ' || (work_id - 43) || ' of original Thirukkappu'
    FROM works
    WHERE work_id IN (44, 45, 46)
    ON CONFLICT (work_id, collection_id) DO UPDATE
        SET position_in_collection = EXCLUDED.position_in_collection;

    -- Assign to Devaram collection
    INSERT INTO work_collections (work_id, collection_id, position_in_collection, is_primary, notes)
    SELECT
        work_id,
        devaram_collection_id,
        work_id - 43,  -- Position 1, 2, 3
        FALSE,
        'By Sambandar'
    FROM works
    WHERE work_id IN (44, 45, 46)
    ON CONFLICT (work_id, collection_id) DO UPDATE
        SET position_in_collection = EXCLUDED.position_in_collection;

    -- Assign to Thirumurai collection
    INSERT INTO work_collections (work_id, collection_id, position_in_collection, is_primary, notes)
    SELECT
        work_id,
        thirumurai_collection_id,
        work_id - 43,  -- Position 1, 2, 3
        TRUE,  -- Primary collection
        'முதலாம், இரண்டாம், மூன்றாம் திருமுறை'
    FROM works
    WHERE work_id IN (44, 45, 46)
    ON CONFLICT (work_id, collection_id) DO UPDATE
        SET position_in_collection = EXCLUDED.position_in_collection,
            is_primary = EXCLUDED.is_primary;

    -- ========================================================================
    -- Appar's works (Thirumurai 4-6)
    -- ========================================================================
    -- Assign to Appar collection
    INSERT INTO work_collections (work_id, collection_id, position_in_collection, is_primary, notes)
    SELECT
        work_id,
        appar_collection_id,
        work_id - 46,  -- Position 1, 2, 3
        FALSE,
        'Part ' || (work_id - 46) || ' of original Devaram'
    FROM works
    WHERE work_id IN (47, 48, 49)
    ON CONFLICT (work_id, collection_id) DO UPDATE
        SET position_in_collection = EXCLUDED.position_in_collection;

    -- Assign to Devaram collection
    INSERT INTO work_collections (work_id, collection_id, position_in_collection, is_primary, notes)
    SELECT
        work_id,
        devaram_collection_id,
        work_id - 43,  -- Position 4, 5, 6
        FALSE,
        'By Appar'
    FROM works
    WHERE work_id IN (47, 48, 49)
    ON CONFLICT (work_id, collection_id) DO UPDATE
        SET position_in_collection = EXCLUDED.position_in_collection;

    -- Assign to Thirumurai collection
    INSERT INTO work_collections (work_id, collection_id, position_in_collection, is_primary, notes)
    SELECT
        work_id,
        thirumurai_collection_id,
        work_id - 43,  -- Position 4, 5, 6
        TRUE,  -- Primary collection
        'நான்காம், ஐந்தாம், ஆறாம் திருமுறை'
    FROM works
    WHERE work_id IN (47, 48, 49)
    ON CONFLICT (work_id, collection_id) DO UPDATE
        SET position_in_collection = EXCLUDED.position_in_collection,
            is_primary = EXCLUDED.is_primary;

    -- ========================================================================
    -- Sundarar's work (Thirumurai 7)
    -- ========================================================================
    -- Assign to Sundarar collection
    INSERT INTO work_collections (work_id, collection_id, position_in_collection, is_primary, notes)
    VALUES (
        50,
        sundarar_collection_id,
        1,
        FALSE,
        'Original Thirupattu (single work, not split)'
    )
    ON CONFLICT (work_id, collection_id) DO UPDATE
        SET position_in_collection = EXCLUDED.position_in_collection;

    -- Assign to Devaram collection
    INSERT INTO work_collections (work_id, collection_id, position_in_collection, is_primary, notes)
    VALUES (
        50,
        devaram_collection_id,
        7,
        FALSE,
        'By Sundarar'
    )
    ON CONFLICT (work_id, collection_id) DO UPDATE
        SET position_in_collection = EXCLUDED.position_in_collection;

    -- Assign to Thirumurai collection
    INSERT INTO work_collections (work_id, collection_id, position_in_collection, is_primary, notes)
    VALUES (
        50,
        thirumurai_collection_id,
        7,
        TRUE,  -- Primary collection
        'ஏழாம் திருமுறை'
    )
    ON CONFLICT (work_id, collection_id) DO UPDATE
        SET position_in_collection = EXCLUDED.position_in_collection,
            is_primary = EXCLUDED.is_primary;

    -- ========================================================================
    -- Remaining Thirumurai (8-12) - Add to Thirumurai collection
    -- ========================================================================
    -- You can add the remaining Thirumurai works here when ready
    -- work_id 51-78 depending on your data

    RAISE NOTICE 'Collections created and works assigned successfully!';
END $$;

COMMIT;

-- ============================================================================
-- VERIFICATION
-- ============================================================================

-- View collections created
SELECT
    collection_id,
    collection_name,
    collection_name_tamil,
    collection_type,
    description
FROM collections
WHERE collection_name LIKE '%Devaram%' OR collection_name = 'Thirumurai'
ORDER BY sort_order;

-- View work assignments
SELECT
    w.work_id,
    w.work_name_tamil,
    c.collection_name,
    wc.position_in_collection,
    wc.is_primary,
    wc.notes
FROM work_collections wc
JOIN works w ON wc.work_id = w.work_id
JOIN collections c ON wc.collection_id = c.collection_id
WHERE c.collection_name LIKE '%Devaram%' OR c.collection_name = 'Thirumurai'
ORDER BY c.sort_order, wc.position_in_collection;
