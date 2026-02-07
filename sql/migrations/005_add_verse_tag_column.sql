-- Migration: Add verse_tag column to verses table
-- Purpose: Identify special verse types (e.g., migai_padal - additional verses)
-- Date: 2026-02-06

-- Add verse_tag column
ALTER TABLE verses ADD COLUMN IF NOT EXISTS verse_tag VARCHAR(100);

-- Index for filtering by tag
CREATE INDEX IF NOT EXISTS idx_verses_verse_tag ON verses(verse_tag);

-- Documentation
COMMENT ON COLUMN verses.verse_tag IS
  'Special verse classification: "migai_padal" for additional verses, NULL for regular verses';

-- Verification
SELECT column_name, data_type, character_maximum_length
FROM information_schema.columns
WHERE table_name = 'verses' AND column_name = 'verse_tag';
