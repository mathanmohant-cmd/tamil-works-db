#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Delete all Five Great Epics (ஐம்பெருங்காப்பியங்கள்) and collection 13

Works deleted (ஐம்பெருங்காப்பியங்கள் - 5 epics):
1. சிலப்பதிகாரம் (Silapathikaram) - ~5,270 verses
   3 Kandams: வஞ்சிக் காண்டம், மதுரைக் காண்டம், வஞ்சிக் காண்டம்
2. மணிமேகலை (Manimegalai) - 4,461 lines
   1 Pathigam + 30 Kathais
3. சீவக சிந்தாமணி (Seevaka Sinthamani) - 3,146 verses
   14 Ilampagams - Jain epic
4. வளையாபதி (Valayapathi) - 72 verses
   Fragmentary epic - only fragments survive
5. குண்டலகேசி (Kundalakesi) - 19 verses
   Fragmentary Buddhist epic - only fragments survive

Collection: 13 (Five Great Epics)

Usage:
    python delete_five_great_epics.py [database_url]

Examples:
    python delete_five_great_epics.py
    python delete_five_great_epics.py postgresql://postgres:postgres@localhost/tamil_literature
"""

import os
import sys
import psycopg2

# 5 epic names (English)
FIVE_GREAT_EPICS = [
    'Silapathikaram',
    'Manimegalai',
    'Seevaka Sinthamani',
    'Valayapathi',
    'Kundalakesi'
]

# 5 epic names (Tamil)
FIVE_GREAT_EPICS_TAMIL = [
    'சிலப்பதிகாரம்',
    'மணிமேகலை',
    'சீவக சிந்தாமணி',
    'வளையாபதி',
    'குண்டலகேசி'
]

COLLECTION_ID = 13


def delete_work_by_id(cursor, work_id):
    """Delete a single work and all its data"""
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


def delete_five_great_epics(connection_string):
    """Delete all 5 Five Great Epics and collection 13"""
    print("\n" + "="*70)
    print("  DELETE FIVE GREAT EPICS (ஐம்பெருங்காப்பியங்கள்)")
    print("="*70)

    try:
        conn = psycopg2.connect(connection_string)
        conn.autocommit = False  # Use transaction
        cursor = conn.cursor()

        # Find all works in collection 13
        print("\nSearching for Five Great Epics...")
        cursor.execute("""
            SELECT w.work_id, w.work_name, w.work_name_tamil
            FROM works w
            JOIN work_collections wc ON w.work_id = wc.work_id
            WHERE wc.collection_id = %s
            ORDER BY wc.position_in_collection
        """, (COLLECTION_ID,))
        found_works = cursor.fetchall()

        if not found_works:
            print("\n✗ No Five Great Epics found in collection 13")
            cursor.close()
            conn.close()
            return False

        print(f"\nFound {len(found_works)} epic(s):")
        for work_id, work_name, work_name_tamil in found_works:
            print(f"  - {work_name_tamil} ({work_name}) - ID: {work_id}")

        # Get total stats
        cursor.execute("""
            SELECT
                COUNT(DISTINCT s.section_id) as sections,
                COUNT(DISTINCT v.verse_id) as verses,
                COUNT(DISTINCT l.line_id) as lines,
                COUNT(DISTINCT w.word_id) as words
            FROM works wk
            JOIN work_collections wc ON wk.work_id = wc.work_id
            LEFT JOIN sections s ON wk.work_id = s.work_id
            LEFT JOIN verses v ON wk.work_id = v.work_id
            LEFT JOIN lines l ON v.verse_id = l.verse_id
            LEFT JOIN words w ON l.line_id = w.line_id
            WHERE wc.collection_id = %s
        """, (COLLECTION_ID,))
        stats = cursor.fetchone()
        section_count, verse_count, line_count, word_count = stats

        print(f"\nThis will delete:")
        print(f"  - {len(found_works)} epic(s)")
        print(f"  - {section_count:,} sections")
        print(f"  - {verse_count:,} verses")
        print(f"  - {line_count:,} lines")
        print(f"  - {word_count:,} words")
        print(f"  - Collection 13 (ஐம்பெருங்காப்பியங்கள்)")

        response = input("\nAre you sure? (yes/no): ").strip().lower()
        if response not in ['yes', 'y']:
            print("Deletion cancelled.")
            cursor.close()
            conn.close()
            return False

        print("\nDeleting Five Great Epics...")
        for i, (work_id, work_name, work_name_tamil) in enumerate(found_works, 1):
            print(f"  [{i}/{len(found_works)}] Deleting {work_name_tamil}...")
            delete_work_by_id(cursor, work_id)

        print("  ✓ Deleted all epics and data")

        # Delete collection 13
        cursor.execute("DELETE FROM collections WHERE collection_id = %s", (COLLECTION_ID,))
        print("  ✓ Deleted collection 13 (ஐம்பெருங்காப்பியங்கள்)")

        conn.commit()
        print(f"\n✓ Successfully deleted {len(found_works)} Five Great Epic(s)")
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

    if delete_five_great_epics(db_connection):
        print("\n✓ Deletion complete")
        sys.exit(0)
    else:
        print("\n✗ Deletion failed or cancelled")
        sys.exit(1)


if __name__ == '__main__':
    main()
