-- Collection Tree Export
-- Generated: 2025-12-24T03:15:05.544678
-- Source: postgresql://postgres:postgres@localhost:5432/tamil_literature
-- 
-- Instructions:
-- 1. Connect to your Railway database
-- 2. Run this SQL file: psql $DATABASE_URL -f collections_export.sql
-- 

-- Clear existing collection data
DELETE FROM work_collections;
DELETE FROM collections;

-- Reset sequences (only work_collections has SERIAL, collections uses INTEGER)
-- collections table uses INTEGER PRIMARY KEY, not SERIAL, so no sequence
DO $$ BEGIN
  IF EXISTS (SELECT 1 FROM pg_class WHERE relname = 'work_collections_work_collection_id_seq') THEN
    PERFORM setval('work_collections_work_collection_id_seq', 1, false);
  END IF;
END $$;

-- Insert collections
INSERT INTO collections (collection_id, collection_name, collection_name_tamil, collection_type, description, parent_collection_id, sort_order, created_at)
VALUES (7, 'Collection for Search Filter', 'தமிழ் இலக்கியம் ', 'custom', '', NULL, NULL, '2025-12-21 13:17:20.668343');
INSERT INTO collections (collection_id, collection_name, collection_name_tamil, collection_type, description, parent_collection_id, sort_order, created_at)
VALUES (3, 'Sanga Ilakkiyam', 'சங்க இலக்கியம்', 'tradition', '', 7, 0, '2025-12-21 12:58:27.402602');
INSERT INTO collections (collection_id, collection_name, collection_name_tamil, collection_type, description, parent_collection_id, sort_order, created_at)
VALUES (8, 'காப்பியங்கள்', 'காப்பியங்கள்', 'tradition', '', 7, 0, '2025-12-21 13:19:03.730279');
INSERT INTO collections (collection_id, collection_name, collection_name_tamil, collection_type, description, parent_collection_id, sort_order, created_at)
VALUES (6, 'இலக்கண நூல்கள்', 'இலக்கண நூல்கள்', 'custom', '', 7, NULL, '2025-12-21 13:16:22.465048');
INSERT INTO collections (collection_id, collection_name, collection_name_tamil, collection_type, description, parent_collection_id, sort_order, created_at)
VALUES (4, 'பதினெண்மேற்கணக்கு', 'பதினெண்மேற்கணக்கு', 'tradition', '', 3, 1, '2025-12-21 13:07:41.108945');
INSERT INTO collections (collection_id, collection_name, collection_name_tamil, collection_type, description, parent_collection_id, sort_order, created_at)
VALUES (5, 'பதினெண்கீழ்க்கணக்கு', 'பதினெண்கீழ்க்கணக்கு', 'tradition', '', 3, 2, '2025-12-21 13:08:48.012271');
INSERT INTO collections (collection_id, collection_name, collection_name_tamil, collection_type, description, parent_collection_id, sort_order, created_at)
VALUES (9, 'ஐம்பெருங்காப்பியங்கள்', 'ஐம்பெருங்காப்பியங்கள்', 'tradition', '', 8, NULL, '2025-12-21 13:19:55.650729');
INSERT INTO collections (collection_id, collection_name, collection_name_tamil, collection_type, description, parent_collection_id, sort_order, created_at)
VALUES (1, 'Ettuthogai', 'எட்டுத்தொகை ', 'custom', '', 4, NULL, '2025-12-21 12:52:40.920481');
INSERT INTO collections (collection_id, collection_name, collection_name_tamil, collection_type, description, parent_collection_id, sort_order, created_at)
VALUES (2, 'Patthupattu', 'பாத்துப்பாட்டு', 'custom', '', 4, NULL, '2025-12-21 12:56:25.393182');

-- Insert work-collection mappings
INSERT INTO work_collections (work_collection_id, work_id, collection_id, position_in_collection, is_primary, notes)
VALUES (1, 2, 1, 1, FALSE, NULL);
INSERT INTO work_collections (work_collection_id, work_id, collection_id, position_in_collection, is_primary, notes)
VALUES (4, 3, 1, 2, FALSE, NULL);
INSERT INTO work_collections (work_collection_id, work_id, collection_id, position_in_collection, is_primary, notes)
VALUES (18, 4, 1, 3, FALSE, NULL);
INSERT INTO work_collections (work_collection_id, work_id, collection_id, position_in_collection, is_primary, notes)
VALUES (19, 5, 1, 4, FALSE, NULL);
INSERT INTO work_collections (work_collection_id, work_id, collection_id, position_in_collection, is_primary, notes)
VALUES (20, 6, 1, 5, FALSE, NULL);
INSERT INTO work_collections (work_collection_id, work_id, collection_id, position_in_collection, is_primary, notes)
VALUES (21, 7, 1, 6, FALSE, NULL);
INSERT INTO work_collections (work_collection_id, work_id, collection_id, position_in_collection, is_primary, notes)
VALUES (22, 8, 1, 7, FALSE, NULL);
INSERT INTO work_collections (work_collection_id, work_id, collection_id, position_in_collection, is_primary, notes)
VALUES (23, 9, 1, 8, FALSE, NULL);
INSERT INTO work_collections (work_collection_id, work_id, collection_id, position_in_collection, is_primary, notes)
VALUES (5, 10, 2, 1, FALSE, NULL);
INSERT INTO work_collections (work_collection_id, work_id, collection_id, position_in_collection, is_primary, notes)
VALUES (6, 11, 2, 2, FALSE, NULL);
INSERT INTO work_collections (work_collection_id, work_id, collection_id, position_in_collection, is_primary, notes)
VALUES (7, 12, 2, 3, FALSE, NULL);
INSERT INTO work_collections (work_collection_id, work_id, collection_id, position_in_collection, is_primary, notes)
VALUES (8, 13, 2, 4, FALSE, NULL);
INSERT INTO work_collections (work_collection_id, work_id, collection_id, position_in_collection, is_primary, notes)
VALUES (9, 14, 2, 5, FALSE, NULL);
INSERT INTO work_collections (work_collection_id, work_id, collection_id, position_in_collection, is_primary, notes)
VALUES (10, 15, 2, 6, FALSE, NULL);
INSERT INTO work_collections (work_collection_id, work_id, collection_id, position_in_collection, is_primary, notes)
VALUES (14, 16, 2, 7, FALSE, NULL);
INSERT INTO work_collections (work_collection_id, work_id, collection_id, position_in_collection, is_primary, notes)
VALUES (15, 17, 2, 8, FALSE, NULL);
INSERT INTO work_collections (work_collection_id, work_id, collection_id, position_in_collection, is_primary, notes)
VALUES (16, 18, 2, 9, FALSE, NULL);
INSERT INTO work_collections (work_collection_id, work_id, collection_id, position_in_collection, is_primary, notes)
VALUES (17, 19, 2, 10, FALSE, NULL);
INSERT INTO work_collections (work_collection_id, work_id, collection_id, position_in_collection, is_primary, notes)
VALUES (24, 27, 5, 1, FALSE, NULL);
INSERT INTO work_collections (work_collection_id, work_id, collection_id, position_in_collection, is_primary, notes)
VALUES (25, 28, 5, 2, FALSE, NULL);
INSERT INTO work_collections (work_collection_id, work_id, collection_id, position_in_collection, is_primary, notes)
VALUES (26, 29, 5, 3, FALSE, NULL);
INSERT INTO work_collections (work_collection_id, work_id, collection_id, position_in_collection, is_primary, notes)
VALUES (27, 30, 5, 4, FALSE, NULL);
INSERT INTO work_collections (work_collection_id, work_id, collection_id, position_in_collection, is_primary, notes)
VALUES (28, 32, 5, 5, FALSE, NULL);
INSERT INTO work_collections (work_collection_id, work_id, collection_id, position_in_collection, is_primary, notes)
VALUES (29, 31, 5, 6, FALSE, NULL);
INSERT INTO work_collections (work_collection_id, work_id, collection_id, position_in_collection, is_primary, notes)
VALUES (30, 33, 5, 7, FALSE, NULL);
INSERT INTO work_collections (work_collection_id, work_id, collection_id, position_in_collection, is_primary, notes)
VALUES (31, 36, 5, 8, FALSE, NULL);
INSERT INTO work_collections (work_collection_id, work_id, collection_id, position_in_collection, is_primary, notes)
VALUES (32, 34, 5, 9, FALSE, NULL);
INSERT INTO work_collections (work_collection_id, work_id, collection_id, position_in_collection, is_primary, notes)
VALUES (33, 35, 5, 10, FALSE, NULL);
INSERT INTO work_collections (work_collection_id, work_id, collection_id, position_in_collection, is_primary, notes)
VALUES (34, 20, 5, 11, FALSE, NULL);
INSERT INTO work_collections (work_collection_id, work_id, collection_id, position_in_collection, is_primary, notes)
VALUES (35, 37, 5, 12, FALSE, NULL);
INSERT INTO work_collections (work_collection_id, work_id, collection_id, position_in_collection, is_primary, notes)
VALUES (36, 38, 5, 13, FALSE, NULL);
INSERT INTO work_collections (work_collection_id, work_id, collection_id, position_in_collection, is_primary, notes)
VALUES (37, 39, 5, 14, FALSE, NULL);
INSERT INTO work_collections (work_collection_id, work_id, collection_id, position_in_collection, is_primary, notes)
VALUES (38, 40, 5, 15, FALSE, NULL);
INSERT INTO work_collections (work_collection_id, work_id, collection_id, position_in_collection, is_primary, notes)
VALUES (39, 42, 5, 16, FALSE, NULL);
INSERT INTO work_collections (work_collection_id, work_id, collection_id, position_in_collection, is_primary, notes)
VALUES (40, 41, 5, 17, FALSE, NULL);
INSERT INTO work_collections (work_collection_id, work_id, collection_id, position_in_collection, is_primary, notes)
VALUES (41, 43, 5, 18, FALSE, NULL);
INSERT INTO work_collections (work_collection_id, work_id, collection_id, position_in_collection, is_primary, notes)
VALUES (42, 1, 6, 1, FALSE, NULL);
INSERT INTO work_collections (work_collection_id, work_id, collection_id, position_in_collection, is_primary, notes)
VALUES (43, 22, 8, 1, FALSE, NULL);
INSERT INTO work_collections (work_collection_id, work_id, collection_id, position_in_collection, is_primary, notes)
VALUES (44, 21, 9, 1, FALSE, NULL);
INSERT INTO work_collections (work_collection_id, work_id, collection_id, position_in_collection, is_primary, notes)
VALUES (45, 23, 9, 2, FALSE, NULL);
INSERT INTO work_collections (work_collection_id, work_id, collection_id, position_in_collection, is_primary, notes)
VALUES (46, 24, 9, 3, FALSE, NULL);
INSERT INTO work_collections (work_collection_id, work_id, collection_id, position_in_collection, is_primary, notes)
VALUES (48, 25, 9, 4, FALSE, NULL);
INSERT INTO work_collections (work_collection_id, work_id, collection_id, position_in_collection, is_primary, notes)
VALUES (47, 26, 9, 5, FALSE, NULL);

-- Update work_collections sequence to current max
-- Note: collections table has no sequence (uses INTEGER PRIMARY KEY, not SERIAL)
DO $$ BEGIN
  IF EXISTS (SELECT 1 FROM pg_class WHERE relname = 'work_collections_work_collection_id_seq') THEN
    PERFORM setval('work_collections_work_collection_id_seq', (SELECT COALESCE(MAX(work_collection_id), 0) FROM work_collections));
  END IF;
END $$;

-- Export complete!
