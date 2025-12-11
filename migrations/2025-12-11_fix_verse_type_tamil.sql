-- Migration: Fix verse_type_tamil display
-- Date: 2025-12-11
-- Description: Update word_details view to get verse_type_tamil from verse_hierarchy
--              and fix Kambaramayanam verse types

-- Step 1: Update word_details view to use verse_hierarchy for verse_type fields
DROP VIEW IF EXISTS word_details CASCADE;

CREATE VIEW word_details AS
SELECT
    w.word_id,
    w.word_text,
    w.word_text_transliteration,
    w.word_root,
    w.word_type,
    w.word_position,
    w.sandhi_split,
    w.meaning,
    l.line_id,
    l.line_number,
    l.line_text,
    v.verse_id,
    v.verse_number,
    vh.verse_type,           -- Changed from v.verse_type
    vh.verse_type_tamil,     -- Changed from v.verse_type_tamil
    vh.work_name,
    vh.work_name_tamil,
    vh.hierarchy_path,
    vh.hierarchy_path_tamil
FROM words w
INNER JOIN lines l ON w.line_id = l.line_id
INNER JOIN verses v ON l.verse_id = v.verse_id
INNER JOIN verse_hierarchy vh ON v.verse_id = vh.verse_id;

-- Step 2: Fix Kambaramayanam verse types (if data exists)
UPDATE verses
SET verse_type = 'verse',
    verse_type_tamil = 'பாடல்'
WHERE work_id IN (SELECT work_id FROM works WHERE work_name = 'Kambaramayanam')
  AND (verse_type_tamil IS NULL OR verse_type_tamil = '' OR verse_type_tamil != 'பாடல்');

-- Verification queries
-- Check that verse_type_tamil is now available in word_details
SELECT 'Verification: word_details view columns' AS check_name;
SELECT column_name
FROM information_schema.columns
WHERE table_name = 'word_details'
  AND column_name LIKE '%verse_type%'
ORDER BY ordinal_position;

-- Check sample data
SELECT 'Verification: Sample verse types from each work' AS check_name;
SELECT DISTINCT
    w.work_name,
    v.verse_type,
    v.verse_type_tamil
FROM verses v
JOIN works w ON v.work_id = w.work_id
ORDER BY w.work_name
LIMIT 10;
