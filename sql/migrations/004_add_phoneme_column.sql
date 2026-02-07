-- Migration: Add phoneme column to words table
-- Date: 2026-01-26
-- Purpose: Store phonemic representation of Tamil words with decomposed consonant+vowel combinations
--
-- Phonemic representation decomposes all consonant+vowel combinations into constituent parts:
-- Pattern: [consonant][vowel_sign] → [consonant][்][independent_vowel]
-- Example: ஒல்லென → ஒல்ல்என (where லெ → ல் + எ)

BEGIN;

-- Add phoneme column to words table
ALTER TABLE words
ADD COLUMN IF NOT EXISTS phoneme VARCHAR(200);

-- Add comment describing the column
COMMENT ON COLUMN words.phoneme IS 'Phonemic representation with decomposed consonant+vowel combinations. Example: ஒல்லென → ஒல்ல்என';

-- Add index for potential phoneme-based searches
-- Partial index (WHERE phoneme IS NOT NULL) reduces index size since column starts NULL
CREATE INDEX IF NOT EXISTS idx_words_phoneme ON words(phoneme) WHERE phoneme IS NOT NULL;

-- Verify migration
SELECT
    column_name,
    data_type,
    character_maximum_length,
    is_nullable,
    column_default
FROM information_schema.columns
WHERE table_name = 'words'
    AND column_name = 'phoneme';

COMMIT;

-- Migration completed successfully
-- Next steps:
--   1. Run: python scripts/tamil_phoneme_converter.py (test converter)
--   2. Run: python scripts/populate_phoneme_column.py (populate all words)
--   3. Run: psql -U postgres -d tamil_literature -f sql/verify_phoneme_column.sql (verify)
