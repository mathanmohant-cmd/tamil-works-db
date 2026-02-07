#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Delete all 4 Bharathiyar poetry works (பாரதியார் கவிதைகள்) and collection 328

Works deleted:
1. National and Social Reform Poetry (தேசிய மற்றும் சமூகச் சீர்திருத்தக் கவிதைகள்)
2. Devotional and Spiritual Poetry (பக்தி மற்றும் ஆன்மிகக் கவிதைகள்)
3. Epic and Narrative Poetry (காப்பியக் கவிதைகள்)
4. Modern Free Verse Poetry (நவீன வசனக் கவிதை)

All poetry by Subramania Bharathiyar (1882-1921 CE)

Collection ID: 328 (இருபதாம் நூற்றாண்டு தமிழ் இலக்கியம் - Modern Tamil Literature)

Deletion Order (respects foreign key constraints):
1. words (deepest level)
2. lines
3. verse_collections (before verses)
4. verses
5. section_collections (before sections)
6. sections
7. work_collections (before works)
8. works
9. collection (if empty after work deletion)

Usage:
    python delete_bharathiyar.py [database_url]

Examples:
    python delete_bharathiyar.py
    python delete_bharathiyar.py postgresql://postgres:postgres@localhost/tamil_literature
"""

import os
import sys
import psycopg2

COLLECTION_ID = 328


def get_connection_string():
    """Get database connection string"""
    if len(sys.argv) > 1:
        return sys.argv[1]

    db_url = os.getenv("DATABASE_URL")
    if db_url:
        return db_url

    # Default local connection
    return "postgresql://postgres:postgres@localhost/tamil_literature"


def delete_collection_works(cursor, collection_id: int):
    """
    Delete all works in a collection following referential integrity order

    Returns:
        tuple: (works_deleted, sections_deleted, verses_deleted, lines_deleted, words_deleted)
    """
    # Get all work IDs in the collection
    cursor.execute("""
        SELECT w.work_id, w.work_name_tamil
        FROM works w
        JOIN work_collections wc ON w.work_id = wc.work_id
        WHERE wc.collection_id = %s
        ORDER BY wc.position_in_collection
    """, [collection_id])

    works = cursor.fetchall()
    if not works:
        return (0, 0, 0, 0, 0)

    work_ids = [w[0] for w in works]
    work_names = [w[1] for w in works]

    print(f"\nDeleting {len(works)} works:")
    for name in work_names:
        print(f"  - {name}")

    # Delete words (deepest level)
    cursor.execute("""
        DELETE FROM words
        WHERE line_id IN (
            SELECT l.line_id FROM lines l
            JOIN verses v ON l.verse_id = v.verse_id
            WHERE v.work_id = ANY(%s)
        )
    """, [work_ids])
    words_deleted = cursor.rowcount

    # Delete lines
    cursor.execute("""
        DELETE FROM lines
        WHERE verse_id IN (
            SELECT verse_id FROM verses WHERE work_id = ANY(%s)
        )
    """, [work_ids])
    lines_deleted = cursor.rowcount

    # Delete verse collections
    cursor.execute("""
        DELETE FROM verse_collections
        WHERE verse_id IN (
            SELECT verse_id FROM verses WHERE work_id = ANY(%s)
        )
    """, [work_ids])

    # Delete verses
    cursor.execute("DELETE FROM verses WHERE work_id = ANY(%s)", [work_ids])
    verses_deleted = cursor.rowcount

    # Delete section collections
    cursor.execute("""
        DELETE FROM section_collections
        WHERE section_id IN (
            SELECT section_id FROM sections WHERE work_id = ANY(%s)
        )
    """, [work_ids])

    # Delete sections
    cursor.execute("DELETE FROM sections WHERE work_id = ANY(%s)", [work_ids])
    sections_deleted = cursor.rowcount

    # Delete work_collections
    cursor.execute("DELETE FROM work_collections WHERE work_id = ANY(%s)", [work_ids])

    # Delete works
    cursor.execute("DELETE FROM works WHERE work_id = ANY(%s)", [work_ids])
    works_deleted = cursor.rowcount

    return (works_deleted, sections_deleted, verses_deleted, lines_deleted, words_deleted)


def main():
    """Main execution"""
    # Set stdout to UTF-8 for Windows console (Tamil text support)
    if sys.platform == 'win32':
        import codecs
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, errors='replace')
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, errors='replace')

    print("=" * 70)
    print("Delete பாரதியார் கவிதைகள் (Bharathiyar Poetry)")
    print("Collection 328: இருபதாம் நூற்றாண்டு தமிழ் இலக்கியம் (Modern Tamil Literature)")
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
            print(f"  {work_name_ta}")
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

        # 4. Delete all works in collection
        works_del, sections_del, verses_del, lines_del, words_del = delete_collection_works(cursor, COLLECTION_ID)

        print(f"\nDeletion summary:")
        print(f"  Works: {works_del}")
        print(f"  Sections: {sections_del}")
        print(f"  Verses: {verses_del}")
        print(f"  Lines: {lines_del}")
        print(f"  Words: {words_del}")

        # 5. Delete collection (now empty)
        if works_del > 0:
            print(f"\nDeleting collection {COLLECTION_ID}...")
            cursor.execute("DELETE FROM collections WHERE collection_id = %s", (COLLECTION_ID,))
            print(f"  ✓ Deleted collection {COLLECTION_ID}")

        # 6. Commit transaction
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
