#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Delete Seerapuranam work

This script deletes:
- Seerapuranam work (சீறாப்புராணம்)
- Standalone devotional work (no collection)

Usage:
    python delete_seerapuranam.py [database_url]
"""

import os
import sys
import psycopg2

def delete_seerapuranam(connection_string):
    """Delete Seerapuranam work"""
    print("\n" + "="*70)
    print("  DELETE SEERAPURANAM")
    print("="*70)

    try:
        conn = psycopg2.connect(connection_string)
        conn.autocommit = False  # Use transaction
        cursor = conn.cursor()

        # Check what exists
        cursor.execute("""
            SELECT work_id, work_name, work_name_tamil
            FROM works
            WHERE work_name = 'Seerapuranam'
        """)
        work_row = cursor.fetchone()

        if not work_row:
            print("\n✗ Seerapuranam work not found")
            return False

        work_id, work_name, work_name_tamil = work_row
        print(f"\nFound work: {work_name_tamil} ({work_name}) - ID: {work_id}")
        print("\nThis will delete:")
        print(f"  - Work: {work_name_tamil} (all data: sections, verses, lines, words)")
        print(f"  - NOTE: Seerapuranam is a standalone work (no collection)")

        response = input("\nAre you sure? (yes/no): ").strip().lower()
        if response not in ['yes', 'y']:
            print("Deletion cancelled.")
            return False

        print("\nDeleting Seerapuranam work...")
        print(f"  Deleting work {work_id}...")
        delete_work_by_id(cursor, work_id)

        conn.commit()
        print("\n✓ Successfully deleted Seerapuranam work")
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

    if delete_seerapuranam(db_connection):
        print("\n✓ Deletion complete")
        sys.exit(0)
    else:
        print("\n✗ Deletion failed")
        sys.exit(1)

if __name__ == '__main__':
    main()
