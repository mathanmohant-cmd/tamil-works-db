# Verse Type Strategy

## Overview

This document defines the consistent strategy for `verse_type` and `verse_type_tamil` fields across the Tamil Literature database.

## Schema Design

The `verses` table has two related but distinct fields:

```sql
verse_type VARCHAR(50),         -- General verse form (English)
verse_type_tamil VARCHAR(50),   -- General verse form (Tamil)
meter VARCHAR(100),              -- Specific prosody/meter (if applicable)
```

## Current Values by Work

| Work | verse_type | verse_type_tamil | Notes |
|------|-----------|------------------|-------|
| Thirukkural | `kural` | `குறள்` | Specific to this work |
| Tolkappiyam | `nurpaa` | `நூற்பா` | Traditional grammar text form |
| Sangam Literature | `poem` | `பாடல்` | Generic for classical poetry |
| Silapathikaram | `poem` | `பாடல்` | Epic narrative poetry |
| Kambaramayanam | `poem` | `பாடல்` | Epic narrative poetry |

## Design Principles

### 1. General vs. Specific

- **`verse_type` / `verse_type_tamil`**: General classification
  - Examples: `poem`, `kural`, `nurpaa`
  - Tamil: `பாடல்`, `குறள்`, `நூற்பா`

- **`meter`**: Specific prosody (currently unused, reserved for future)
  - Examples: `venba`, `aasiriyappa`, `kalippa`, `viruttam`
  - Tamil: `வெண்பா`, `ஆசிரியப்பா`, `கலிப்பா`, `விருத்தம்`

### 2. Source of Truth

**Parser scripts are the source of truth** for verse_type values:

- `scripts/thirukkural_bulk_import.py` → `kural` / `குறள்`
- `scripts/tolkappiyam_bulk_import.py` → `nurpaa` / `நூற்பா`
- `scripts/sangam_bulk_import.py` → `poem` / `பாடல்`
- `scripts/silapathikaram_bulk_import.py` → `poem` / `பாடல்`
- `scripts/kambaramayanam_bulk_import.py` → `poem` / `பாடல்`

SQL files (`sql/schema.sql`, `sql/complete_setup.sql`, etc.) contain sample data for testing and must match parser outputs.

### 3. Why "poem" for Epics?

We use the generic term "poem" (`பாடல்`) for Silapathikaram and Kambaramayanam because:

1. **Simplicity**: These works contain multiple meter types within them
2. **Consistency**: Aligns with Sangam literature classification
3. **Extensibility**: The `meter` field is reserved for specific prosody analysis in the future
4. **User-Facing**: Most users understand "poem" better than technical meter names

## Future Enhancements

If meter-specific analysis is needed:

1. **Parse and populate `meter` field** in parser scripts
2. **Keep `verse_type` generic** for high-level filtering
3. **Use `meter` for detailed prosody searches**

Example:
```python
'verse_type': 'poem',
'verse_type_tamil': 'பாடல்',
'meter': 'venba'  # Specific meter for this verse
```

## Migration Strategy

When updating verse_type values:

1. **Update parser scripts first** (source of truth)
2. **Update SQL sample data** to match parsers
3. **Create migration script** for existing database data
4. **Run migration on all environments** (local, Railway, etc.)
5. **Refresh views** to pick up changes

## Consistency Checklist

Before deploying:

- [ ] Parser scripts have correct verse_type values
- [ ] SQL sample data matches parser outputs
- [ ] Migration scripts use work names (not hardcoded IDs)
- [ ] Views refreshed after data changes
- [ ] All environments updated (local + Railway)

## Related Files

- Parser scripts: `scripts/*_bulk_import.py`
- SQL schema: `sql/schema.sql`
- Sample data: `sql/complete_setup.sql`, `sql/sample_word_data.sql`
- Migrations: `migrations/2025-12-11_complete_fix.sql`
- Deployment guide: `DEPLOY_RAILWAY_FIX.md`
