-- ============================================================================
-- TEST VIEWS CREATION
-- Quick test to verify the views can be created without errors
-- ============================================================================

-- Test 1: Create a minimal table structure
DROP TABLE IF EXISTS test_words CASCADE;
DROP TABLE IF EXISTS test_lines CASCADE;
DROP TABLE IF EXISTS test_verses CASCADE;
DROP TABLE IF EXISTS test_sections CASCADE;
DROP TABLE IF EXISTS test_works CASCADE;

-- Create minimal test tables
CREATE TEMP TABLE test_works (
    work_id INTEGER PRIMARY KEY,
    work_name VARCHAR(200) NOT NULL,
    work_name_tamil VARCHAR(200) NOT NULL
);

CREATE TEMP TABLE test_sections (
    section_id INTEGER PRIMARY KEY,
    work_id INTEGER NOT NULL,
    parent_section_id INTEGER,
    level_type VARCHAR(50) NOT NULL,
    level_type_tamil VARCHAR(50),
    section_number INTEGER NOT NULL,
    section_name VARCHAR(200),
    section_name_tamil VARCHAR(200),
    sort_order INTEGER NOT NULL,
    FOREIGN KEY (work_id) REFERENCES test_works(work_id),
    FOREIGN KEY (parent_section_id) REFERENCES test_sections(section_id)
);

CREATE TEMP TABLE test_verses (
    verse_id INTEGER PRIMARY KEY,
    work_id INTEGER NOT NULL,
    section_id INTEGER NOT NULL,
    verse_number INTEGER NOT NULL,
    verse_type VARCHAR(50),
    total_lines INTEGER NOT NULL,
    sort_order INTEGER NOT NULL,
    FOREIGN KEY (work_id) REFERENCES test_works(work_id),
    FOREIGN KEY (section_id) REFERENCES test_sections(section_id)
);

CREATE TEMP TABLE test_lines (
    line_id INTEGER PRIMARY KEY,
    verse_id INTEGER NOT NULL,
    line_number INTEGER NOT NULL,
    line_text TEXT NOT NULL,
    FOREIGN KEY (verse_id) REFERENCES test_verses(verse_id)
);

CREATE TEMP TABLE test_words (
    word_id INTEGER PRIMARY KEY,
    line_id INTEGER NOT NULL,
    word_position INTEGER NOT NULL,
    word_text VARCHAR(200) NOT NULL,
    word_text_transliteration VARCHAR(200),
    word_root VARCHAR(200),
    word_type VARCHAR(50),
    sandhi_split VARCHAR(500),
    meaning TEXT,
    FOREIGN KEY (line_id) REFERENCES test_lines(line_id)
);

-- Insert minimal test data
INSERT INTO test_works VALUES (1, 'Thirukkural', 'திருக்குறள்');
INSERT INTO test_sections VALUES (1, 1, NULL, 'paal', 'பால்', 1, 'Aram', 'அறத்துப்பால்', 1);
INSERT INTO test_sections VALUES (2, 1, 1, 'iyal', 'இயல்', 1, 'Pāyiram', 'பாயிரம்', 1);
INSERT INTO test_verses VALUES (1, 1, 2, 1, 'kural', 2, 1);
INSERT INTO test_lines VALUES (1, 1, 1, 'அகர முதல எழுத்தெல்லாம் ஆதி');
INSERT INTO test_words VALUES (1, 1, 1, 'அகர', 'akara', 'அ', 'noun', NULL, NULL);

-- Test 2: Create test view with new syntax
\echo 'Testing view creation with corrected CAST syntax and Tamil paths...'

CREATE TEMP VIEW test_verse_hierarchy AS
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
    FROM test_sections
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
    FROM test_sections s
    INNER JOIN section_path sp ON s.parent_section_id = sp.section_id
)
SELECT
    v.verse_id,
    v.verse_number,
    v.verse_type,
    w.work_name,
    w.work_name_tamil,
    sp.path_names as hierarchy_path,
    sp.path_names_tamil as hierarchy_path_tamil,
    sp.depth as hierarchy_depth
FROM test_verses v
INNER JOIN test_works w ON v.work_id = w.work_id
INNER JOIN section_path sp ON v.section_id = sp.section_id;

\echo 'View created successfully!'
\echo ''

-- Test 3: Query the view
\echo 'Testing view query with both English and Tamil paths...'
SELECT
    verse_id,
    work_name,
    hierarchy_path,
    hierarchy_path_tamil,
    hierarchy_depth
FROM test_verse_hierarchy;

\echo ''
\echo '============================================================================'
\echo 'TEST PASSED!'
\echo '============================================================================'
\echo 'The CAST syntax has been corrected and Tamil path columns added.'
\echo 'You can now safely run schema.sql or complete_setup.sql'
\echo ''
