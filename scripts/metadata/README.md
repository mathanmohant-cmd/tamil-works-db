# Work Metadata Schema Specification

This directory contains centralized metadata for all Tamil literary works in the database. Each Python file defines metadata for one collection of works.

## Directory Structure

```
metadata/
├── README.md (this file)
├── __init__.py
├── sangam_metadata.py              # 18 Sangam works
├── eighteen_lesser_texts_metadata.py  # 18 works
├── five_great_epics_metadata.py    # 5 epics
├── five_minor_epics_metadata.py    # 5 minor epics
├── thirumurai_metadata.py          # 14 Thirumurai works
├── naalayira_divya_prabandham_metadata.py  # 24 NDPD works
├── devotional_standalone_metadata.py  # Standalone devotional works
├── neethinoolkal_metadata.py       # 21 ethical literature works
├── sitrilakkiyangal_metadata.py    # 20 minor literary works
├── siddhar_padalgal_metadata.py    # 36 Siddhar works
├── bharathiyar_metadata.py         # 4 Bharathiyar thematic groups
├── kambaramayanam_metadata.py      # Kambaramayanam epic
└── tolkappiyam_metadata.py         # Tolkappiyam grammar
```

## Metadata File Structure

Each metadata file MUST export these module-level constants:

```python
COLLECTION_ID = 327          # Integer collection ID
COLLECTION_NAME = 'Siddhar Padalgal'        # English collection name
COLLECTION_NAME_TAMIL = 'சித்தர் பாடல்கள்'  # Tamil collection name

WORK_METADATA = {
    # Work entries (see below)
}
```

## Work Metadata Schema

Each entry in `WORK_METADATA` follows this structure:

```python
WORK_METADATA = {
    'work_key': {                              # String key or numeric ID
        # ===== REQUIRED FIELDS =====
        'work_name': str,                      # English work name
        'work_name_tamil': str,                # Tamil work name
        'canonical_order': int,                # Global sort position (e.g., 327001)
        'position_in_collection': int,         # Position within this collection (1, 2, 3...)
        'chronology_start_year': int,          # Approximate start year (negative = BCE)

        # ===== CHRONOLOGY (optional but recommended) =====
        'chronology_end_year': int,            # Approximate end year (negative = BCE)
        'chronology_confidence': str,          # 'high', 'medium', or 'low'
        'chronology_notes': str,               # Scholarly debates, dating evidence, etc.

        # ===== AUTHORSHIP (optional but recommended) =====
        'author': str,                         # English author name
        'author_tamil': str,                   # Tamil author name

        # ===== DESCRIPTIVE (optional) =====
        'period': str,                         # Human-readable period (e.g., "5th-10th century CE")
        'description': str,                    # Long English description

        # ===== PARSER-SPECIFIC (optional, varies by collection) =====
        'file': str,                           # Source filename
        'folder': str,                         # Source folder path
        'structure': str,                      # Parsing pattern hint
        'type': str,                           # Section structure type
        # ... additional custom fields as needed
    }
}
```

## Field Specifications

### Required Fields

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `work_name` | str | English work name | `"Agathiyar Gnanam"` |
| `work_name_tamil` | str | Tamil work name | `"அகத்தியர் ஞானம்"` |
| `canonical_order` | int | Global sort position | `327001` |
| `position_in_collection` | int | Position within collection | `1` |
| `chronology_start_year` | int | Start year (negative = BCE) | `600` or `-100` |

### Optional Standard Fields

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `chronology_end_year` | int | Must be >= start_year | End year of composition period |
| `chronology_confidence` | str | Must be: `'high'`, `'medium'`, or `'low'` | Confidence level in dating |
| `chronology_notes` | str | - | Scholarly notes, debates, evidence |
| `author` | str | - | English author name |
| `author_tamil` | str | - | Tamil author name |
| `period` | str | - | Human-readable period description |
| `description` | str | - | Long English description |

### Parser-Specific Fields

These fields are used by import scripts and vary by collection:

- `file`: Source filename (e.g., `"1 அகத்தியர் ஞானம்.txt"`)
- `folder`: Source folder path
- `structure`: Parsing strategy hint (e.g., `"adhikaram"`, `"simple"`)
- `type`: Section structure type (e.g., `"thogai"`, `"padal"`)
- `files`: List of multiple source files (for Bharathiyar)
- `file_names`: Dict mapping file numbers to names
- `verse_numbering`: Numbering scheme (e.g., `"global"`, `"section_reset"`)
- `structure_pattern`: Structure variant (e.g., `"dual_at"`, `"nested_double_star"`)

You can add custom fields as needed for your specific parsing logic.

## Canonical Order Scheme

The `canonical_order` field follows this numbering scheme:

| Range | Category | Example |
|-------|----------|---------|
| 100-199 | Tolkappiyam (grammar) | 100: Tolkappiyam |
| 200-299 | Sangam literature | 201-218: Sangam works |
| 260 | Thirukkural | 261: Thirukkural |
| 280-290 | Five Great Epics | 281-285: Silapathikaram, etc. |
| 321001+ | Thirumurai works | 321001-321014 |
| 322001+ | NDPD works | 322001-322024 |
| 325001+ | Ethical Literature | 325001-325021 |
| 326001+ | Minor Literary Works | 326001-326020 |
| 327001+ | Siddhar Padalgal | 327001-327036 |
| 328001+ | Bharathiyar works | 328001-328004 |
| 400-499 | Kambaramayanam | 400: Kambaramayanam |

**Convention:** Use `(collection_id * 1000) + position` for works in collections 321+

## Chronology Confidence Levels

| Level | Meaning | Example |
|-------|---------|---------|
| `'high'` | Well-documented, scholarly consensus | Bharathiyar (1882-1921 CE) |
| `'medium'` | Reasonable estimates, some scholarly debate | Thirukkural (300-500 CE) |
| `'low'` | Uncertain, wide range of estimates | Agathiyar Gnanam (600-900 CE) |

## Complete Example

```python
# scripts/metadata/siddhar_padalgal_metadata.py

"""
Metadata for Siddhar Padalgal (சித்தர் பாடல்கள்) collection.
36 mystical and spiritual poetry works by Tamil Siddhars.
"""

COLLECTION_ID = 327
COLLECTION_NAME = 'Siddhar Padalgal'
COLLECTION_NAME_TAMIL = 'சித்தர் பாடல்கள்'

WORK_METADATA = {
    1: {
        'work_name': 'Agathiyar Gnanam',
        'work_name_tamil': 'அகத்தியர் ஞானம்',
        'author': 'Agathiyar',
        'author_tamil': 'அகத்தியர்',
        'chronology_start_year': 600,
        'chronology_end_year': 900,
        'chronology_confidence': 'low',
        'chronology_notes': 'Estimated 7th-9th century CE based on linguistic analysis. '
                           'Agathiyar is a legendary Siddhar, actual composition date uncertain.',
        'canonical_order': 327001,
        'position_in_collection': 1,
        'period': '7th-9th century CE',
        'description': 'Wisdom teachings attributed to the legendary Siddhar Agathiyar, '
                      'covering spiritual enlightenment and yogic practices.',
        # Parser-specific
        'file': '1 அகத்தியர் ஞானம்.txt',
    },
    2: {
        'work_name': 'Agathiyar Vaithiya Kaviyam 300',
        'work_name_tamil': 'அகத்தியர் வைத்திய காவியம் 300',
        'author': 'Agathiyar',
        'author_tamil': 'அகத்தியர்',
        'chronology_start_year': 600,
        'chronology_end_year': 900,
        'chronology_confidence': 'low',
        'chronology_notes': 'Part of Siddha medicine tradition, estimated 7th-9th century CE.',
        'canonical_order': 327002,
        'position_in_collection': 2,
        'period': '7th-9th century CE',
        'description': '300 verses on Siddha medicine and healing practices.',
        # Parser-specific
        'file': '2 அகத்தியர் வைத்திய காவியம் 300.txt',
    },
    # ... 34 more works
}
```

## Usage in Import Scripts

### Step 1: Import Metadata

```python
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import from centralized metadata
from metadata.siddhar_padalgal_metadata import (
    WORK_METADATA,
    COLLECTION_ID,
    COLLECTION_NAME,
    COLLECTION_NAME_TAMIL
)
```

### Step 2: Iterate Through Metadata

```python
from shared.base_importer import BaseWorkImporter

class SiddharPadalgalImporter(BaseWorkImporter):
    def __init__(self, database_url=None):
        super().__init__(
            database_url=database_url,
            collection_id=COLLECTION_ID,
            collection_name=COLLECTION_NAME,
            collection_name_tamil=COLLECTION_NAME_TAMIL
        )
        self.metadata = WORK_METADATA

    def parse_and_import(self):
        """Parse all works and import"""
        for work_key, work_meta in self.metadata.items():
            print(f"Processing: {work_meta['work_name_tamil']}...")

            # Create work (validates automatically via BaseWorkImporter)
            work_id = self._create_work(
                work_name=work_meta['work_name'],
                work_name_tamil=work_meta['work_name_tamil'],
                metadata=work_meta
            )

            # Parse text file
            file_path = self._get_file_path(work_meta['file'])
            self._parse_work_file(work_id, file_path, work_meta)

        # Bulk insert with single transaction
        self.bulk_insert()
```

## Validation

The `metadata_validator.py` module automatically validates all metadata during import:

- **Required fields present**: Raises `ValueError` if any required field missing
- **Field types correct**: Checks that integers are ints, strings are strs
- **Chronology values valid**:
  - `chronology_confidence` must be `'high'`, `'medium'`, or `'low'`
  - `chronology_end_year` must be >= `chronology_start_year`
- **Work keys unique**: Ensures no duplicate keys within a metadata file

If validation fails, you'll see a clear error message:
```
ValueError: Metadata validation failed for work 'agathiyar_gnanam':
  - Missing required field: work_name_tamil
  - chronology_confidence must be one of {'high', 'medium', 'low'}, got 'very_high'
```

## Updating Work Metadata

When scholarly research updates information about a work:

1. **Edit the metadata file** with new information
2. **Delete the existing work** from database: `python scripts/delete_work.py "Work Name"`
3. **Re-run the import script**: `python scripts/collection_bulk_import.py`
4. **Verify changes**: Query database to confirm updates

The metadata file serves as the single source of truth - all changes flow through it.

## Adding New Works

To add a new work to a collection:

1. **Add entry to metadata file** with all required fields
2. **Assign canonical_order**: Use next available number in collection range
3. **Assign position_in_collection**: Use next sequential position
4. **Run import script**: The new work will be created automatically

## Collection ID Reference

See `COLLECTION_IDS.md` in project root for complete collection ID scheme and assignments.

## Questions or Issues?

- Check `scripts/shared/metadata_validator.py` for validation logic
- See `scripts/shared/base_importer.py` for how metadata is processed
- Review existing metadata files for working examples
- Consult `CLAUDE.md` for project-wide conventions
