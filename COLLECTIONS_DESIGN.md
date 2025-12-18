# Collections System - Comprehensive Design

## Overview

A flexible system where works can belong to multiple collections, each with its own ordering and metadata.

## Database Schema

### Core Design: Many-to-Many Relationship

```sql
-- Collections table (literary periods, traditions, categories)
CREATE TABLE collections (
    collection_id SERIAL PRIMARY KEY,
    collection_name VARCHAR(100) NOT NULL UNIQUE,
    collection_name_tamil VARCHAR(100),
    collection_type VARCHAR(50) NOT NULL,  -- 'period', 'tradition', 'genre', 'custom'
    description TEXT,
    parent_collection_id INTEGER REFERENCES collections(collection_id),  -- For hierarchies
    sort_order INTEGER,  -- For ordering collections themselves
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Junction table: Works can belong to multiple collections
CREATE TABLE work_collections (
    work_collection_id SERIAL PRIMARY KEY,
    work_id INTEGER NOT NULL REFERENCES works(work_id) ON DELETE CASCADE,
    collection_id INTEGER NOT NULL REFERENCES collections(collection_id) ON DELETE CASCADE,
    position_in_collection INTEGER,  -- Order within this specific collection
    is_primary BOOLEAN DEFAULT FALSE,  -- Mark primary collection for each work
    notes TEXT,  -- Collection-specific notes about this work
    UNIQUE (work_id, collection_id),
    UNIQUE (collection_id, position_in_collection)  -- Ensure unique positions
);

CREATE INDEX idx_work_collections_work ON work_collections(work_id);
CREATE INDEX idx_work_collections_collection ON work_collections(collection_id);
CREATE INDEX idx_collections_type ON collections(collection_type);
CREATE INDEX idx_collections_parent ON collections(parent_collection_id);
```

### Update works table

```sql
-- Keep traditional_sort_order for backward compatibility
-- But it becomes just another collection membership
ALTER TABLE works
ADD COLUMN primary_collection_id INTEGER REFERENCES collections(collection_id);

-- Add index
CREATE INDEX idx_works_primary_collection ON works(primary_collection_id);
```

## Pre-defined Collections

### Seed Data

```sql
-- ============================================================================
-- LITERARY PERIODS
-- ============================================================================

INSERT INTO collections (collection_id, collection_name, collection_name_tamil, collection_type, description, sort_order) VALUES
(1, 'Sangam Literature', 'சங்க இலக்கியம்', 'period', 'Classical Tamil literature from 300 BCE - 300 CE', 1),
(2, 'Post-Sangam Literature', 'சங்கத்துக்கு பிந்தைய இலக்கியம்', 'period', 'Tamil literature from 300 CE - 600 CE', 2),
(3, 'Medieval Literature', 'இடைக்கால இலக்கியம்', 'period', 'Tamil literature from 600 CE - 1800 CE', 3),
(4, 'Modern Literature', 'நவீன இலக்கியம்', 'period', 'Tamil literature from 1800 CE onwards', 4);

-- ============================================================================
-- TRADITIONAL CANONS (Sub-collections of periods)
-- ============================================================================

-- Sangam Sub-collections
INSERT INTO collections (collection_id, collection_name, collection_name_tamil, collection_type, description, parent_collection_id, sort_order) VALUES
(10, 'Ettuthokai', 'எட்டுத்தொகை', 'canon', 'Eight Anthologies - Classical Sangam poetry collections', 1, 1),
(11, 'Pathupaattu', 'பத்துப்பாட்டு', 'canon', 'Ten Idylls - Long poems of Sangam period', 1, 2);

-- Post-Sangam Sub-collections
INSERT INTO collections (collection_id, collection_name, collection_name_tamil, collection_type, description, parent_collection_id, sort_order) VALUES
(20, 'Eighteen Minor Classics', 'பதினெண்கீழ்க்கணக்கு', 'canon', 'Eighteen didactic works including Thirukkural', 2, 1),
(21, 'Five Great Epics', 'ஐம்பெரும்காப்பியங்கள்', 'canon', 'Five major Tamil epics', 2, 2);

-- Medieval Sub-collections
INSERT INTO collections (collection_id, collection_name, collection_name_tamil, collection_type, description, parent_collection_id, sort_order) VALUES
(30, 'Shaiva Literature', 'சைவ இலக்கியம்', 'tradition', 'Shaiva devotional literature', 3, 1),
(31, 'Vaishnava Literature', 'வைணவ இலக்கியம்', 'tradition', 'Vaishnava devotional literature', 3, 2),
(32, 'Medieval Epics', 'இடைக்கால காப்பியங்கள்', 'canon', 'Medieval Tamil epics including Kambaramayanam', 3, 3);

-- ============================================================================
-- GENRE COLLECTIONS (Cross-period)
-- ============================================================================

INSERT INTO collections (collection_id, collection_name, collection_name_tamil, collection_type, description, sort_order) VALUES
(50, 'Epic Poetry', 'காப்பியம்', 'genre', 'Tamil epic literature across all periods', 10),
(51, 'Devotional Literature', 'பக்தி இலக்கியம்', 'genre', 'Devotional works across traditions', 11),
(52, 'Ethical Literature', 'அற இலக்கியம்', 'genre', 'Works on ethics, morals, and virtuous living', 12),
(53, 'Grammar & Linguistics', 'இலக்கணம்', 'genre', 'Grammatical and linguistic treatises', 13);

-- ============================================================================
-- SPECIAL COLLECTIONS
-- ============================================================================

INSERT INTO collections (collection_id, collection_name, collection_name_tamil, collection_type, description, sort_order) VALUES
(100, 'Traditional Canon', 'பாரம்பரிய நூல்கள்', 'custom', 'Traditional 22-work classical canon', 1),
(101, 'Tolkappiyam Tradition', 'தொல்காப்பியம் மரபு', 'custom', 'Works following Tolkappiyam grammar', 2);
```

## Populate Work-Collection Relationships

```sql
-- ============================================================================
-- SANGAM WORKS → Collections
-- ============================================================================

-- Natrrinai (work_id will vary, using placeholder 2)
INSERT INTO work_collections (work_id, collection_id, position_in_collection, is_primary) VALUES
(2, 1, 1, TRUE),    -- Sangam Literature, position 1, PRIMARY
(2, 10, 1, FALSE),  -- Ettuthokai, position 1
(2, 100, 2, FALSE); -- Traditional Canon, position 2

-- Kurunthokai
INSERT INTO work_collections (work_id, collection_id, position_in_collection, is_primary) VALUES
(3, 1, 2, TRUE),    -- Sangam Literature, position 2, PRIMARY
(3, 10, 2, FALSE),  -- Ettuthokai, position 2
(3, 100, 3, FALSE); -- Traditional Canon, position 3

-- ... (repeat for all 18 Sangam works)

-- ============================================================================
-- POST-SANGAM WORKS → Collections
-- ============================================================================

-- Thirukkural
INSERT INTO work_collections (work_id, collection_id, position_in_collection, is_primary) VALUES
(20, 2, 1, TRUE),    -- Post-Sangam Literature, position 1, PRIMARY
(20, 20, 1, FALSE),  -- Eighteen Minor Classics, position 1
(20, 52, 1, FALSE),  -- Ethical Literature, position 1
(20, 100, 20, FALSE); -- Traditional Canon, position 20

-- Silapathikaram
INSERT INTO work_collections (work_id, collection_id, position_in_collection, is_primary) VALUES
(21, 2, 2, TRUE),    -- Post-Sangam Literature, position 2, PRIMARY
(21, 21, 1, FALSE),  -- Five Great Epics, position 1
(21, 50, 1, FALSE),  -- Epic Poetry, position 1
(21, 100, 21, FALSE); -- Traditional Canon, position 21

-- ============================================================================
-- MEDIEVAL WORKS → Collections
-- ============================================================================

-- Kambaramayanam
INSERT INTO work_collections (work_id, collection_id, position_in_collection, is_primary) VALUES
(22, 3, 1, TRUE),    -- Medieval Literature, position 1, PRIMARY
(22, 32, 1, FALSE),  -- Medieval Epics, position 1
(22, 50, 2, FALSE),  -- Epic Poetry, position 2
(22, 100, 22, FALSE); -- Traditional Canon, position 22

-- ============================================================================
-- FUTURE: SHAIVA WORKS (Examples)
-- ============================================================================

-- Thevaram (when added, work_id = 23)
-- INSERT INTO work_collections (work_id, collection_id, position_in_collection, is_primary) VALUES
-- (23, 3, 2, TRUE),    -- Medieval Literature, position 2, PRIMARY
-- (23, 30, 1, FALSE),  -- Shaiva Literature, position 1
-- (23, 51, 1, FALSE);  -- Devotional Literature, position 1

-- Thiruvachakam (work_id = 24)
-- INSERT INTO work_collections (work_id, collection_id, position_in_collection, is_primary) VALUES
-- (24, 3, 3, TRUE),    -- Medieval Literature, position 3, PRIMARY
-- (24, 30, 2, FALSE),  -- Shaiva Literature, position 2
-- (24, 51, 2, FALSE);  -- Devotional Literature, position 2
```

## Useful Views

### View: Works with their primary collection

```sql
CREATE VIEW works_with_primary_collection AS
SELECT
    w.*,
    c.collection_name,
    c.collection_name_tamil,
    c.collection_type,
    wc.position_in_collection,
    wc.notes AS collection_notes
FROM works w
LEFT JOIN work_collections wc ON w.work_id = wc.work_id AND wc.is_primary = TRUE
LEFT JOIN collections c ON wc.collection_id = c.collection_id;
```

### View: Collection hierarchy with work counts

```sql
CREATE VIEW collection_hierarchy AS
WITH RECURSIVE coll_tree AS (
    -- Base case: top-level collections
    SELECT
        c.collection_id,
        c.collection_name,
        c.collection_name_tamil,
        c.collection_type,
        c.parent_collection_id,
        c.sort_order,
        0 AS depth,
        ARRAY[c.collection_id] AS path,
        c.collection_name::TEXT AS full_path
    FROM collections c
    WHERE c.parent_collection_id IS NULL

    UNION ALL

    -- Recursive case: child collections
    SELECT
        c.collection_id,
        c.collection_name,
        c.collection_name_tamil,
        c.collection_type,
        c.parent_collection_id,
        c.sort_order,
        ct.depth + 1,
        ct.path || c.collection_id,
        ct.full_path || ' > ' || c.collection_name
    FROM collections c
    JOIN coll_tree ct ON c.parent_collection_id = ct.collection_id
)
SELECT
    ct.*,
    COUNT(DISTINCT wc.work_id) AS work_count
FROM coll_tree ct
LEFT JOIN work_collections wc ON ct.collection_id = wc.collection_id
GROUP BY ct.collection_id, ct.collection_name, ct.collection_name_tamil,
         ct.collection_type, ct.parent_collection_id, ct.sort_order,
         ct.depth, ct.path, ct.full_path
ORDER BY ct.path;
```

### View: Works in collection with hierarchy

```sql
CREATE VIEW works_in_collections AS
SELECT
    w.work_id,
    w.work_name,
    w.work_name_tamil,
    c.collection_id,
    c.collection_name,
    c.collection_name_tamil,
    c.collection_type,
    wc.position_in_collection,
    wc.is_primary,
    pc.collection_name AS parent_collection_name,
    pc.collection_name_tamil AS parent_collection_name_tamil
FROM works w
JOIN work_collections wc ON w.work_id = wc.work_id
JOIN collections c ON wc.collection_id = c.collection_id
LEFT JOIN collections pc ON c.parent_collection_id = pc.collection_id
ORDER BY c.collection_id, wc.position_in_collection;
```

## API Endpoints

### Backend Implementation

```python
# In database.py

def get_collections(self, collection_type: Optional[str] = None) -> List[Dict]:
    """Get all collections, optionally filtered by type"""
    with self.get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            query = """
                SELECT
                    c.*,
                    pc.collection_name AS parent_collection_name,
                    COUNT(DISTINCT wc.work_id) AS work_count
                FROM collections c
                LEFT JOIN collections pc ON c.parent_collection_id = pc.collection_id
                LEFT JOIN work_collections wc ON c.collection_id = wc.collection_id
            """
            params = []

            if collection_type:
                query += " WHERE c.collection_type = %s"
                params.append(collection_type)

            query += """
                GROUP BY c.collection_id, pc.collection_name
                ORDER BY c.sort_order, c.collection_name
            """

            cur.execute(query, params)
            return [dict(row) for row in cur.fetchall()]

def get_works_by_collection(self, collection_id: int,
                            include_descendants: bool = False) -> List[Dict]:
    """Get all works in a collection, optionally including descendant collections"""
    with self.get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            if include_descendants:
                # Use recursive CTE to get all descendant collections
                query = """
                    WITH RECURSIVE coll_tree AS (
                        SELECT collection_id FROM collections WHERE collection_id = %s
                        UNION ALL
                        SELECT c.collection_id
                        FROM collections c
                        JOIN coll_tree ct ON c.parent_collection_id = ct.collection_id
                    )
                    SELECT DISTINCT
                        w.*,
                        wc.position_in_collection,
                        wc.is_primary,
                        c.collection_name,
                        c.collection_name_tamil
                    FROM works w
                    JOIN work_collections wc ON w.work_id = wc.work_id
                    JOIN collections c ON wc.collection_id = c.collection_id
                    WHERE wc.collection_id IN (SELECT collection_id FROM coll_tree)
                    ORDER BY wc.position_in_collection, w.work_name
                """
            else:
                query = """
                    SELECT
                        w.*,
                        wc.position_in_collection,
                        wc.is_primary
                    FROM works w
                    JOIN work_collections wc ON w.work_id = wc.work_id
                    WHERE wc.collection_id = %s
                    ORDER BY wc.position_in_collection
                """

            cur.execute(query, (collection_id,))
            return [dict(row) for row in cur.fetchall()]

def get_work_collections(self, work_id: int) -> List[Dict]:
    """Get all collections a work belongs to"""
    with self.get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT
                    c.*,
                    wc.position_in_collection,
                    wc.is_primary,
                    wc.notes,
                    pc.collection_name AS parent_collection_name
                FROM collections c
                JOIN work_collections wc ON c.collection_id = wc.collection_id
                LEFT JOIN collections pc ON c.parent_collection_id = pc.collection_id
                WHERE wc.work_id = %s
                ORDER BY wc.is_primary DESC, c.sort_order
            """, (work_id,))
            return [dict(row) for row in cur.fetchall()]
```

### API Routes (main.py)

```python
# Pydantic models
class Collection(BaseModel):
    collection_id: int
    collection_name: str
    collection_name_tamil: Optional[str]
    collection_type: str
    description: Optional[str]
    parent_collection_id: Optional[int]
    parent_collection_name: Optional[str]
    sort_order: Optional[int]
    work_count: int

class WorkCollection(BaseModel):
    work_id: int
    collection_id: int
    position_in_collection: Optional[int]
    is_primary: bool
    notes: Optional[str]

# Endpoints
@app.get("/collections", response_model=List[Collection])
def get_collections(
    collection_type: Optional[str] = Query(None,
        pattern="^(period|tradition|genre|canon|custom)$",
        description="Filter by collection type")
):
    """Get all collections, optionally filtered by type"""
    try:
        return db.get_collections(collection_type=collection_type)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/collections/{collection_id}/works", response_model=List[Work])
def get_collection_works(
    collection_id: int,
    include_descendants: bool = Query(False,
        description="Include works from descendant collections")
):
    """Get all works in a specific collection"""
    try:
        return db.get_works_by_collection(collection_id, include_descendants)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/works/{work_id}/collections", response_model=List[Collection])
def get_work_collections(work_id: int):
    """Get all collections a work belongs to"""
    try:
        return db.get_work_collections(work_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Update existing /works endpoint
@app.get("/works", response_model=List[Work])
def get_works(
    sort_by: str = Query("alphabetical",
        pattern="^(alphabetical|traditional|chronological|collection)$"),
    collection_id: Optional[int] = Query(None,
        description="Filter by collection ID"),
    collection_type: Optional[str] = Query(None,
        description="Filter by collection type (period/tradition/genre)")
):
    """
    Get works with flexible filtering and sorting

    - **sort_by**: alphabetical, traditional, chronological, or collection
    - **collection_id**: Filter by specific collection
    - **collection_type**: Filter by collection type
    """
    try:
        if collection_id:
            return db.get_works_by_collection(collection_id)

        # ... existing logic with collection filtering
        return db.get_works(sort_by=sort_by, collection_type=collection_type)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

## Parser Script Integration

### Update each parser to assign collections

```python
# Example: thirukkural_bulk_import.py

def _ensure_work_and_collections_exist(self):
    """Create work and assign to collections"""

    # Create work (existing code)
    self.cursor.execute("""
        INSERT INTO works (...)
        VALUES (...)
    """, (...))

    # Assign to collections
    collections_to_assign = [
        (2, 1, True),   # Post-Sangam Literature (primary)
        (20, 1, False), # Eighteen Minor Classics
        (52, 1, False), # Ethical Literature
        (100, 20, False) # Traditional Canon (position 20)
    ]

    for collection_id, position, is_primary in collections_to_assign:
        self.cursor.execute("""
            INSERT INTO work_collections
            (work_id, collection_id, position_in_collection, is_primary)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (work_id, collection_id) DO NOTHING
        """, (self.work_id, collection_id, position, is_primary))

    self.conn.commit()
```

## Migration Script

```sql
-- File: sql/migrations/002_add_collections_system.sql

-- Create collections table
CREATE TABLE IF NOT EXISTS collections (
    collection_id SERIAL PRIMARY KEY,
    collection_name VARCHAR(100) NOT NULL UNIQUE,
    collection_name_tamil VARCHAR(100),
    collection_type VARCHAR(50) NOT NULL,
    description TEXT,
    parent_collection_id INTEGER REFERENCES collections(collection_id),
    sort_order INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create work_collections junction table
CREATE TABLE IF NOT EXISTS work_collections (
    work_collection_id SERIAL PRIMARY KEY,
    work_id INTEGER NOT NULL REFERENCES works(work_id) ON DELETE CASCADE,
    collection_id INTEGER NOT NULL REFERENCES collections(collection_id) ON DELETE CASCADE,
    position_in_collection INTEGER,
    is_primary BOOLEAN DEFAULT FALSE,
    notes TEXT,
    UNIQUE (work_id, collection_id),
    UNIQUE (collection_id, position_in_collection)
);

-- Indexes
CREATE INDEX idx_work_collections_work ON work_collections(work_id);
CREATE INDEX idx_work_collections_collection ON work_collections(collection_id);
CREATE INDEX idx_collections_type ON collections(collection_type);
CREATE INDEX idx_collections_parent ON collections(parent_collection_id);

-- Add primary_collection_id to works
ALTER TABLE works ADD COLUMN IF NOT EXISTS primary_collection_id INTEGER REFERENCES collections(collection_id);
CREATE INDEX idx_works_primary_collection ON works(primary_collection_id);

-- Insert seed collections (from above)
-- ... (all INSERT statements)

-- Migrate existing traditional_sort_order to Traditional Canon collection
-- This maps existing works to collection_id = 100 (Traditional Canon)
INSERT INTO work_collections (work_id, collection_id, position_in_collection, is_primary)
SELECT
    work_id,
    100 AS collection_id,
    traditional_sort_order AS position_in_collection,
    FALSE AS is_primary
FROM works
WHERE traditional_sort_order IS NOT NULL
ON CONFLICT (work_id, collection_id) DO NOTHING;

-- Verify migration
SELECT
    w.work_name,
    c.collection_name,
    wc.position_in_collection,
    wc.is_primary
FROM works w
JOIN work_collections wc ON w.work_id = wc.work_id
JOIN collections c ON wc.collection_id = c.collection_id
ORDER BY c.collection_id, wc.position_in_collection;
```

## Benefits of This Design

1. **Flexibility**: Works can belong to multiple collections simultaneously
2. **Hierarchy**: Collections can have parent-child relationships (Sangam → Ettuthokai)
3. **Extensibility**: Easy to add new collections without schema changes
4. **Historical Accuracy**: Can represent different scholarly traditions
5. **UI-Friendly**: Natural organization for browse/filter interfaces
6. **Future-Proof**: Supports any organizational scheme (period, tradition, genre, custom)

## Example Queries

### Get all Sangam works ordered by position
```sql
SELECT w.*, wc.position_in_collection
FROM works w
JOIN work_collections wc ON w.work_id = wc.work_id
WHERE wc.collection_id = 1  -- Sangam Literature
ORDER BY wc.position_in_collection;
```

### Get all devotional works (across all traditions)
```sql
SELECT DISTINCT w.*
FROM works w
JOIN work_collections wc ON w.work_id = wc.work_id
WHERE wc.collection_id = 51;  -- Devotional Literature
```

### Get collection hierarchy
```sql
SELECT * FROM collection_hierarchy;
```

### Get works in Traditional Canon
```sql
SELECT w.*, wc.position_in_collection
FROM works w
JOIN work_collections wc ON w.work_id = wc.work_id
WHERE wc.collection_id = 100  -- Traditional Canon
ORDER BY wc.position_in_collection;
```

## What do you think?

This design gives you:
- ✅ Multiple collection memberships per work
- ✅ Hierarchical collections (Period → Canon → Work)
- ✅ Easy to add new collections without code changes
- ✅ Backward compatible with traditional_sort_order
- ✅ Scales to hundreds of works and dozens of collections

Should we proceed with implementing this?
