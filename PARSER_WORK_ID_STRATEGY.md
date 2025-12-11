# Parser work_id Assignment Strategy

**Last Updated:** 2025-12-05

## Strategy: Dynamic Assignment (Option 1)

All parsers use `MAX(work_id) + 1` to ensure work_ids are assigned in **import order**.

## Implementation

All bulk import parsers follow this pattern:

```python
def _ensure_work_exists(self):
    """Ensure work entry exists"""
    work_name_english = 'WorkName'
    work_name_tamil = 'தமிழ்_பெயர்'

    # Check if work already exists by name
    self.cursor.execute("SELECT work_id FROM works WHERE work_name = %s", (work_name_english,))
    existing = self.cursor.fetchone()

    if existing:
        self.work_id = existing[0]
        print(f"  Work {work_name_tamil} already exists (ID: {self.work_id})")
    else:
        # Get next available work_id
        self.cursor.execute("SELECT COALESCE(MAX(work_id), 0) + 1 FROM works")
        self.work_id = self.cursor.fetchone()[0]

        print(f"  Creating work entry (ID: {self.work_id})...")
        # ... insert work
```

## Updated Parsers

✅ **thirukkural_bulk_import.py**
- Changed from: `self.work_id = 3` (hardcoded)
- Changed to: Dynamic `MAX(work_id) + 1`

✅ **sangam_bulk_import.py**
- Changed from: Hardcoded work_ids 4-21 in SANGAM_WORKS dictionary
- Changed to: Dynamic assignment for each work in `_ensure_works_exist()`
- Note: Each of the 18 Sangam works gets its own work_id

✅ **silapathikaram_bulk_import.py**
- Already using dynamic assignment ✓

✅ **kambaramayanam_bulk_import.py**
- Already using dynamic assignment ✓

✅ **tolkappiyam_bulk_import.py**
- Changed from: `WORK_ID = 1` (hardcoded)
- Changed to: Dynamic `MAX(work_id) + 1`

## Current Database State

**After running parsers in this order:**
1. Thirukkural → work_id 3
2. Sangam (18 works) → work_ids 4-21
3. Silapathikaram → work_id 22
4. Kambaramayanam → work_id 23
5. Tolkappiyam → work_id 1

**Gap:** work_id 2 is currently unassigned.

## Future Imports

**Next fresh import order will be:**
1. Thirukkural → work_id 1
2. Sangam (18 works) → work_ids 2-19
3. Silapathikaram → work_id 20
4. Kambaramayanam → work_id 21
5. Tolkappiyam → work_id 22

## Benefits

1. **Import order determines IDs** - No hardcoded values
2. **Flexible** - Can import in any order
3. **Re-import safe** - Checks by name first
4. **No gaps** - Sequential from 1 when starting fresh
5. **Consistent** - All parsers use same strategy

## Recommendations

- Import works in the desired priority order
- For fresh database: Import in this order for traditional sequencing:
  1. Tolkappiyam (grammar foundation)
  2. Thirukkural (ethics)
  3. Sangam Literature (classical poetry)
  4. Silapathikaram (epic)
  5. Kambaramayanam (epic)
