# Canonical Ordering - Final Implementation

## Decision

**Use ONLY collections for ordering. Remove `traditional_sort_order` from works table.**

## Rationale

- **Single source of truth**: Collections manage all organizational schemes
- **Flexibility**: Works can have positions in multiple collections (Traditional Canon, Sangam Age Works, etc.)
- **No redundancy**: Avoid confusion between `traditional_sort_order` and collection positions
- **Scalable**: Easy to add new ordering schemes without schema changes

## How It Works

### Canonical Ordering via Collections

**Traditional Canon collection (ID = 100)** defines the canonical 1-22 order:

```sql
-- Natrrinai is position 2 in Traditional Canon
INSERT INTO work_collections (work_id, collection_id, position_in_collection)
VALUES (2, 100, 2);

-- Thirukkural is position 20 in Traditional Canon
INSERT INTO work_collections (work_id, collection_id, position_in_collection)
VALUES (20, 100, 20);
```

### Database Schema Changes

#### works table - REMOVED `traditional_sort_order`

```sql
CREATE TABLE works (
    work_id INTEGER PRIMARY KEY,
    work_name VARCHAR(200) NOT NULL,
    work_name_tamil VARCHAR(200) NOT NULL,
    -- traditional_sort_order REMOVED
    chronology_start_year INTEGER,
    chronology_end_year INTEGER,
    primary_collection_id INTEGER,  -- FK to collections
    ...
);
```

#### verse_hierarchy view - Uses `canonical_position`

```sql
CREATE VIEW verse_hierarchy AS
SELECT
    v.verse_id,
    v.verse_type,
    w.work_name,
    wc_canon.position_in_collection as canonical_position,  -- From collection!
    ...
FROM verses v
JOIN works w ON v.work_id = w.work_id
LEFT JOIN work_collections wc_canon ON w.work_id = wc_canon.work_id
    AND wc_canon.collection_id = 100;  -- Traditional Canon
```

#### word_details view - Inherits `canonical_position`

```sql
CREATE VIEW word_details AS
SELECT
    w.word_id,
    w.word_text,
    vh.canonical_position,  -- Comes from verse_hierarchy
    ...
FROM words w
JOIN verses v ON w.line_id IN (SELECT line_id FROM lines WHERE verse_id = v.verse_id)
JOIN verse_hierarchy vh ON v.verse_id = vh.verse_id;
```

## Backend API

### Search Endpoint

**Sort search results by canonical order:**

```bash
GET /search?q=அறம்&sort_by=canonical
```

**Backend implementation:**

```python
# database.py
def search_words(self, search_term, sort_by="alphabetical"):
    if sort_by == "canonical":
        order_clause = """
            ORDER BY wd.canonical_position ASC NULLS LAST,
                     wd.work_name, wd.verse_id
        """
    # ... execute query
```

**Result:** Words appear in Traditional Canon order (Natrrinai, Kurunthokai, ..., Thirukkural, ...)

### Works Endpoint

**Get works in canonical order:**

```bash
GET /works?sort_by=canonical
```

**Backend implementation:**

```python
# database.py
def get_works(self, sort_by="alphabetical"):
    if sort_by == "canonical":
        order_clause = """
            ORDER BY wc_canon.position_in_collection ASC NULLS LAST
        """
        from_clause = """
            FROM works w
            LEFT JOIN work_collections wc_canon
                ON w.work_id = wc_canon.work_id
                AND wc_canon.collection_id = 100
        """
    # ... execute query
```

**Result:** Works appear in 1-22 canonical order, then alphabetical for non-canonical works

## Frontend Usage

### Display Search Results in Canonical Order

```javascript
// Frontend code (Vue.js)
const searchResults = await axios.get('/search', {
  params: {
    q: searchTerm,
    sort_by: 'canonical'  // ← Use canonical ordering
  }
});

// Results are already sorted:
// - Natrrinai (position 2)
// - Kurunthokai (position 3)
// - ...
// - Thirukkural (position 20)
// - Modern works (NULL, sorted alphabetically)
```

### UI Sort Dropdown

```html
<select v-model="sortBy">
  <option value="alphabetical">Alphabetical (A-Z)</option>
  <option value="canonical">Traditional Canon (1-22)</option>
  <option value="chronological">Chronological (Oldest First)</option>
</select>
```

## Data Seeding

Works are assigned to Traditional Canon collection in `sql/seed_work_collections.sql`:

```sql
-- Natrrinai → Traditional Canon position 2
INSERT INTO work_collections (work_id, collection_id, position_in_collection)
SELECT work_id, 100, 2
FROM works WHERE work_name = 'Natrrinai';

-- Thirukkural → Traditional Canon position 20
INSERT INTO work_collections (work_id, collection_id, position_in_collection)
SELECT work_id, 100, 20
FROM works WHERE work_name = 'Thirukkural';

-- ... (all 22 works)
```

## Benefits

### 1. Single Source of Truth
- Canonical order defined ONCE in `work_collections` table
- No duplication between `traditional_sort_order` and collection positions

### 2. Multiple Orderings
Works can have positions in multiple collections:
- Position 20 in "Traditional Canon"
- Position 1 in "Eighteen Minor Classics"
- Position 1 in "Ethical Literature"

### 3. NULL Handling
- Works not in Traditional Canon have `canonical_position = NULL`
- SQL `ORDER BY ... NULLS LAST` places them after canonical works
- No confusion about what NULL means

### 4. Future-Proof
Add new orderings without schema changes:
```sql
-- Create "Bhakti Canon" collection
INSERT INTO collections VALUES (200, 'Bhakti Canon', ...);

-- Assign works to it
INSERT INTO work_collections VALUES
  (thevaram_id, 200, 1),
  (thiruvachakam_id, 200, 2);
```

## Migration Notes

### For Existing Data

If `traditional_sort_order` exists in your database:

```sql
-- 1. Migrate to collections
INSERT INTO work_collections (work_id, collection_id, position_in_collection)
SELECT work_id, 100, traditional_sort_order
FROM works
WHERE traditional_sort_order IS NOT NULL;

-- 2. Drop old column
ALTER TABLE works DROP COLUMN traditional_sort_order;

-- 3. Recreate views
DROP VIEW word_details;
DROP VIEW verse_hierarchy;
-- ... recreate from complete_setup.sql
```

### Updated Files

**Schema:**
- `sql/complete_setup.sql` - Removed `traditional_sort_order`, added `canonical_position` to views

**Backend:**
- `webapp/backend/database.py` - Uses `canonical_position` for sorting
- `webapp/backend/main.py` - API accepts `sort_by=canonical`

**Parsers:**
- `scripts/thirukkural_bulk_import.py` - Removed `traditional_sort_order` from INSERT

**Seed Data:**
- `sql/seed_work_collections.sql` - Maps all 22 works to Traditional Canon collection

## API Examples

### Search with canonical ordering

```bash
# Search for அறம் in canonical order
curl 'http://localhost:8000/search?q=அறம்&sort_by=canonical'

# Response includes canonical_position in results
{
  "results": [
    {
      "word_text": "அறம்",
      "work_name": "Natrrinai",
      "canonical_position": 2,  // ← From Traditional Canon collection
      ...
    },
    {
      "word_text": "அறம்",
      "work_name": "Thirukkural",
      "canonical_position": 20,
      ...
    }
  ]
}
```

### Get works in canonical order

```bash
curl 'http://localhost:8000/works?sort_by=canonical'

# Response
[
  {"work_id": 2, "work_name": "Natrrinai", "canonical_position": 2},
  {"work_id": 3, "work_name": "Kurunthokai", "canonical_position": 3},
  ...
  {"work_id": 20, "work_name": "Thirukkural", "canonical_position": 20},
  ...
]
```

## Summary

✅ **Removed** `traditional_sort_order` from works table

✅ **Added** `canonical_position` derived from Traditional Canon collection (ID=100)

✅ **Updated** views to use `canonical_position` from `work_collections` join

✅ **Updated** backend to sort by `canonical_position`

✅ **Updated** API to accept `sort_by=canonical`

**Result:** Frontend can now display results in canonical order by passing `sort_by=canonical` parameter!
