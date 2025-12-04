-- ============================================================================
-- TAMIL LITERATURE DATABASE - SAVED QUERIES
-- ============================================================================
-- This file contains all commonly used queries organized by category
-- Save this file and use it as a reference for querying the database
-- ============================================================================

-- ============================================================================
-- SECTION 1: BASIC QUERIES - Getting Started
-- ============================================================================

-- 1.1: View all literary works in the database
SELECT
    work_id,
    work_name,
    work_name_tamil,
    author,
    period
FROM works
ORDER BY work_id;

-- 1.2: Count total records in database
SELECT
    (SELECT COUNT(*) FROM works) as total_works,
    (SELECT COUNT(*) FROM sections) as total_sections,
    (SELECT COUNT(*) FROM verses) as total_verses,
    (SELECT COUNT(*) FROM lines) as total_lines,
    (SELECT COUNT(*) FROM words) as total_words;

-- 1.3: View sample data from Thirukkural
SELECT *
FROM word_details
WHERE work_name = 'Thirukkural'
LIMIT 10;

-- ============================================================================
-- SECTION 2: WORD SEARCH QUERIES
-- ============================================================================

-- 2.1: Find all occurrences of a specific word
-- Replace 'அறம்' with your search word
SELECT
    word_text,
    line_text,
    work_name,
    hierarchy_path,
    verse_number,
    line_number,
    word_position
FROM word_details
WHERE word_text = 'அறம்'
ORDER BY work_name, verse_number, line_number, word_position;

-- 2.2: Find words by root form (all derived forms)
-- Replace 'முதல்' with your search root
SELECT
    word_text,
    word_root,
    line_text,
    work_name,
    hierarchy_path
FROM word_details
WHERE word_root = 'முதல்'
ORDER BY work_name, verse_number;

-- 2.3: Case-insensitive word search (useful for transliteration)
SELECT
    word_text,
    word_text_transliteration,
    line_text,
    hierarchy_path
FROM word_details
WHERE LOWER(word_text_transliteration) LIKE LOWER('%aram%')
ORDER BY work_name;

-- 2.4: Find words by type (noun, verb, etc.)
SELECT
    word_text,
    word_type,
    line_text,
    hierarchy_path
FROM word_details
WHERE word_type = 'noun'
LIMIT 50;

-- 2.5: Search for partial word matches
-- Replace 'அற%' with your pattern (% is wildcard)
SELECT DISTINCT
    word_text,
    word_root,
    COUNT(*) as frequency
FROM word_details
WHERE word_text LIKE 'அற%'
GROUP BY word_text, word_root
ORDER BY frequency DESC;

-- ============================================================================
-- SECTION 3: LINE AND VERSE QUERIES
-- ============================================================================

-- 3.1: Find lines containing specific text
-- Replace '%அறம்%' with your search text
SELECT
    line_text,
    line_text_translation,
    verse_number,
    work_name,
    hierarchy_path
FROM lines l
INNER JOIN verses v ON l.verse_id = v.verse_id
INNER JOIN verse_hierarchy vh ON v.verse_id = vh.verse_id
WHERE line_text LIKE '%அறம்%'
ORDER BY work_name, verse_number, line_number;

-- 3.2: Get a complete verse with all its lines
-- Replace verse_id = 1 with your target verse
SELECT
    v.verse_number,
    v.verse_type,
    l.line_number,
    l.line_text,
    l.line_text_transliteration,
    l.line_text_translation
FROM verses v
INNER JOIN lines l ON v.verse_id = l.verse_id
WHERE v.verse_id = 1
ORDER BY l.line_number;

-- 3.3: Get a verse with all words broken down
-- Replace verse_id = 1 with your target verse
SELECT
    l.line_number,
    l.line_text as complete_line,
    w.word_position,
    w.word_text,
    w.word_root,
    w.word_type,
    w.meaning
FROM verses v
INNER JOIN lines l ON v.verse_id = l.verse_id
INNER JOIN words w ON l.line_id = w.line_id
WHERE v.verse_id = 1
ORDER BY l.line_number, w.word_position;

-- 3.4: Search verses by type/meter
-- Replace 'kural' with desired verse type
SELECT
    vh.work_name,
    vh.hierarchy_path,
    v.verse_number,
    v.meter,
    l.line_text
FROM verses v
INNER JOIN verse_hierarchy vh ON v.verse_id = vh.verse_id
INNER JOIN lines l ON v.verse_id = l.verse_id
WHERE v.verse_type = 'kural'
ORDER BY v.verse_number, l.line_number
LIMIT 20;

-- ============================================================================
-- SECTION 4: HIERARCHICAL QUERIES
-- ============================================================================

-- 4.1: View complete hierarchy for Thirukkural
SELECT
    level_type,
    section_number,
    section_name,
    section_name_tamil,
    parent_section_id
FROM sections
WHERE work_id = 3  -- Thirukkural
ORDER BY sort_order;

-- 4.2: Get all verses in a specific section
-- Replace section_id = 6 with your target section
SELECT
    vh.hierarchy_path,
    v.verse_number,
    l.line_number,
    l.line_text,
    l.line_text_translation
FROM verses v
INNER JOIN verse_hierarchy vh ON v.verse_id = vh.verse_id
INNER JOIN lines l ON v.verse_id = l.verse_id
WHERE v.section_id = 6
ORDER BY v.verse_number, l.line_number;

-- 4.3: Get all content under a high-level section (recursive)
-- This gets everything under section_id = 1 (Aram Paal in Thirukkural)
WITH RECURSIVE subsections AS (
    -- Start with the parent section
    SELECT section_id
    FROM sections
    WHERE section_id = 1

    UNION ALL

    -- Recursively get all child sections
    SELECT s.section_id
    FROM sections s
    INNER JOIN subsections ss ON s.parent_section_id = ss.section_id
)
SELECT
    vh.hierarchy_path,
    v.verse_number,
    l.line_number,
    l.line_text
FROM verses v
INNER JOIN subsections ss ON v.section_id = ss.section_id
INNER JOIN verse_hierarchy vh ON v.verse_id = vh.verse_id
INNER JOIN lines l ON v.verse_id = l.verse_id
ORDER BY v.sort_order, l.line_number
LIMIT 100;  -- Remove LIMIT to get all

-- 4.4: View section hierarchy as a tree
WITH RECURSIVE section_tree AS (
    SELECT
        section_id,
        work_id,
        parent_section_id,
        level_type,
        section_name,
        0 as depth,
        section_name as path
    FROM sections
    WHERE parent_section_id IS NULL

    UNION ALL

    SELECT
        s.section_id,
        s.work_id,
        s.parent_section_id,
        s.level_type,
        s.section_name,
        st.depth + 1,
        st.path || ' > ' || s.section_name
    FROM sections s
    INNER JOIN section_tree st ON s.parent_section_id = st.section_id
)
SELECT
    REPEAT('  ', depth) || section_name as tree_structure,
    level_type,
    depth
FROM section_tree
WHERE work_id = 3  -- Change to view other works
ORDER BY path;

-- ============================================================================
-- SECTION 5: STATISTICAL QUERIES
-- ============================================================================

-- 5.1: Word frequency across entire database
SELECT
    word_text,
    word_root,
    COUNT(*) as frequency,
    COUNT(DISTINCT verse_id) as unique_verses
FROM word_details
GROUP BY word_text, word_root
ORDER BY frequency DESC
LIMIT 100;

-- 5.2: Word frequency in a specific work
-- Replace 'Thirukkural' with target work
SELECT
    word_text,
    word_root,
    COUNT(*) as frequency,
    COUNT(DISTINCT verse_id) as unique_verses
FROM word_details
WHERE work_name = 'Thirukkural'
GROUP BY word_text, word_root
ORDER BY frequency DESC
LIMIT 100;

-- 5.3: Statistics per section (e.g., Adhikaram statistics)
SELECT
    s.section_name,
    s.section_name_tamil,
    COUNT(DISTINCT v.verse_id) as total_verses,
    COUNT(DISTINCT l.line_id) as total_lines,
    COUNT(DISTINCT w.word_id) as total_words,
    ROUND(AVG(line_word_count.words_per_line), 2) as avg_words_per_line
FROM sections s
INNER JOIN verses v ON s.section_id = v.section_id
INNER JOIN lines l ON v.verse_id = l.verse_id
INNER JOIN words w ON l.line_id = w.line_id
LEFT JOIN (
    SELECT line_id, COUNT(*) as words_per_line
    FROM words
    GROUP BY line_id
) line_word_count ON l.line_id = line_word_count.line_id
WHERE s.level_type = 'adhikaram' AND s.work_id = 3
GROUP BY s.section_id, s.section_name, s.section_name_tamil
ORDER BY s.sort_order;

-- 5.4: Compare word usage across different works
-- Replace 'அறம்' with target word
SELECT
    work_name,
    COUNT(*) as occurrences,
    COUNT(DISTINCT verse_id) as unique_verses,
    COUNT(DISTINCT line_id) as unique_lines
FROM word_details
WHERE word_text = 'அறம்'
GROUP BY work_name
ORDER BY occurrences DESC;

-- 5.5: Most common word roots
SELECT
    word_root,
    COUNT(DISTINCT word_text) as unique_forms,
    COUNT(*) as total_occurrences,
    STRING_AGG(DISTINCT word_text, ', ') as example_forms
FROM word_details
WHERE word_root IS NOT NULL
GROUP BY word_root
ORDER BY total_occurrences DESC
LIMIT 50;

-- 5.6: Vocabulary size per work
SELECT
    work_name,
    COUNT(DISTINCT word_text) as unique_words,
    COUNT(DISTINCT word_root) as unique_roots,
    COUNT(*) as total_words,
    ROUND(COUNT(DISTINCT word_text)::numeric / COUNT(*)::numeric, 4) as type_token_ratio
FROM word_details
GROUP BY work_name
ORDER BY unique_words DESC;

-- ============================================================================
-- SECTION 6: ADVANCED ANALYSIS QUERIES
-- ============================================================================

-- 6.1: Word co-occurrence analysis
-- Find words that commonly appear with a target word in the same line
WITH target_lines AS (
    SELECT DISTINCT line_id
    FROM words
    WHERE word_text = 'அறம்'  -- Replace with your target word
)
SELECT
    w.word_text,
    w.word_root,
    COUNT(*) as co_occurrence_count,
    ROUND(COUNT(*)::numeric / (SELECT COUNT(*) FROM target_lines)::numeric * 100, 2) as co_occurrence_percentage
FROM target_lines tl
INNER JOIN words w ON tl.line_id = w.line_id
WHERE w.word_text != 'அறம்'  -- Exclude the target word itself
GROUP BY w.word_text, w.word_root
ORDER BY co_occurrence_count DESC
LIMIT 50;

-- 6.2: Context window around a specific word
-- Shows words before and after target word
WITH target_words AS (
    SELECT word_id, line_id, word_position, word_text as target
    FROM words
    WHERE word_text = 'அறம்'
    LIMIT 1  -- Remove LIMIT to see all occurrences
)
SELECT
    tw.target as target_word,
    w.word_position - tw.word_position as relative_position,
    w.word_text,
    w.word_type,
    CASE
        WHEN w.word_id = tw.word_id THEN '>>> TARGET <<<'
        WHEN w.word_position < tw.word_position THEN 'BEFORE'
        ELSE 'AFTER'
    END as position_marker,
    l.line_text
FROM target_words tw
INNER JOIN words w ON tw.line_id = w.line_id
INNER JOIN lines l ON w.line_id = l.line_id
WHERE w.word_position BETWEEN tw.word_position - 5 AND tw.word_position + 5
ORDER BY tw.word_id, w.word_position;

-- 6.3: Find all sandhi-split words (compound words)
SELECT
    word_text,
    sandhi_split,
    word_type,
    line_text,
    work_name,
    hierarchy_path
FROM word_details
WHERE sandhi_split IS NOT NULL
ORDER BY work_name
LIMIT 100;

-- 6.4: Word position analysis (where words typically appear in lines)
SELECT
    word_text,
    word_root,
    AVG(word_position) as avg_position,
    MIN(word_position) as earliest_position,
    MAX(word_position) as latest_position,
    COUNT(*) as frequency
FROM word_details
WHERE word_text = 'அறம்'  -- Replace with target word
GROUP BY word_text, word_root;

-- 6.5: Find verses with similar vocabulary
-- Shows verses that share many words with a target verse
WITH target_verse_words AS (
    SELECT DISTINCT word_root
    FROM words w
    INNER JOIN lines l ON w.line_id = l.line_id
    WHERE l.verse_id = 1  -- Replace with target verse
)
SELECT
    v.verse_id,
    vh.work_name,
    vh.hierarchy_path,
    COUNT(DISTINCT w.word_root) as shared_words,
    STRING_AGG(DISTINCT l.line_text, ' | ') as verse_text
FROM target_verse_words tvw
INNER JOIN words w ON tvw.word_root = w.word_root
INNER JOIN lines l ON w.line_id = l.line_id
INNER JOIN verses v ON l.verse_id = v.verse_id
INNER JOIN verse_hierarchy vh ON v.verse_id = vh.verse_id
WHERE v.verse_id != 1  -- Exclude the target verse itself
GROUP BY v.verse_id, vh.work_name, vh.hierarchy_path
HAVING COUNT(DISTINCT w.word_root) >= 3  -- Minimum shared words
ORDER BY shared_words DESC
LIMIT 20;

-- ============================================================================
-- SECTION 7: CROSS-REFERENCE QUERIES
-- ============================================================================

-- 7.1: View all cross-references
SELECT
    w1.work_name as source_work,
    vh1.hierarchy_path as source_path,
    cr.reference_type,
    w2.work_name as target_work,
    vh2.hierarchy_path as target_path,
    cr.notes
FROM cross_references cr
INNER JOIN verses v1 ON cr.source_verse_id = v1.verse_id
INNER JOIN verses v2 ON cr.target_verse_id = v2.verse_id
INNER JOIN verse_hierarchy vh1 ON v1.verse_id = vh1.verse_id
INNER JOIN verse_hierarchy vh2 ON v2.verse_id = vh2.verse_id
INNER JOIN works w1 ON v1.work_id = w1.work_id
INNER JOIN works w2 ON v2.work_id = w2.work_id
ORDER BY w1.work_name, v1.verse_number;

-- 7.2: Find verses with commentaries
SELECT
    vh.work_name,
    vh.hierarchy_path,
    v.verse_number,
    c.commentator,
    c.commentator_tamil,
    c.commentary_period,
    LEFT(c.commentary_text, 100) as commentary_preview
FROM commentaries c
INNER JOIN verses v ON c.verse_id = v.verse_id
INNER JOIN verse_hierarchy vh ON v.verse_id = vh.verse_id
ORDER BY vh.work_name, v.verse_number;

-- ============================================================================
-- SECTION 8: MAINTENANCE AND UTILITY QUERIES
-- ============================================================================

-- 8.1: Check data integrity - verses without lines
SELECT
    w.work_name,
    v.verse_id,
    v.verse_number,
    v.total_lines,
    COUNT(l.line_id) as actual_lines
FROM verses v
INNER JOIN works w ON v.work_id = w.work_id
LEFT JOIN lines l ON v.verse_id = l.verse_id
GROUP BY w.work_name, v.verse_id, v.verse_number, v.total_lines
HAVING COUNT(l.line_id) != v.total_lines
ORDER BY w.work_name, v.verse_number;

-- 8.2: Check for lines without words
SELECT
    w.work_name,
    l.line_id,
    l.line_text,
    COUNT(wd.word_id) as word_count
FROM lines l
INNER JOIN verses v ON l.verse_id = v.verse_id
INNER JOIN works w ON v.work_id = w.work_id
LEFT JOIN words wd ON l.line_id = wd.line_id
GROUP BY w.work_name, l.line_id, l.line_text
HAVING COUNT(wd.word_id) = 0
ORDER BY w.work_name;

-- 8.3: Database size and table statistics
SELECT
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size,
    pg_total_relation_size(schemaname||'.'||tablename) AS size_bytes
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- 8.4: Index usage statistics
SELECT
    schemaname,
    tablename,
    indexname,
    idx_scan as index_scans,
    idx_tup_read as tuples_read,
    idx_tup_fetch as tuples_fetched
FROM pg_stat_user_indexes
ORDER BY idx_scan DESC;

-- 8.5: Find duplicate words in same line (data quality check)
SELECT
    l.line_id,
    l.line_text,
    w.word_text,
    COUNT(*) as occurrence_count
FROM words w
INNER JOIN lines l ON w.line_id = l.line_id
GROUP BY l.line_id, l.line_text, w.word_text
HAVING COUNT(*) > 1
ORDER BY occurrence_count DESC;

-- ============================================================================
-- SECTION 9: EXPORT QUERIES
-- ============================================================================

-- 9.1: Export complete work in readable format
SELECT
    vh.hierarchy_path,
    v.verse_number,
    STRING_AGG(l.line_text, E'\n' ORDER BY l.line_number) as verse_text,
    STRING_AGG(l.line_text_translation, E'\n' ORDER BY l.line_number) as translation
FROM verses v
INNER JOIN verse_hierarchy vh ON v.verse_id = vh.verse_id
INNER JOIN lines l ON v.verse_id = l.verse_id
WHERE vh.work_name = 'Thirukkural'  -- Replace with target work
GROUP BY vh.hierarchy_path, v.verse_number, v.sort_order
ORDER BY v.sort_order;

-- 9.2: Export word list with frequencies (for concordance)
SELECT
    word_text,
    word_root,
    word_type,
    COUNT(*) as frequency,
    STRING_AGG(DISTINCT work_name, ', ') as appears_in_works
FROM word_details
GROUP BY word_text, word_root, word_type
ORDER BY frequency DESC;

-- 9.3: Export all verses from a specific section as JSON
SELECT json_agg(
    json_build_object(
        'verse_number', v.verse_number,
        'hierarchy', vh.hierarchy_path,
        'lines', (
            SELECT json_agg(
                json_build_object(
                    'line_number', l.line_number,
                    'text', l.line_text,
                    'translation', l.line_text_translation
                ) ORDER BY l.line_number
            )
            FROM lines l
            WHERE l.verse_id = v.verse_id
        )
    ) ORDER BY v.sort_order
) as section_json
FROM verses v
INNER JOIN verse_hierarchy vh ON v.verse_id = vh.verse_id
WHERE v.section_id = 6;  -- Replace with target section

-- ============================================================================
-- SECTION 10: CUSTOM QUERY TEMPLATES
-- ============================================================================

-- 10.1: Template: Search and replace pattern
-- Use this to find words matching a pattern
/*
SELECT
    word_text,
    line_text,
    hierarchy_path
FROM word_details
WHERE word_text ~ '^[pattern]'  -- PostgreSQL regex
ORDER BY work_name;
*/

-- 10.2: Template: Complex filtering
/*
SELECT *
FROM word_details
WHERE work_name = 'WorkName'
  AND hierarchy_path LIKE '%SectionName%'
  AND word_type = 'type'
  AND word_text LIKE 'pattern%'
ORDER BY verse_number, line_number;
*/

-- 10.3: Template: Aggregation by custom grouping
/*
SELECT
    [grouping_field],
    COUNT(*) as count,
    COUNT(DISTINCT verse_id) as unique_verses
FROM word_details
WHERE [conditions]
GROUP BY [grouping_field]
ORDER BY count DESC;
*/

-- ============================================================================
-- END OF SAVED QUERIES
-- ============================================================================

-- NOTES:
-- 1. Replace placeholder values (like 'அறம்', section_id = 6, etc.) with actual values
-- 2. Add LIMIT clauses to large result sets for testing
-- 3. Create indexes on frequently queried columns for better performance
-- 4. Use EXPLAIN ANALYZE before running expensive queries
-- 5. For very large datasets, consider materialized views for complex aggregations
