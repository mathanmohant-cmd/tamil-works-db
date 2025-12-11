# Parser Fixes - December 5, 2025

## Problem Summary

When running bulk import parsers after dropping and recreating the database, parsers were failing with:
```
psycopg2.errors.UniqueViolation: duplicate key value violates unique constraint "sections_pkey"
DETAIL: Key (section_id)=(1) already exists.
```

## Root Causes

### 1. Hardcoded IDs Starting at 1
**Files affected:**
- `thirukkural_bulk_import.py`
- `silapathikaram_bulk_import.py`
- `kambaramayanam_bulk_import.py`

**Problem:** IDs were hardcoded to start at 1 in `__init__()`:
```python
self.section_id = 1
self.verse_id = 1
self.line_id = 1
self.word_id = 1
```

**Issue:** When a parser ran after another work was already imported, it would try to insert duplicate IDs.

**Fix:** Query the database for current MAX IDs:
```python
# Get existing max IDs from database
self.cursor.execute("SELECT COALESCE(MAX(section_id), 0) FROM sections")
self.section_id = self.cursor.fetchone()[0] + 1

self.cursor.execute("SELECT COALESCE(MAX(verse_id), 0) FROM verses")
self.verse_id = self.cursor.fetchone()[0] + 1

self.cursor.execute("SELECT COALESCE(MAX(line_id), 0) FROM lines")
self.line_id = self.cursor.fetchone()[0] + 1

self.cursor.execute("SELECT COALESCE(MAX(word_id), 0) FROM words")
self.word_id = self.cursor.fetchone()[0] + 1
```

### 2. Multiple Works in Loop - Duplicate work_id Assignment
**File affected:** `sangam_bulk_import.py`

**Problem:** When creating 18 Sangam works, the script queried `MAX(work_id)` **inside the loop** for each work:
```python
for filename, work_info in self.SANGAM_WORKS.items():
    # ...
    # Get next available work_id
    self.cursor.execute("SELECT COALESCE(MAX(work_id), 0) + 1 FROM works")
    new_work_id = self.cursor.fetchone()[0]  # ← WRONG! Same ID for all new works
    work_info['work_id'] = new_work_id
```

**Issue:** All 18 new works would get the same work_id (e.g., all get ID=3).

**Fix:** Query MAX once before the loop, increment manually:
```python
# Get next available work_id ONCE before the loop
self.cursor.execute("SELECT COALESCE(MAX(work_id), 0) FROM works")
next_work_id = self.cursor.fetchone()[0] + 1

for filename, work_info in self.SANGAM_WORKS.items():
    # ...
    if not existing:
        work_info['work_id'] = next_work_id
        # ... append to self.works ...
        next_work_id += 1  # ← Increment for next work
```

### 3. Sequences Not Reset When Dropping Tables
**File affected:** `setup_railway_db.py`

**Problem:** The `drop_tables()` function dropped tables but not their sequences:
```python
cursor.execute("""
    DROP TABLE IF EXISTS words CASCADE;
    DROP TABLE IF EXISTS lines CASCADE;
    -- ... etc
""")
```

**Issue:** If sequences existed (from previous schema versions), they could cause conflicts.

**Fix:** Also drop sequences:
```python
# Drop tables
cursor.execute("""
    DROP TABLE IF EXISTS words CASCADE;
    -- ... etc
""")

# Reset sequences
cursor.execute("""
    DROP SEQUENCE IF EXISTS works_work_id_seq CASCADE;
    DROP SEQUENCE IF EXISTS sections_section_id_seq CASCADE;
    DROP SEQUENCE IF EXISTS verses_verse_id_seq CASCADE;
    DROP SEQUENCE IF EXISTS lines_line_id_seq CASCADE;
    DROP SEQUENCE IF EXISTS words_word_id_seq CASCADE;
""")
```

## Files Modified

1. ✅ `scripts/thirukkural_bulk_import.py` - Added MAX ID queries in `__init__()`
2. ✅ `scripts/silapathikaram_bulk_import.py` - Set IDs to None (properly set in `_ensure_work_exists()`)
3. ✅ `scripts/kambaramayanam_bulk_import.py` - Set IDs to None (properly set in `_ensure_work_exists()`)
4. ✅ `scripts/sangam_bulk_import.py` - Fixed work_id allocation in `_ensure_works_exist()`
5. ✅ `scripts/setup_railway_db.py` - Added sequence dropping
6. ✅ `CLAUDE.md` - Added critical ID allocation patterns section

## Already Correct

- ✅ `tolkappiyam_bulk_import.py` - Already queried MAX IDs in `__init__()`
- ✅ `sangam_bulk_import.py` - Already queried MAX IDs for sections/verses/lines/words

## Testing Results

After fixes, all parsers can now be run in **any order**:

```bash
# Clean database
python scripts/setup_railway_db.py

# Import in any order - all work correctly
python scripts/thirukkural_bulk_import.py      # ✓ Works
python scripts/tolkappiyam_bulk_import.py       # ✓ Works
python scripts/sangam_bulk_import.py            # ✓ Works (18 works, IDs 3-20)
python scripts/silapathikaram_bulk_import.py    # ✓ Works
python scripts/kambaramayanam_bulk_import.py    # ✓ Works
```

## Key Lessons for Future Parsers

1. **ALWAYS** query `MAX(id)` from database for ALL ID fields
2. **NEVER** hardcode starting IDs to 1
3. **For multiple works in one script**: Query MAX once, increment manually
4. **Test parsers** after other works have been imported (not just on empty database)
5. **Schema uses INTEGER PRIMARY KEY** (not SERIAL) - manual ID management required
