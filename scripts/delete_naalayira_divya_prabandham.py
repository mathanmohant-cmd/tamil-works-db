#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Delete Naalayira Divya Prabandham works and collections

This script deletes:
- 24 Naalayira Divya Prabandham works
- Sub-collections: 3221, 3222, 3223, 3224 (four "thousands")
- Main collection: 322 (நாலாயிரத் திவ்விய பிரபந்தம்)

Deletion order:
1. Delete all 24 works
2. Delete sub-collections (3221-3224)
3. Delete main collection (322)

Usage:
    python delete_naalayira_divya_prabandham.py [database_url]
"""

import os
import sys
import psycopg2

def delete_naalayira_divya_prabandham(connection_string):
    """Delete all Naalayira Divya Prabandham works and collections"""
    print("\n" + "="*70)
    print("  DELETE NAALAYIRA DIVYA PRABANDHAM")
    print("="*70)

    conn = None
    cursor = None

    try:
        conn = psycopg2.connect(connection_string)
        conn.autocommit = False  # Use transaction
        cursor = conn.cursor()

        # Check what exists
        cursor.execute("""
            SELECT COUNT(*) FROM works w
            JOIN work_collections wc ON w.work_id = wc.work_id
            WHERE wc.collection_id IN (322, 3221, 3222, 3223, 3224)
        """)
        work_count = cursor.fetchone()[0]

        if work_count == 0:
            print("\n✗ No Naalayira Divya Prabandham works found")
            return False

        print(f"\nFound {work_count} Naalayira Divya Prabandham works")
        print("\nThis will delete:")
        print(f"  - {work_count} works (all data: sections, verses, lines, words)")
        print("  - Sub-collections:")
        print("      3221 (முதல் ஆயிரம் - First Thousand)")
        print("      3222 (இரண்டாம் ஆயிரம் - Second Thousand)")
        print("      3223 (மூன்றாம் ஆயிரம் - Third Thousand)")
        print("      3224 (நான்காம் ஆயிரம் - Fourth Thousand)")
        print("  - Main collection 322 (நாலாயிரத் திவ்விய பிரபந்தம்)")

        response = input("\nAre you sure? (yes/no): ").strip().lower()
        if response not in ['yes', 'y']:
            print("Deletion cancelled.")
            return False

        print("\nDeleting Naalayira Divya Prabandham data...")

        # 1. Delete all works in all collections
        all_collections = [322, 3221, 3222, 3223, 3224]

        for coll_id in all_collections:
            cursor.execute("""
                SELECT work_id FROM work_collections WHERE collection_id = %s
            """, (coll_id,))
            work_ids = [row[0] for row in cursor.fetchall()]

            for work_id in work_ids:
                print(f"  Deleting work {work_id}...")
                delete_work_by_id(cursor, work_id)

        # 2. Delete sub-collections (four "thousands")
        print("  Deleting sub-collections (3221-3224)...")
        sub_collections = [3221, 3222, 3223, 3224]
        for coll_id in sub_collections:
            cursor.execute("DELETE FROM collections WHERE collection_id = %s", (coll_id,))

        # 3. Delete main collection
        print("  Deleting main collection 322 (நாலாயிரத் திவ்விய பிரபந்தம்)...")
        cursor.execute("DELETE FROM collections WHERE collection_id = 322")

        conn.commit()
        print("\n✓ Successfully deleted all Naalayira Divya Prabandham data")
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

    if delete_naalayira_divya_prabandham(db_connection):
        print("\n✓ Deletion complete")
        sys.exit(0)
    else:
        print("\n✗ Deletion failed")
        sys.exit(1)

if __name__ == '__main__':
    main()
