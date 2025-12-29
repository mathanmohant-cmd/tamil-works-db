-- Migration: Add JSONB metadata columns to all tables
-- Created: 2025-12-27
-- Purpose: Support flexible metadata at all hierarchical levels
--
-- IDEMPOTENT: This migration can be run multiple times safely.
-- - Uses IF NOT EXISTS for columns and indexes
-- - Uses CREATE OR REPLACE for functions and views
-- - Safe to run on existing databases with or without metadata columns

-- ============================================================================
-- STEP 1: Add metadata columns to all tables
-- ============================================================================
ALTER TABLE works ADD COLUMN IF NOT EXISTS metadata JSONB;
ALTER TABLE sections ADD COLUMN IF NOT EXISTS metadata JSONB;
ALTER TABLE verses ADD COLUMN IF NOT EXISTS metadata JSONB;
ALTER TABLE lines ADD COLUMN IF NOT EXISTS metadata JSONB;
ALTER TABLE words ADD COLUMN IF NOT EXISTS metadata JSONB;

-- ============================================================================
-- STEP 2: Create GIN indexes for fast JSON queries
-- ============================================================================
CREATE INDEX IF NOT EXISTS idx_works_metadata ON works USING GIN (metadata);
CREATE INDEX IF NOT EXISTS idx_sections_metadata ON sections USING GIN (metadata);
CREATE INDEX IF NOT EXISTS idx_verses_metadata ON verses USING GIN (metadata);
CREATE INDEX IF NOT EXISTS idx_lines_metadata ON lines USING GIN (metadata);
CREATE INDEX IF NOT EXISTS idx_words_metadata ON words USING GIN (metadata);

-- ============================================================================
-- STEP 3: Create helper functions for metadata manipulation
-- ============================================================================

-- Helper function to safely add/update metadata fields
CREATE OR REPLACE FUNCTION add_metadata(
  table_name TEXT,
  id_column TEXT,
  record_id INTEGER,
  key TEXT,
  value JSONB
) RETURNS void AS $$
BEGIN
  EXECUTE format(
    'UPDATE %I SET metadata = coalesce(metadata, ''{}''::jsonb) || jsonb_build_object($1, $2) WHERE %I = $3',
    table_name,
    id_column
  ) USING key, value, record_id;
END;
$$ LANGUAGE plpgsql;

-- Helper function to get metadata value
CREATE OR REPLACE FUNCTION get_metadata(
  table_name TEXT,
  id_column TEXT,
  record_id INTEGER,
  key TEXT
) RETURNS JSONB AS $$
DECLARE
  result JSONB;
BEGIN
  EXECUTE format(
    'SELECT metadata->$1 FROM %I WHERE %I = $2',
    table_name,
    id_column
  ) USING key, record_id INTO result;
  RETURN result;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- STEP 4: Create convenience views for common metadata access
-- ============================================================================

-- Create view for works with metadata expanded
CREATE OR REPLACE VIEW works_with_metadata AS
SELECT
  w.*,
  w.metadata->>'tradition' as tradition,
  w.metadata->>'time_period' as time_period,
  w.metadata->>'collection_name' as collection_name,
  (w.metadata->>'collection_id')::integer as collection_metadata_id,
  w.metadata->'authors' as authors,
  w.metadata->'themes' as themes
FROM works w;

-- Create view for verses with metadata expanded
CREATE OR REPLACE VIEW verses_with_metadata AS
SELECT
  v.*,
  v.metadata->>'saint' as saint,
  v.metadata->>'deity' as deity,
  v.metadata->>'raga' as raga,
  v.metadata->>'meter' as metadata_meter,  -- Renamed to avoid conflict with existing meter column
  v.metadata->'themes' as themes,
  v.metadata->'literary_devices' as literary_devices
FROM verses v;

-- ============================================================================
-- STEP 5: Add documentation comments
-- ============================================================================

COMMENT ON COLUMN works.metadata IS 'Flexible metadata storage (tradition, time_period, authors, etc.)';
COMMENT ON COLUMN sections.metadata IS 'Flexible metadata storage (thematic_category, musical_mode, etc.)';
COMMENT ON COLUMN verses.metadata IS 'Flexible metadata storage (saint, deity, raga, meter, themes, etc.)';
COMMENT ON COLUMN lines.metadata IS 'Flexible metadata storage (line-specific annotations)';
COMMENT ON COLUMN words.metadata IS 'Flexible metadata storage (etymology, semantic_field, theological_significance, etc.)';

-- ============================================================================
-- Migration Complete
-- ============================================================================
--
-- Metadata columns have been added to:
--   - works, sections, verses, lines, words
--
-- GIN indexes created for fast JSON queries on all metadata columns
--
-- Helper functions available:
--   - add_metadata(table_name, id_column, record_id, key, value)
--   - get_metadata(table_name, id_column, record_id, key)
--
-- Convenience views available:
--   - works_with_metadata
--   - verses_with_metadata
--
-- This migration is idempotent and can be run multiple times safely.
-- ============================================================================
