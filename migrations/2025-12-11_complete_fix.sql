-- Complete Fix for verse_type_tamil Issue
-- Date: 2025-12-11
-- Purpose: Update NULL verse_type_tamil values and refresh views
--
-- This is a complete, idempotent script that can be run multiple times safely.
-- It updates data and refreshes views in the correct order.

-- ============================================================================
-- STEP 1: Update verse_type and verse_type_tamil for works with NULL values
-- ============================================================================

DO $$
DECLARE
    silapathikaram_id INTEGER;
    kambaramayanam_id INTEGER;
    updated_silap INTEGER;
    updated_kamba INTEGER;
BEGIN
    -- Get work IDs dynamically
    SELECT work_id INTO silapathikaram_id FROM works WHERE work_name = 'Silapathikaram';
    SELECT work_id INTO kambaramayanam_id FROM works WHERE work_name = 'Kambaramayanam';

    -- Update Silapathikaram if work exists and has NULL values
    IF silapathikaram_id IS NOT NULL THEN
        UPDATE verses
        SET verse_type = 'poem',
            verse_type_tamil = 'பாடல்'
        WHERE work_id = silapathikaram_id
          AND verse_type IS NULL;

        GET DIAGNOSTICS updated_silap = ROW_COUNT;
        RAISE NOTICE 'Updated % Silapathikaram verses', updated_silap;
    END IF;

    -- Update Kambaramayanam if work exists and has NULL values
    IF kambaramayanam_id IS NOT NULL THEN
        UPDATE verses
        SET verse_type = 'poem',
            verse_type_tamil = 'பாடல்'
        WHERE work_id = kambaramayanam_id
          AND verse_type IS NULL;

        GET DIAGNOSTICS updated_kamba = ROW_COUNT;
        RAISE NOTICE 'Updated % Kambaramayanam verses', updated_kamba;
    END IF;
END $$;

-- ============================================================================
-- STEP 2: Refresh Views (drop and recreate to pick up data changes)
-- ============================================================================

-- Drop dependent views first
DROP VIEW IF EXISTS word_details CASCADE;
DROP VIEW IF EXISTS verse_hierarchy CASCADE;

-- Recreate verse_hierarchy view
CREATE VIEW verse_hierarchy AS
WITH RECURSIVE section_path AS (
    SELECT
        section_id,
        work_id,
        parent_section_id,
        level_type,
        section_name,
        section_name_tamil,
        section_number,
        sort_order,
        1 as depth,
        section_id::TEXT as path,
        level_type || ':' || section_name as path_names,
        COALESCE(level_type_tamil, level_type) || ':' || COALESCE(section_name_tamil, section_name) as path_names_tamil
    FROM sections
    WHERE parent_section_id IS NULL

    UNION ALL

    SELECT
        s.section_id,
        s.work_id,
        s.parent_section_id,
        s.level_type,
        s.section_name,
        s.section_name_tamil,
        s.section_number,
        s.sort_order,
        sp.depth + 1,
        sp.path || '/' || s.section_id::TEXT,
        sp.path_names || ' > ' || s.level_type || ':' || s.section_name,
        sp.path_names_tamil || ' > ' || COALESCE(s.level_type_tamil, s.level_type) || ':' || COALESCE(s.section_name_tamil, s.section_name)
    FROM sections s
    INNER JOIN section_path sp ON s.parent_section_id = sp.section_id
)
SELECT
    v.verse_id,
    v.verse_number,
    v.verse_type,
    v.verse_type_tamil,
    w.work_name,
    w.work_name_tamil,
    sp.path_names as hierarchy_path,
    sp.path_names_tamil as hierarchy_path_tamil,
    sp.depth as hierarchy_depth
FROM verses v
INNER JOIN works w ON v.work_id = w.work_id
INNER JOIN section_path sp ON v.section_id = sp.section_id;

-- Recreate word_details view
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
    vh.verse_type,
    vh.verse_type_tamil,
    vh.work_name,
    vh.work_name_tamil,
    vh.hierarchy_path,
    vh.hierarchy_path_tamil
FROM words w
INNER JOIN lines l ON w.line_id = l.line_id
INNER JOIN verses v ON l.verse_id = v.verse_id
INNER JOIN verse_hierarchy vh ON v.verse_id = vh.verse_id;

-- ============================================================================
-- STEP 3: Verification
-- ============================================================================

-- Check NULL verse_type_tamil by work
SELECT
    'Verification: verse_type_tamil by work' as info,
    NULL::TEXT as work_name,
    NULL::BIGINT as total_verses,
    NULL::BIGINT as null_count;

SELECT
    NULL::TEXT as info,
    w.work_name,
    COUNT(*) as total_verses,
    COUNT(CASE WHEN v.verse_type_tamil IS NULL THEN 1 END) as null_count
FROM verses v
JOIN works w ON v.work_id = w.work_id
GROUP BY w.work_id, w.work_name
ORDER BY w.work_name;

-- Check views exist and have data
SELECT
    'Verification: View row counts' as info,
    NULL::TEXT as view_name,
    NULL::BIGINT as row_count;

SELECT
    NULL::TEXT as info,
    'verse_hierarchy' as view_name,
    COUNT(*) as row_count
FROM verse_hierarchy
UNION ALL
SELECT
    NULL::TEXT,
    'word_details',
    COUNT(*)
FROM word_details;

-- Sample verse_type_tamil values
SELECT
    'Verification: Sample verse types' as info,
    NULL::TEXT as verse_type,
    NULL::TEXT as verse_type_tamil,
    NULL::BIGINT as count;

SELECT
    NULL::TEXT as info,
    verse_type,
    verse_type_tamil,
    COUNT(*) as count
FROM verses
WHERE verse_type_tamil IS NOT NULL
GROUP BY verse_type, verse_type_tamil
ORDER BY verse_type;
