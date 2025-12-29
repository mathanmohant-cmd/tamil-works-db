# Metadata Implementation Checklist

## What You Have Now

✅ **Migration SQL file** - `sql/migrations/add_metadata_columns.sql`
  - Adds JSONB `metadata` column to all tables (works, sections, verses, lines, words)
  - Creates GIN indexes for fast JSON queries
  - Includes helper functions and views

✅ **Integration Guide** - `scripts/METADATA_INTEGRATION_GUIDE.md`
  - Complete guide with examples for all metadata levels
  - Query examples
  - Performance notes

✅ **Thirumurai Example** - `scripts/thirumurai_metadata_example.py`
  - Shows exact code changes needed for Thirumurai import
  - Saint metadata for Devaram works (Files 1-7)
  - Complete metadata for Thiruvasagam, Thirumanthiram, Periya Puranam
  - Updated bulk_insert methods with metadata

✅ **Divya Prabandham Example** - `scripts/naalayira_divya_prabandham_metadata_example.py`
  - Metadata for all 12 Alvars
  - Divya Desam (108 temples) metadata structure
  - Detailed examples for Thiruppavai and Thiruvaymozhi
  - Helper functions for creating metadata

## Next Steps

### 1. Run the Migration (5 minutes)

```bash
# Connect to your database and run:
psql tamil_literature -f sql/migrations/add_metadata_columns.sql

# Or if using password:
psql -U postgres -d tamil_literature -f sql/migrations/add_metadata_columns.sql

# Verify columns were added:
psql tamil_literature -c "\d works"
psql tamil_literature -c "\d sections"
psql tamil_literature -c "\d verses"
```

### 2. Update Devotional Literature Import Scripts (2-3 hours per script)

For each import script in `scripts/`:

#### A. Thirumurai (`thirumurai_bulk_import.py`)
- [ ] Add `import json` at top
- [ ] Copy saint metadata from `thirumurai_metadata_example.py`
- [ ] Update `_create_work()` to include metadata dictionary
- [ ] Update `_create_section()` to include pathigam metadata
- [ ] Update `_create_verse()` to include verse metadata
- [ ] Update `bulk_insert_works()` to serialize and include metadata
- [ ] Update `bulk_insert_sections()` to serialize and include metadata
- [ ] Update `bulk_insert_verses()` to serialize and include metadata

#### B. Naalayira Divya Prabandham (`naalayira_divya_prabandham_bulk_import.py`)
- [ ] Add `import json` at top
- [ ] Copy Alvar metadata from `naalayira_divya_prabandham_metadata_example.py`
- [ ] Copy Divya Desam metadata (or subset)
- [ ] Update work creation to include Alvar metadata
- [ ] Update verse creation to include divya desam references
- [ ] Update bulk_insert methods

#### C. Other Devotional Works
- [ ] `thiruppugazh_bulk_import.py` - Add Murugan worship metadata
- [ ] `thembavani_bulk_import.py` - Add Christian devotional metadata
- [ ] `seerapuranam_bulk_import.py` - Add Islamic devotional metadata

### 3. Test with Small Dataset (30 minutes)

```bash
# Import one work to test metadata
python scripts/thirumurai_bulk_import.py

# Query to verify metadata was imported
psql tamil_literature -c "
SELECT work_name_tamil,
       metadata->>'tradition' as tradition,
       metadata->>'saint' as saint,
       metadata->>'time_period' as period
FROM works
WHERE metadata->>'collection_id' = '321'
LIMIT 5;
"

# Check verse metadata
psql tamil_literature -c "
SELECT verse_id,
       metadata->>'alvar' as alvar,
       metadata->>'deity' as deity,
       metadata->>'raga' as raga
FROM verses
WHERE metadata IS NOT NULL
LIMIT 10;
"
```

### 4. Full Import (1-2 hours)

Once testing confirms metadata is working:

```bash
# Import all devotional literature with metadata
python scripts/import_devotional_literature.py
```

### 5. Verify and Query (30 minutes)

```sql
-- Count works by tradition
SELECT metadata->>'tradition' as tradition, COUNT(*)
FROM works
WHERE metadata->>'tradition' IS NOT NULL
GROUP BY metadata->>'tradition';

-- Find all works from 7th century
SELECT work_name_tamil, metadata->>'saint', metadata->>'time_period'
FROM works
WHERE metadata->>'time_period' LIKE '%7th century%';

-- Find verses addressing specific deity at specific temple
SELECT v.verse_id, l.line_text,
       v.metadata->>'deity' as deity,
       v.metadata->>'divya_desam' as temple
FROM verses v
JOIN lines l ON v.verse_id = l.verse_id
WHERE v.metadata->>'divya_desam' = 'திருவரங்கம்'
LIMIT 20;

-- Find all pathigams with musical mode (pann)
SELECT section_name_tamil,
       metadata->>'pann' as musical_mode,
       metadata->>'temple' as temple
FROM sections
WHERE metadata->>'pann' IS NOT NULL
LIMIT 10;

-- Get statistics on metadata coverage
SELECT
  'works' as table_name,
  COUNT(*) as total_rows,
  COUNT(metadata) as with_metadata,
  ROUND(100.0 * COUNT(metadata) / COUNT(*), 2) as percentage
FROM works
UNION ALL
SELECT 'sections', COUNT(*), COUNT(metadata),
       ROUND(100.0 * COUNT(metadata) / COUNT(*), 2)
FROM sections
UNION ALL
SELECT 'verses', COUNT(*), COUNT(metadata),
       ROUND(100.0 * COUNT(metadata) / COUNT(*), 2)
FROM verses;
```

## Key Metadata Fields by Tradition

### Shaivite (Thirumurai)
- `tradition`: "Shaivite"
- `collection_id`: 321
- `saint`: Name of Nayanmar (e.g., "திருஞானசம்பந்தர்")
- `deity_focus`: "Shiva"
- `pann`: Musical mode (section level)
- `temple`: Temple name (section/verse level)

### Vaishnavite (Naalayira Divya Prabandham)
- `tradition`: "Vaishnavite"
- `collection_id`: 322
- `alvar`: Name of Alvar (e.g., "நம்மாழ்வார்")
- `deity_focus`: "Vishnu"
- `divya_desam`: One of 108 sacred temples
- `deity_form`: Specific form (Ranganatha, Venkateswara, etc.)

### Others
- **Thiruppugazh**: `tradition`: "Murugan worship", `deity_focus`: "Murugan"
- **Thembavani**: `tradition`: "Christian", `deity_focus`: "Christ"
- **Seerapuranam**: `tradition`: "Islamic", `subject`: "Prophet Muhammad"

## Performance Impact

- Migration: ~1 second (just adds columns)
- Import with metadata: ~5-10% slower than without (still 1000x faster than row-by-row)
- Queries on metadata with GIN index: Very fast (<100ms for most queries)

## Optional: Add to Existing Data Later

If you already imported devotional literature without metadata, you can add it later:

```sql
-- Example: Add metadata to existing Thirumurai works
UPDATE works
SET metadata = '{
  "tradition": "Shaivite",
  "collection_id": 321,
  "liturgical_use": true
}'::jsonb
WHERE work_name LIKE '%Devaram%';

-- Or use helper function:
SELECT add_metadata('works', 'work_id', 100, 'saint', '"திருஞானசம்பந்தர்"'::jsonb);
```

## Questions?

- See `scripts/METADATA_INTEGRATION_GUIDE.md` for detailed examples
- See `scripts/thirumurai_metadata_example.py` for Shaivite examples
- See `scripts/naalayira_divya_prabandham_metadata_example.py` for Vaishnavite examples
- Test queries in `sql/migrations/add_metadata_columns.sql` for helper functions

## Timeline Estimate

- Migration: 5 minutes
- Update one import script: 2-3 hours
- Update all devotional scripts: 1-2 days
- Testing and verification: 1-2 hours
- **Total: 2-3 days for complete metadata integration**
