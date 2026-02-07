# Master Orchestrators - Eighteen Lesser Texts

This directory contains master orchestration scripts for importing and deleting all Eighteen Lesser Texts (பதினெண்கீழ்க்கணக்கு) as a collection.

## Available Scripts

### import_all.py
Imports all available Eighteen Lesser Texts works into collection 201.

**Usage:**
```bash
# Import all works
python import_all.py

# Specify database URL
python import_all.py postgresql://postgres:postgres@localhost/tamil_literature
```

**What it does:**
1. Calls individual work import scripts sequentially
2. Each work is imported atomically (separate transaction)
3. Collection 201 created by first work if needed
4. Reports progress (X/N) for each work
5. Shows summary at the end

**Current Status:**
- ✅ 10/18 works ready (flat structure works)
- ⏳ 8/18 works pending (thinai, paththu, adhikaram, thirukkural structures)

### delete_all.py
Deletes all Eighteen Lesser Texts works and collection 201.

**Usage:**
```bash
# Delete all works
python delete_all.py

# Specify database URL
python delete_all.py postgresql://postgres:postgres@localhost/tamil_literature
```

**What it does:**
1. Uses **hybrid search** to find works:
   - Searches by collection JOIN (finds properly linked works)
   - Searches by work name list (finds orphaned works)
2. Reports orphans if found
3. Shows deletion stats
4. Confirms with user before deleting
5. Calls individual delete scripts when available
6. Falls back to inline deletion if script missing
7. Deletes collection 201 after all works deleted

**Features:**
- ✅ Finds orphaned works (not linked to collection)
- ✅ Works even if individual delete scripts missing
- ✅ Atomic deletion for each work
- ✅ Progress reporting

## Architecture

The master orchestrators are **thin convenience wrappers** that:
- Coordinate individual work scripts
- Manage collection lifecycle
- Report progress and errors
- Continue on failures (resilient)

**Responsibilities:**
- ❌ Do NOT manage collection creation (individual scripts do)
- ❌ Do NOT handle parsing (individual scripts do)
- ✅ Only coordinate and report

## Examples

### Import All Available Works
```bash
cd scripts/eighteen_lesser_texts/master
python import_all.py
```

Output:
```
======================================================================
  MASTER IMPORT: Eighteen Lesser Texts (10 works ready)
======================================================================

Note: Each work import is atomic (separate transaction)
      Collection 201 created by first work if needed

Importing 10 works...

[1/10] Importing Nanmanikkadigai...
    Phase 1: Parsing file...
    [OK] Phase 1 complete: Parsed 106 paadals
    Phase 2: Bulk inserting into database...
    [OK] Phase 2 complete: All data inserted atomically
    [OK] Import complete!

[2/10] Importing Inna Narpathu...
...

======================================================================
  IMPORT SUMMARY
======================================================================
  ✓ Successfully imported: 10/10 works

✓ All 10 works imported successfully!

Note: This imported 10/18 total works
      Remaining works need structure-specific parsers
```

### Delete All Works
```bash
cd scripts/eighteen_lesser_texts/master
python delete_all.py
```

Output:
```
======================================================================
  DELETE ALL: Eighteen Lesser Texts + Collection 201
======================================================================

Searching for Eighteen Lesser Texts...

Found 10 work(s):
  - நான்மணிக்கடிகை (Nanmanikkadigai) - ID: 150
  - இன்னா நாற்பது (Inna Narpathu) - ID: 151
  ...

This will delete:
  - 10 works (Eighteen Lesser Texts)
  - 10 sections
  - 840 verses
  - 3,360 lines
  - 25,200 words
  - Collection 201 (பதினெண்கீழ்க்கணக்கு)

Are you sure? (yes/no): yes

Deleting 10 works...

[1/10] Deleting நான்மணிக்கடிகை...
  ✓ Deleted நான்மணிக்கடிகை

...

Deleting collection 201...
  ✓ Deleted collection 201 (பதினெண்கீழ்க்கணக்கு)

======================================================================
  DELETION SUMMARY
======================================================================
  ✓ Successfully deleted: 10/10 works

✓ All 10 works deleted successfully!
```

## Error Handling

The orchestrators are resilient:
- **Import**: Continues on failure, shows which works failed
- **Delete**: Continues on failure, skips collection deletion if any work failed
- **Orphan Detection**: Finds and reports orphaned works

## Notes

- Each work import is atomic (single transaction)
- N separate transactions for N works
- Fast enough to re-run entire collection on failure
- ID management ensures delete + reimport works correctly
- Master scripts do NOT create collections (individual scripts do)

## See Also

- `../works/README.md` - Individual work scripts documentation
- `../shared/` - Shared infrastructure (BaseWorkImporter, metadata, utilities)
- `../../CLAUDE.md` - Project-wide documentation
