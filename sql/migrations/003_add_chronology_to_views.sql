-- Migration: Add chronology fields to views
-- Date: 2026-01-01
-- Purpose: Add chronology_start_year, chronology_end_year, chronology_confidence
--          to verse_hierarchy and word_details views for chronological sorting

-- Drop existing views
DROP VIEW IF EXISTS word_details CASCADE;
DROP VIEW IF EXISTS verse_hierarchy CASCADE;

-- Recreate verse_hierarchy with chronology fields
CREATE VIEW verse_hierarchy AS
WITH RECURSIVE section_path AS (
    -- Base case: top-level sections
    SELECT
        section_id,
        work_id,
        level_type,
        level_type_tamil,
        section_number,
        section_name,
        section_name_tamil,
        sort_order,
        ARRAY[section_name]::VARCHAR[] as path_names,
        ARRAY[section_name_tamil]::VARCHAR[] as path_names_tamil,
        1 as depth
    FROM sections
    WHERE parent_section_id IS NULL

    UNION ALL

    -- Recursive case: child sections
    SELECT
        s.section_id,
        s.work_id,
        s.level_type,
        s.level_type_tamil,
        s.section_number,
        s.section_name,
        s.section_name_tamil,
        s.sort_order,
        sp.path_names || s.section_name,
        sp.path_names_tamil || s.section_name_tamil,
        sp.depth + 1
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
    w.canonical_order as canonical_position,
    w.chronology_start_year,
    w.chronology_end_year,
    w.chronology_confidence,
    sp.path_names as hierarchy_path,
    sp.path_names_tamil as hierarchy_path_tamil,
    sp.depth as hierarchy_depth
FROM verses v
INNER JOIN works w ON v.work_id = w.work_id
INNER JOIN section_path sp ON v.section_id = sp.section_id;

-- Recreate word_details with chronology fields from verse_hierarchy
CREATE VIEW word_details AS
WITH work_verse_counts AS (
    SELECT
        work_id,
        COUNT(DISTINCT verse_id) as work_verse_count
    FROM verses
    GROUP BY work_id
)
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
    v.work_id,
    v.total_lines,
    vh.verse_type,
    vh.verse_type_tamil,
    vh.work_name,
    vh.work_name_tamil,
    vh.canonical_position,
    vh.chronology_start_year,
    vh.chronology_end_year,
    vh.chronology_confidence,
    vh.hierarchy_path,
    vh.hierarchy_path_tamil,
    wvc.work_verse_count
FROM words w
INNER JOIN lines l ON w.line_id = l.line_id
INNER JOIN verses v ON l.verse_id = v.verse_id
INNER JOIN verse_hierarchy vh ON v.verse_id = vh.verse_id
INNER JOIN work_verse_counts wvc ON v.work_id = wvc.work_id;

-- Verify the views were created successfully
SELECT 'verse_hierarchy view created' as status, COUNT(*) as row_count FROM verse_hierarchy
UNION ALL
SELECT 'word_details view created' as status, COUNT(*) as row_count FROM word_details;
