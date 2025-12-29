#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Delete Thiruvisaippa works and collections

This script deletes:
- 10 Thiruvisaippa works (9 works + திருப்பல்லாண்டு)
- Sub-collection 32191 (திருவிசைப்பா sub-collection)
- Main collection 3219 (ஒன்பதாம் திருமுறை - 9th Thirumurai)

Usage:
    python delete_thiruvisaippa.py [database_url]
"""

import os
import sys
import psycopg2

def delete_thiruvisaippa(connection_string):
    """Delete all Thiruvisaippa works and collections"""
    print("\n" + "="*70)
    print("  DELETE THIRUVISAIPPA")
    print("="*70)

    try:
        conn = psycopg2.connect(connection_string)
        conn.autocommit = False  # Use transaction
        cursor = conn.cursor()

        # Check what exists
        cursor.execute("""
            SELECT COUNT(*) FROM works w
            JOIN work_collections wc ON w.work_id = wc.work_id
            WHERE wc.collection_id IN (3219, 32191)
        """)
        work_count = cursor.fetchone()[0]

        if work_count == 0:
            print("\n✗ No Thiruvisaippa works found")
            return False

        print(f"\nFound {work_count} Thiruvisaippa works")
        print("\nThis will delete:")
        print("  - 10 works (9 Thiruvisaippa works + திருப்பல்லாண்டு)")
        print("    All data: sections, verses, lines, words")
        print("  - Sub-collection 32191 (திருவிசைப்பா)")
        print("  - Main collection 3219 (ஒன்பதாம் திருமுறை - 9th Thirumurai)")

        response = input("\nAre you sure? (yes/no): ").strip().lower()
        if response not in ['yes', 'y']:
            print("Deletion cancelled.")
            return False

        print("\nDeleting Thiruvisaippa data...")

        # 1. Delete all works in both collections
        collections = [3219, 32191]

        for coll_id in collections:
            cursor.execute("""
                SELECT work_id FROM work_collections WHERE collection_id = %s
            """, (coll_id,))
            work_ids = [row[0] for row in cursor.fetchall()]

            for work_id in work_ids:
                print(f"  Deleting work {work_id}...")
                delete_work_by_id(cursor, work_id)

        # 2. Delete sub-collection first
        print("  Deleting sub-collection 32191 (திருவிசைப்பா)...")
        cursor.execute("DELETE FROM collections WHERE collection_id = 32191")

        # 3. Delete main collection
        print("  Deleting main collection 3219 (ஒன்பதாம் திருமுறை)...")
        cursor.execute("DELETE FROM collections WHERE collection_id = 3219")

        conn.commit()
        print("\n✓ Successfully deleted all Thiruvisaippa data")
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

    if delete_thiruvisaippa(db_connection):
        print("\n✓ Deletion complete")
        sys.exit(0)
    else:
        print("\n✗ Deletion failed")
        sys.exit(1)

if __name__ == '__main__':
    main()
