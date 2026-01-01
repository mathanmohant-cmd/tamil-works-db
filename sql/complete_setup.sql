-- ============================================================================
-- COMPLETE DATABASE SETUP
-- This file contains the complete schema for the Tamil Literature Database
-- Run this file to create all tables, indexes, and views
-- ============================================================================
--
-- IMPORTANT: This file contains ONLY the schema definition.
-- To populate data, use the parser scripts in the scripts/ directory:
--   - python scripts/thirukkural_bulk_import.py
--   - python scripts/sangam_bulk_import.py
--   - python scripts/silapathikaram_bulk_import.py
--   - python scripts/kambaramayanam_bulk_import.py
--
-- Usage:
-- psql $DATABASE_URL -f sql/complete_setup.sql
--
-- ============================================================================

-- Tamil Literary Works Database Schema
-- Supports: Tolkappiyam, Sangam Literature, Thirukkural, Silapathikaram, Kambaramayanam

-- ============================================================================
-- MAIN TABLES
-- ============================================================================

-- Literary works table
CREATE TABLE works (
    work_id SERIAL PRIMARY KEY,
    work_name VARCHAR(200) NOT NULL,
    work_name_tamil VARCHAR(200) NOT NULL,
    period VARCHAR(100),
    author VARCHAR(200),
    author_tamil VARCHAR(200),
    description TEXT,
    chronology_start_year INTEGER,  -- Approximate start year (negative = BCE)
    chronology_end_year INTEGER,  -- Approximate end year (negative = BCE)
    chronology_confidence VARCHAR(20),  -- 'high', 'medium', 'low', 'disputed'
    chronology_notes TEXT,  -- Scholarly variations and dating debates
    canonical_order INTEGER,  -- Traditional Tamil literary canon ordering (100=Tolkappiyam, 200s=Sangam, 260=Thirukkural, 280=Silapathikaram, 400=Kambaramayanam)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB  -- Flexible metadata: tradition, collection info, saints/authors, musical tradition, themes, etc.
);

-- Collections table (literary periods, traditions, genres, canons)
CREATE TABLE collections (
    collection_id SERIAL PRIMARY KEY,
    collection_name VARCHAR(100) NOT NULL UNIQUE,
    collection_name_tamil VARCHAR(100),
    collection_type VARCHAR(50) NOT NULL,  -- 'period', 'tradition', 'genre', 'canon', 'custom'
    entity_type VARCHAR(20) DEFAULT 'work',  -- 'work', 'section', 'verse', or 'mixed'
    description TEXT,
    parent_collection_id INTEGER,  -- For hierarchical collections (FK self-reference added below)
    sort_order INTEGER,  -- For ordering collections themselves
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Add foreign key constraints for collections
ALTER TABLE collections
    ADD CONSTRAINT fk_collections_parent
    FOREIGN KEY (parent_collection_id) REFERENCES collections(collection_id);

-- Removed: primary_collection_id FK constraint
-- Use work_collections many-to-many table instead

-- Junction table: Works can belong to multiple collections
CREATE TABLE work_collections (
    work_collection_id SERIAL PRIMARY KEY,
    work_id INTEGER NOT NULL,
    collection_id INTEGER NOT NULL,
    position_in_collection INTEGER,  -- Order within this specific collection
    is_primary BOOLEAN DEFAULT FALSE,  -- Mark primary collection for each work
    notes TEXT,  -- Collection-specific notes about this work
    FOREIGN KEY (work_id) REFERENCES works(work_id) ON DELETE CASCADE,
    FOREIGN KEY (collection_id) REFERENCES collections(collection_id) ON DELETE CASCADE,
    UNIQUE (work_id, collection_id),
    UNIQUE (collection_id, position_in_collection)
);

-- Indexes for collections (work_collections created above)
CREATE INDEX idx_collections_type ON collections(collection_type);
CREATE INDEX idx_collections_entity_type ON collections(entity_type);
CREATE INDEX idx_collections_parent ON collections(parent_collection_id);
-- Index on primary_collection_id removed (column no longer exists)
CREATE INDEX idx_work_collections_work ON work_collections(work_id);
CREATE INDEX idx_work_collections_collection ON work_collections(collection_id);
CREATE INDEX idx_work_collections_position ON work_collections(collection_id, position_in_collection);

-- Insert designated filter collection (Tamil Literature root)
-- This collection serves as the root for the filter UI tree
-- User can build the hierarchy under this collection via Admin UI
INSERT INTO collections (collection_id, collection_name, collection_name_tamil, collection_type, description, parent_collection_id, sort_order)
VALUES (1, 'Tamil Literature', 'தமிழ் இலக்கியம்', 'canon', 'Root collection for canonical Tamil Literature hierarchy - used by filter UI', NULL, 1)
ON CONFLICT (collection_id) DO NOTHING;

-- Reset sequence to prevent conflicts (collection_id is SERIAL)
SELECT setval('collections_collection_id_seq', (SELECT COALESCE(MAX(collection_id), 0) + 1 FROM collections), false);

-- Hierarchical sections table (flexible structure for all levels)
CREATE TABLE sections (
    section_id SERIAL PRIMARY KEY,
    work_id INTEGER NOT NULL,
    parent_section_id INTEGER,  -- NULL for top-level sections
    level_type VARCHAR(50) NOT NULL,  -- e.g., 'paal', 'kandam', 'adhikaram', 'padalam'
    level_type_tamil VARCHAR(50),
    section_number INTEGER NOT NULL,
    section_name VARCHAR(200),
    section_name_tamil VARCHAR(200),
    description TEXT,
    sort_order INTEGER NOT NULL,  -- For maintaining order within same level
    metadata JSONB,  -- Flexible metadata: musical mode (pann), thematic category, temple location, etc.
    FOREIGN KEY (work_id) REFERENCES works(work_id),
    FOREIGN KEY (parent_section_id) REFERENCES sections(section_id),
    UNIQUE (work_id, parent_section_id, level_type, section_number)
);

-- Create index for hierarchical queries
CREATE INDEX idx_sections_parent ON sections(parent_section_id);
CREATE INDEX idx_sections_work ON sections(work_id);

-- Verses/Poems/Sutras table (the atomic textual unit before lines)
CREATE TABLE verses (
    verse_id SERIAL PRIMARY KEY,
    work_id INTEGER NOT NULL,
    section_id INTEGER NOT NULL,  -- Links to the most specific section (e.g., adhikaram)
    verse_number INTEGER NOT NULL,
    verse_type VARCHAR(200),  -- Type/name of verse: 'kural', 'Mangala Vaazhththu Paadal', 'Kaanal Vari', etc.
    verse_type_tamil VARCHAR(200),  -- Tamil type/name: 'குறள்', 'மங்கல வாழ்த்துப் பாடல்', 'கானல் வரி', etc.
    meter VARCHAR(100),  -- Poetic meter if applicable
    total_lines INTEGER NOT NULL,
    sort_order INTEGER NOT NULL,
    metadata JSONB,  -- Flexible metadata: saint/alvar, deity, raga/talam, themes, literary devices, divya desam, etc.
    FOREIGN KEY (work_id) REFERENCES works(work_id),
    FOREIGN KEY (section_id) REFERENCES sections(section_id),
    UNIQUE (work_id, section_id, verse_number)
);

CREATE INDEX idx_verses_section ON verses(section_id);
CREATE INDEX idx_verses_work ON verses(work_id);

-- Lines table
CREATE TABLE lines (
    line_id SERIAL PRIMARY KEY,
    verse_id INTEGER NOT NULL,
    line_number INTEGER NOT NULL,  -- Line number within the verse (1, 2, 3, 4...)
    line_text TEXT NOT NULL,
    line_text_transliteration TEXT,  -- Roman transliteration
    line_text_translation TEXT,  -- English/other language translation
    metadata JSONB,  -- Flexible metadata: line-specific annotations, rhetorical figures, syntax notes, etc.
    FOREIGN KEY (verse_id) REFERENCES verses(verse_id),
    UNIQUE (verse_id, line_number)
);

CREATE INDEX idx_lines_verse ON lines(verse_id);

-- Words table (every word with its position)
CREATE TABLE words (
    word_id SERIAL PRIMARY KEY,
    line_id INTEGER NOT NULL,
    word_position INTEGER NOT NULL,  -- Position in the line (1, 2, 3...)
    word_text VARCHAR(200) NOT NULL,
    word_text_transliteration VARCHAR(200),
    word_root VARCHAR(200),  -- Root/base form of the word
    word_type VARCHAR(50),  -- noun, verb, adjective, etc.
    sandhi_split VARCHAR(500),  -- If word is result of sandhi, show components
    meaning TEXT,
    metadata JSONB,  -- Flexible metadata: etymology, semantic field, theological significance, frequency, etc.
    FOREIGN KEY (line_id) REFERENCES lines(line_id),
    UNIQUE (line_id, word_position)
);

CREATE INDEX idx_words_line ON words(line_id);
CREATE INDEX idx_words_text ON words(word_text);
CREATE INDEX idx_words_root ON words(word_root);
CREATE INDEX idx_words_text_line ON words(word_text, line_id);
CREATE INDEX idx_words_root_text ON words(word_root, word_text) WHERE word_root IS NOT NULL;

-- Junction table: Sections can belong to multiple collections
-- Enables collections by theme (thinai), structure type, etc.
CREATE TABLE section_collections (
    section_collection_id SERIAL PRIMARY KEY,
    section_id INTEGER NOT NULL,
    collection_id INTEGER NOT NULL,
    position_in_collection INTEGER,  -- Order within this specific collection
    notes TEXT,  -- Collection-specific notes about this section
    FOREIGN KEY (section_id) REFERENCES sections(section_id) ON DELETE CASCADE,
    FOREIGN KEY (collection_id) REFERENCES collections(collection_id) ON DELETE CASCADE,
    UNIQUE (section_id, collection_id)
);

-- Junction table: Verses can belong to multiple collections
-- Enables collections by author, meter, theme, thinai, etc.
CREATE TABLE verse_collections (
    verse_collection_id SERIAL PRIMARY KEY,
    verse_id INTEGER NOT NULL,
    collection_id INTEGER NOT NULL,
    position_in_collection INTEGER,  -- Order within this specific collection
    notes TEXT,  -- Collection-specific notes about this verse (author, meter, etc.)
    FOREIGN KEY (verse_id) REFERENCES verses(verse_id) ON DELETE CASCADE,
    FOREIGN KEY (collection_id) REFERENCES collections(collection_id) ON DELETE CASCADE,
    UNIQUE (verse_id, collection_id)
);

-- Indexes for junction tables
CREATE INDEX idx_section_collections_section ON section_collections(section_id);
CREATE INDEX idx_section_collections_collection ON section_collections(collection_id);
CREATE INDEX idx_verse_collections_verse ON verse_collections(verse_id);
CREATE INDEX idx_verse_collections_collection ON verse_collections(collection_id);

-- GIN indexes for JSONB metadata columns (for fast JSON queries)
CREATE INDEX idx_works_metadata ON works USING GIN (metadata);
CREATE INDEX idx_sections_metadata ON sections USING GIN (metadata);
CREATE INDEX idx_verses_metadata ON verses USING GIN (metadata);
CREATE INDEX idx_lines_metadata ON lines USING GIN (metadata);
CREATE INDEX idx_words_metadata ON words USING GIN (metadata);

-- Full-text search for words (if your database supports it)
-- For SQLite:
-- CREATE VIRTUAL TABLE words_fts USING fts5(word_text, word_root, content=words, content_rowid=word_id);

-- ============================================================================
-- METADATA AND ANNOTATION TABLES
-- ============================================================================

-- Commentary/annotations on verses
CREATE TABLE commentaries (
    commentary_id SERIAL PRIMARY KEY,
    verse_id INTEGER NOT NULL,
    commentator VARCHAR(200),
    commentator_tamil VARCHAR(200),
    commentary_text TEXT NOT NULL,
    commentary_period VARCHAR(100),
    FOREIGN KEY (verse_id) REFERENCES verses(verse_id)
);

-- Cross-references between verses
CREATE TABLE cross_references (
    reference_id SERIAL PRIMARY KEY,
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
    w.canonical_order as canonical_position,  -- Direct from works table
    w.chronology_start_year,
    w.chronology_end_year,
    w.chronology_confidence,
    sp.path_names as hierarchy_path,
    sp.path_names_tamil as hierarchy_path_tamil,
    sp.depth as hierarchy_depth
FROM verses v
INNER JOIN works w ON v.work_id = w.work_id
INNER JOIN section_path sp ON v.section_id = sp.section_id;

-- Complete word information with full context
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
    v.work_id,  -- Work ID for efficient JOINs
    v.section_id,  -- Section ID for efficient JOINs
    v.total_lines,  -- Total lines in this verse
    vh.verse_type,
    vh.verse_type_tamil,
    vh.work_name,
    vh.work_name_tamil,
    vh.canonical_position,  -- From works.canonical_order (via verse_hierarchy view)
    vh.chronology_start_year,
    vh.chronology_end_year,
    vh.chronology_confidence,
    vh.hierarchy_path,
    vh.hierarchy_path_tamil,
    wvc.work_verse_count,  -- Total verses in the work
    s.sort_order as section_sort_order,  -- Section sort order for hierarchical sorting
    v.sort_order as verse_sort_order     -- Verse sort order for hierarchical sorting
FROM words w
INNER JOIN lines l ON w.line_id = l.line_id
INNER JOIN verses v ON l.verse_id = v.verse_id
INNER JOIN sections s ON v.section_id = s.section_id
INNER JOIN verse_hierarchy vh ON v.verse_id = vh.verse_id
INNER JOIN work_verse_counts wvc ON v.work_id = wvc.work_id;

-- Removed: works_with_primary_collection view
-- Use work_collections table for collection relationships instead
-- Query example: SELECT w.*, c.* FROM works w JOIN work_collections wc ON w.work_id = wc.work_id JOIN collections c ON wc.collection_id = c.collection_id WHERE wc.is_primary = TRUE;

-- View: Collection hierarchy with item counts (works, sections, verses)
CREATE VIEW collection_hierarchy AS
WITH RECURSIVE coll_tree AS (
    -- Base case: top-level collections
    SELECT
        c.collection_id,
        c.collection_name,
        c.collection_name_tamil,
        c.collection_type,
        c.entity_type,
        c.parent_collection_id,
        c.sort_order,
        0 AS depth,
        ARRAY[c.collection_id] AS path,
        c.collection_name::TEXT AS full_path
    FROM collections c
    WHERE c.parent_collection_id IS NULL

    UNION ALL

    -- Recursive case: child collections
    SELECT
        c.collection_id,
        c.collection_name,
        c.collection_name_tamil,
        c.collection_type,
        c.entity_type,
        c.parent_collection_id,
        c.sort_order,
        ct.depth + 1,
        ct.path || c.collection_id,
        ct.full_path || ' > ' || c.collection_name
    FROM collections c
    JOIN coll_tree ct ON c.parent_collection_id = ct.collection_id
)
SELECT
    ct.*,
    COUNT(DISTINCT wc.work_id) AS work_count,
    COUNT(DISTINCT sc.section_id) AS section_count,
    COUNT(DISTINCT vc.verse_id) AS verse_count
FROM coll_tree ct
LEFT JOIN work_collections wc ON ct.collection_id = wc.collection_id
LEFT JOIN section_collections sc ON ct.collection_id = sc.collection_id
LEFT JOIN verse_collections vc ON ct.collection_id = vc.collection_id
GROUP BY ct.collection_id, ct.collection_name, ct.collection_name_tamil,
         ct.collection_type, ct.entity_type, ct.parent_collection_id, ct.sort_order,
         ct.depth, ct.path, ct.full_path
ORDER BY ct.path;

-- View: Works in collections with hierarchy
CREATE VIEW works_in_collections AS
SELECT
    w.work_id,
    w.work_name,
    w.work_name_tamil,
    c.collection_id,
    c.collection_name,
    c.collection_name_tamil,
    c.collection_type,
    wc.position_in_collection,
    wc.is_primary,
    pc.collection_name AS parent_collection_name,
    pc.collection_name_tamil AS parent_collection_name_tamil
FROM works w
JOIN work_collections wc ON w.work_id = wc.work_id
JOIN collections c ON wc.collection_id = c.collection_id
LEFT JOIN collections pc ON c.parent_collection_id = pc.collection_id
ORDER BY c.collection_id, wc.position_in_collection;

-- View: Sections in collections with hierarchy
CREATE VIEW sections_in_collections AS
SELECT
    s.section_id,
    s.work_id,
    s.section_name,
    s.section_name_tamil,
    s.level_type,
    s.level_type_tamil,
    c.collection_id,
    c.collection_name,
    c.collection_name_tamil,
    c.collection_type,
    sc.position_in_collection,
    sc.notes,
    pc.collection_name AS parent_collection_name,
    pc.collection_name_tamil AS parent_collection_name_tamil
FROM sections s
JOIN section_collections sc ON s.section_id = sc.section_id
JOIN collections c ON sc.collection_id = c.collection_id
LEFT JOIN collections pc ON c.parent_collection_id = pc.collection_id
ORDER BY c.collection_id, sc.position_in_collection;

-- View: Verses in collections with hierarchy
CREATE VIEW verses_in_collections AS
SELECT
    v.verse_id,
    v.work_id,
    v.verse_number,
    v.verse_type,
    v.verse_type_tamil,
    c.collection_id,
    c.collection_name,
    c.collection_name_tamil,
    c.collection_type,
    vc.position_in_collection,
    vc.notes,
    pc.collection_name AS parent_collection_name,
    pc.collection_name_tamil AS parent_collection_name_tamil
FROM verses v
JOIN verse_collections vc ON v.verse_id = vc.verse_id
JOIN collections c ON vc.collection_id = c.collection_id
LEFT JOIN collections pc ON c.parent_collection_id = pc.collection_id
ORDER BY c.collection_id, vc.position_in_collection;

-- ============================================================================
-- COMMON QUERY EXAMPLES
-- ============================================================================
--
-- Note: No sample data is inserted by default. Use parser scripts to populate:
--   - python scripts/thirukkural_bulk_import.py
--   - python scripts/sangam_bulk_import.py
--   - python scripts/silapathikaram_bulk_import.py
--   - python scripts/kambaramayanam_bulk_import.py
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

-- ============================================================================
-- ADMIN USERS TABLE
-- ============================================================================

CREATE TABLE admin_users (
    user_id SERIAL PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index for username lookup
CREATE INDEX idx_admin_users_username ON admin_users(username);
