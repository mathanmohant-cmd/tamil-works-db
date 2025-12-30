#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Delete Thembavani work

This script deletes:
- Thembavani work (தேம்பாவணி) by Veeramaamunivar
- Standalone devotional work (collection 323: பக்தி இலக்கியம்)

Deletion order:
1. Delete the work (cascades to sections, verses, lines, words)
2. Delete collection 323 if it becomes empty

Usage:
    python delete_thembavani.py [database_url]
"""

import os
import sys
import psycopg2

def delete_thembavani(connection_string):
    """Delete Thembavani work"""
    print("\n" + "="*70)
    print("  DELETE THEMBAVANI")
    print("="*70)

    conn = None
    cursor = None

    try:
        conn = psycopg2.connect(connection_string)
        conn.autocommit = False  # Use transaction
        cursor = conn.cursor()

        # Check what exists
        cursor.execute("""
            SELECT work_id, work_name, work_name_tamil
            FROM works
            WHERE work_name = 'Thembavani'
        """)
        work_row = cursor.fetchone()

        if not work_row:
            print("\n✗ Thembavani work not found")
            return False

        work_id, work_name, work_name_tamil = work_row
        print(f"\nFound work: {work_name_tamil} ({work_name}) - ID: {work_id}")
        print("\nThis will delete:")
        print(f"  - Work: {work_name_tamil} (all data: sections, verses, lines, words)")

        response = input("\nAre you sure? (yes/no): ").strip().lower()
        if response not in ['yes', 'y']:
            print("Deletion cancelled.")
            return False

        print("\nDeleting Thembavani work...")
        print(f"  Deleting work {work_id}...")
        delete_work_by_id(cursor, work_id)

        # Check and delete collection 323 if empty
        delete_collection_if_empty(cursor, 323)

        conn.commit()
        print("\n✓ Successfully deleted Thembavani work")
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

def delete_collection_if_empty(cursor, collection_id=323):
    """
    Delete collection 323 (பக்தி இலக்கியம்) if it has no more works.
    This should be called AFTER the work has been deleted.
    """
    # Check if collection 323 has any works left
    cursor.execute("""
        SELECT COUNT(*) FROM work_collections WHERE collection_id = %s
    """, (collection_id,))
    work_count = cursor.fetchone()[0]

    if work_count == 0:
        print(f"\n  Collection {collection_id} (பக்தி இலக்கியம்) is now empty")
        print(f"  Deleting collection {collection_id}...")
        cursor.execute("DELETE FROM collections WHERE collection_id = %s", (collection_id,))
        print(f"  ✓ Deleted empty collection {collection_id}")
    else:
        print(f"\n  Collection {collection_id} still has {work_count} work(s), keeping it")

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

    if delete_thembavani(db_connection):
        print("\n✓ Deletion complete")
        sys.exit(0)
    else:
        print("\n✗ Deletion failed")
        sys.exit(1)

if __name__ == '__main__':
    main()
