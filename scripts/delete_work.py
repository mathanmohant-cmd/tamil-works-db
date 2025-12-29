#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Delete works and all their related data from the database

Usage:
    python delete_work.py "Work Name"                    # Delete by name
    python delete_work.py --collection-id <id>           # Delete all works in collection AND the collection
    python delete_work.py --work-id <id>                 # Delete by work ID

Examples:
    python delete_work.py "Thirukkural"
    python delete_work.py --collection-id 3211           # Delete all Devaram works + collection
    python delete_work.py --collection-id 51             # Delete all 18 Sangam works + collection
    python delete_work.py --work-id 42
"""

import os
import sys
import psycopg2

def get_connection_string():
    """Get database connection string"""
    # Check if old-style args (positional): delete_work.py "Work Name" "db_url"
    # Only applies when first arg is NOT a flag
    if len(sys.argv) > 2 and not sys.argv[1].startswith('--') and not sys.argv[2].startswith('--'):
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

        # Get collection membership counts
        cursor.execute("SELECT COUNT(*) FROM work_collections WHERE work_id = %s", [work_id])
        work_coll_count = cursor.fetchone()[0]

        cursor.execute("""
            SELECT COUNT(*) FROM section_collections sc
            JOIN sections s ON sc.section_id = s.section_id
            WHERE s.work_id = %s
        """, [work_id])
        section_coll_count = cursor.fetchone()[0]

        cursor.execute("""
            SELECT COUNT(*) FROM verse_collections vc
            JOIN verses v ON vc.verse_id = v.verse_id
            WHERE v.work_id = %s
        """, [work_id])
        verse_coll_count = cursor.fetchone()[0]

        print(f"\nData to be deleted:")
        print(f"  Sections: {section_count}")
        print(f"  Verses: {verse_count}")
        print(f"  Words: {word_count}")
        print(f"  Collection memberships:")
        print(f"    Work-level: {work_coll_count}")
        print(f"    Section-level: {section_coll_count}")
        print(f"    Verse-level: {verse_coll_count}")

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

        # Delete from verse collections (before deleting verses)
        print("  Removing verses from collections...")
        cursor.execute("""
            DELETE FROM verse_collections
            WHERE verse_id IN (
                SELECT verse_id FROM verses WHERE work_id = %s
            )
        """, [work_id])
        verse_coll_deleted = cursor.rowcount
        if verse_coll_deleted > 0:
            print(f"    ✓ Removed {verse_coll_deleted} verse-level collection memberships")

        # Delete verses
        print("  Deleting verses...")
        cursor.execute("DELETE FROM verses WHERE work_id = %s", [work_id])
        print(f"    ✓ Deleted {cursor.rowcount} verses")

        # Delete from section collections (before deleting sections)
        print("  Removing sections from collections...")
        cursor.execute("""
            DELETE FROM section_collections
            WHERE section_id IN (
                SELECT section_id FROM sections WHERE work_id = %s
            )
        """, [work_id])
        section_coll_deleted = cursor.rowcount
        if section_coll_deleted > 0:
            print(f"    ✓ Removed {section_coll_deleted} section-level collection memberships")

        # Delete sections
        print("  Deleting sections...")
        cursor.execute("DELETE FROM sections WHERE work_id = %s", [work_id])
        print(f"    ✓ Deleted {cursor.rowcount} sections")

        # Delete from work_collections
        print("  Removing work from collections...")
        cursor.execute("DELETE FROM work_collections WHERE work_id = %s", [work_id])
        work_coll_deleted = cursor.rowcount
        if work_coll_deleted > 0:
            print(f"    ✓ Removed from {work_coll_deleted} work-level collections")

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

def get_works_in_collection(cursor, collection_id):
    """Get all work IDs in a collection (checks both primary_collection_id and work_collections table)"""
    # Check work_collections table first (Sangam pattern)
    cursor.execute("""
        SELECT DISTINCT w.work_id, w.work_name, w.work_name_tamil
        FROM work_collections wc
        JOIN works w ON wc.work_id = w.work_id
        WHERE wc.collection_id = %s
        ORDER BY w.work_id
    """, [collection_id])

    results = cursor.fetchall()

    # If no results, check primary_collection_id (Devaram pattern)
    if not results:
        cursor.execute("""
            SELECT work_id, work_name, work_name_tamil
            FROM works
            WHERE primary_collection_id = %s
            ORDER BY work_id
        """, [collection_id])
        results = cursor.fetchall()

    return results

def delete_collection_and_works(collection_id, connection_string):
    """Delete a collection and all its works"""
    print(f"\nDeleting collection: {collection_id}")

    try:
        conn = psycopg2.connect(connection_string)
        conn.autocommit = False  # Use transaction
        cursor = conn.cursor()

        # Get collection info
        cursor.execute("""
            SELECT collection_id, collection_name, collection_name_tamil, description
            FROM collections
            WHERE collection_id = %s
        """, [collection_id])

        coll_result = cursor.fetchone()
        if not coll_result:
            print(f"✗ Collection {collection_id} not found in database")
            return False

        coll_id, coll_name, coll_name_tamil, coll_desc = coll_result

        print(f"\nFound collection:")
        print(f"  ID: {coll_id}")
        print(f"  Name: {coll_name} / {coll_name_tamil}")
        print(f"  Description: {coll_desc}")

        # Get all works in collection
        works = get_works_in_collection(cursor, collection_id)

        if not works:
            print(f"\n⚠️  No works found in collection {collection_id}")
            response = input("Delete empty collection? (yes/no): ").strip().lower()
            if response not in ['yes', 'y']:
                print("Deletion cancelled.")
                return False
        else:
            print(f"\nWorks in collection ({len(works)}):")
            for work_id, work_name, work_name_tamil in works:
                print(f"  - [{work_id}] {work_name_tamil or work_name}")

            print(f"\n⚠️  WARNING: This will delete:")
            print(f"  - {len(works)} work(s) and all their data (sections, verses, lines, words)")
            print(f"  - The collection '{coll_name_tamil}'")

            response = input("\nAre you sure? (yes/no): ").strip().lower()
            if response not in ['yes', 'y']:
                print("Deletion cancelled.")
                return False

            # Delete all works
            print(f"\nDeleting {len(works)} work(s)...")
            for work_id, work_name, work_name_tamil in works:
                if not delete_work_by_id(cursor, work_id):
                    print(f"✗ Failed to delete work {work_id}")
                    conn.rollback()
                    return False

        # Delete the collection itself
        print(f"\nDeleting collection {coll_id}...")
        cursor.execute("DELETE FROM collections WHERE collection_id = %s", [collection_id])
        print(f"  ✓ Deleted collection")

        conn.commit()
        cursor.close()
        conn.close()

        print(f"\n✓ Successfully deleted collection {coll_id} and all {len(works)} work(s)")
        return True

    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        if conn:
            conn.rollback()
        return False

def delete_work_by_id(cursor, work_id):
    """Delete a work by ID (used within a transaction)"""
    # Delete words
    cursor.execute("""
        DELETE FROM words
        WHERE line_id IN (
            SELECT l.line_id FROM lines l
            JOIN verses v ON l.verse_id = v.verse_id
            WHERE v.work_id = %s
        )
    """, [work_id])

    # Delete lines
    cursor.execute("""
        DELETE FROM lines
        WHERE verse_id IN (SELECT verse_id FROM verses WHERE work_id = %s)
    """, [work_id])

    # Delete verse collections
    cursor.execute("""
        DELETE FROM verse_collections
        WHERE verse_id IN (SELECT verse_id FROM verses WHERE work_id = %s)
    """, [work_id])

    # Delete verses
    cursor.execute("DELETE FROM verses WHERE work_id = %s", [work_id])

    # Delete section collections
    cursor.execute("""
        DELETE FROM section_collections
        WHERE section_id IN (SELECT section_id FROM sections WHERE work_id = %s)
    """, [work_id])

    # Delete sections
    cursor.execute("DELETE FROM sections WHERE work_id = %s", [work_id])

    # Delete work collections
    cursor.execute("DELETE FROM work_collections WHERE work_id = %s", [work_id])

    # Delete work
    cursor.execute("DELETE FROM works WHERE work_id = %s", [work_id])

    return True

def main():
    # Parse arguments
    if len(sys.argv) < 2:
        print("\nUsage:")
        print('  python delete_work.py "Work Name" [database_url]')
        print('  python delete_work.py --collection-id <id>')
        print('  python delete_work.py --work-id <id>')
        print("\nExamples:")
        print('  python delete_work.py "Tolkappiyam"')
        print('  python delete_work.py --collection-id 3211   # Delete all Devaram works')
        print('  python delete_work.py --collection-id 51     # Delete all 18 Sangam works')
        print('  python delete_work.py --work-id 42')
        sys.exit(1)

    connection_string = get_connection_string()

    print("\n" + "="*70)
    print("  DELETE WORK/COLLECTION FROM DATABASE")
    print("="*70)

    # Handle --collection-id
    if sys.argv[1] == '--collection-id':
        if len(sys.argv) < 3:
            print("✗ Error: --collection-id requires a collection ID")
            sys.exit(1)

        collection_id = int(sys.argv[2])
        if delete_collection_and_works(collection_id, connection_string):
            print("\n✓ Collection and works deleted successfully")
        else:
            print("\n✗ Deletion failed")
            sys.exit(1)

    # Handle --work-id
    elif sys.argv[1] == '--work-id':
        if len(sys.argv) < 3:
            print("✗ Error: --work-id requires a work ID")
            sys.exit(1)

        work_id = int(sys.argv[2])
        conn = psycopg2.connect(connection_string)
        conn.autocommit = False
        cursor = conn.cursor()

        try:
            # Get work info
            cursor.execute("""
                SELECT work_name, work_name_tamil FROM works WHERE work_id = %s
            """, [work_id])
            result = cursor.fetchone()
            if not result:
                print(f"✗ Work ID {work_id} not found")
                sys.exit(1)

            work_name, work_name_tamil = result
            print(f"\nDeleting work: [{work_id}] {work_name_tamil or work_name}")

            response = input("Are you sure? (yes/no): ").strip().lower()
            if response not in ['yes', 'y']:
                print("Deletion cancelled.")
                sys.exit(0)

            if delete_work_by_id(cursor, work_id):
                conn.commit()
                print(f"\n✓ Work {work_id} deleted successfully")
            else:
                conn.rollback()
                print(f"\n✗ Deletion failed")
                sys.exit(1)
        finally:
            cursor.close()
            conn.close()

    # Handle work name (original behavior)
    else:
        work_name = sys.argv[1]
        if delete_work(work_name, connection_string):
            print("\n✓ Work deleted successfully")
            print("\nYou can now re-run the import script to re-import this work.")
        else:
            print("\n✗ Deletion failed")
            sys.exit(1)

if __name__ == '__main__':
    main()
