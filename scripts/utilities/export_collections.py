"""
Export collections and work_collections tables to SQL INSERT statements.

This script exports the collection tree structure from your local database
and generates a SQL file that can be run on Railway or any other PostgreSQL database.

Usage:
    python export_collections.py [source_db_url] [output_file]

    If not provided:
    - source_db_url defaults to: postgresql://postgres:postgres@localhost/tamil_literature
    - output_file defaults to: collections_export.sql
"""

import sys
import psycopg2
from datetime import datetime

def export_collections(source_db_url=None, output_file='collections_export.sql'):
    """Export collections and work_collections to SQL INSERT statements."""

    # Default database URL
    if not source_db_url:
        source_db_url = 'postgresql://postgres:postgres@localhost/tamil_literature'

    print(f"Connecting to source database: {source_db_url}")

    try:
        # Connect to source database
        conn = psycopg2.connect(source_db_url)
        cur = conn.cursor()

        # Read collections in hierarchical order (parents before children)
        # Using recursive CTE to ensure proper insertion order
        cur.execute("""
            WITH RECURSIVE collection_tree AS (
                -- Root collections (no parent)
                SELECT collection_id, collection_name, collection_name_tamil,
                       collection_type, description, parent_collection_id,
                       sort_order, created_at, 0 as level
                FROM collections
                WHERE parent_collection_id IS NULL

                UNION ALL

                -- Child collections
                SELECT c.collection_id, c.collection_name, c.collection_name_tamil,
                       c.collection_type, c.description, c.parent_collection_id,
                       c.sort_order, c.created_at, ct.level + 1
                FROM collections c
                INNER JOIN collection_tree ct ON c.parent_collection_id = ct.collection_id
            )
            SELECT collection_id, collection_name, collection_name_tamil,
                   collection_type, description, parent_collection_id,
                   sort_order, created_at
            FROM collection_tree
            ORDER BY level, sort_order, collection_id
        """)
        collections = cur.fetchall()

        # Read work_collections
        cur.execute("""
            SELECT work_collection_id, work_id, collection_id,
                   position_in_collection, is_primary, notes
            FROM work_collections
            ORDER BY collection_id, position_in_collection
        """)
        work_collections = cur.fetchall()

        print(f"Found {len(collections)} collections")
        print(f"Found {len(work_collections)} work-collection mappings")

        # Generate SQL file
        with open(output_file, 'w', encoding='utf-8') as f:
            # Header
            f.write("-- Collection Tree Export\n")
            f.write(f"-- Generated: {datetime.now().isoformat()}\n")
            f.write(f"-- Source: {source_db_url}\n")
            f.write("-- \n")
            f.write("-- Instructions:\n")
            f.write("-- 1. Connect to your Railway database\n")
            f.write("-- 2. Run this SQL file: psql $DATABASE_URL -f collections_export.sql\n")
            f.write("-- \n\n")

            # Clear existing data
            f.write("-- Clear existing collection data\n")
            f.write("DELETE FROM work_collections;\n")
            f.write("DELETE FROM collections;\n\n")

            # Reset sequences (only if they exist)
            f.write("-- Reset sequences (only work_collections has SERIAL, collections uses INTEGER)\n")
            f.write("-- collections table uses INTEGER PRIMARY KEY, not SERIAL, so no sequence\n")
            f.write("DO $$ BEGIN\n")
            f.write("  IF EXISTS (SELECT 1 FROM pg_class WHERE relname = 'work_collections_work_collection_id_seq') THEN\n")
            f.write("    PERFORM setval('work_collections_work_collection_id_seq', 1, false);\n")
            f.write("  END IF;\n")
            f.write("END $$;\n\n")

            # Insert collections
            f.write("-- Insert collections\n")
            for row in collections:
                collection_id, name, name_tamil, coll_type, desc, parent_id, sort_order, created_at = row

                # Handle NULL values
                name_str = 'NULL' if name is None else f"'{name.replace("'", "''")}'"
                name_tamil_str = 'NULL' if name_tamil is None else f"'{name_tamil.replace("'", "''")}'"
                coll_type_str = 'NULL' if coll_type is None else f"'{coll_type.replace("'", "''")}'"
                desc_str = 'NULL' if desc is None else f"'{desc.replace("'", "''")}'"
                parent_id_str = 'NULL' if parent_id is None else str(parent_id)
                sort_order_str = 'NULL' if sort_order is None else str(sort_order)
                created_at_str = 'CURRENT_TIMESTAMP' if created_at is None else f"'{created_at}'"

                f.write(f"""INSERT INTO collections (collection_id, collection_name, collection_name_tamil, collection_type, description, parent_collection_id, sort_order, created_at)
VALUES ({collection_id}, {name_str}, {name_tamil_str}, {coll_type_str}, {desc_str}, {parent_id_str}, {sort_order_str}, {created_at_str});\n""")

            f.write("\n")

            # Insert work_collections
            f.write("-- Insert work-collection mappings\n")
            for row in work_collections:
                wc_id, work_id, collection_id, position, is_primary, notes = row

                position_str = 'NULL' if position is None else str(position)
                is_primary_str = 'FALSE' if is_primary is None else ('TRUE' if is_primary else 'FALSE')
                notes_str = 'NULL' if notes is None else f"'{notes.replace("'", "''")}'"

                f.write(f"""INSERT INTO work_collections (work_collection_id, work_id, collection_id, position_in_collection, is_primary, notes)
VALUES ({wc_id}, {work_id}, {collection_id}, {position_str}, {is_primary_str}, {notes_str});\n""")

            f.write("\n")

            # Update sequences to max values (only work_collections has a sequence)
            f.write("-- Update work_collections sequence to current max\n")
            f.write("-- Note: collections table has no sequence (uses INTEGER PRIMARY KEY, not SERIAL)\n")
            f.write("DO $$ BEGIN\n")
            f.write("  IF EXISTS (SELECT 1 FROM pg_class WHERE relname = 'work_collections_work_collection_id_seq') THEN\n")
            f.write("    PERFORM setval('work_collections_work_collection_id_seq', (SELECT COALESCE(MAX(work_collection_id), 0) FROM work_collections));\n")
            f.write("  END IF;\n")
            f.write("END $$;\n")

            f.write("\n-- Export complete!\n")

        print(f"\nExport successful!")
        print(f"SQL file created: {output_file}")
        print(f"\nTo import on Railway:")
        print(f"1. Get your Railway database URL from dashboard")
        print(f"2. Run: psql <RAILWAY_DATABASE_URL> -f {output_file}")

        cur.close()
        conn.close()

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    # Parse command line arguments
    source_db = sys.argv[1] if len(sys.argv) > 1 else None
    output = sys.argv[2] if len(sys.argv) > 2 else 'collections_export.sql'

    export_collections(source_db, output)
