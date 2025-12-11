-- Tamil Literary Works Database Schema
-- Supports: Tolkappiyam, Sangam Literature, Thirukkural, Silapathikaram, Kambaramayanam

-- ============================================================================
-- MAIN TABLES
-- ============================================================================

-- Literary works table
CREATE TABLE works (
    work_id INTEGER PRIMARY KEY,
    work_name VARCHAR(200) NOT NULL,
    work_name_tamil VARCHAR(200) NOT NULL,
    period VARCHAR(100),
    author VARCHAR(200),
    author_tamil VARCHAR(200),
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Hierarchical sections table (flexible structure for all levels)
CREATE TABLE sections (
    section_id INTEGER PRIMARY KEY,
    work_id INTEGER NOT NULL,
    parent_section_id INTEGER,  -- NULL for top-level sections
    level_type VARCHAR(50) NOT NULL,  -- e.g., 'paal', 'kandam', 'adhikaram', 'padalam'
    level_type_tamil VARCHAR(50),
    section_number INTEGER NOT NULL,
    section_name VARCHAR(200),
    section_name_tamil VARCHAR(200),
    description TEXT,
    sort_order INTEGER NOT NULL,  -- For maintaining order within same level
    FOREIGN KEY (work_id) REFERENCES works(work_id),
    FOREIGN KEY (parent_section_id) REFERENCES sections(section_id),
    UNIQUE (work_id, parent_section_id, level_type, section_number)
);

-- Create index for hierarchical queries
CREATE INDEX idx_sections_parent ON sections(parent_section_id);
CREATE INDEX idx_sections_work ON sections(work_id);

-- Verses/Poems/Sutras table (the atomic textual unit before lines)
CREATE TABLE verses (
    verse_id INTEGER PRIMARY KEY,
    work_id INTEGER NOT NULL,
    section_id INTEGER NOT NULL,  -- Links to the most specific section (e.g., adhikaram)
    verse_number INTEGER NOT NULL,
    verse_type VARCHAR(50),  -- e.g., 'kural', 'venba', 'kalippa', 'noorpa', 'poem'
    verse_type_tamil VARCHAR(50),
    meter VARCHAR(100),  -- Poetic meter if applicable
    total_lines INTEGER NOT NULL,
    sort_order INTEGER NOT NULL,
    FOREIGN KEY (work_id) REFERENCES works(work_id),
    FOREIGN KEY (section_id) REFERENCES sections(section_id),
    UNIQUE (work_id, section_id, verse_number)
);

CREATE INDEX idx_verses_section ON verses(section_id);
CREATE INDEX idx_verses_work ON verses(work_id);

-- Lines table
CREATE TABLE lines (
    line_id INTEGER PRIMARY KEY,
    verse_id INTEGER NOT NULL,
    line_number INTEGER NOT NULL,  -- Line number within the verse (1, 2, 3, 4...)
    line_text TEXT NOT NULL,
    line_text_transliteration TEXT,  -- Roman transliteration
    line_text_translation TEXT,  -- English/other language translation
    FOREIGN KEY (verse_id) REFERENCES verses(verse_id),
    UNIQUE (verse_id, line_number)
);

CREATE INDEX idx_lines_verse ON lines(verse_id);

-- Words table (every word with its position)
CREATE TABLE words (
    word_id INTEGER PRIMARY KEY,
    line_id INTEGER NOT NULL,
    word_position INTEGER NOT NULL,  -- Position in the line (1, 2, 3...)
    word_text VARCHAR(200) NOT NULL,
    word_text_transliteration VARCHAR(200),
    word_root VARCHAR(200),  -- Root/base form of the word
    word_type VARCHAR(50),  -- noun, verb, adjective, etc.
    sandhi_split VARCHAR(500),  -- If word is result of sandhi, show components
    meaning TEXT,
    FOREIGN KEY (line_id) REFERENCES lines(line_id),
    UNIQUE (line_id, word_position)
);

CREATE INDEX idx_words_line ON words(line_id);
CREATE INDEX idx_words_text ON words(word_text);
CREATE INDEX idx_words_root ON words(word_root);

-- Full-text search for words (if your database supports it)
-- For SQLite:
-- CREATE VIRTUAL TABLE words_fts USING fts5(word_text, word_root, content=words, content_rowid=word_id);

-- ============================================================================
-- METADATA AND ANNOTATION TABLES
-- ============================================================================

-- Commentary/annotations on verses
CREATE TABLE commentaries (
    commentary_id INTEGER PRIMARY KEY,
    verse_id INTEGER NOT NULL,
    commentator VARCHAR(200),
    commentator_tamil VARCHAR(200),
    commentary_text TEXT NOT NULL,
    commentary_period VARCHAR(100),
    FOREIGN KEY (verse_id) REFERENCES verses(verse_id)
);

-- Cross-references between verses
CREATE TABLE cross_references (
    reference_id INTEGER PRIMARY KEY,
    source_verse_id INTEGER NOT NULL,
    target_verse_id INTEGER NOT NULL,
    reference_type VARCHAR(50),  -- 'parallel', 'quote', 'allusion', etc.
    notes TEXT,
    FOREIGN KEY (source_verse_id) REFERENCES verses(verse_id),
    FOREIGN KEY (target_verse_id) REFERENCES verses(verse_id)
);

-- ============================================================================
-- VIEWS FOR EASIER QUERYING
-- ============================================================================

-- Complete hierarchical path for each verse
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

-- Complete word information with full context
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
-- COMMON QUERY EXAMPLES
-- ============================================================================
--
-- Note: No sample data is inserted by default. Use parser scripts to populate:
--   - python scripts/thirukkural_parser.py
--   - python scripts/sangam_parser.py
--
-- ============================================================================

-- Query 1: Find all occurrences of a specific word
-- SELECT * FROM word_details WHERE word_text = 'அறம்';

-- Query 2: Get complete hierarchy for a specific verse
-- SELECT * FROM verse_hierarchy WHERE verse_id = 1;

-- Query 3: Find all verses in a specific section
-- SELECT v.*, l.line_text
-- FROM verses v
-- INNER JOIN lines l ON v.verse_id = l.verse_id
-- WHERE v.section_id = 6
-- ORDER BY v.verse_number, l.line_number;

-- Query 4: Search for words by root form
-- SELECT * FROM word_details WHERE word_root = 'முதல்';

-- Query 5: Get all content under a specific high-level section (e.g., all of Aram paal)
-- WITH RECURSIVE subsections AS (
--     SELECT section_id FROM sections WHERE section_id = 1
--     UNION ALL
--     SELECT s.section_id FROM sections s
--     INNER JOIN subsections ss ON s.parent_section_id = ss.section_id
-- )
-- SELECT v.verse_id, v.verse_number, l.line_text
-- FROM verses v
-- INNER JOIN subsections ss ON v.section_id = ss.section_id
-- INNER JOIN lines l ON v.verse_id = l.verse_id
-- ORDER BY v.sort_order, l.line_number;

-- Query 6: Find lines containing a specific word
-- SELECT l.line_text, vh.work_name, vh.hierarchy_path
-- FROM words w
-- INNER JOIN lines l ON w.line_id = l.line_id
-- INNER JOIN verses v ON l.verse_id = v.verse_id
-- INNER JOIN verse_hierarchy vh ON v.verse_id = vh.verse_id
-- WHERE w.word_text = 'அறம்';

-- Query 7: Get word frequency across entire work or section
-- SELECT word_text, word_root, COUNT(*) as frequency
-- FROM word_details
-- WHERE work_name = 'Thirukkural'
-- GROUP BY word_text, word_root
-- ORDER BY frequency DESC;

-- Query 8: Get complete text of a specific adhikaram/chapter with hierarchy
-- SELECT
--     vh.hierarchy_path,
--     v.verse_number,
--     l.line_number,
--     l.line_text
-- FROM verses v
-- INNER JOIN verse_hierarchy vh ON v.verse_id = vh.verse_id
-- INNER JOIN lines l ON v.verse_id = l.verse_id
-- WHERE v.section_id = 6
-- ORDER BY v.verse_number, l.line_number;
