-- ============================================================================
-- Migration: Add Collections System
-- Date: 2025-12-18
-- Description: Adds collections tables and relationships for organizing works
-- ============================================================================

BEGIN;

-- ============================================================================
-- STEP 1: Create Collections Tables
-- ============================================================================

-- Collections table (literary periods, traditions, genres, canons)
CREATE TABLE IF NOT EXISTS collections (
    collection_id INTEGER PRIMARY KEY,
    collection_name VARCHAR(100) NOT NULL UNIQUE,
    collection_name_tamil VARCHAR(100),
    collection_type VARCHAR(50) NOT NULL,  -- 'period', 'tradition', 'genre', 'canon', 'custom'
    description TEXT,
    parent_collection_id INTEGER,  -- For hierarchical collections
    sort_order INTEGER,  -- For ordering collections themselves
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Add foreign key constraint for parent collections (self-reference)
ALTER TABLE collections
    ADD CONSTRAINT fk_collections_parent
    FOREIGN KEY (parent_collection_id) REFERENCES collections(collection_id);

-- Junction table: Works can belong to multiple collections
CREATE TABLE IF NOT EXISTS work_collections (
    work_collection_id SERIAL PRIMARY KEY,
    work_id INTEGER NOT NULL,
    collection_id INTEGER NOT NULL,
    position_in_collection INTEGER,  -- Order within this specific collection
    is_primary BOOLEAN DEFAULT FALSE,  -- Mark primary collection for each work
    notes TEXT,  -- Collection-specific notes about this work
    FOREIGN KEY (work_id) REFERENCES works(work_id) ON DELETE CASCADE,
    FOREIGN KEY (collection_id) REFERENCES collections(collection_id) ON DELETE CASCADE,
    UNIQUE (work_id, collection_id),
    UNIQUE (collection_id, position_in_collection)
);

-- Add primary_collection_id to works table
ALTER TABLE works
    ADD COLUMN IF NOT EXISTS primary_collection_id INTEGER;

ALTER TABLE works
    ADD CONSTRAINT fk_works_primary_collection
    FOREIGN KEY (primary_collection_id) REFERENCES collections(collection_id);

-- ============================================================================
-- STEP 2: Create Indexes
-- ============================================================================

CREATE INDEX IF NOT EXISTS idx_collections_type ON collections(collection_type);
CREATE INDEX IF NOT EXISTS idx_collections_parent ON collections(parent_collection_id);
CREATE INDEX IF NOT EXISTS idx_works_primary_collection ON works(primary_collection_id);
CREATE INDEX IF NOT EXISTS idx_work_collections_work ON work_collections(work_id);
CREATE INDEX IF NOT EXISTS idx_work_collections_collection ON work_collections(collection_id);

-- ============================================================================
-- STEP 3: Create Views
-- ============================================================================

-- Drop views if they exist (for clean migration)
DROP VIEW IF EXISTS works_in_collections CASCADE;
DROP VIEW IF EXISTS collection_hierarchy CASCADE;
DROP VIEW IF EXISTS works_with_primary_collection CASCADE;

-- View: Works with their primary collection
CREATE VIEW works_with_primary_collection AS
SELECT
    w.*,
    c.collection_name,
    c.collection_name_tamil,
    c.collection_type,
    wc.position_in_collection,
    wc.notes AS collection_notes
FROM works w
LEFT JOIN work_collections wc ON w.work_id = wc.work_id AND wc.is_primary = TRUE
LEFT JOIN collections c ON wc.collection_id = c.collection_id;

-- View: Collection hierarchy with work counts
CREATE VIEW collection_hierarchy AS
WITH RECURSIVE coll_tree AS (
    -- Base case: top-level collections
    SELECT
        c.collection_id,
        c.collection_name,
        c.collection_name_tamil,
        c.collection_type,
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
    COUNT(DISTINCT wc.work_id) AS work_count
FROM coll_tree ct
LEFT JOIN work_collections wc ON ct.collection_id = wc.collection_id
GROUP BY ct.collection_id, ct.collection_name, ct.collection_name_tamil,
         ct.collection_type, ct.parent_collection_id, ct.sort_order,
         ct.depth, ct.path, ct.full_path
ORDER BY ct.path;

-- View: Works in collections with hierarchy
CREATE VIEW works_in_collections AS
SELECT
    w.work_id,
    w.work_name,
    w.work_name_tamil,
    c.collection_id,
    c.collection_name,
    c.collection_name_tamil,
    c.collection_type,
    wc.position_in_collection,
    wc.is_primary,
    pc.collection_name AS parent_collection_name,
    pc.collection_name_tamil AS parent_collection_name_tamil
FROM works w
JOIN work_collections wc ON w.work_id = wc.work_id
JOIN collections c ON wc.collection_id = c.collection_id
LEFT JOIN collections pc ON c.parent_collection_id = pc.collection_id
ORDER BY c.collection_id, wc.position_in_collection;

-- ============================================================================
-- STEP 4: Migrate Existing traditional_sort_order Data
-- ============================================================================

-- Create Traditional Canon collection if seeded
-- This will be populated by seed_collections.sql

-- Migrate existing traditional_sort_order to Traditional Canon collection (ID=100)
-- Only if Traditional Canon collection exists and works have traditional_sort_order
INSERT INTO work_collections (work_id, collection_id, position_in_collection, is_primary)
SELECT
    work_id,
    100 AS collection_id,  -- Traditional Canon
    traditional_sort_order AS position_in_collection,
    FALSE AS is_primary
FROM works
WHERE traditional_sort_order IS NOT NULL
  AND EXISTS (SELECT 1 FROM collections WHERE collection_id = 100)
ON CONFLICT (work_id, collection_id) DO NOTHING;

-- ============================================================================
-- STEP 5: Add Comments for Documentation
-- ============================================================================

COMMENT ON TABLE collections IS 'Literary collections: periods, traditions, genres, and canons';
COMMENT ON TABLE work_collections IS 'Many-to-many junction table linking works to collections';
COMMENT ON COLUMN collections.collection_type IS 'Type: period, tradition, genre, canon, or custom';
COMMENT ON COLUMN collections.parent_collection_id IS 'Parent collection ID for hierarchical organization';
COMMENT ON COLUMN work_collections.is_primary IS 'Marks the primary collection for each work';
COMMENT ON COLUMN work_collections.position_in_collection IS 'Sort order within the collection';
COMMENT ON COLUMN works.primary_collection_id IS 'Primary collection this work belongs to';

-- ============================================================================
-- VERIFICATION
-- ============================================================================

-- Verify tables were created
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'collections') THEN
        RAISE EXCEPTION 'Migration failed: collections table not created';
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'work_collections') THEN
        RAISE EXCEPTION 'Migration failed: work_collections table not created';
    END IF;

    RAISE NOTICE 'Collections system migration completed successfully';
END $$;

-- Display migration summary
SELECT
    'Collections table' AS item,
    COUNT(*) AS count
FROM collections
UNION ALL
SELECT
    'Work-collection relationships',
    COUNT(*)
FROM work_collections
UNION ALL
SELECT
    'Works with primary collection',
    COUNT(*)
FROM works
WHERE primary_collection_id IS NOT NULL;

COMMIT;

-- ============================================================================
-- POST-MIGRATION STEPS
-- ============================================================================
--
-- After running this migration, you should:
--
-- 1. Load collection seed data:
--    psql $DATABASE_URL -f sql/seed_collections.sql
--
-- 2. Load work-collection relationships:
--    psql $DATABASE_URL -f sql/seed_work_collections.sql
--
-- 3. Verify the migration:
--    SELECT * FROM collection_hierarchy;
--    SELECT * FROM works_with_primary_collection;
--
-- ============================================================================
