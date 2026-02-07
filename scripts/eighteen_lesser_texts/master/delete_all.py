#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Master Orchestrator: Delete all Eighteen Lesser Texts + collection
Uses hybrid search to find both linked and orphaned works.

Usage:
    python delete_all.py [database_url]
"""

import os
import sys
from pathlib import Path
import psycopg2
import subprocess


# Collection metadata
COLLECTION_ID = 201
COLLECTION_NAME_ENGLISH = 'Eighteen Lesser Texts'
COLLECTION_NAME_TAMIL = 'பதினெண்கீழ்க்கணக்கு'

# All 18 work names (English) for orphan detection
EIGHTEEN_LESSER_TEXTS = [
    'Naladiyar',
    'Nanmanikkadigai',
    'Inna Narpathu',
    'Iniyavai Narpathu',
    'Kar Narpathu',
    'Kalavazhi Narpathu',
    'Ainthinai Aimbathu',
    'Ainthinai Ezhubathu',
    'Thinaymozhi Aimbathu',
    'Thinaimalai Noorraimpathu',
    'Thirigadugam',
    'Asarakkovai',
    'Pazhamozhi Nanuru',
    'Sirupanchamoolam',
    'Muthumozhikkanchi',
    'Elathi',
    'Kainnilai',
    'Thirukkural'
]


def find_works_hybrid_search(connection_string):
    """Find all Eighteen Lesser Texts using hybrid search

    Hybrid Search Strategy:
    1. Search by collection JOIN (finds properly linked works)
    2. Search by work name list (finds orphaned works)
    3. Merge results and identify orphans

    Returns:
        List of (work_id, work_name, work_name_tamil) tuples
    """
    conn = psycopg2.connect(connection_string)
    cursor = conn.cursor()

    print("\nSearching for Eighteen Lesser Texts...")

    # STEP 1: Search by collection JOIN (properly linked works)
    cursor.execute("""
        SELECT w.work_id, w.work_name, w.work_name_tamil
        FROM works w
        JOIN work_collections wc ON w.work_id = wc.work_id
        WHERE wc.collection_id = %s
        ORDER BY wc.position_in_collection
    """, (COLLECTION_ID,))
    found_by_collection = {row[0]: row for row in cursor.fetchall()}

    # STEP 2: Search by work name list (finds orphans)
    cursor.execute("""
        SELECT work_id, work_name, work_name_tamil
        FROM works
        WHERE work_name = ANY(%s)
    """, (EIGHTEEN_LESSER_TEXTS,))
    found_by_name = cursor.fetchall()

    # STEP 3: Identify orphans and merge results
    orphan_count = 0
    all_works_to_delete = {}

    for work_id, work_name, work_name_tamil in found_by_name:
        if work_id not in found_by_collection:
            orphan_count += 1
        all_works_to_delete[work_id] = (work_id, work_name, work_name_tamil)

    # Merge both result sets
    all_works_to_delete.update(found_by_collection)
    found_works = list(all_works_to_delete.values())

    # Report findings
    if not found_works:
        print("✗ No Eighteen Lesser Texts found")
        cursor.close()
        conn.close()
        return []

    print(f"\nFound {len(found_works)} work(s):")
    for work_id, work_name, work_name_tamil in found_works:
        if work_id not in found_by_collection:
            print(f"  - {work_name_tamil} ({work_name}) - ID: {work_id} [ORPHAN]")
        else:
            print(f"  - {work_name_tamil} ({work_name}) - ID: {work_id}")

    if orphan_count > 0:
        print(f"\n⚠ Warning: Found {orphan_count} orphaned work(s) not linked to collection {COLLECTION_ID}")
        print(f"  These works exist in the database but are not properly linked to the collection.")

    cursor.close()
    conn.close()
    return found_works


def delete_all_works(database_url):
    """Delete all works using individual delete scripts"""

    print("\n" + "="*70)
    print(f"  DELETE ALL: Eighteen Lesser Texts + Collection {COLLECTION_ID}")
    print("="*70)

    # Find works using hybrid search
    found_works = find_works_hybrid_search(database_url)

    if not found_works:
        print("\n✗ No works to delete")
        return False

    # Get total stats
    try:
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()

        work_ids = [work[0] for work in found_works]
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
            WHERE wk.work_id = ANY(%s)
        """, (work_ids,))
        stats = cursor.fetchone()

        print(f"\nThis will delete:")
        print(f"  - {len(found_works)} works (Eighteen Lesser Texts)")
        print(f"  - {stats[0]:,} sections")
        print(f"  - {stats[1]:,} verses")
        print(f"  - {stats[2]:,} lines")
        print(f"  - {stats[3]:,} words")
        print(f"  - Collection {COLLECTION_ID} ({COLLECTION_NAME_TAMIL})")

        cursor.close()
        conn.close()

    except Exception as e:
        print(f"\n✗ Error getting stats: {e}")
        return False

    response = input("\nAre you sure? (yes/no): ").strip().lower()
    if response not in ['yes', 'y']:
        print("Deletion cancelled.")
        return False

    # Delete each work using individual delete scripts
    print(f"\nDeleting {len(found_works)} works...")
    works_dir = Path(__file__).parent.parent / 'works'

    success_count = 0
    failed_works = []

    for i, (work_id, work_name, work_name_tamil) in enumerate(found_works, 1):
        # Convert work name to script name
        script_name = f"delete_{work_name.lower().replace(' ', '_')}.py"
        script_path = works_dir / script_name

        print(f"\n[{i}/{len(found_works)}] Deleting {work_name_tamil}...")

        if not script_path.exists():
            print(f"  ⚠ Delete script not found: {script_name}")
            print(f"  ℹ Using generic deletion for work_id {work_id}")

            # Fall back to inline deletion
            try:
                conn = psycopg2.connect(database_url)
                conn.autocommit = False
                cursor = conn.cursor()

                # Delete in reverse dependency order
                cursor.execute("""
                    DELETE FROM words
                    WHERE line_id IN (
                        SELECT l.line_id FROM lines l
                        JOIN verses v ON l.verse_id = v.verse_id
                        WHERE v.work_id = %s
                    )
                """, (work_id,))

                cursor.execute("""
                    DELETE FROM lines
                    WHERE verse_id IN (SELECT verse_id FROM verses WHERE work_id = %s)
                """, (work_id,))

                cursor.execute("DELETE FROM verses WHERE work_id = %s", (work_id,))
                cursor.execute("DELETE FROM sections WHERE work_id = %s", (work_id,))
                cursor.execute("DELETE FROM work_collections WHERE work_id = %s", (work_id,))
                cursor.execute("DELETE FROM works WHERE work_id = %s", (work_id,))

                conn.commit()
                cursor.close()
                conn.close()

                print(f"  ✓ Deleted {work_name_tamil}")
                success_count += 1

            except Exception as e:
                print(f"  ✗ Failed: {e}")
                if 'conn' in locals():
                    conn.rollback()
                    conn.close()
                failed_works.append(work_name)

        else:
            # Use individual delete script (auto-confirms)
            try:
                # Run delete script with 'yes' piped to stdin
                result = subprocess.run([
                    sys.executable,
                    str(script_path),
                    database_url
                ], input='yes\n', check=True, capture_output=True, text=True, encoding='utf-8')

                print(f"  ✓ Deleted {work_name_tamil}")
                success_count += 1

            except subprocess.CalledProcessError as e:
                print(f"  ✗ Failed to delete {work_name}")
                if e.stderr:
                    error_lines = e.stderr.split('\n')[:3]
                    for line in error_lines:
                        if line.strip():
                            print(f"    {line}")
                failed_works.append(work_name)

            except Exception as e:
                print(f"  ✗ Unexpected error: {e}")
                failed_works.append(work_name)

    # Delete collection
    if success_count == len(found_works):
        print(f"\nDeleting collection {COLLECTION_ID}...")
        try:
            conn = psycopg2.connect(database_url)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM collections WHERE collection_id = %s", (COLLECTION_ID,))
            conn.commit()
            cursor.close()
            conn.close()
            print(f"  ✓ Deleted collection {COLLECTION_ID} ({COLLECTION_NAME_TAMIL})")
        except Exception as e:
            print(f"  ✗ Failed to delete collection: {e}")

    # Summary
    print("\n" + "="*70)
    print("  DELETION SUMMARY")
    print("="*70)
    print(f"  ✓ Successfully deleted: {success_count}/{len(found_works)} works")

    if failed_works:
        print(f"  ✗ Failed: {len(failed_works)} work(s)")
        for work in failed_works:
            print(f"    - {work}")
        return False
    else:
        print(f"\n✓ All {len(found_works)} works deleted successfully!")
        return True


def main():
    db_connection = os.getenv('DATABASE_URL',
                              "postgresql://postgres:postgres@localhost/tamil_literature")
    if len(sys.argv) > 1:
        db_connection = sys.argv[1]

    print(f"Database: {db_connection[:50]}...")

    if delete_all_works(db_connection):
        print("\n✓ Master delete complete")
        sys.exit(0)
    else:
        print("\n✗ Master delete incomplete (see errors above)")
        sys.exit(1)


if __name__ == '__main__':
    main()
