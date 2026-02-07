#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Delete Kambaramayanam work and optionally collection 500

This script deletes:
- Kambaramayanam work (கம்பராமாயணம்)
- Optionally collection 500 (காப்பியங்கள் / Epics) if no other works are in it

Usage:
    python delete_kambaramayanam.py [database_url]

Examples:
    python delete_kambaramayanam.py
    python delete_kambaramayanam.py postgresql://postgres:postgres@localhost/tamil_literature
"""

import os
import sys
import psycopg2

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

def delete_kambaramayanam(connection_string):
    """Delete Kambaramayanam work and optionally collection 500"""
    print("\n" + "="*70)
    print("  DELETE KAMBARAMAYANAM (கம்பராமாயணம்)")
    print("="*70)

    try:
        conn = psycopg2.connect(connection_string)
        conn.autocommit = False  # Use transaction
        cursor = conn.cursor()

        # Check if work exists
        cursor.execute("""
            SELECT work_id, work_name, work_name_tamil
            FROM works
            WHERE work_name_tamil = 'கம்பராமாயணம்'
        """)
        work_row = cursor.fetchone()

        if not work_row:
            print("\n✗ Kambaramayanam work not found")
            cursor.close()
            conn.close()
            return False

        work_id, work_name, work_name_tamil = work_row
        print(f"\nFound work: {work_name_tamil} ({work_name}) - ID: {work_id}")

        # Get stats
        cursor.execute("""
            SELECT COUNT(*) FROM sections WHERE work_id = %s
        """, (work_id,))
        section_count = cursor.fetchone()[0]

        cursor.execute("""
            SELECT COUNT(*) FROM verses WHERE work_id = %s
        """, (work_id,))
        verse_count = cursor.fetchone()[0]

        cursor.execute("""
            SELECT COUNT(*) FROM lines l
            JOIN verses v ON l.verse_id = v.verse_id
            WHERE v.work_id = %s
        """, (work_id,))
        line_count = cursor.fetchone()[0]

        cursor.execute("""
            SELECT COUNT(*) FROM words w
            JOIN lines l ON w.line_id = l.line_id
            JOIN verses v ON l.verse_id = v.verse_id
            WHERE v.work_id = %s
        """, (work_id,))
        word_count = cursor.fetchone()[0]

        print("\nThis will delete:")
        print(f"  - Work: {work_name_tamil}")
        print(f"  - {section_count:,} sections")
        print(f"  - {verse_count:,} verses")
        print(f"  - {line_count:,} lines")
        print(f"  - {word_count:,} words")

        # Check if collection 500 exists and how many works it has
        cursor.execute("""
            SELECT COUNT(*) FROM work_collections WHERE collection_id = 500
        """)
        works_in_collection = cursor.fetchone()[0]

        delete_collection = False
        if works_in_collection == 1:
            print(f"  - Collection 500 (காப்பியங்கள் / Epics) - only contains this work")
            delete_collection = True
        elif works_in_collection > 1:
            print(f"\nNote: Collection 500 (காப்பியங்கள் / Epics) has {works_in_collection} works.")
            print("      It will NOT be deleted.")

        response = input("\nAre you sure? (yes/no): ").strip().lower()
        if response not in ['yes', 'y']:
            print("Deletion cancelled.")
            cursor.close()
            conn.close()
            return False

        print("\nDeleting Kambaramayanam...")
        delete_work_by_id(cursor, work_id)
        print("  ✓ Deleted work and all data")

        # Delete collection 500 if it only contained Kambaramayanam
        if delete_collection:
            cursor.execute("DELETE FROM collections WHERE collection_id = 500")
            print("  ✓ Deleted collection 500 (காப்பியங்கள் / Epics)")

        conn.commit()
        print("\n✓ Successfully deleted Kambaramayanam")
        cursor.close()
        conn.close()
        return True

    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        if 'conn' in locals():
            conn.rollback()
            conn.close()
        return False

def main():
    # Get database connection string
    db_connection = os.getenv('DATABASE_URL', "postgresql://postgres:postgres@localhost/tamil_literature")
    if len(sys.argv) > 1:
        db_connection = sys.argv[1]

    print(f"Database: {db_connection[:50]}...")

    if delete_kambaramayanam(db_connection):
        print("\n✓ Deletion complete")
        sys.exit(0)
    else:
        print("\n✗ Deletion failed or cancelled")
        sys.exit(1)

if __name__ == '__main__':
    main()
