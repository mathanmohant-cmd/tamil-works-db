#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Delete Thiruvarutpa - Balakrishnapillai Edition

This script deletes:
- Thiruvarutpa - Balakrishnapillai Edition (திருவருட்பா - பாலகிருஷ்ணபிள்ளை பதிப்பு)

Usage:
    python delete_thiruvarutpa_balakrishnapillai.py [database_url]
"""

import os
import sys
import psycopg2

def delete_thiruvarutpa_balakrishnapillai(connection_string):
    """Delete Thiruvarutpa Balakrishnapillai Edition"""
    print("\n" + "="*70)
    print("  DELETE THIRUVARUTPA - BALAKRISHNAPILLAI EDITION")
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
            WHERE work_name = 'Thiruvarutpa - Balakrishnapillai Edition'
        """)
        works = cursor.fetchall()

        if not works:
            print("\n✗ Thiruvarutpa Balakrishnapillai Edition not found")
            return False

        work_id, work_name, work_name_tamil = works[0]
        print(f"\nFound: {work_name_tamil} ({work_name}) - ID: {work_id}")

        print("\nThis will delete:")
        print(f"  - 1 work with all data: sections, verses, lines, words")

        response = input("\nAre you sure? (yes/no): ").strip().lower()
        if response not in ['yes', 'y']:
            print("Deletion cancelled.")
            return False

        print("\nDeleting Thiruvarutpa works...")
        for work_id, work_name, work_name_tamil in works:
            print(f"  Deleting work {work_id}: {work_name_tamil}...")
            delete_work_by_id(cursor, work_id)

        conn.commit()
        print("\n✓ Successfully deleted Thiruvarutpa works")
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

    if delete_thiruvarutpa_balakrishnapillai(db_connection):
        print("\n✓ Deletion complete")
        sys.exit(0)
    else:
        print("\n✗ Deletion failed")
        sys.exit(1)

if __name__ == '__main__':
    main()
