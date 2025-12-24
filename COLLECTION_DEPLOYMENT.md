# Collection Tree Deployment Guide

This guide explains how to deploy the collection tree feature to Railway or any production database.

## Overview

The collection tree feature allows users to filter works by browsing a hierarchical structure. Unlike works (which are imported via scripts), collections are created manually via admin tools/SQL.

## Important: Search Works Without Collections

✅ **The search functionality works independently of collections.**

- Collections are **optional** - they only provide filtering capabilities
- If no collections exist, the CollectionTree component shows a friendly message
- Users can still search across all works using the "All works" mode
- The core search API (`/search`) doesn't depend on the `collections` table

## Deploying Collections to Railway

### Step 1: Export from Local Database

Run the export script from your local environment:

```bash
cd scripts

# Using default settings (localhost database)
python export_collections.py

# Or specify custom database URL and output file
python export_collections.py "postgresql://user:pass@localhost/dbname" my_collections.sql
```

This generates a SQL file (default: `collections_export.sql`) containing:
- All collections from the `collections` table
- All work-collection mappings from the `work_collections` table
- Proper sequence resets and updates

### Step 2: Import to Railway Database

1. **Get your Railway database URL** from the Railway dashboard:
   - Go to your project → Database → Connect
   - Copy the `DATABASE_URL` (starts with `postgresql://`)

2. **Run the SQL file**:

```bash
# Method 1: Using psql directly
psql "postgresql://user:pass@hostname/database" -f collections_export.sql

# Method 2: Using Railway CLI (if installed)
railway run psql < collections_export.sql
```

3. **Verify the import**:

```bash
# Connect to Railway database
psql "postgresql://user:pass@hostname/database"

# Check collections
SELECT COUNT(*) FROM collections;
SELECT COUNT(*) FROM work_collections;

# View collection tree structure
SELECT collection_id, parent_collection_id, collection_name_tamil, sort_order
FROM collections
ORDER BY sort_order;
```

## Database Schema

### Collections Table

```sql
CREATE TABLE collections (
    collection_id INTEGER PRIMARY KEY,  -- Note: INTEGER, not SERIAL (no auto-sequence)
    collection_name VARCHAR(100) NOT NULL UNIQUE,
    collection_name_tamil VARCHAR(100),
    collection_type VARCHAR(50) NOT NULL,  -- 'period', 'tradition', 'genre', 'canon', 'custom'
    description TEXT,
    parent_collection_id INTEGER REFERENCES collections(collection_id),
    sort_order INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Important:** The `collection_id` uses `INTEGER` not `SERIAL`, so there's no auto-generated sequence. You must manually manage IDs when inserting collections.

### Work_Collections Table (Junction)

```sql
CREATE TABLE work_collections (
    work_collection_id SERIAL PRIMARY KEY,
    work_id INTEGER NOT NULL REFERENCES works(work_id) ON DELETE CASCADE,
    collection_id INTEGER NOT NULL REFERENCES collections(collection_id) ON DELETE CASCADE,
    position_in_collection INTEGER,
    is_primary BOOLEAN DEFAULT FALSE,
    notes TEXT,
    UNIQUE (work_id, collection_id),
    UNIQUE (collection_id, position_in_collection)
);
```

## Creating Collections (Admin)

To create new collections, you can:

### Option 1: Direct SQL

```sql
-- Add a root collection
INSERT INTO collections (collection_name, collection_name_tamil, collection_type, sort_order)
VALUES ('Tamil Literature', 'தமிழ் இலக்கியம்', 'custom', 1);

-- Add a child collection
INSERT INTO collections (parent_collection_id, collection_name, collection_name_tamil, collection_type, sort_order)
VALUES (1, 'Sangam Literature', 'சங்க இலக்கியம்', 'period', 1);

-- Add works to a collection
INSERT INTO work_collections (collection_id, work_id, position_in_collection)
VALUES (2, 5, 1), (2, 6, 2), (2, 7, 3);
```

### Option 2: Admin Script (Recommended)

Create a Python script for easier management:

```python
import psycopg2

conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()

# Insert collection
cur.execute("""
    INSERT INTO collections (collection_name_tamil, collection_type, sort_order)
    VALUES (%s, %s, %s) RETURNING collection_id
""", ("தமிழ் இலக்கியம்", "custom", 1))

collection_id = cur.fetchone()[0]

# Add works
cur.execute("""
    INSERT INTO work_collections (collection_id, work_id, position_in_collection)
    VALUES (%s, %s, %s)
""", (collection_id, 5, 1))

conn.commit()
```

## API Endpoints

The collection feature adds these endpoints:

- `GET /collections/tree` - Returns hierarchical collection tree with work counts
- `GET /collections/{collection_id}/works` - Returns all works in a collection

Both endpoints are optional and the app works fine if they return empty results.

## Frontend Behavior

- **No collections**: Shows message "No collections available. Search will work with all works."
- **Has collections**: Shows expandable tree with filtering
- **Auto-expand**: Expands all on first open, or expands only selected collections if works are already selected

## Updating Collections

To update collections after the initial deployment:

1. Make changes to your local database (add/edit collections)
2. Re-run the export script: `python export_collections.py`
3. Re-import the generated SQL file to Railway

**Note**: The export script includes `DELETE` statements, so it will clear existing collections before importing. If you want to add incrementally, edit the generated SQL file to remove the DELETE statements.

## Troubleshooting

### Collections not showing in UI

1. Check API endpoint: `curl https://yourapp.railway.app/collections/tree`
2. Check browser console for errors
3. Verify database has collections: `SELECT COUNT(*) FROM collections;`

### Search not working

Collections are optional - if search isn't working, it's unrelated to collections. Check:
- Backend API is running
- Database connection is valid
- Works table has data

### Import errors

Common issues:
- **Foreign key violations**: Make sure work_ids in work_collections match existing works
- **Sequence errors**: The script resets sequences, but if you have existing data, adjust manually
- **Permission errors**: Ensure your Railway database user has INSERT/DELETE permissions

## Best Practices

1. **Keep collections in sync**: Update collections when adding new works
2. **Use sort_order**: Always set sort_order to control display order
3. **Test locally first**: Always test collection changes locally before deploying
4. **Version control SQL**: Commit the generated collections_export.sql to git
5. **Backup before import**: Railway provides automatic backups, but you can also use `pg_dump`

## Example Collection Structure

```
தமிழ் இலக்கியம் (Tamil Literature)
├── சங்க இலக்கியம் (Sangam Literature)
│   ├── எட்டுத்தொகை (Eight Anthologies)
│   │   ├── நற்றிணை (Natrinai)
│   │   ├── குறுந்தொகை (Kuruntokai)
│   │   └── ...
│   └── பத்துப்பாட்டு (Ten Idylls)
├── பதினெண்மேற்கணக்கு (Eighteen Greater Texts)
│   ├── திருக்குறள் (Thirukkural)
│   └── ...
└── ஐம்பெருங்காப்பியங்கள் (Five Great Epics)
    ├── சிலப்பதிகாரம் (Silapathikaram)
    └── ...
```
