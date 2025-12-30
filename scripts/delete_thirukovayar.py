#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Delete Thirukovayar work

This script deletes:
- Thirukovayar work (திருக்கோவையார்)
- Collection 3218 (எட்டாம் திருமுறை - 8th Thirumurai) IF it becomes empty
  (i.e., if Thiruvasagam has also been deleted)

Usage:
    python delete_thirukovayar.py [database_url]
"""

import os
import sys
import psycopg2

def delete_thirukovayar(connection_string):
    """Delete Thirukovayar work and collection 3218 if it becomes empty"""
    print("\n" + "="*70)
    print("  DELETE THIRUKOVAYAR")
    print("="*70)

    try:
        conn = psycopg2.connect(connection_string)
        conn.autocommit = False  # Use transaction
        cursor = conn.cursor()

        # Check what exists
        cursor.execute("""
            SELECT w.work_id, w.work_name, w.work_name_tamil
            FROM works w
            JOIN work_collections wc ON w.work_id = wc.work_id
            WHERE wc.collection_id = 3218
              AND w.work_name_tamil = 'திருக்கோவையார்'
        """)
        work_row = cursor.fetchone()

        if not work_row:
            print("\n✗ Thirukovayar work not found")
            return False

        work_id, work_name, work_name_tamil = work_row
        print(f"\nFound work: {work_name_tamil} ({work_name}) - ID: {work_id}")

        # Check how many works are in collection 3218
        cursor.execute("""
            SELECT COUNT(*) FROM work_collections WHERE collection_id = 3218
        """)
        work_count = cursor.fetchone()[0]

        print("\nThis will delete:")
        print(f"  - Work: {work_name_tamil} (all data: sections, verses, lines, words)")
        if work_count <= 1:
            print(f"  - Collection 3218 (எட்டாம் திருமுறை) - will be DELETED (becomes empty)")
        else:
            print(f"  - NOTE: Collection 3218 (எட்டாம் திருமுறை) will NOT be deleted")
            print(f"    because it still contains {work_count - 1} other work(s)")

        response = input("\nAre you sure? (yes/no): ").strip().lower()
        if response not in ['yes', 'y']:
            print("Deletion cancelled.")
            return False

        print("\nDeleting Thirukovayar work...")
        print(f"  Deleting work {work_id}...")
        delete_work_by_id(cursor, work_id)

        # Check if collection 3218 is now empty and delete if so
        cursor.execute("""
            SELECT COUNT(*) FROM work_collections WHERE collection_id = 3218
        """)
        remaining_works = cursor.fetchone()[0]

        if remaining_works == 0:
            print(f"  Collection 3218 (எட்டாம் திருமுறை) is now empty, deleting...")
            cursor.execute("DELETE FROM collections WHERE collection_id = 3218")
            print(f"  ✓ Deleted empty collection 3218")

        conn.commit()
        print("\n✓ Successfully deleted Thirukovayar work")
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

    if delete_thirukovayar(db_connection):
        print("\n✓ Deletion complete")
        sys.exit(0)
    else:
        print("\n✗ Deletion failed")
        sys.exit(1)

if __name__ == '__main__':
    main()
