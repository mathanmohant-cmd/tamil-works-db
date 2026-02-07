# Eighteen Lesser Texts (பதினெண்கீழ்க்கணக்கு)

Modular atomic import/delete architecture for all 18 Eighteen Lesser Texts works.

## Architecture Overview

This directory implements a **modular orchestrated architecture** with:
- ✅ **Individual atomic scripts** for each work (import + delete pairs)
- ✅ **Master orchestrators** for coordinated bulk operations
- ✅ **Shared infrastructure** for code reuse (BaseWorkImporter)
- ✅ **Proper atomicity** - no orphaned works possible

## Directory Structure

```
eighteen_lesser_texts/
├── master/              # Master orchestration scripts
│   ├── import_all.py   # Import all available works
│   ├── delete_all.py   # Delete all works (hybrid search)
│   └── README.md       # Master orchestration docs
│
├── works/              # Individual work scripts (36 files when complete)
│   ├── import_*.py     # 18 import scripts (10 ready, 8 pending)
│   ├── delete_*.py     # 18 delete scripts (10 ready, 8 pending)
│   └── README.md       # Individual work usage docs
│
└── shared/             # Shared infrastructure
    ├── __init__.py
    ├── base_importer.py      # BaseWorkImporter class (~300 lines)
    ├── work_metadata.py      # Metadata for all 18 works
    └── utils.py              # Shared utilities
```

## Current Status

### ✅ Completed Infrastructure
- **Folder structure** organized by responsibility
- **BaseWorkImporter class** eliminates 200+ lines of duplicate code per script
- **WORK_METADATA dictionary** centralizes all work metadata
- **Shared utilities** for line cleaning, word splitting
- **Master orchestrators** for bulk import/delete
- **10 flat structure works** complete with import/delete pairs
- **Comprehensive documentation** (3 README files)

### ⏳ Pending Work (8 works)
- **Naladiyar** - Adhikaram structure (need hierarchy parsing)
- **5 Thinai works** - Need thinai section parsing
- **Muthumozhikkanchi** - Paththu structure
- **Thirukkural** - Special 3-level hierarchy (may use existing standalone script)

## Quick Start

### Import All Available Works

```bash
cd scripts/eighteen_lesser_texts/master
python import_all.py
```

This imports 10/18 works currently available (all flat structure works).

### Delete All Works

```bash
cd scripts/eighteen_lesser_texts/master
python delete_all.py
```

Uses hybrid search to find and delete all Eighteen Lesser Texts works, including orphans.

### Import Single Work

```bash
cd scripts/eighteen_lesser_texts/works
python import_inna_narpathu.py
```

### Delete Single Work

```bash
cd scripts/eighteen_lesser_texts/works
python delete_inna_narpathu.py
```

## Key Features

### 🔒 Atomicity Guaranteed
- Each work import is a single transaction
- Work + collection link + all data inserted together
- Rollback on any error
- No orphaned works possible (work_collections always inserted with work)

### 🔄 Delete + Reimport Safe
- ID allocation uses MAX queries at initialization
- After deletion, MAX IDs remain at highest ever used
- Next import starts from MAX + 1
- No ID conflicts

### 🔍 Orphan Detection (Delete Script)
The master delete script uses **hybrid search**:
1. Search by collection JOIN (finds properly linked works)
2. Search by work name list (finds orphaned works from broken imports)
3. Reports orphans before deletion

### 📊 Progress Reporting
- Master import shows X/N progress for each work
- Detailed phase reporting (parse → insert)
- Summary at end showing success/failure counts

### 💪 Error Resilience
- Individual scripts rollback on error (clean state)
- Master orchestrators continue on failure (report at end)
- Clear error messages with troubleshooting hints

## Architecture Decisions

### Why Individual Scripts Are Primary
- Users can import single works directly
- Easier to test and debug
- Supports selective imports
- Better modularity

### Why Master is Thin Wrapper
- Individual scripts manage collection creation
- Individual scripts handle atomicity
- Master just coordinates and reports
- No duplicate logic

### Why BaseWorkImporter Class
- Eliminates 200+ lines of duplicate code per script
- Ensures consistent transaction handling
- Single source of truth for:
  - ID allocation
  - Collection creation
  - Atomic bulk insert
  - Error handling

### Why Separate Folders
- **master/** - Orchestration only
- **works/** - Individual scripts only
- **shared/** - Reusable infrastructure
- Clear separation of concerns

## Workflow Examples

### First Time Setup

```bash
# 1. Import all available works
cd scripts/eighteen_lesser_texts/master
python import_all.py

# 2. Verify in database
psql -U postgres -d tamil_literature -c "
  SELECT COUNT(*) FROM works w
  JOIN work_collections wc ON w.work_id = wc.work_id
  WHERE wc.collection_id = 201;
"
# Expected: 10

# 3. Check for orphans (should be 0)
psql -U postgres -d tamil_literature -c "
  SELECT COUNT(*) FROM works
  WHERE work_name IN ('Nanmanikkadigai', 'Inna Narpathu', ...)
  AND work_id NOT IN (
    SELECT work_id FROM work_collections WHERE collection_id = 201
  );
"
# Expected: 0
```

### Reimport After Changes

```bash
# 1. Delete all works
cd scripts/eighteen_lesser_texts/master
python delete_all.py

# 2. Reimport all works
python import_all.py

# 3. Verify IDs incremented (no conflicts)
psql -U postgres -d tamil_literature -c "SELECT MAX(work_id) FROM works"
```

### Add Single Work

```bash
# Import just one work
cd scripts/eighteen_lesser_texts/works
python import_kar_narpathu.py

# Verify it's linked to collection
psql -U postgres -d tamil_literature -c "
  SELECT w.work_name, wc.collection_id, wc.position_in_collection
  FROM works w
  JOIN work_collections wc ON w.work_id = wc.work_id
  WHERE w.work_name = 'Kar Narpathu';
"
```

### Remove Single Work

```bash
# Delete just one work
cd scripts/eighteen_lesser_texts/works
python delete_kar_narpathu.py
```

## Testing

### Test Atomicity (Error Rollback)

```bash
# 1. Note current work count
psql -U postgres -d tamil_literature -c "SELECT COUNT(*) FROM works"

# 2. Modify an import script to inject an error (e.g., invalid SQL)
# 3. Run the modified import script
python import_modified_work.py

# 4. Verify rollback - work count unchanged
psql -U postgres -d tamil_literature -c "SELECT COUNT(*) FROM works"
```

### Test Delete + Reimport

```bash
# Run the delete+reimport example above
# Verify MAX IDs increment correctly
```

### Test Orphan Detection

```bash
# 1. Manually create orphan (INSERT work without collection link)
psql -U postgres -d tamil_literature -c "
  INSERT INTO works (work_id, work_name, work_name_tamil)
  VALUES (9999, 'Test Orphan', 'சோதனை');
"

# 2. Run delete script - should detect orphan
cd scripts/eighteen_lesser_texts/master
python delete_all.py

# Output should show:
# ⚠ Warning: Found 1 orphaned work(s)
#   - சோதனை (Test Orphan) - ID: 9999 [ORPHAN]
```

## File Counts

- **Shared infrastructure**: 4 files (init, base, metadata, utils)
- **Master orchestrators**: 2 files (import, delete)
- **Individual scripts**: 20 files (10 works × 2 scripts each)
- **Documentation**: 4 files (3 READMEs + this overview)
- **Total**: 30 files

**When complete (all 18 works):**
- Individual scripts: 36 files (18 works × 2 scripts each)
- **Total**: 46 files

## Next Steps

To complete the remaining 8 works:

1. **Create thinai structure parser** (5 works)
   - Copy from existing `ainthinai_aimbathu_bulk_import.py`
   - Add section creation for thinai markers (@N)

2. **Create adhikaram structure parser** (1 work: Naladiyar)
   - Copy from existing `naladiyar_bulk_import.py`
   - Add 3-level hierarchy (Paal→Iyal→Adhikaram)

3. **Create paththu structure parser** (1 work: Muthumozhikkanchi)
   - Copy from existing `muthumozhikkanchi_bulk_import.py`
   - Add paththu section grouping

4. **Integrate Thirukkural** (1 work)
   - May reuse existing standalone `thirukkural_bulk_import.py`
   - Or refactor to inherit from BaseWorkImporter

## See Also

- `master/README.md` - Master orchestration documentation
- `works/README.md` - Individual work scripts documentation
- `shared/base_importer.py` - Core infrastructure
- `../CLAUDE.md` - Project-wide documentation
- `../../COLLECTION_ID_MAP.md` - Collection ID scheme

## Success Criteria

✅ **Folder structure created** with master/, works/, shared/ separation
✅ **BaseWorkImporter class** extracts all duplicate code (200+ lines per script)
✅ **10 individual import scripts** generated and ready
✅ **10 individual delete scripts** generated and ready
✅ **Master import orchestrator** calls individuals sequentially
✅ **Master delete orchestrator** uses hybrid search + calls individuals
✅ **Individual scripts are standalone** - can import single works directly
✅ **Collection management** handled by individual scripts (idempotent)
✅ **Each work import is atomic** - single transaction with rollback on error
✅ **ID management robust** - delete + reimport doesn't create conflicts
✅ **No orphaned works** - work_collections always inserted with work
✅ **Error resilience** - master continues on individual failures
✅ **Documentation complete** - 4 README files

⏳ **Remaining**: 8 structure-specific parsers (thinai, paththu, adhikaram, thirukkural)
