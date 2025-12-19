# Canonical and Chronological Sorting Implementation

## Overview
Added support for two new sorting methods for search results:
1. **Traditional Canon** - Sort by traditional Tamil literary canon order
2. **Chronological** - Sort by estimated chronological composition dates

## Database Changes

### Schema Update
**File**: `sql/complete_setup.sql`

Added `canonical_order INTEGER` field to `works` table (line 39):
```sql
canonical_order INTEGER,  -- Traditional Tamil literary canon ordering
```

### Canonical Order Values

| Work | Canonical Order | Period | Notes |
|------|----------------|--------|-------|
| Tolkappiyam | 100 | ~500 BCE - 100 CE | Foundation grammar (NOT YET IMPORTED) |
| Sangam works (18) | 200-217 | 300 BCE - 300 CE | Classical anthology |
| Thirukkural | 260 | 300-500 CE | Post-Sangam ethics |
| Silapathikaram | 280 | 100-300 CE | Transitional epic |
| Kambaramayanam | 400 | 1100-1200 CE | Medieval epic |

## Import Scripts Updated

All import scripts now populate the `canonical_order` field:

### 1. thirukkural_bulk_import.py
```python
canonical_order = 260  # Post-Sangam transitional period
```

### 2. sangam_bulk_import.py
```python
# Maps traditional_order (2-19) to canonical_order (200-217)
canonical_order = 198 + work_info['traditional_order']
```

Result:
- நற்றிணை (Natrrinai): 200
- குறுந்தொகை (Kurunthokai): 201
- ஐங்குறுநூறு (Ainkurunuru): 202
- And so on... (18 total works: 200-217)

### 3. silapathikaram_bulk_import.py
```python
canonical_order = 280  # Transitional period epic
```

### 4. kambaramayanam_bulk_import.py
```python
canonical_order = 400  # Medieval epic
```

## Backend Implementation

**File**: `webapp/backend/database.py`

### Query Changes
Added JOINs with `works` table when using canonical or chronological sorting:

```python
if sort_by in ("canonical", "chronological"):
    # Join works table to access canonical_order and chronology_start_year
    query = """
        SELECT wd.*, w.canonical_order, w.chronology_start_year
        FROM word_details wd
        LEFT JOIN works w ON wd.work_name = w.work_name
        WHERE 1=1
    """
```

### Sort Logic
```python
if sort_by == "canonical":
    order_clause = """
        ORDER BY w.canonical_order ASC NULLS LAST,
                 wd.verse_id, wd.line_number, wd.word_position
    """
elif sort_by == "chronological":
    order_clause = """
        ORDER BY w.chronology_start_year ASC NULLS LAST,
                 wd.verse_id, wd.line_number, wd.word_position
    """
```

## Setup Script Updates

**File**: `scripts/setup_railway_db.py`

Updated `drop_tables()` function to include new tables:
- `collections`
- `work_collections`
- `admin_users`

And their sequences:
- `collections_collection_id_seq`
- `admin_users_user_id_seq`

## Frontend

The frontend (`webapp/frontend/src/App.vue`) already has UI controls for:
- "Alphabetical" (wd.work_name)
- "Traditional Canon" (w.canonical_order)
- "Chronological" (w.chronology_start_year)
- "Collection Order" (wc.position_in_collection)

No frontend changes needed - backend now properly supports all options!

## Usage

### Database Rebuild Required
To use the new sorting options:

1. **Drop and recreate database:**
```bash
python scripts/setup_railway_db.py "postgresql://..."
```

2. **Import works with canonical order:**
```bash
python scripts/thirukkural_bulk_import.py "postgresql://..."
python scripts/sangam_bulk_import.py "postgresql://..."
python scripts/silapathikaram_bulk_import.py "postgresql://..."
python scripts/kambaramayanam_bulk_import.py "postgresql://..."
```

### Testing Sort Options
Search for a common word like "அறம்" or "சொல்" and try each sort option:

- **Alphabetical**: அகநானூறு → கம்பராமாயணம் → குறுந்தொகை → ...
- **Traditional Canon**: நற்றிணை (200) → குறுந்தொகை (201) → ... → திருக்குறள் (260) → சிலப்பதிகாரம் (280) → கம்பராமாயணம் (400)
- **Chronological**: Sangam works (-100 CE) → Thirukkural (300 CE) → Silapathikaram (400 CE) → Kambaramayanam (1100 CE)

## Notes

- **Tolkappiyam** will have canonical_order=100 when imported (currently not in database)
- All chronology dates are approximate and documented in `chronology_notes` field
- Canonical order follows traditional Tamil literary classification
- NULLS LAST ensures works without canonical_order appear at the end
