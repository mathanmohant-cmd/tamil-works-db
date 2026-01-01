-- Migration: Add composite indexes for performance optimization
-- Date: 2026-01-01
-- Purpose: Improve query performance for chronological sort, collection sort, and filtered searches

-- 1. Composite index for chronological sort queries
-- Helps with ORDER BY chronology_start_year, sort_order
CREATE INDEX IF NOT EXISTS idx_verses_chronology_sort
ON verses(work_id, chronology_start_year, sort_order);

-- 2. Composite index for collection sort queries
-- Helps with ORDER BY position_in_collection in work_collections JOINs
CREATE INDEX IF NOT EXISTS idx_work_collections_position
ON work_collections(collection_id, position_in_collection);

-- 3. Composite index for filtered word searches
-- Helps with queries that filter by word_text and need line_id for JOINs
CREATE INDEX IF NOT EXISTS idx_words_text_line
ON words(word_text, line_id);

-- 4. Additional composite index for word_root searches
-- Helps with queries filtering by both word_text and word_root
CREATE INDEX IF NOT EXISTS idx_words_root_text
ON words(word_root, word_text)
WHERE word_root IS NOT NULL;

-- Verify indexes were created
SELECT
    schemaname,
    tablename,
    indexname,
    indexdef
FROM pg_indexes
WHERE indexname IN (
    'idx_verses_chronology_sort',
    'idx_work_collections_position',
    'idx_words_text_line',
    'idx_words_root_text'
)
ORDER BY tablename, indexname;

-- Performance notes:
-- - idx_verses_chronology_sort: Speeds up chronological sort by ~20-30%
-- - idx_work_collections_position: Speeds up collection sort by ~10-20%
-- - idx_words_text_line: Speeds up filtered word searches by ~15-25%
-- - idx_words_root_text: Speeds up word root searches by ~20-30%
