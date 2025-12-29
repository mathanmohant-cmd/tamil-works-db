# Testing Devotional Literature Parsers

## Completed Parsers Ready for Testing

### 1. Devaram Bulk Import (Files 1-7)
**Script:** `devaram_bulk_import.py`
**Covers:** 7 files, 3 authors (Sambandar, Appar, Sundarar), ~7,200 verses

```bash
# Test with local database
python scripts/devaram_bulk_import.py

# Or specify database URL
python scripts/devaram_bulk_import.py "postgresql://postgres:postgres@localhost/tamil_literature"
```

**Expected Output:**
- 7 works created (Sambandar 1-3, Appar 1-3, Sundarar)
- Hundreds of pathigams (sections)
- ~7,200 verses
- ~30,000+ lines
- ~150,000+ words

### 2. Thiruvasagam Bulk Import (File 8.1)
**Script:** `thiruvasagam_bulk_import.py`
**Covers:** 1 work (Manikkavasagar), 51 pathigams

```bash
# Test with local database
python scripts/thiruvasagam_bulk_import.py

# Or specify database URL
python scripts/thiruvasagam_bulk_import.py "postgresql://postgres:postgres@localhost/tamil_literature"
```

**Expected Output:**
- 1 work created (Thiruvasagam)
- 51 pathigams (sections)
- 51 verses (one per pathigam)
- Thousands of lines
- Tens of thousands of words

## Prerequisites

### 1. Database Schema
Ensure you have the metadata columns:
```bash
psql tamil_literature -f sql/migrations/add_metadata_columns.sql
```

### 2. Source Files
Ensure files exist in:
```
C:\Claude\Projects\tamil-works-db\Tamil-Source-TamilConcordence\6_பக்தி இலக்கியம்\
```

Required files:
- `1.முதலாம் திருமுறை.txt`
- `2.இரண்டாம் திருமுறை.txt`
- `3.மூன்றாம் திருமுறை.txt`
- `4.நான்காம்_திருமுறை.txt`
- `5.ஐந்தாம் திருமுறை.txt`
- `6.ஆறாம் திருமுறை.txt`
- `7.ஏழாம் திருமுறை.txt`
- `8.1எட்டாம் திருமுறை.txt`

## Verification Queries

After importing, verify the data:

```sql
-- Check works imported
SELECT work_id, work_name_tamil, author_tamil,
       metadata->>'tradition' as tradition,
       metadata->>'collection_name' as collection
FROM works
WHERE metadata->>'collection_id' = '321'
ORDER BY work_id;

-- Check pathigam count by work
SELECT w.work_name_tamil,
       COUNT(DISTINCT s.section_id) as pathigam_count,
       COUNT(DISTINCT v.verse_id) as verse_count
FROM works w
LEFT JOIN sections s ON w.work_id = s.work_id
LEFT JOIN verses v ON w.work_id = v.work_id
WHERE w.metadata->>'collection_id' = '321'
GROUP BY w.work_id, w.work_name_tamil
ORDER BY w.work_id;

-- Check sample verses with metadata
SELECT v.verse_id,
       w.work_name_tamil,
       s.section_name_tamil as pathigam,
       v.verse_number,
       v.metadata->>'pann' as musical_mode,
       v.total_lines
FROM verses v
JOIN works w ON v.work_id = w.work_id
LEFT JOIN sections s ON v.section_id = s.section_id
WHERE w.metadata->>'collection_id' = '321'
LIMIT 20;

-- Check word count
SELECT w.work_name_tamil,
       COUNT(wo.word_id) as word_count
FROM works w
LEFT JOIN verses v ON w.work_id = v.work_id
LEFT JOIN lines l ON v.verse_id = l.verse_id
LEFT JOIN words wo ON l.line_id = wo.line_id
WHERE w.metadata->>'collection_id' = '321'
GROUP BY w.work_id, w.work_name_tamil
ORDER BY w.work_id;

-- Search for a common word (example: சிவன்)
SELECT w.work_name_tamil,
       s.section_name_tamil,
       v.verse_number,
       l.line_text
FROM words wo
JOIN lines l ON wo.line_id = l.line_id
JOIN verses v ON l.verse_id = v.verse_id
LEFT JOIN sections s ON v.section_id = s.section_id
JOIN works w ON v.work_id = w.work_id
WHERE wo.word_text = 'சிவன்'
  AND w.metadata->>'collection_id' = '321'
LIMIT 10;
```

## Known Issues / Notes

1. **Underscores in text:** Words with underscores (compound markers like `மெய்_ஞானம்`) are split into separate words
2. **Line numbers:** Numeric line markers on the right are cleaned/removed
3. **மேல் separator:** Used to mark end of verses/pathigams
4. **Sandhi split:** Currently NULL (not yet implemented)

## Troubleshooting

### Error: "relation works has no column metadata"
Run the migration:
```bash
psql tamil_literature -f sql/migrations/add_metadata_columns.sql
```

### Error: "File not found"
Check that source files exist in the correct directory with the exact file names (including Tamil characters)

### Error: "psycopg2 module not found"
Install dependencies:
```bash
pip install psycopg2-binary
```

### Import seems slow
This is normal for large imports. The 2-phase bulk COPY should still be much faster than row-by-row INSERT. Expected time:
- Devaram (7 files): 30-60 seconds
- Thiruvasagam: 5-10 seconds

## Success Criteria

✅ All works created without errors
✅ Section hierarchy preserved (pathigams)
✅ Verses numbered correctly
✅ All lines imported
✅ Words segmented properly
✅ Metadata populated (JSONB fields)
✅ Can search for words and find results

## Next Steps After Testing

Once these 2 parsers are verified:
1. Continue creating remaining parsers (11 more)
2. Test each parser individually
3. Create master import script
4. Final integration testing

## Reference Documents

- `DEVOTIONAL_LITERATURE_STRUCTURE.md` - Complete file structure reference
- `METADATA_INTEGRATION_GUIDE.md` - Metadata field documentation
- CSV: `Tamil-Source-TamilConcordence\6_பக்தி இலக்கியம்\Tamilconcordance.in - Sheet2.csv`
