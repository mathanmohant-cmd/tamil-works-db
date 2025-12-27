# Database Design Fixes - 2025-12-25

## Summary

Fixed two major database design issues:
1. **Removed hardcoded collection_id = 100** from views
2. **Migrated to SERIAL auto-increment IDs** for all primary keys

---

## Issue 1: Hardcoded Collection ID in Views

### Problem
The `verse_hierarchy` and `word_details` views used a hardcoded `collection_id = 100` (Traditional Canon) that didn't exist:

```sql
-- OLD (BROKEN)
LEFT JOIN work_collections wc_canon ON w.work_id = wc_canon.work_id
  AND wc_canon.collection_id = 100;  -- Collection 100 doesn't exist!
-- Result: canonical_position was always NULL
```

This caused a mismatch:
- **Backend `get_works()`**: Used `w.canonical_order as canonical_position` ✓ (worked)
- **Backend `search_words()`**: Used `wd.canonical_position` from view ✗ (always NULL)
- **Frontend**: Expected `canonical_position` for sorting (worked for works list, broken for search results)

### Solution
Changed views to use `works.canonical_order` directly:

```sql
-- NEW (FIXED)
SELECT
    v.verse_id,
    ...
    w.canonical_order as canonical_position,  -- Direct from works table
    ...
FROM verses v
INNER JOIN works w ON v.work_id = w.work_id
INNER JOIN section_path sp ON v.section_id = sp.section_id;
-- No more collection join!
```

### Files Changed
- `sql/complete_setup.sql` - Updated view definitions (lines 237, 273)
  - This file is used by `scripts/setup_railway_db.py` for database setup
- Database views recreated in production (temp_recreate_views.sql, then deleted)

### Verification
```bash
# Confirmed canonical_position now has real values:
SELECT work_name, canonical_position FROM verse_hierarchy LIMIT 5;
# Tolkappiyam | 100
# Natrrinai   | 200
# ...

# Backend search confirmed working:
# First result canonical_position: 206 (Aganaanuru)
```

---

## Issue 2: Manual ID Management (INTEGER → SERIAL)

### Problem
All primary keys were `INTEGER PRIMARY KEY` instead of `SERIAL`:
- Parsers had to manually query `SELECT COALESCE(MAX(id), 0) + 1` before inserting
- Error-prone if parser forgets to query MAX
- No database-level guarantee of uniqueness

### Solution
Migrated all primary keys to SERIAL (auto-increment):

**For existing database (with data):**
- Created `sql/migrate_to_serial_ids.sql` migration script
- Added sequences for all ID columns
- Set sequences to start from `MAX(id) + 1`
- Preserved all existing data and foreign keys

**For new databases:**
- Updated `sql/complete_setup.sql` schema to use SERIAL from the start
- New installations using `setup_railway_db.py` will automatically have SERIAL IDs

### Tables Migrated
| Table | Sequence Created | Next Value |
|-------|------------------|------------|
| works | works_work_id_seq | 79 |
| collections | collections_collection_id_seq | 11 |
| sections | sections_section_id_seq | 1564 |
| verses | verses_verse_id_seq | 43550 |
| lines | lines_line_id_seq | 194181 |
| words | words_word_id_seq | 1141329 |
| commentaries | commentaries_commentary_id_seq | 1 |
| cross_references | cross_references_reference_id_seq | 1 |

### Files Changed
- `sql/migrate_to_serial_ids.sql` - Migration script for existing databases (NEW)
- `sql/complete_setup.sql` - Changed all `INTEGER PRIMARY KEY` to `SERIAL PRIMARY KEY`
  - Used by `scripts/setup_railway_db.py` for fresh database installations

### Verification
```bash
# Tested sequences:
SELECT nextval('works_work_id_seq'), nextval('sections_section_id_seq');
# 79 | 1564  ✓ Correct!
```

---

## Impact on Parsers

### Before (Manual ID Management)
```python
class ThirukkuralBulkImporter:
    def __init__(self, db_connection_string: str):
        # Had to manually query MAX IDs
        self.cursor.execute("SELECT COALESCE(MAX(section_id), 0) FROM sections")
        self.section_id = self.cursor.fetchone()[0] + 1

        self.cursor.execute("SELECT COALESCE(MAX(verse_id), 0) FROM verses")
        self.verse_id = self.cursor.fetchone()[0] + 1
        # ... repeat for all tables
```

### After (SERIAL Auto-Increment)
```python
class ThirukkuralBulkImporter:
    def __init__(self, db_connection_string: str):
        # Can now use INSERT ... RETURNING pattern
        pass

    def insert_work(self):
        self.cursor.execute("""
            INSERT INTO works (work_name, work_name_tamil, ...)
            VALUES (%s, %s, ...)
            RETURNING work_id
        """, values)
        self.work_id = self.cursor.fetchone()[0]  # Auto-generated!
```

**Note:** Existing parsers still use manual ID management for backward compatibility. They can be refactored gradually.

---

## Testing Performed

### ✅ View Fix Testing
1. Queried `verse_hierarchy` - confirmed canonical_position has real values
2. Queried `word_details` - confirmed canonical_position inherited from verse_hierarchy
3. Backend search test - confirmed search results include correct canonical_position (206 for Aganaanuru)

### ✅ SERIAL Migration Testing
1. Migration script executed successfully
2. All sequences created with correct starting values
3. nextval() tested - returns expected IDs
4. Existing data preserved - all 78 works, 43,549 verses, 1,141,328 words intact

---

## Recommendations Moving Forward

### Immediate
- [x] Remove hardcoded collection_id = 100 from views
- [x] Migrate to SERIAL IDs
- [ ] Update parser templates to use INSERT ... RETURNING pattern

### Future
- [ ] Refactor existing parsers to use SERIAL pattern (optional - they still work)
- [ ] Populate `work_collections` table to assign works to collections
- [ ] Create collection management utility for organizing works

---

## Files Added/Modified

### Added
- `sql/migrate_to_serial_ids.sql` - SERIAL migration script (for existing databases)
- `DB_DESIGN_FIXES_2025-12-25.md` - This documentation

### Modified
- `sql/complete_setup.sql` - View definitions fixed, SERIAL types added
  - This is the single source of truth for schema
  - Used by `scripts/setup_railway_db.py` (Python wrapper for database setup)
- Database views recreated in production (verse_hierarchy, word_details)

### Database Setup Architecture
```
┌─────────────────────────────────┐
│ scripts/setup_railway_db.py     │  ← Python wrapper
│ - Tests connection              │
│ - Drops existing tables         │
│ - Executes SQL file ────────────┼──┐
│ - Verifies setup                │  │
└─────────────────────────────────┘  │
                                     │
                                     ▼
                    ┌────────────────────────────────┐
                    │ sql/complete_setup.sql         │  ← Source of truth
                    │ - CREATE TABLE statements      │
                    │ - CREATE VIEW statements       │
                    │ - CREATE INDEX statements      │
                    │ - All SERIAL IDs               │
                    │ - Fixed canonical_position     │
                    └────────────────────────────────┘
```

**There is NO redundancy** - `setup_railway_db.py` is a convenience wrapper that executes `complete_setup.sql`.

---

## Current Database Status

- **Works:** 78
- **Verses:** 43,549
- **Words:** 1,141,328
- **Collections:** 10
- **All primary keys:** SERIAL (auto-increment)
- **All views:** Using canonical_order (no collection dependency)

---

**Date:** 2025-12-25
**Status:** ✅ All fixes applied and tested
**Breaking Changes:** None (backward compatible)
