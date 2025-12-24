-- Verify what's in Railway database after import

-- Check if collections exist
SELECT 'Collections count:' as check_type, COUNT(*) as count FROM collections;

-- Check if work_collections exist
SELECT 'Work-collection mappings count:' as check_type, COUNT(*) as count FROM work_collections;

-- Check if works exist (should not have been affected)
SELECT 'Works count:' as check_type, COUNT(*) as count FROM works;

-- Show all collections
SELECT collection_id, collection_name_tamil, parent_collection_id
FROM collections
ORDER BY collection_id;

-- Show sample work_collections
SELECT * FROM work_collections LIMIT 10;

-- Check for any constraint violations or issues
SELECT
    wc.work_collection_id,
    wc.work_id,
    wc.collection_id,
    w.work_name_tamil,
    c.collection_name_tamil
FROM work_collections wc
LEFT JOIN works w ON wc.work_id = w.work_id
LEFT JOIN collections c ON wc.collection_id = c.collection_id
LIMIT 10;
