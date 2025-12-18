# Canonical Order System - Revised Design

## Problem Statement

The current `traditional_sort_order` column assumes a single linear canonical sequence (1, 2, 3...). This doesn't scale when adding:
- Works outside the main classical canon
- Multiple literary traditions (Shaiva, Vaishnava, etc.)
- Modern literature
- Regional works

## Proposed Solution: Multi-Level Categorization

### Option 1: Category-Based Ordering (Recommended)

Add categorization to the `works` table:

```sql
ALTER TABLE works
ADD COLUMN literary_period VARCHAR(50);  -- 'sangam', 'post-sangam', 'medieval', 'modern', etc.

ALTER TABLE works
ADD COLUMN literary_category VARCHAR(50);  -- 'secular', 'shaiva', 'vaishnava', 'jaina', 'buddhist'

ALTER TABLE works
ADD COLUMN sort_within_category INTEGER;  -- Sort order within its category
```

**Example Data:**

| work_name | literary_period | literary_category | sort_within_category | traditional_sort_order |
|-----------|----------------|-------------------|---------------------|----------------------|
| Natrrinai | sangam | secular | 1 | 2 |
| Kurunthokai | sangam | secular | 2 | 3 |
| Thirukkural | post-sangam | secular | 1 | 20 |
| Silapathikaram | post-sangam | jaina | 1 | 21 |
| Kambaramayanam | medieval | secular | 1 | 22 |
| Thevaram | medieval | shaiva | 1 | NULL |
| Thiruvachakam | medieval | shaiva | 2 | NULL |
| Divya Prabandham | medieval | vaishnava | 1 | NULL |
| Bharathiyar Kavithaigal | modern | secular | 1 | NULL |

**Sorting Strategies:**

1. **Traditional Canon Only:**
   ```sql
   ORDER BY traditional_sort_order ASC NULLS LAST
   ```

2. **By Period, then Category:**
   ```sql
   ORDER BY
     CASE literary_period
       WHEN 'sangam' THEN 1
       WHEN 'post-sangam' THEN 2
       WHEN 'medieval' THEN 3
       WHEN 'modern' THEN 4
     END,
     literary_category,
     sort_within_category
   ```

3. **Chronological (ignores categories):**
   ```sql
   ORDER BY (chronology_start_year + chronology_end_year) / 2 ASC NULLS LAST
   ```

### Option 2: Separate Canonical Sequences Table

Create a many-to-many relationship for multiple canonical orderings:

```sql
CREATE TABLE canonical_sequences (
    sequence_id SERIAL PRIMARY KEY,
    sequence_name VARCHAR(100) NOT NULL,  -- 'traditional_18', 'muvar_literature', 'bhakti_canon'
    sequence_description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE work_sequence_positions (
    position_id SERIAL PRIMARY KEY,
    sequence_id INTEGER REFERENCES canonical_sequences(sequence_id),
    work_id INTEGER REFERENCES works(work_id),
    position INTEGER NOT NULL,  -- Position within this sequence
    UNIQUE (sequence_id, work_id),
    UNIQUE (sequence_id, position)
);
```

**Example Data:**

canonical_sequences:
| sequence_id | sequence_name | sequence_description |
|-------------|---------------|---------------------|
| 1 | traditional_18 | Traditional 18 works of Sangam literature |
| 2 | post_sangam_classics | Post-Sangam ethical and epic literature |
| 3 | shaiva_canon | Shaiva Siddhanta canonical texts |
| 4 | vaishnava_canon | Vaishnava canonical texts |

work_sequence_positions:
| sequence_id | work_id | position |
|-------------|---------|----------|
| 1 | 2 | 1 | (Natrrinai - position 1 in traditional_18)
| 1 | 3 | 2 | (Kurunthokai - position 2 in traditional_18)
| 2 | 20 | 1 | (Thirukkural - position 1 in post_sangam_classics)
| 3 | 25 | 1 | (Thevaram - position 1 in shaiva_canon)

**API Usage:**
```bash
GET /works?sequence=traditional_18
GET /works?sequence=shaiva_canon
GET /works?sequence=all&sort_by=chronological
```

### Option 3: Simple NULL-Safe Design (Minimal Changes)

Keep current schema but use NULL for non-canonical works:

**Rules:**
- `traditional_sort_order` = 1-22 for the established canon
- `traditional_sort_order` = NULL for everything else
- Sort NULL values last

**Sorting:**
```sql
-- Traditional canon first, then alphabetical
ORDER BY traditional_sort_order ASC NULLS LAST, work_name ASC

-- Traditional canon first, then chronological
ORDER BY traditional_sort_order ASC NULLS LAST,
         (chronology_start_year + chronology_end_year) / 2 ASC
```

**Pros:**
- No schema changes needed
- Clear distinction between canonical and non-canonical
- Simple to implement

**Cons:**
- No way to order non-canonical works meaningfully
- Can't represent multiple canonical traditions

## Recommended Approach: Hybrid (Option 1 + 3)

**Phase 1: Keep current design, use NULL for non-canonical**
- Works immediately
- Minimal changes
- Clear for users what's "traditional canon" vs. not

**Phase 2: Add categories (when needed)**
```sql
ALTER TABLE works
ADD COLUMN literary_period VARCHAR(50);
ADD COLUMN literary_category VARCHAR(50);
ADD COLUMN sort_within_category INTEGER;
```

**Phase 3: Add multiple sequences table (if needed)**
- Only if you need to represent multiple scholarly traditions
- E.g., different regional canons, different religious traditions

## Implementation Plan

### Step 1: Document the 22 canonical works

Create a reference table in documentation:

| Position | Work Name | Period | Category |
|----------|-----------|--------|----------|
| 1 | Tolkāppiyam | Pre-Sangam | Grammar |
| 2-9 | Ettuthokai (8 works) | Sangam | Poetry Anthologies |
| 10-19 | Pathupaattu (10 works) | Sangam | Long Poems |
| 20 | Thirukkural | Post-Sangam | Ethics |
| 21 | Silapathikaram | Post-Sangam | Epic |
| 22 | Kambaramayanam | Medieval | Epic |

### Step 2: Add categories to parsers

Update each parser with category metadata:

```python
# In thirukkural_bulk_import.py
self.cursor.execute("""
    INSERT INTO works (
        ..., traditional_sort_order, literary_period, literary_category, ...
    )
    VALUES (%s, ..., %s, %s, %s, ...)
""", (
    ..., 20, 'post-sangam', 'secular', ...
))
```

### Step 3: Update API to filter by category

```python
@app.get("/works")
def get_works(
    sort_by: str = "alphabetical",
    period: Optional[str] = None,  # sangam, post-sangam, medieval, modern
    category: Optional[str] = None,  # secular, shaiva, vaishnava, etc.
    canonical_only: bool = False  # Only show works with traditional_sort_order
):
```

### Step 4: UI considerations

**Work Filter Options:**
- ☐ Show canonical works only (traditional_sort_order IS NOT NULL)
- ☐ Show all works
- Filter by period: [Sangam] [Post-Sangam] [Medieval] [Modern]
- Filter by category: [Secular] [Shaiva] [Vaishnava] [Jaina]

**Sort Options:**
- Alphabetical (A-Z)
- Traditional Canon (1-22, then others)
- Chronological (Oldest to Newest)
- By Category

## Examples of Future Additions

### Bhakti Literature (Medieval, 600-900 CE)

**Shaiva:**
- Thevaram (traditional_sort_order: NULL, period: medieval, category: shaiva)
- Thiruvachakam (NULL, medieval, shaiva)
- Thiruvasagam (NULL, medieval, shaiva)

**Vaishnava:**
- Divya Prabandham (NULL, medieval, vaishnava)
  - Contains 4000 pasurams by 12 Alwars

### Modern Literature (1800s-2000s)

- Bharathiyar Kavithaigal (NULL, modern, secular)
- Bharathidasan Works (NULL, modern, secular)
- Kalki's Works (NULL, modern, secular)

### Regional/Folk Literature

- Villu Pattu (NULL, folk, secular)
- Therukoothu Scripts (NULL, folk, secular)

## Migration Path

For existing database:

```sql
-- Add new columns
ALTER TABLE works
ADD COLUMN IF NOT EXISTS literary_period VARCHAR(50);

ALTER TABLE works
ADD COLUMN IF NOT EXISTS literary_category VARCHAR(50);

ALTER TABLE works
ADD COLUMN IF NOT EXISTS sort_within_category INTEGER;

-- Update existing works
UPDATE works SET
    literary_period = 'sangam',
    literary_category = 'secular',
    sort_within_category = traditional_sort_order - 1
WHERE traditional_sort_order BETWEEN 2 AND 19;

UPDATE works SET
    literary_period = 'post-sangam',
    literary_category = 'secular',
    sort_within_category = 1
WHERE work_name = 'Thirukkural';

UPDATE works SET
    literary_period = 'post-sangam',
    literary_category = 'jaina',
    sort_within_category = 1
WHERE work_name = 'Silapathikaram';

UPDATE works SET
    literary_period = 'medieval',
    literary_category = 'secular',
    sort_within_category = 1
WHERE work_name = 'Kambaramayanam';
```

## Decision Points

**Question 1: Do you want to maintain multiple canonical sequences?**
- YES → Use Option 2 (separate sequences table)
- NO → Use Option 1 (categories) or Option 3 (NULL-safe)

**Question 2: Do you need to categorize non-canonical works?**
- YES → Add literary_period and literary_category columns
- NO → Just use NULL for traditional_sort_order

**Question 3: Will users want to filter/sort by period or tradition?**
- YES → Add category columns + API filters
- NO → Keep it simple with NULL-safe design

## My Recommendation

**Start Simple (Option 3), Evolve as Needed:**

1. **Now:** Use NULL for `traditional_sort_order` on non-canonical works
2. **Soon:** Add `literary_period` and `literary_category` when you add your first non-canonical work
3. **Later:** Add `canonical_sequences` table if you need multiple traditions

This gives you flexibility without over-engineering upfront.

**What do you think? Which option fits your vision for the database?**
