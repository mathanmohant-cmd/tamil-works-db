#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Delete all 36 Siddhar mystical poetry works (சித்தர் பாடல்கள்) and collection 327

Works deleted:
1-36. All Siddhar Padalgal (Songs of the Siddhars)
Including works by Agathiyar, Sivavaakiyar, Pattinatthu Siddhar, and 33 other Siddhars

Usage:
    python delete_siddhar_padalgal.py [database_url]

Examples:
    python delete_siddhar_padalgal.py
    python delete_siddhar_padalgal.py postgresql://postgres:postgres@localhost/tamil_literature
"""

import os
import sys
import io
import psycopg2

# Work names for deletion (English names from WORK_METADATA)
WORK_NAMES = [
    'Agathiyar Gnanam',
    'Agappey Siddhar Paadal',
    'Azhugani Siddhar Paadal',
    'Adhinathar (Vedantha Siddhar) Paadal',
    'Idaikkaadu Siddhar Paadal',
    'Ramadhevar - Poosaavidhi',
    'Uroma Rishi Gnanam',
    'Ekanathar (Brahmanantha Siddhar) Paadal',
    'Kanjamalai Siddhar Paadal',
    'Kaduveli Siddhar Paadal',
    'Kadaendra Nathar (Vilaiyaadu Siddhar) Paadal',
    'Karuvurar - Poojaavidhi',
    'Kalluli Siddhar Paadal',
    'Kaagapusundar',
    'Kaayakka Kappal',
    'Kaarai Siddhar',
    'Kudhambai Siddhar',
    'Kongana Siddhar',
    'Kailayakka Kampali Sattai Muni Nayanar',
    'Sangili Siddhar Paadal',
    'Sattai Muni Gnanam',
    'Sathiya Nathar (Gnana Siddhar) Paadal',
    'Sadhotha Nathar (Yoga Siddhar) Paadal',
    'Sivavaakiyar',
    'Sooriyaanandhar Soothiram',
    'Thadangan Siddhar Paadalkal',
    'Thirikona Siddhar Paadal',
    'Thirumoolar Nayanar',
    'Thiruvalluvar Gnanam',
    'Pattinatthu Siddhar Gnanam',
    'Pathiragiriyaarin Meygnaanap Pulambal',
    'Paambaatti Siddhar',
    'Punnaakku Siddhar Paadal',
    'Machaendhira Nathar (Nondi Siddhar) Paadal',
    'Vagulinathar (Mauna Siddhar) Paadal',
    'Valmiki'
]

COLLECTION_ID = 327


def get_connection_string():
    """Get database connection string"""
    if len(sys.argv) > 1:
        return sys.argv[1]

    db_url = os.getenv("DATABASE_URL")
    if db_url:
        return db_url

    # Default local connection
    return "postgresql://postgres:postgres@localhost/tamil_literature"


def delete_single_work(cursor, work_name: str):
    """
    Delete a single work following referential integrity order

    Deletion order:
    1. Delete words (deepest level)
    2. Delete lines
    3. Delete verse_collections (before verses)
    4. Delete verses
    5. Delete section_collections (before sections)
    6. Delete sections
    7. Delete work_collections (before work)
    8. Delete work
    """
    # Get work ID
    cursor.execute("""
        SELECT work_id, work_name, work_name_tamil
        FROM works
        WHERE work_name = %s OR work_name_tamil = %s
    """, [work_name, work_name])

    result = cursor.fetchone()
    if not result:
        print(f"  ✗ Work '{work_name}' not found")
        return False

    work_id, work_name_en, work_name_ta = result

    # Delete words
    cursor.execute("""
        DELETE FROM words
        WHERE line_id IN (
            SELECT l.line_id FROM lines l
            JOIN verses v ON l.verse_id = v.verse_id
            WHERE v.work_id = %s
        )
    """, [work_id])
    words_deleted = cursor.rowcount

    # Delete lines
    cursor.execute("""
        DELETE FROM lines
        WHERE verse_id IN (
            SELECT verse_id FROM verses WHERE work_id = %s
        )
    """, [work_id])
    lines_deleted = cursor.rowcount

    # Delete verse collections
    cursor.execute("""
        DELETE FROM verse_collections
        WHERE verse_id IN (
            SELECT verse_id FROM verses WHERE work_id = %s
        )
    """, [work_id])

    # Delete verses
    cursor.execute("DELETE FROM verses WHERE work_id = %s", [work_id])
    verses_deleted = cursor.rowcount

    # Delete section collections
    cursor.execute("""
        DELETE FROM section_collections
        WHERE section_id IN (
            SELECT section_id FROM sections WHERE work_id = %s
        )
    """, [work_id])

    # Delete sections
    cursor.execute("DELETE FROM sections WHERE work_id = %s", [work_id])
    sections_deleted = cursor.rowcount

    # Delete work_collections
    cursor.execute("DELETE FROM work_collections WHERE work_id = %s", [work_id])

    # Delete work
    cursor.execute("DELETE FROM works WHERE work_id = %s", [work_id])

    print(f"  ✓ Deleted {work_name_en}: {sections_deleted} sections, {verses_deleted} verses, "
          f"{lines_deleted} lines, {words_deleted} words")
    return True


def main():
    """Main execution"""
    # Set stdout to UTF-8 for Windows console (Tamil text support)
    if sys.platform == 'win32':
        import codecs
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, errors='replace')
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, errors='replace')

    print("=" * 70)
    print("Delete சித்தர் பாடல்கள் (Siddhar Padalgal)")
    print("Collection 327: Thirty-Six Mystical Poetry Works by Tamil Siddhars")
    print("=" * 70)

    db_url = get_connection_string()

    try:
        conn = psycopg2.connect(db_url)
        conn.autocommit = False  # Use transaction
        cursor = conn.cursor()

        # 1. Check if collection exists
        cursor.execute("SELECT collection_id, collection_name_tamil FROM collections WHERE collection_id = %s",
                      (COLLECTION_ID,))
        collection = cursor.fetchone()

        if not collection:
            print(f"\n✗ Collection {COLLECTION_ID} not found")
            sys.exit(0)

        print(f"\nFound collection: {collection[1]} (ID: {collection[0]})")

        # 2. Get all works in collection and show summary
        cursor.execute("""
            SELECT w.work_id, w.work_name, w.work_name_tamil,
                   (SELECT COUNT(*) FROM sections WHERE work_id = w.work_id) as sections,
                   (SELECT COUNT(*) FROM verses WHERE work_id = w.work_id) as verses,
                   (SELECT COUNT(*) FROM words wd
                    JOIN lines l ON wd.line_id = l.line_id
                    JOIN verses v ON l.verse_id = v.verse_id
                    WHERE v.work_id = w.work_id) as words
            FROM works w
            JOIN work_collections wc ON w.work_id = wc.work_id
            WHERE wc.collection_id = %s
            ORDER BY wc.position_in_collection
        """, (COLLECTION_ID,))

        works = cursor.fetchall()

        if not works:
            print(f"\n✗ No works found in collection {COLLECTION_ID}")
            cursor.execute("DELETE FROM collections WHERE collection_id = %s", (COLLECTION_ID,))
            conn.commit()
            print(f"  ✓ Deleted empty collection {COLLECTION_ID}")
            sys.exit(0)

        print(f"\nWorks to be deleted ({len(works)}):")
        total_sections = 0
        total_verses = 0
        total_words = 0

        for work_id, work_name, work_name_ta, sections, verses, words in works:
            print(f"  {work_name}")
            print(f"    Sections: {sections}, Verses: {verses}, Words: {words}")
            total_sections += sections
            total_verses += verses
            total_words += words

        print(f"\nTotal data to be deleted:")
        print(f"  Works: {len(works)}")
        print(f"  Sections: {total_sections}")
        print(f"  Verses: {total_verses}")
        print(f"  Words: {total_words}")

        # 3. Ask for confirmation
        response = input(f"\nDelete all {len(works)} works and collection {COLLECTION_ID}? (yes/no): ").strip().lower()
        if response not in ['yes', 'y']:
            print("Deletion cancelled.")
            sys.exit(0)

        # 4. Delete each work
        print("\nDeleting works...")
        for work_name in WORK_NAMES:
            delete_single_work(cursor, work_name)

        # 5. Check if collection has remaining works
        cursor.execute("""
            SELECT COUNT(*) FROM work_collections
            WHERE collection_id = %s
        """, (COLLECTION_ID,))
        remaining = cursor.fetchone()[0]

        # 6. Delete collection if empty
        if remaining == 0:
            print(f"\nDeleting collection {COLLECTION_ID}...")
            cursor.execute("DELETE FROM collections WHERE collection_id = %s",
                          (COLLECTION_ID,))
            print(f"  ✓ Deleted collection {COLLECTION_ID}")
        else:
            print(f"\n⚠ Collection {COLLECTION_ID} has {remaining} remaining works, keeping collection.")

        # 7. Commit transaction
        conn.commit()
        print("\n✓ Deletion complete!")

        cursor.close()
        conn.close()

    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        if conn:
            conn.rollback()
        sys.exit(1)


if __name__ == '__main__':
    main()
