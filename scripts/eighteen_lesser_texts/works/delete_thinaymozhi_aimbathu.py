#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Atomic delete for திணைமொழி ஐம்பது (Thinaymozhi Aimbathu)

Usage:
    python delete_thinaymozhi_aimbathu.py [database_url]
"""

import os
import sys
import psycopg2

WORK_NAME_ENGLISH = 'Thinaymozhi Aimbathu'
WORK_NAME_TAMIL = 'திணைமொழி ஐம்பது'


def delete_work(connection_string):
    """Delete work and all its data atomically"""
    print("\n" + "="*70)
    print(f"  DELETE {WORK_NAME_TAMIL} ({WORK_NAME_ENGLISH})")
    print("="*70)

    try:
        conn = psycopg2.connect(connection_string)
        conn.autocommit = False  # Use transaction
        cursor = conn.cursor()

        # Find work
        cursor.execute(
            "SELECT work_id FROM works WHERE work_name = %s",
            (WORK_NAME_ENGLISH,)
        )
        result = cursor.fetchone()

        if not result:
            print(f"\n✗ Work '{WORK_NAME_ENGLISH}' not found")
            cursor.close()
            conn.close()
            return False

        work_id = result[0]

        # Get deletion stats
        cursor.execute("""
            SELECT
                COUNT(DISTINCT s.section_id) as sections,
                COUNT(DISTINCT v.verse_id) as verses,
                COUNT(DISTINCT l.line_id) as lines,
                COUNT(DISTINCT w.word_id) as words
            FROM works wk
            LEFT JOIN sections s ON wk.work_id = s.work_id
            LEFT JOIN verses v ON wk.work_id = v.work_id
            LEFT JOIN lines l ON v.verse_id = l.verse_id
            LEFT JOIN words w ON l.line_id = w.line_id
            WHERE wk.work_id = %s
        """, (work_id,))
        stats = cursor.fetchone()

        print(f"\nThis will delete:")
        print(f"  - 1 work ({WORK_NAME_TAMIL})")
        print(f"  - {stats[0]:,} sections")
        print(f"  - {stats[1]:,} verses")
        print(f"  - {stats[2]:,} lines")
        print(f"  - {stats[3]:,} words")

        response = input("\nAre you sure? (yes/no): ").strip().lower()
        if response not in ['yes', 'y']:
            print("Deletion cancelled.")
            cursor.close()
            conn.close()
            return False

        print("\nDeleting work data...")

        # Delete in reverse dependency order
        cursor.execute("""
            DELETE FROM words
            WHERE line_id IN (
                SELECT l.line_id FROM lines l
                JOIN verses v ON l.verse_id = v.verse_id
                WHERE v.work_id = %s
            )
        """, (work_id,))
        print(f"  ✓ Deleted {cursor.rowcount:,} words")

        cursor.execute("""
            DELETE FROM lines
            WHERE verse_id IN (SELECT verse_id FROM verses WHERE work_id = %s)
        """, (work_id,))
        print(f"  ✓ Deleted {cursor.rowcount:,} lines")

        cursor.execute("DELETE FROM verses WHERE work_id = %s", (work_id,))
        print(f"  ✓ Deleted {cursor.rowcount:,} verses")

        cursor.execute("DELETE FROM sections WHERE work_id = %s", (work_id,))
        print(f"  ✓ Deleted {cursor.rowcount:,} sections")

        cursor.execute("DELETE FROM work_collections WHERE work_id = %s", (work_id,))
        print(f"  ✓ Unlinked from collections")

        cursor.execute("DELETE FROM works WHERE work_id = %s", (work_id,))
        print(f"  ✓ Deleted work entry")

        conn.commit()
        print(f"\n✓ Successfully deleted {WORK_NAME_TAMIL}")

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
    db_connection = os.getenv('DATABASE_URL',
                              "postgresql://postgres:postgres@localhost/tamil_literature")
    if len(sys.argv) > 1:
        db_connection = sys.argv[1]

    print(f"Database: {db_connection[:50]}...")

    if delete_work(db_connection):
        print("\n✓ Deletion complete")
        sys.exit(0)
    else:
        print("\n✗ Deletion failed or cancelled")
        sys.exit(1)


if __name__ == '__main__':
    main()
