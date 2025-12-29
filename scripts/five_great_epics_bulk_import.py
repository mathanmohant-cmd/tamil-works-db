#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Master script to import all Five Great Epics (ஐம்பெருங்காப்பியங்கள்)

This script runs all 5 epic parsers in sequence for the Five Great Epics collection.
Each parser uses the 2-phase bulk COPY pattern for optimal performance.

The Five Great Epics (ஐம்பெருங்காப்பியங்கள்):
1. Silapathikaram (சிலப்பதிகாரம்)
2. Manimegalai (மணிமேகலை)
3. Seevaka Sinthamani (சீவக சிந்தாமணி)
4. Valayapathi (வளையாபதி)
5. Kundalakesi (குண்டலகேசி)

Usage:
    python import_five_great_epics.py [database_url]

Examples:
    python import_five_great_epics.py
    python import_five_great_epics.py postgresql://user:pass@host/tamil_literature
"""

import sys
import os
import time
from pathlib import Path
from datetime import datetime

# Set UTF-8 encoding for Windows console (environment variable only - let individual parsers handle streams)
if sys.platform == 'win32':
    os.environ['PYTHONIOENCODING'] = 'utf-8'

# Add scripts directory to path for imports
script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir))

# Import all epic parser modules
from silapathikaram_bulk_import import main as import_silapathikaram
from manimegalai_bulk_import import main as import_manimegalai
from seevaka_sinthamani_bulk_import import main as import_seevaka_sinthamani
from valayapathi_bulk_import import main as import_valayapathi
from kundalakesi_bulk_import import main as import_kundalakesi


# Define all 5 epics in traditional order
FIVE_GREAT_EPICS = [
    {
        'name': 'Silapathikaram',
        'tamil': 'சிலப்பதிகாரம்',
        'function': import_silapathikaram,
        'verses': '~5,270',  # Approximate - varies by edition
        'description': '3 Kandams → Kaathais → Verses'
    },
    {
        'name': 'Manimegalai',
        'tamil': 'மணிமேகலை',
        'function': import_manimegalai,
        'verses': 4461,  # Total lines across 30 Kathais + 1 Pathigam
        'description': '1 Pathigam + 30 Kathais'
    },
    {
        'name': 'Seevaka Sinthamani',
        'tamil': 'சீவக சிந்தாமணி',
        'function': import_seevaka_sinthamani,
        'verses': 3146,
        'description': '14 Ilampagams → 3,146 verses'
    },
    {
        'name': 'Valayapathi',
        'tamil': 'வளையாபதி',
        'function': import_valayapathi,
        'verses': 72,
        'description': '72 verses (fragmentary epic - only fragments survive)'
    },
    {
        'name': 'Kundalakesi',
        'tamil': 'குண்டலகேசி',
        'function': import_kundalakesi,
        'verses': 19,
        'description': '19 verses (fragmentary Buddhist epic)'
    }
]


def print_header():
    """Print script header"""
    print("=" * 80)
    print("FIVE GREAT EPICS (ஐம்பெருங்காப்பியங்கள்) - BULK IMPORT")
    print("=" * 80)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Total epics: {len(FIVE_GREAT_EPICS)}")
    print("=" * 80)
    print()


def print_work_header(work_num, work):
    """Print header for each epic"""
    print()
    print("-" * 80)
    print(f"[{work_num}/{len(FIVE_GREAT_EPICS)}] {work['name']} ({work['tamil']})")
    verse_display = f"{work['verses']:,}" if isinstance(work['verses'], int) else work['verses']
    print(f"Expected verses: {verse_display} | {work['description']}")
    print("-" * 80)


def print_summary(results):
    """Print summary of all imports"""
    print()
    print("=" * 80)
    print("IMPORT SUMMARY")
    print("=" * 80)

    successful = [r for r in results if r['success']]
    failed = [r for r in results if not r['success']]

    print(f"Total epics: {len(results)}")
    print(f"Successful: {len(successful)}")
    print(f"Failed: {len(failed)}")
    print(f"Total time: {sum(r['duration'] for r in results):.2f}s")
    print()

    if successful:
        print("✓ SUCCESSFUL IMPORTS:")
        for r in successful:
            verse_display = f"{r['verses']:,}" if isinstance(r['verses'], int) else r['verses']
            print(f"  • {r['name']:<30} {verse_display:>10} verses in {r['duration']:>6.2f}s")

    if failed:
        print()
        print("✗ FAILED IMPORTS:")
        for r in failed:
            print(f"  • {r['name']:<30} Error: {r['error']}")

    print("=" * 80)
    print(f"Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)


def create_collection(db_url):
    """Create the ஐம்பெரும்காப்பியங்கள் collection if it doesn't exist"""
    import psycopg2

    collection_id = 251
    collection_name = 'Five Great Epics'
    collection_name_tamil = 'ஐம்பெரும்காப்பியங்கள்'

    conn = psycopg2.connect(db_url)
    cursor = conn.cursor()

    try:
        # Check if collection exists
        cursor.execute("SELECT collection_id FROM collections WHERE collection_id = %s", (collection_id,))
        existing = cursor.fetchone()

        if not existing:
            print(f"Creating collection: {collection_name_tamil}")
            cursor.execute("""
                INSERT INTO collections (collection_id, collection_name, collection_name_tamil,
                                        collection_type, description, parent_collection_id, sort_order)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (collection_id, collection_name, collection_name_tamil, 'genre',
                  'Five Great Epics - Classic Tamil epic poetry from 2nd to 10th century CE',
                  None, 251))
            conn.commit()
            print(f"✓ Created collection {collection_name_tamil}\n")
        else:
            print(f"Collection {collection_name_tamil} already exists\n")
    finally:
        cursor.close()
        conn.close()


def link_work_to_collection(db_url, work_name, position):
    """Link a work to the ஐம்பெரும்காப்பியங்கள் collection"""
    import psycopg2

    collection_id = 251

    conn = psycopg2.connect(db_url)
    cursor = conn.cursor()

    try:
        # Get work_id by name
        cursor.execute("SELECT work_id FROM works WHERE work_name = %s", (work_name,))
        result = cursor.fetchone()

        if result:
            work_id = result[0]
            cursor.execute("""
                INSERT INTO work_collections (work_id, collection_id, position_in_collection, is_primary, notes)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (work_id, collection_id) DO NOTHING
            """, (work_id, collection_id, position, True, None))
            conn.commit()
            print(f"  ✓ Linked to collection (position {position})")
    finally:
        cursor.close()
        conn.close()


def main():
    """Main execution function"""
    # Get database URL from command line or environment
    db_url = None
    if len(sys.argv) > 1:
        db_url = sys.argv[1]
    else:
        db_url = os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@localhost/tamil_literature')

    print_header()
    print(f"Database: {db_url.split('@')[-1] if '@' in db_url else db_url}")
    print()

    # Create collection before importing works
    create_collection(db_url)

    # Track results
    results = []

    # Process each epic
    for i, work in enumerate(FIVE_GREAT_EPICS, 1):
        print_work_header(i, work)

        start_time = time.time()
        success = False
        error_msg = None

        try:
            # Temporarily override sys.argv for the parser
            original_argv = sys.argv.copy()
            sys.argv = [sys.argv[0], db_url]

            # Run the parser
            work['function']()

            # Restore original argv
            sys.argv = original_argv

            success = True
            duration = time.time() - start_time
            print(f"✓ Completed in {duration:.2f}s")

            # Link work to collection
            link_work_to_collection(db_url, work['name'], i)

        except Exception as e:
            duration = time.time() - start_time
            error_msg = str(e)
            print(f"✗ Failed after {duration:.2f}s")
            print(f"Error: {error_msg}")

            # Restore original argv
            sys.argv = original_argv

        # Record result
        results.append({
            'name': work['name'],
            'tamil': work['tamil'],
            'verses': work['verses'],
            'success': success,
            'duration': duration,
            'error': error_msg
        })

    # Print summary
    print_summary(results)

    # Return exit code based on results
    failed_count = len([r for r in results if not r['success']])
    return 0 if failed_count == 0 else 1


if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
