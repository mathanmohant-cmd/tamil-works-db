-- Migration 003: Remove primary_collection_id from works table
-- This field is redundant - use work_collections many-to-many table instead

-- Drop dependent views first (CASCADE will handle any dependencies)
DROP VIEW IF EXISTS works_with_primary_collection CASCADE;

-- Drop the foreign key constraint
ALTER TABLE works DROP CONSTRAINT IF EXISTS fk_works_primary_collection;

-- Drop the index
DROP INDEX IF EXISTS idx_works_primary_collection;

-- Drop the column
ALTER TABLE works DROP COLUMN IF EXISTS primary_collection_id CASCADE;

COMMENT ON TABLE works IS 'Works table - use work_collections for collection relationships';
