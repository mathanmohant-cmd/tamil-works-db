-- ============================================================================
-- DATABASE VERIFICATION SCRIPT
-- Run this after setting up the database to verify all foreign keys are valid
-- ============================================================================

-- Usage:
-- psql $NEON_DB_URL -f verify_setup.sql

\echo '============================================================================'
\echo 'TAMIL LITERARY WORKS DATABASE - VERIFICATION REPORT'
\echo '============================================================================'
\echo ''

-- Check 1: Verify all 5 works exist
\echo '1. Checking WORKS table...'
SELECT
    work_id,
    work_name,
    work_name_tamil,
    author
FROM works
ORDER BY work_id;

\echo ''
\echo '   Expected: 5 works (IDs 1-5)'
\echo ''

-- Check 2: Verify sections reference valid works
\echo '2. Checking SECTIONS foreign keys...'
SELECT
    'Total sections' as check_type,
    COUNT(*) as count
FROM sections
UNION ALL
SELECT
    'Sections with invalid work_id' as check_type,
    COUNT(*) as count
FROM sections s
WHERE NOT EXISTS (
    SELECT 1 FROM works w WHERE w.work_id = s.work_id
)
UNION ALL
SELECT
    'Sections with invalid parent_section_id' as check_type,
    COUNT(*) as count
FROM sections s
WHERE s.parent_section_id IS NOT NULL
  AND NOT EXISTS (
    SELECT 1 FROM sections s2 WHERE s2.section_id = s.parent_section_id
);

\echo ''
\echo '   Expected: 0 invalid foreign keys'
\echo ''

-- Check 3: Verify verses reference valid works and sections
\echo '3. Checking VERSES foreign keys...'
SELECT
    'Total verses' as check_type,
    COUNT(*) as count
FROM verses
UNION ALL
SELECT
    'Verses with invalid work_id' as check_type,
    COUNT(*) as count
FROM verses v
WHERE NOT EXISTS (
    SELECT 1 FROM works w WHERE w.work_id = v.work_id
)
UNION ALL
SELECT
    'Verses with invalid section_id' as check_type,
    COUNT(*) as count
FROM verses v
WHERE NOT EXISTS (
    SELECT 1 FROM sections s WHERE s.section_id = v.section_id
);

\echo ''
\echo '   Expected: 0 invalid foreign keys'
\echo ''

-- Check 4: Verify lines reference valid verses
\echo '4. Checking LINES foreign keys...'
SELECT
    'Total lines' as check_type,
    COUNT(*) as count
FROM lines
UNION ALL
SELECT
    'Lines with invalid verse_id' as check_type,
    COUNT(*) as count
FROM lines l
WHERE NOT EXISTS (
    SELECT 1 FROM verses v WHERE v.verse_id = l.verse_id
);

\echo ''
\echo '   Expected: 0 invalid foreign keys'
\echo ''

-- Check 5: Verify words reference valid lines
\echo '5. Checking WORDS foreign keys...'
SELECT
    'Total words' as check_type,
    COUNT(*) as count
FROM words
UNION ALL
SELECT
    'Words with invalid line_id' as check_type,
    COUNT(*) as count
FROM words w
WHERE NOT EXISTS (
    SELECT 1 FROM lines l WHERE l.line_id = w.line_id
);

\echo ''
\echo '   Expected: 0 invalid foreign keys'
\echo ''

-- Check 6: Summary by work
\echo '6. Data summary by work...'
SELECT
    w.work_name,
    COUNT(DISTINCT s.section_id) as sections,
    COUNT(DISTINCT v.verse_id) as verses,
    COUNT(DISTINCT l.line_id) as lines,
    COUNT(DISTINCT wd.word_id) as words
FROM works w
LEFT JOIN sections s ON w.work_id = s.work_id
LEFT JOIN verses v ON w.work_id = v.work_id
LEFT JOIN lines l ON v.verse_id = l.verse_id
LEFT JOIN words wd ON l.line_id = wd.line_id
GROUP BY w.work_id, w.work_name
ORDER BY w.work_id;

\echo ''
\echo '7. Testing views...'
SELECT
    'verse_hierarchy view' as view_name,
    COUNT(*) as record_count
FROM verse_hierarchy
UNION ALL
SELECT
    'word_details view' as view_name,
    COUNT(*) as record_count
FROM word_details;

\echo ''
\echo '8. Sample query: Find word "முதல்" (first) across all works'
SELECT
    work_name,
    hierarchy_path,
    line_text,
    word_text,
    word_position
FROM word_details
WHERE word_root = 'முதல்'
ORDER BY work_name, verse_id, line_number, word_position;

\echo ''
\echo '============================================================================'
\echo 'VERIFICATION COMPLETE'
\echo '============================================================================'
\echo ''
\echo 'If all foreign key checks show 0 invalid records, the database is set up correctly.'
\echo ''
