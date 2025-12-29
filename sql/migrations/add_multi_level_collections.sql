-- ============================================================================
-- Migration: Add Multi-Level Collections Support
-- ============================================================================
-- This migration adds support for section-level and verse-level collections
-- in addition to the existing work-level collections.
--
-- Changes:
-- 1. Add entity_type column to collections table
-- 2. Create section_collections junction table
-- 3. Create verse_collections junction table
-- 4. Add indexes for new tables
-- 5. Update views to support multi-level collections
--
-- Run this on existing databases to add multi-level collection support.
-- Safe to run multiple times (uses IF NOT EXISTS checks).
-- ============================================================================

-- Step 1: Add entity_type column to collections table (if not exists)
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'collections' AND column_name = 'entity_type'
    ) THEN
        ALTER TABLE collections
        ADD COLUMN entity_type VARCHAR(20) DEFAULT 'work';

        RAISE NOTICE 'Added entity_type column to collections table';
    ELSE
        RAISE NOTICE 'entity_type column already exists in collections table';
    END IF;
END $$;

-- Step 2: Create section_collections table (if not exists)
CREATE TABLE IF NOT EXISTS section_collections (
    section_collection_id SERIAL PRIMARY KEY,
    section_id INTEGER NOT NULL,
    collection_id INTEGER NOT NULL,
    position_in_collection INTEGER,
    notes TEXT,
    FOREIGN KEY (section_id) REFERENCES sections(section_id) ON DELETE CASCADE,
    FOREIGN KEY (collection_id) REFERENCES collections(collection_id) ON DELETE CASCADE,
    UNIQUE (section_id, collection_id)
);

-- Step 3: Create verse_collections table (if not exists)
CREATE TABLE IF NOT EXISTS verse_collections (
    verse_collection_id SERIAL PRIMARY KEY,
    verse_id INTEGER NOT NULL,
    collection_id INTEGER NOT NULL,
    position_in_collection INTEGER,
    notes TEXT,
    FOREIGN KEY (verse_id) REFERENCES verses(verse_id) ON DELETE CASCADE,
    FOREIGN KEY (collection_id) REFERENCES collections(collection_id) ON DELETE CASCADE,
    UNIQUE (verse_id, collection_id)
);

-- Step 4: Create indexes (if not exists)
CREATE INDEX IF NOT EXISTS idx_collections_entity_type ON collections(entity_type);
CREATE INDEX IF NOT EXISTS idx_section_collections_section ON section_collections(section_id);
CREATE INDEX IF NOT EXISTS idx_section_collections_collection ON section_collections(collection_id);
CREATE INDEX IF NOT EXISTS idx_verse_collections_verse ON verse_collections(verse_id);
CREATE INDEX IF NOT EXISTS idx_verse_collections_collection ON verse_collections(collection_id);

-- Step 5: Drop and recreate views to include multi-level collection support

-- Drop existing views
DROP VIEW IF EXISTS collection_hierarchy CASCADE;
DROP VIEW IF EXISTS sections_in_collections CASCADE;
DROP VIEW IF EXISTS verses_in_collections CASCADE;

-- Recreate collection_hierarchy view with item counts for all entity types
CREATE VIEW collection_hierarchy AS
WITH RECURSIVE coll_tree AS (
    -- Base case: top-level collections
    SELECT
        c.collection_id,
        c.collection_name,
        c.collection_name_tamil,
        c.collection_type,
        c.entity_type,
        c.parent_collection_id,
        c.sort_order,
        0 AS depth,
        ARRAY[c.collection_id] AS path,
        c.collection_name::TEXT AS full_path
    FROM collections c
    WHERE c.parent_collection_id IS NULL

    UNION ALL

    -- Recursive case: child collections
    SELECT
        c.collection_id,
        c.collection_name,
        c.collection_name_tamil,
        c.collection_type,
        c.entity_type,
        c.parent_collection_id,
        c.sort_order,
        ct.depth + 1,
        ct.path || c.collection_id,
        ct.full_path || ' > ' || c.collection_name
    FROM collections c
    JOIN coll_tree ct ON c.parent_collection_id = ct.collection_id
)
SELECT
    ct.*,
    COUNT(DISTINCT wc.work_id) AS work_count,
    COUNT(DISTINCT sc.section_id) AS section_count,
    COUNT(DISTINCT vc.verse_id) AS verse_count
FROM coll_tree ct
LEFT JOIN work_collections wc ON ct.collection_id = wc.collection_id
LEFT JOIN section_collections sc ON ct.collection_id = sc.collection_id
LEFT JOIN verse_collections vc ON ct.collection_id = vc.collection_id
GROUP BY ct.collection_id, ct.collection_name, ct.collection_name_tamil,
         ct.collection_type, ct.entity_type, ct.parent_collection_id, ct.sort_order,
         ct.depth, ct.path, ct.full_path
ORDER BY ct.path;

-- Create sections_in_collections view
CREATE VIEW sections_in_collections AS
SELECT
    s.section_id,
    s.work_id,
    s.section_name,
    s.section_name_tamil,
    s.level_type,
    s.level_type_tamil,
    c.collection_id,
    c.collection_name,
    c.collection_name_tamil,
    c.collection_type,
    sc.position_in_collection,
    sc.notes,
    pc.collection_name AS parent_collection_name,
    pc.collection_name_tamil AS parent_collection_name_tamil
FROM sections s
JOIN section_collections sc ON s.section_id = sc.section_id
JOIN collections c ON sc.collection_id = c.collection_id
LEFT JOIN collections pc ON c.parent_collection_id = pc.collection_id
ORDER BY c.collection_id, sc.position_in_collection;

-- Create verses_in_collections view
CREATE VIEW verses_in_collections AS
SELECT
    v.verse_id,
    v.work_id,
    v.verse_number,
    v.verse_type,
    v.verse_type_tamil,
    c.collection_id,
    c.collection_name,
    c.collection_name_tamil,
    c.collection_type,
    vc.position_in_collection,
    vc.notes,
    pc.collection_name AS parent_collection_name,
    pc.collection_name_tamil AS parent_collection_name_tamil
FROM verses v
JOIN verse_collections vc ON v.verse_id = vc.verse_id
JOIN collections c ON vc.collection_id = c.collection_id
LEFT JOIN collections pc ON c.parent_collection_id = pc.collection_id
ORDER BY c.collection_id, vc.position_in_collection;

-- Success message
DO $$
BEGIN
    RAISE NOTICE '============================================================================';
    RAISE NOTICE 'Migration completed successfully!';
    RAISE NOTICE 'Multi-level collections support has been added to the database.';
    RAISE NOTICE '';
    RAISE NOTICE 'New features:';
    RAISE NOTICE '  - Collections can now contain works, sections, or verses';
    RAISE NOTICE '  - Section-level collections (e.g., all Kurinji sections)';
    RAISE NOTICE '  - Verse-level collections (e.g., all verses by a specific author)';
    RAISE NOTICE '  - Updated views: collection_hierarchy, sections_in_collections, verses_in_collections';
    RAISE NOTICE '';
    RAISE NOTICE 'Backend search API now uses hierarchical sorting by default.';
    RAISE NOTICE '============================================================================';
END $$;
