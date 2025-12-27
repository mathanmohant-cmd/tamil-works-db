-- ============================================================================
-- MIGRATION: Convert INTEGER PRIMARY KEYs to SERIAL (auto-increment)
-- ============================================================================
-- This migration adds sequences to existing ID columns without recreating tables
-- Preserves all existing data and foreign key relationships
--
-- Run with: PGPASSWORD=postgres psql -U postgres tamil_literature -f sql/migrate_to_serial_ids.sql
-- ============================================================================

BEGIN;

-- ============================================================================
-- 1. WORKS TABLE
-- ============================================================================
-- Create sequence starting from next available ID
CREATE SEQUENCE IF NOT EXISTS works_work_id_seq;
SELECT setval('works_work_id_seq', COALESCE((SELECT MAX(work_id) FROM works), 0) + 1, false);

-- Set default to use sequence
ALTER TABLE works ALTER COLUMN work_id SET DEFAULT nextval('works_work_id_seq');

-- Assign sequence ownership (so it's dropped when column is dropped)
ALTER SEQUENCE works_work_id_seq OWNED BY works.work_id;

COMMENT ON COLUMN works.work_id IS 'Auto-increment primary key (SERIAL equivalent)';

-- ============================================================================
-- 2. COLLECTIONS TABLE (already has SERIAL work_collection_id, but collection_id is INTEGER)
-- ============================================================================
CREATE SEQUENCE IF NOT EXISTS collections_collection_id_seq;
SELECT setval('collections_collection_id_seq', COALESCE((SELECT MAX(collection_id) FROM collections), 0) + 1, false);

ALTER TABLE collections ALTER COLUMN collection_id SET DEFAULT nextval('collections_collection_id_seq');
ALTER SEQUENCE collections_collection_id_seq OWNED BY collections.collection_id;

COMMENT ON COLUMN collections.collection_id IS 'Auto-increment primary key (SERIAL equivalent)';

-- ============================================================================
-- 3. SECTIONS TABLE
-- ============================================================================
CREATE SEQUENCE IF NOT EXISTS sections_section_id_seq;
SELECT setval('sections_section_id_seq', COALESCE((SELECT MAX(section_id) FROM sections), 0) + 1, false);

ALTER TABLE sections ALTER COLUMN section_id SET DEFAULT nextval('sections_section_id_seq');
ALTER SEQUENCE sections_section_id_seq OWNED BY sections.section_id;

COMMENT ON COLUMN sections.section_id IS 'Auto-increment primary key (SERIAL equivalent)';

-- ============================================================================
-- 4. VERSES TABLE
-- ============================================================================
CREATE SEQUENCE IF NOT EXISTS verses_verse_id_seq;
SELECT setval('verses_verse_id_seq', COALESCE((SELECT MAX(verse_id) FROM verses), 0) + 1, false);

ALTER TABLE verses ALTER COLUMN verse_id SET DEFAULT nextval('verses_verse_id_seq');
ALTER SEQUENCE verses_verse_id_seq OWNED BY verses.verse_id;

COMMENT ON COLUMN verses.verse_id IS 'Auto-increment primary key (SERIAL equivalent)';

-- ============================================================================
-- 5. LINES TABLE
-- ============================================================================
CREATE SEQUENCE IF NOT EXISTS lines_line_id_seq;
SELECT setval('lines_line_id_seq', COALESCE((SELECT MAX(line_id) FROM lines), 0) + 1, false);

ALTER TABLE lines ALTER COLUMN line_id SET DEFAULT nextval('lines_line_id_seq');
ALTER SEQUENCE lines_line_id_seq OWNED BY lines.line_id;

COMMENT ON COLUMN lines.line_id IS 'Auto-increment primary key (SERIAL equivalent)';

-- ============================================================================
-- 6. WORDS TABLE
-- ============================================================================
CREATE SEQUENCE IF NOT EXISTS words_word_id_seq;
SELECT setval('words_word_id_seq', COALESCE((SELECT MAX(word_id) FROM words), 0) + 1, false);

ALTER TABLE words ALTER COLUMN word_id SET DEFAULT nextval('words_word_id_seq');
ALTER SEQUENCE words_word_id_seq OWNED BY words.word_id;

COMMENT ON COLUMN words.word_id IS 'Auto-increment primary key (SERIAL equivalent)';

-- ============================================================================
-- 7. COMMENTARIES TABLE
-- ============================================================================
CREATE SEQUENCE IF NOT EXISTS commentaries_commentary_id_seq;
SELECT setval('commentaries_commentary_id_seq', COALESCE((SELECT MAX(commentary_id) FROM commentaries), 0) + 1, false);

ALTER TABLE commentaries ALTER COLUMN commentary_id SET DEFAULT nextval('commentaries_commentary_id_seq');
ALTER SEQUENCE commentaries_commentary_id_seq OWNED BY commentaries.commentary_id;

COMMENT ON COLUMN commentaries.commentary_id IS 'Auto-increment primary key (SERIAL equivalent)';

-- ============================================================================
-- 8. CROSS_REFERENCES TABLE
-- ============================================================================
CREATE SEQUENCE IF NOT EXISTS cross_references_reference_id_seq;
SELECT setval('cross_references_reference_id_seq', COALESCE((SELECT MAX(reference_id) FROM cross_references), 0) + 1, false);

ALTER TABLE cross_references ALTER COLUMN reference_id SET DEFAULT nextval('cross_references_reference_id_seq');
ALTER SEQUENCE cross_references_reference_id_seq OWNED BY cross_references.reference_id;

COMMENT ON COLUMN cross_references.reference_id IS 'Auto-increment primary key (SERIAL equivalent)';

-- ============================================================================
-- Verify sequences
-- ============================================================================
DO $$
DECLARE
    seq_info RECORD;
BEGIN
    RAISE NOTICE '';
    RAISE NOTICE '============================================================================';
    RAISE NOTICE 'MIGRATION COMPLETE - Sequence Status';
    RAISE NOTICE '============================================================================';

    FOR seq_info IN
        SELECT
            schemaname,
            sequencename,
            last_value,
            increment_by
        FROM pg_sequences
        WHERE sequencename LIKE '%_id_seq'
        ORDER BY sequencename
    LOOP
        RAISE NOTICE 'Sequence: % | Next Value: %',
            seq_info.sequencename,
            seq_info.last_value + seq_info.increment_by;
    END LOOP;

    RAISE NOTICE '============================================================================';
END $$;

COMMIT;

-- ============================================================================
-- USAGE NOTES:
-- ============================================================================
-- After this migration, you can insert new records without specifying IDs:
--
--   INSERT INTO works (work_name, work_name_tamil, ...)
--   VALUES ('New Work', 'புதிய நூல்', ...)
--   RETURNING work_id;  -- Returns auto-generated ID
--
-- Parsers can now simplify ID management:
--   - Remove: SELECT COALESCE(MAX(id), 0) + 1 queries
--   - Use: INSERT ... RETURNING id pattern instead
-- ============================================================================
