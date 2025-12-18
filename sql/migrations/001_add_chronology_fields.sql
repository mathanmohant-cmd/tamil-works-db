-- ============================================================================
-- Migration: Add chronology fields to works table
-- Date: 2025-12-18
-- Description: Adds traditional_sort_order and chronological dating fields
-- ============================================================================

-- Add new columns to works table (if they don't exist)
ALTER TABLE works
ADD COLUMN IF NOT EXISTS traditional_sort_order INTEGER;

ALTER TABLE works
ADD COLUMN IF NOT EXISTS chronology_start_year INTEGER;

ALTER TABLE works
ADD COLUMN IF NOT EXISTS chronology_end_year INTEGER;

ALTER TABLE works
ADD COLUMN IF NOT EXISTS chronology_confidence VARCHAR(20);

ALTER TABLE works
ADD COLUMN IF NOT EXISTS chronology_notes TEXT;

-- Add comments for documentation
COMMENT ON COLUMN works.traditional_sort_order IS 'Traditional sequence in Tamil literary canon (1, 2, 3...)';
COMMENT ON COLUMN works.chronology_start_year IS 'Approximate start year (negative = BCE, positive = CE)';
COMMENT ON COLUMN works.chronology_end_year IS 'Approximate end year (negative = BCE, positive = CE)';
COMMENT ON COLUMN works.chronology_confidence IS 'Confidence level: high, medium, low, disputed';
COMMENT ON COLUMN works.chronology_notes IS 'Scholarly variations and dating debates';

-- Verify the migration
SELECT
    column_name,
    data_type,
    is_nullable
FROM information_schema.columns
WHERE table_name = 'works'
    AND column_name IN (
        'traditional_sort_order',
        'chronology_start_year',
        'chronology_end_year',
        'chronology_confidence',
        'chronology_notes'
    )
ORDER BY ordinal_position;
