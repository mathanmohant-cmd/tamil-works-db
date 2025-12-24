-- Check current collection mappings to debug mixed-up collections

-- Show all works in பதினெண்கீழ்க்கணக்கு
SELECT
    c.collection_name_tamil,
    w.work_name_tamil,
    w.work_id,
    wc.position_in_collection
FROM work_collections wc
JOIN collections c ON wc.collection_id = c.collection_id
JOIN works w ON wc.work_id = w.work_id
WHERE c.collection_name_tamil = 'பதினெண்கீழ்க்கணக்கு'
ORDER BY wc.position_in_collection;

-- Show all works in ஐம்பெருங்காப்பியங்கள்
SELECT
    c.collection_name_tamil,
    w.work_name_tamil,
    w.work_id,
    wc.position_in_collection
FROM work_collections wc
JOIN collections c ON wc.collection_id = c.collection_id
JOIN works w ON wc.work_id = w.work_id
WHERE c.collection_name_tamil = 'ஐம்பெருங்காப்பியங்கள்'
ORDER BY wc.position_in_collection;

-- Show ALL collection mappings with work names
SELECT
    c.collection_id,
    c.collection_name_tamil,
    c.collection_name,
    w.work_id,
    w.work_name_tamil,
    w.work_name,
    wc.position_in_collection
FROM work_collections wc
JOIN collections c ON wc.collection_id = c.collection_id
JOIN works w ON wc.work_id = w.work_id
ORDER BY c.collection_id, wc.position_in_collection;
