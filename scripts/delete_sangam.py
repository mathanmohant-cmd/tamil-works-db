#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Delete all 18 Sangam Literature works (சங்க இலக்கியம்) and collection 51

Works deleted:
1. நற்றிணை (Natrrinai)
2. குறுந்தொகை (Kurunthokai)
3. ஐங்குறுநூறு (Ainkurunuru)
4. பதிற்றுப்பத்து (Pathitrupathu)
5. பரிபாடல் (Paripaadal)
6. கலித்தொகை (Kalithokai)
7. அகநானூறு (Aganaanuru)
8. புறநானூறு (Puranaanuru)
9. திருமுருகாற்றுப்படை (Thirumurugaatruppadai)
10. பொருநராற்றுப்படை (Porunaraatruppadai)
11. சிறுபாணாற்றுப்படை (Sirupanaatruppadai)
12. பெரும்பாணாற்றுப்படை (Perumpanaatruppadai)
13. முல்லைப்பாட்டு (Mullaippaattu)
14. மதுரைக்காஞ்சி (Madurai kanchi)
15. நெடுநல்வாடை (Nedunalvaadai)
16. குறிஞ்சிப்பாட்டு (Kurinchippaattu)
17. பட்டினப்பாலை (Pattinappaalai)
18. மலைபடுகடாம் (Malaipadukataam)

Collection: 51 (பதினெண்மேல்கணக்கு - Eighteen Major Works)

Usage:
    python delete_sangam.py [database_url] [--yes]

Options:
    --yes, -y    Skip confirmation prompt

Examples:
    python delete_sangam.py
    python delete_sangam.py --yes
    python delete_sangam.py postgresql://postgres:postgres@localhost/tamil_literature --yes
"""

import os
import sys
import psycopg2

# 18 Sangam work names (Tamil)
SANGAM_WORKS_TAMIL = [
    'நற்றிணை',
    'குறுந்தொகை',
    'ஐங்குறுநூறு',
    'பதிற்றுப்பத்து',
    'பரிபாடல்',
    'கலித்தொகை',
    'அகநானூறு',
    'புறநானூறு',
    'திருமுருகாற்றுப்படை',
    'பொருநராற்றுப்படை',
    'சிறுபாணாற்றுப்படை',
    'பெரும்பாணாற்றுப்படை',
    'முல்லைப்பாட்டு',
    'மதுரைக்காஞ்சி',
    'நெடுநல்வாடை',
    'குறிஞ்சிப்பாட்டு',
    'பட்டினப்பாலை',
    'மலைபடுகடாம்'
]

COLLECTION_ID = 51  # பதினெண்மேல்கணக்கு (Eighteen Major Works)


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


def delete_sangam(connection_string, skip_confirmation=False):
    """Delete all 18 Sangam works and collection 51"""
    print("\n" + "="*70)
    print("  DELETE SANGAM LITERATURE (18 WORKS)")
    print("="*70)

    try:
        conn = psycopg2.connect(connection_string)
        conn.autocommit = False  # Use transaction
        cursor = conn.cursor()

        # Find all Sangam works by Tamil names
        print("\nSearching for Sangam works by name...")
        placeholders = ','.join(['%s'] * len(SANGAM_WORKS_TAMIL))
        cursor.execute(f"""
            SELECT work_id, work_name, work_name_tamil
            FROM works
            WHERE work_name_tamil IN ({placeholders})
            ORDER BY work_id
        """, SANGAM_WORKS_TAMIL)
        found_works = cursor.fetchall()

        if not found_works:
            print("\n✗ No Sangam works found")
            print("Searched for:", ', '.join(SANGAM_WORKS_TAMIL[:5]), "...")
            cursor.close()
            conn.close()
            return False

        print(f"\nFound {len(found_works)} Sangam works:")
        for work_id, work_name, work_name_tamil in found_works:
            print(f"  - {work_name_tamil} ({work_name}) - ID: {work_id}")

        # Get total stats using actual found work IDs
        work_ids = [work[0] for work in found_works]
        placeholders = ','.join(['%s'] * len(work_ids))
        cursor.execute(f"""
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
            WHERE wk.work_id IN ({placeholders})
        """, work_ids)
        stats = cursor.fetchone()
        section_count, verse_count, line_count, word_count = stats

        print(f"\nThis will delete:")
        print(f"  - {len(found_works)} Sangam works")
        print(f"  - {section_count:,} sections")
        print(f"  - {verse_count:,} verses")
        print(f"  - {line_count:,} lines")
        print(f"  - {word_count:,} words")

        # Check if collection 51 exists
        cursor.execute("SELECT COUNT(*) FROM collections WHERE collection_id = %s", (COLLECTION_ID,))
        has_collection = cursor.fetchone()[0] > 0
        if has_collection:
            print(f"  - Collection 51 (பதினெண்மேல்கணக்கு)")

        if not skip_confirmation:
            response = input("\nAre you sure? (yes/no): ").strip().lower()
            if response not in ['yes', 'y']:
                print("Deletion cancelled.")
                cursor.close()
                conn.close()
                return False
        else:
            print("\n--yes flag provided, skipping confirmation...")

        print("\nDeleting Sangam works...")
        for i, (work_id, work_name, work_name_tamil) in enumerate(found_works, 1):
            print(f"  [{i}/{len(found_works)}] Deleting {work_name_tamil}...")
            delete_work_by_id(cursor, work_id)

        print("  ✓ Deleted all works and data")

        # Delete collection 51 if it exists
        if has_collection:
            cursor.execute("DELETE FROM collections WHERE collection_id = %s", (COLLECTION_ID,))
            print("  ✓ Deleted collection 51 (பதினெண்மேல்கணக்கு)")

        conn.commit()
        print("\n✓ Successfully deleted all 18 Sangam works")
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
    # Parse arguments
    skip_confirmation = '--yes' in sys.argv or '-y' in sys.argv

    # Get database connection string
    db_connection = os.getenv('DATABASE_URL', "postgresql://postgres:postgres@localhost/tamil_literature")
    for arg in sys.argv[1:]:
        if arg not in ['--yes', '-y']:
            db_connection = arg
            break

    print(f"Database: {db_connection[:50]}...")

    if delete_sangam(db_connection, skip_confirmation):
        print("\n✓ Deletion complete")
        sys.exit(0)
    else:
        print("\n✗ Deletion failed or cancelled")
        sys.exit(1)


if __name__ == '__main__':
    main()
