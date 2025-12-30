#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Delete Periya Puranam work and collection

This script deletes:
- Periya Puranam work (பெரிய புராணம்)
- Collection 32119 (பன்னிரண்டாம் திருமுறை - 12th Thirumurai / Twelfth Thirumurai)

Usage:
    python delete_periya_puranam.py [database_url]
"""

import os
import sys
import psycopg2

def delete_periya_puranam(connection_string):
    """Delete Periya Puranam work and collection"""
    print("\n" + "="*70)
    print("  DELETE PERIYA PURANAM")
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
            WHERE wc.collection_id = 32119
        """)
        work_row = cursor.fetchone()

        if not work_row:
            print("\n✗ Periya Puranam work not found")
            return False

        work_id, work_name, work_name_tamil = work_row
        print(f"\nFound work: {work_name_tamil} ({work_name}) - ID: {work_id}")
        print("\nThis will delete:")
        print(f"  - Work: {work_name_tamil} (all data: sections, verses, lines, words)")
        print(f"  - Collection 32119 (பன்னிரண்டாம் திருமுறை - 12th Thirumurai / Twelfth Thirumurai)")

        response = input("\nAre you sure? (yes/no): ").strip().lower()
        if response not in ['yes', 'y']:
            print("Deletion cancelled.")
            return False

        print("\nDeleting Periya Puranam data...")

        # 1. Delete work
        print(f"  Deleting work {work_id}...")
        delete_work_by_id(cursor, work_id)

        # 2. Delete collection
        print("  Deleting collection 32119 (பன்னிரண்டாம் திருமுறை - Twelfth Thirumurai)...")
        cursor.execute("DELETE FROM collections WHERE collection_id = 32119")

        conn.commit()
        print("\n✓ Successfully deleted Periya Puranam work and collection")
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

    if delete_periya_puranam(db_connection):
        print("\n✓ Deletion complete")
        sys.exit(0)
    else:
        print("\n✗ Deletion failed")
        sys.exit(1)

if __name__ == '__main__':
    main()
