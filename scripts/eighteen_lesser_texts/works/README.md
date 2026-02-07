# Individual Work Scripts - Eighteen Lesser Texts

This directory contains individual atomic import and delete scripts for each of the 18 Eighteen Lesser Texts (பதினெண்கீழ்க்கணக்கு) works.

## Script Status

### ✅ Ready (10 works - Flat Structure)
- Nanmanikkadigai (நான்மணிக்கடிகை)
- Inna Narpathu (இன்னா நாற்பது)
- Iniyavai Narpathu (இனியவை நாற்பது)
- Kar Narpathu (கார் நாற்பது)
- Kalavazhi Narpathu (களவழி நாற்பது)
- Thirigadugam (திரிகடுகம்)
- Asarakkovai (ஆசாரக்கோவை)
- Pazhamozhi Nanuru (பழமொழி நானூறு)
- Sirupanchamoolam (சிறுபஞ்சமூலம்)
- Elathi (ஏலாதி)

### ⏳ Pending (8 works - Complex Structures)
- **Adhikaram Structure (1 work):**
  - Naladiyar (நாலடியார்)

- **Thinai Structure (5 works):**
  - Ainthinai Aimbathu (ஐந்திணை ஐம்பது)
  - Ainthinai Ezhubathu (ஐந்திணை எழுபது)
  - Thinaymozhi Aimbathu (திணைமொழி ஐம்பது)
  - Thinaimalai Noorraimpathu (திணைமாலை நூற்றைம்பது)
  - Kainnilai (கைந்நிலை)

- **Paththu Structure (1 work):**
  - Muthumozhikkanchi (முதுமொழிக் காஞ்சி)

- **Thirukkural Special (1 work):**
  - Thirukkural (திருக்குறள்) - 3-level hierarchy

## Usage

### Standalone Import (Single Work)

```bash
# Import with default collection (201)
python import_inna_narpathu.py

# Import with custom database URL
python import_inna_narpathu.py postgresql://user:pass@host/db

# Import to different collection
python import_inna_narpathu.py --collection-id 201 --position 3
```

### Standalone Delete (Single Work)

```bash
# Delete a work
python delete_inna_narpathu.py

# With custom database URL
python delete_inna_narpathu.py postgresql://user:pass@host/db
```

### Via Master Orchestrator (Recommended)

```bash
# Import all available works
cd ../master
python import_all.py

# Delete all works
cd ../master
python delete_all.py
```

## Script Architecture

### Import Scripts

Each `import_*.py` script:

1. **Inherits from BaseWorkImporter**
   - Automatic ID allocation
   - Collection creation (idempotent)
   - Atomic transaction handling
   - Bulk insert with single commit

2. **Work Creation**
   - Checks for duplicates
   - Creates work entry (in memory)
   - Links to collection 201 by default
   - All in single transaction

3. **Structure-Specific Parsing**
   - Flat: Single default section
   - Thinai: Sections by thinai (landscape)
   - Paththu: Sections by paththu groups
   - Adhikaram: Hierarchical adhikaram chapters
   - Thirukkural: 3-level (Paal→Iyal→Adhikaram)

4. **Phase 1: Parse**
   - Read concordance file
   - Build in-memory data structures
   - Clean lines and words
   - No database writes

5. **Phase 2: Bulk Insert**
   - PostgreSQL COPY command
   - Single transaction
   - Atomic (all or nothing)
   - Rollback on error

### Delete Scripts

Each `delete_*.py` script:

1. **Find Work**
   - Search by work name
   - Report if not found

2. **Show Stats**
   - Count sections, verses, lines, words
   - Confirm with user

3. **Delete Atomically**
   - Delete in reverse dependency order:
     1. words
     2. lines
     3. verses
     4. sections
     5. work_collections
     6. works
   - Single transaction
   - Rollback on error

## Features

### ✅ Atomicity
- Each work import is a single transaction
- Work + collection link + all data inserted together
- Rollback on any error
- No orphaned works possible

### ✅ ID Management
- Query MAX IDs at initialization
- Works correctly after delete + reimport
- No ID conflicts

### ✅ Collection Management
- Individual scripts create collection if needed (idempotent)
- Collection 201 created by first work
- All works link to same collection

### ✅ Error Handling
- Duplicate detection
- Proper rollback on error
- Clear error messages
- Exit codes for scripting

## Examples

### Example 1: Import Single Work

```bash
$ python import_inna_narpathu.py
======================================================================
Inna Narpathu Atomic Import
======================================================================
Database: postgresql://postgres:postgres@localhost/tamil...
  Starting IDs: work=150, section=500, verse=5000, line=20000, word=100000
  Collection 201 already exists
  Work இன்னா நாற்பது will be linked to collection 201

Phase 1: Parsing file...
Text file: 3-இன்னா நாற்பது.txt
[OK] Phase 1 complete: Parsed 40 paadals
  - Sections: 1
  - Paadals: 40
  - Lines: 160
  - Words: 800

Phase 2: Bulk inserting into database...
  Inserting 1 work(s)...
  Linking 1 work(s) to collection...
  Inserting 1 sections...
  Inserting 40 verses...
  Inserting 160 lines...
  Inserting 800 words...
[OK] Phase 2 complete: All data inserted atomically

[OK] Import complete!
```

### Example 2: Delete Single Work

```bash
$ python delete_inna_narpathu.py
======================================================================
  DELETE இன்னா நாற்பது (Inna Narpathu)
======================================================================
Database: postgresql://postgres:postgres@localhost/tamil...

This will delete:
  - 1 work (இன்னா நாற்பது)
  - 1 sections
  - 40 verses
  - 160 lines
  - 800 words

Are you sure? (yes/no): yes

Deleting work data...
  ✓ Deleted 800 words
  ✓ Deleted 160 lines
  ✓ Deleted 40 verses
  ✓ Deleted 1 sections
  ✓ Unlinked from collections
  ✓ Deleted work entry

✓ Successfully deleted இன்னா நாற்பது

✓ Deletion complete
```

### Example 3: Delete + Reimport (ID Test)

```bash
$ # Check current MAX work_id
$ psql -U postgres -d tamil_literature -c "SELECT MAX(work_id) FROM works"
 max
------
 149

$ # Import work
$ python import_inna_narpathu.py
...
[OK] Import complete!

$ # Check new MAX work_id
$ psql -U postgres -d tamil_literature -c "SELECT MAX(work_id) FROM works"
 max
------
 150

$ # Delete work
$ python delete_inna_narpathu.py
...
✓ Deletion complete

$ # Reimport - should use work_id 151 (not 150)
$ python import_inna_narpathu.py
...
  Starting IDs: work=151, section=...
[OK] Import complete!

$ # Verify new work_id
$ psql -U postgres -d tamil_literature -c "SELECT MAX(work_id) FROM works"
 max
------
 151
```

## See Also

- `../master/README.md` - Master orchestrator documentation
- `../shared/` - Shared infrastructure
  - `base_importer.py` - BaseWorkImporter class
  - `work_metadata.py` - Metadata for all 18 works
  - `utils.py` - Shared utilities
- `../../CLAUDE.md` - Project documentation
