#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Delete Devaram works and collections

This script deletes:
- All 7 Devaram works (Thirumurai 1-7)
- Individual Thirumurai collections (32111-32117)
- Author sub-collections (321111-321113)
- Main Devaram collection (3211)

Usage:
    python delete_devaram.py [database_url]
"""

import os
import sys
import psycopg2

def delete_devaram(connection_string):
    """Delete all Devaram data in correct order"""
    print("\n" + "="*70)
    print("  DELETE DEVARAM")
    print("="*70)

    try:
        conn = psycopg2.connect(connection_string)
        conn.autocommit = False  # Use transaction
        cursor = conn.cursor()

        # Check what exists
        cursor.execute("""
            SELECT COUNT(*) FROM works w
            JOIN work_collections wc ON w.work_id = wc.work_id
            WHERE wc.collection_id IN (32111, 32112, 32113, 32114, 32115, 32116, 32117)
        """)
        work_count = cursor.fetchone()[0]

        if work_count == 0:
            print("\n✗ No Devaram works found")
            return False

        print(f"\nFound {work_count} Devaram works")
        print("\nThis will delete:")
        print("  - 7 Devaram works (all data: sections, verses, lines, words)")
        print("  - Individual Thirumurai collections (முதலாம் திருமுறை - ஏழாம் திருமுறை)")
        print("  - Author sub-collections (சம்பந்தர், அப்பர், சுந்தரர்)")
        print("  - Main Devaram collection (தேவாரம்)")

        response = input("\nAre you sure? (yes/no): ").strip().lower()
        if response not in ['yes', 'y']:
            print("Deletion cancelled.")
            return False

        print("\nDeleting Devaram data...")

        # 1. Delete all works in individual Thirumurai collections
        thirumurai_collections = [32111, 32112, 32113, 32114, 32115, 32116, 32117]

        for coll_id in thirumurai_collections:
            cursor.execute("""
                SELECT work_id FROM work_collections WHERE collection_id = %s
            """, (coll_id,))
            work_ids = [row[0] for row in cursor.fetchall()]

            for work_id in work_ids:
                print(f"  Deleting work {work_id}...")
                delete_work_by_id(cursor, work_id)

        # 2. Delete child collections (individual Thirumurai)
        print("  Deleting individual Thirumurai collections...")
        for coll_id in thirumurai_collections:
            cursor.execute("DELETE FROM collections WHERE collection_id = %s", (coll_id,))

        # 3. Delete author sub-collections
        print("  Deleting author sub-collections...")
        author_collections = [321111, 321112, 321113]
        for coll_id in author_collections:
            cursor.execute("DELETE FROM collections WHERE collection_id = %s", (coll_id,))

        # 4. Delete main Devaram collection
        print("  Deleting main Devaram collection...")
        cursor.execute("DELETE FROM collections WHERE collection_id = 3211")

        conn.commit()
        print("\n✓ Successfully deleted all Devaram data")
        return True

    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        if conn:
            conn.rollback()
        return False
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def delete_work_by_id(cursor, work_id):
    """Delete a work and all its data (within a transaction)"""
    # Delete words
    cursor.execute("""
        DELETE FROM words
        WHERE line_id IN (
            SELECT l.line_id FROM lines l
            JOIN verses v ON l.verse_id = v.verse_id
            WHERE v.work_id = %s
        )
    """, (work_id,))

    # Delete lines
    cursor.execute("""
        DELETE FROM lines
        WHERE verse_id IN (SELECT verse_id FROM verses WHERE work_id = %s)
    """, (work_id,))

    # Delete verse collections
    cursor.execute("""
        DELETE FROM verse_collections
        WHERE verse_id IN (SELECT verse_id FROM verses WHERE work_id = %s)
    """, (work_id,))

    # Delete verses
    cursor.execute("DELETE FROM verses WHERE work_id = %s", (work_id,))

    # Delete section collections
    cursor.execute("""
        DELETE FROM section_collections
        WHERE section_id IN (SELECT section_id FROM sections WHERE work_id = %s)
    """, (work_id,))

    # Delete sections
    cursor.execute("DELETE FROM sections WHERE work_id = %s", (work_id,))

    # Delete work collections
    cursor.execute("DELETE FROM work_collections WHERE work_id = %s", (work_id,))

    # Delete work
    cursor.execute("DELETE FROM works WHERE work_id = %s", (work_id,))

def main():
    # Get database connection string
    db_connection = os.getenv('DATABASE_URL', "postgresql://postgres:postgres@localhost/tamil_literature")
    if len(sys.argv) > 1:
        db_connection = sys.argv[1]

    print(f"Database: {db_connection[:50]}...")

    if delete_devaram(db_connection):
        print("\n✓ Deletion complete")
        sys.exit(0)
    else:
        print("\n✗ Deletion failed")
        sys.exit(1)

if __name__ == '__main__':
    main()
