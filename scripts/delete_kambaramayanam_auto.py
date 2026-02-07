#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Auto-delete Kambaramayanam work (non-interactive)
"""

import os
import psycopg2

db_connection = os.getenv('DATABASE_URL', "postgresql://postgres:postgres@localhost/tamil_literature")

print("="*70)
print("  DELETE KAMBARAMAYANAM (கம்பராமாயணம்) - AUTO")
print("="*70)

try:
    conn = psycopg2.connect(db_connection)
    conn.autocommit = False
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
    else:
        work_id = work_row[0]
        print(f"\nDeleting work: {work_row[2]} (ID: {work_id})")

        # Delete in order
        print("  Deleting words...")
        cursor.execute("""
            DELETE FROM words
            WHERE line_id IN (
                SELECT l.line_id FROM lines l
                JOIN verses v ON l.verse_id = v.verse_id
                WHERE v.work_id = %s
            )
        """, (work_id,))

        print("  Deleting lines...")
        cursor.execute("""
            DELETE FROM lines
            WHERE verse_id IN (SELECT verse_id FROM verses WHERE work_id = %s)
        """, (work_id,))

        print("  Deleting verses...")
        cursor.execute("DELETE FROM verses WHERE work_id = %s", (work_id,))

        print("  Deleting sections...")
        cursor.execute("DELETE FROM sections WHERE work_id = %s", (work_id,))

        print("  Deleting work_collections...")
        cursor.execute("DELETE FROM work_collections WHERE work_id = %s", (work_id,))

        print("  Deleting work...")
        cursor.execute("DELETE FROM works WHERE work_id = %s", (work_id,))

        # Check if collection 500 has other works
        cursor.execute("SELECT COUNT(*) FROM work_collections WHERE collection_id = 500")
        works_in_collection = cursor.fetchone()[0]

        if works_in_collection == 0:
            print("  Deleting empty collection 500...")
            cursor.execute("DELETE FROM collections WHERE collection_id = 500")

        conn.commit()
        print("\n✓ Successfully deleted Kambaramayanam")
        cursor.close()
        conn.close()

except Exception as e:
    print(f"\n✗ Error: {e}")
    import traceback
    traceback.print_exc()
    if 'conn' in locals():
        conn.rollback()
        conn.close()
