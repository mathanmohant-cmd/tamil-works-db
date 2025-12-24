#!/usr/bin/env python3
"""
Import collections using work NAMES to resolve work_ids
This ensures correct mappings regardless of work_id differences
"""
import psycopg2
from psycopg2.extras import RealDictCursor
import json

def import_collections(database_url, input_file):
    """Import collections and resolve work_ids by work name"""

    # Load export data
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    conn = psycopg2.connect(database_url)
    cur = conn.cursor(cursor_factory=RealDictCursor)

    try:
        # Clear existing data
        print("Clearing existing collection data...")
        cur.execute("DELETE FROM work_collections")
        cur.execute("DELETE FROM collections")
        conn.commit()

        # Import collections in order (parents before children)
        print(f"Importing {len(data['collections'])} collections...")

        # Insert in multiple passes to handle parent-child dependencies
        remaining = data['collections'].copy()
        inserted_ids = set()
        passes = 0

        while remaining and passes < 10:  # Safety limit
            passes += 1
            inserted_this_pass = []

            for coll in remaining:
                # Can insert if parent is NULL or already inserted
                parent_id = coll['parent_collection_id']
                if parent_id is None or parent_id in inserted_ids:
                    cur.execute("""
                        INSERT INTO collections
                        (collection_id, collection_name, collection_name_tamil,
                         collection_type, description, parent_collection_id,
                         sort_order, created_at)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """, [
                        coll['collection_id'],
                        coll['collection_name'],
                        coll['collection_name_tamil'],
                        coll['collection_type'],
                        coll['description'],
                        coll['parent_collection_id'],
                        coll['sort_order'],
                        coll['created_at']
                    ])
                    inserted_ids.add(coll['collection_id'])
                    inserted_this_pass.append(coll)

            # Remove inserted collections from remaining
            for coll in inserted_this_pass:
                remaining.remove(coll)

            conn.commit()

        if remaining:
            print(f"  Warning: Could not insert {len(remaining)} collections due to dependency issues")
        print(f"  Imported {len(inserted_ids)} collections in {passes} passes")

        # Build work_name -> work_id mapping for target database
        print("Building work name to ID mapping...")
        cur.execute("SELECT work_id, work_name FROM works")
        work_name_to_id = {row['work_name']: row['work_id'] for row in cur.fetchall()}
        print(f"  Found {len(work_name_to_id)} works in target database")

        # Import work-collection mappings
        print(f"Importing {len(data['work_collections'])} work-collection mappings...")
        imported = 0
        skipped = 0

        for wc in data['work_collections']:
            work_name = wc['work_name']

            if work_name not in work_name_to_id:
                print(f"  Skipping '{work_name}' - not found in target database")
                skipped += 1
                continue

            work_id = work_name_to_id[work_name]

            cur.execute("""
                INSERT INTO work_collections
                (work_collection_id, work_id, collection_id,
                 position_in_collection, is_primary, notes)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, [
                wc['work_collection_id'],
                work_id,  # Use resolved work_id
                wc['collection_id'],
                wc['position_in_collection'],
                wc['is_primary'],
                wc['notes']
            ])
            imported += 1

        conn.commit()
        print(f"  Imported {imported} work-collection mappings")
        if skipped > 0:
            print(f"  Skipped {skipped} mappings (works not found)")

        # Reset sequence if it exists
        cur.execute("""
            SELECT EXISTS (
                SELECT 1 FROM pg_class
                WHERE relname = 'work_collections_work_collection_id_seq'
            )
        """)
        if cur.fetchone()['exists']:
            cur.execute("""
                SELECT setval('work_collections_work_collection_id_seq',
                              (SELECT COALESCE(MAX(work_collection_id), 0) FROM work_collections))
            """)
            conn.commit()
            print("  Reset work_collections sequence")

        print("\nImport complete!")

    except Exception as e:
        conn.rollback()
        print(f"\nError: {e}")
        raise
    finally:
        cur.close()
        conn.close()

if __name__ == '__main__':
    import sys

    if len(sys.argv) < 2:
        print("Usage: python import_collections_by_name.py <database_url> [input_file]")
        print("\nExample:")
        print('  python import_collections_by_name.py "postgresql://..." collections_export.json')
        sys.exit(1)

    db_url = sys.argv[1]
    input_file = sys.argv[2] if len(sys.argv) > 2 else "collections_export.json"

    import_collections(db_url, input_file)
