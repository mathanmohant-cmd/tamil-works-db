-- Safe collection import - check first, then update
-- This won't delete existing data, just shows what would be imported

BEGIN;

-- Show current state
SELECT 'Current collections:' as info, COUNT(*) FROM collections;
SELECT 'Current work_collections:' as info, COUNT(*) FROM work_collections;

-- Don't commit, just show what we would do
ROLLBACK;

-- To actually import:
-- 1. Verify the above counts match expectations
-- 2. Change ROLLBACK to COMMIT
-- 3. Then run the full collections_export.sql
