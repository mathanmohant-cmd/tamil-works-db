#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Delete a specific work and all its related data from the database
Usage: python delete_work.py "Work Name"
"""

import os
import sys
import psycopg2

def get_connection_string():
    """Get database connection string"""
    if len(sys.argv) > 2:
        return sys.argv[2]

    db_url = os.getenv("DATABASE_URL")
    if db_url:
        return db_url

    # Default local connection
    return "postgresql://postgres:postgres@localhost/tamil_literature"

def delete_work(work_name: str, connection_string: str):
    """Delete a work and all its related data"""
    print(f"\nDeleting work: {work_name}")

    try:
        conn = psycopg2.connect(connection_string)
        conn.autocommit = True
        cursor = conn.cursor()

        # First, check if the work exists and get its ID
        cursor.execute("""
            SELECT work_id, work_name, work_name_tamil, author, author_tamil
            FROM works
            WHERE work_name = %s OR work_name_tamil = %s
        """, [work_name, work_name])

        result = cursor.fetchone()
        if not result:
            print(f"✗ Work '{work_name}' not found in database")
            return False

        work_id, work_name_en, work_name_ta, author_en, author_ta = result

        print(f"\nFound work:")
        print(f"  ID: {work_id}")
        print(f"  Name: {work_name_en} / {work_name_ta}")
        print(f"  Author: {author_en} / {author_ta}")

        # Get counts before deletion
        cursor.execute("SELECT COUNT(*) FROM sections WHERE work_id = %s", [work_id])
        section_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM verses WHERE work_id = %s", [work_id])
        verse_count = cursor.fetchone()[0]

        cursor.execute("""
            SELECT COUNT(*) FROM words w
            JOIN lines l ON w.line_id = l.line_id
            JOIN verses v ON l.verse_id = v.verse_id
            WHERE v.work_id = %s
        """, [work_id])
        word_count = cursor.fetchone()[0]

        print(f"\nData to be deleted:")
        print(f"  Sections: {section_count}")
        print(f"  Verses: {verse_count}")
        print(f"  Words: {word_count}")

        response = input("\nAre you sure you want to delete this work? (yes/no): ").strip().lower()
        if response not in ['yes', 'y']:
            print("Deletion cancelled.")
            return False

        # Delete in order of dependencies (CASCADE will handle it, but being explicit)
        print("\nDeleting data...")

        # Delete words (via lines -> verses -> work)
        print("  Deleting words...")
        cursor.execute("""
            DELETE FROM words
            WHERE line_id IN (
                SELECT l.line_id FROM lines l
                JOIN verses v ON l.verse_id = v.verse_id
                WHERE v.work_id = %s
            )
        """, [work_id])
        print(f"    ✓ Deleted {cursor.rowcount} words")

        # Delete lines
        print("  Deleting lines...")
        cursor.execute("""
            DELETE FROM lines
            WHERE verse_id IN (
                SELECT verse_id FROM verses WHERE work_id = %s
            )
        """, [work_id])
        print(f"    ✓ Deleted {cursor.rowcount} lines")

        # Delete verses
        print("  Deleting verses...")
        cursor.execute("DELETE FROM verses WHERE work_id = %s", [work_id])
        print(f"    ✓ Deleted {cursor.rowcount} verses")

        # Delete sections
        print("  Deleting sections...")
        cursor.execute("DELETE FROM sections WHERE work_id = %s", [work_id])
        print(f"    ✓ Deleted {cursor.rowcount} sections")

        # Delete from work_collections
        print("  Removing from collections...")
        cursor.execute("DELETE FROM work_collections WHERE work_id = %s", [work_id])
        print(f"    ✓ Removed from {cursor.rowcount} collections")

        # Delete the work itself
        print("  Deleting work entry...")
        cursor.execute("DELETE FROM works WHERE work_id = %s", [work_id])
        print(f"    ✓ Deleted work")

        cursor.close()
        conn.close()

        print(f"\n✓ Successfully deleted work: {work_name_en} / {work_name_ta}")
        return True

    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    if len(sys.argv) < 2:
        print("\nUsage: python delete_work.py \"Work Name\" [database_url]")
        print("\nExamples:")
        print('  python delete_work.py "Tolkappiyam"')
        print('  python delete_work.py "தொல்காப்பியம்"')
        print('  python delete_work.py "Thirukkural" "postgresql://..."')
        print("\nNote: You can use either English or Tamil name")
        sys.exit(1)

    work_name = sys.argv[1]
    connection_string = get_connection_string()

    print("\n" + "="*70)
    print("  DELETE WORK FROM DATABASE")
    print("="*70)

    if delete_work(work_name, connection_string):
        print("\n✓ Work deleted successfully")
        print("\nYou can now re-run the import script to re-import this work.")
    else:
        print("\n✗ Deletion failed")
        sys.exit(1)

if __name__ == '__main__':
    main()
