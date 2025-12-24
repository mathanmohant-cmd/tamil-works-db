#!/usr/bin/env python3
"""
Export collections with work NAMES instead of work IDs
This ensures portability between databases with different work_id sequences
"""
import psycopg2
from psycopg2.extras import RealDictCursor
import json
from datetime import datetime

def export_collections(database_url, output_file):
    """Export collections and work mappings using work names"""
    conn = psycopg2.connect(database_url)
    cur = conn.cursor(cursor_factory=RealDictCursor)

    # Export collections
    cur.execute("""
        SELECT collection_id, collection_name, collection_name_tamil,
               collection_type, description, parent_collection_id,
               sort_order, created_at
        FROM collections
        ORDER BY collection_id
    """)
    collections = cur.fetchall()

    # Export work-collection mappings with work NAMES
    cur.execute("""
        SELECT wc.work_collection_id, w.work_name, wc.collection_id,
               wc.position_in_collection, wc.is_primary, wc.notes
        FROM work_collections wc
        JOIN works w ON wc.work_id = w.work_id
        ORDER BY wc.collection_id, wc.position_in_collection
    """)
    work_collections = cur.fetchall()

    cur.close()
    conn.close()

    # Convert to regular dicts and handle datetime
    export_data = {
        'exported_at': datetime.now().isoformat(),
        'collections': [dict(row) for row in collections],
        'work_collections': [dict(row) for row in work_collections]
    }

    # Convert datetime objects to strings
    for coll in export_data['collections']:
        if coll['created_at']:
            coll['created_at'] = coll['created_at'].isoformat()

    # Write to file
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(export_data, f, indent=2, ensure_ascii=False)

    print(f"Exported {len(collections)} collections")
    print(f"Exported {len(work_collections)} work-collection mappings")
    print(f"Output: {output_file}")

if __name__ == '__main__':
    import sys

    # Use local database by default
    db_url = sys.argv[1] if len(sys.argv) > 1 else "postgresql://postgres:postgres@localhost:5432/tamil_literature"
    output = sys.argv[2] if len(sys.argv) > 2 else "collections_export.json"

    export_collections(db_url, output)
