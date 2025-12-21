#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Master script to import all Eighteen Lesser Texts (பதினெண்கீழ்க்கணக்கு)

This script runs all 18 parsers in sequence for the Eighteen Lesser Texts collection.
Each parser uses the 2-phase bulk COPY pattern for optimal performance.

Usage:
    python import_eighteen_lesser_texts.py [database_url]

Examples:
    python import_eighteen_lesser_texts.py
    python import_eighteen_lesser_texts.py postgresql://user:pass@host/tamil_literature
"""

import sys
import os
import time
from pathlib import Path
from datetime import datetime

# Fix Windows console encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Add scripts directory to path for imports
script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir))

# Import all parser modules
from thirukkural_bulk_import import main as import_thirukkural
from naladiyar_bulk_import import main as import_naladiyar
from nanmanikkadigai_bulk_import import main as import_nanmanikkadigai
from inna_narpathu_bulk_import import main as import_inna_narpathu
from iniyavai_narpathu_bulk_import import main as import_iniyavai_narpathu
from kar_narpathu_bulk_import import main as import_kar_narpathu
from kalavazhi_narpathu_bulk_import import main as import_kalavazhi_narpathu
from ainthinai_aimbathu_bulk_import import main as import_ainthinai_aimbathu
from ainthinai_ezhubathu_bulk_import import main as import_ainthinai_ezhubathu
from thinaymozhi_aimbathu_bulk_import import main as import_thinaymozhi_aimbathu
from thinaimalai_noorraimpathu_bulk_import import main as import_thinaimalai_noorraimpathu
from thirigadugam_bulk_import import main as import_thirigadugam
from asarakkovai_bulk_import import main as import_asarakkovai
from pazhamozhi_nanuru_bulk_import import main as import_pazhamozhi_nanuru
from sirupanchamoolam_bulk_import import main as import_sirupanchamoolam
from muthumozhikkanchi_bulk_import import main as import_muthumozhikkanchi
from elathi_bulk_import import main as import_elathi
from kainnilai_bulk_import import main as import_kainnilai


# Define all 18 works in logical order
EIGHTEEN_WORKS = [
    {
        'name': 'Thirukkural',
        'tamil': 'திருக்குறள்',
        'function': import_thirukkural,
        'verses': 1330,
        'description': '3 Paals → 10 Iyals → 133 Adhikarams'
    },
    {
        'name': 'Naladiyar',
        'tamil': 'நாலடியார்',
        'function': import_naladiyar,
        'verses': 400,
        'description': 'Adhikaram structure'
    },
    {
        'name': 'Nanmanikkadigai',
        'tamil': 'நான்மணிக்கடிகை',
        'function': import_nanmanikkadigai,
        'verses': 103,
        'description': 'Flat structure'
    },
    {
        'name': 'Inna Narpathu',
        'tamil': 'இன்னா நாற்பது',
        'function': import_inna_narpathu,
        'verses': 41,
        'description': 'Flat structure'
    },
    {
        'name': 'Iniyavai Narpathu',
        'tamil': 'இனியவை நாற்பது',
        'function': import_iniyavai_narpathu,
        'verses': 41,
        'description': 'Flat structure'
    },
    {
        'name': 'Kar Narpathu',
        'tamil': 'கார் நாற்பது',
        'function': import_kar_narpathu,
        'verses': 40,
        'description': 'Flat structure'
    },
    {
        'name': 'Kalavazhi Narpathu',
        'tamil': 'களவழி நாற்பது',
        'function': import_kalavazhi_narpathu,
        'verses': 41,
        'description': 'Flat structure'
    },
    {
        'name': 'Ainthinai Aimbathu',
        'tamil': 'ஐந்திணை ஐம்பது',
        'function': import_ainthinai_aimbathu,
        'verses': 51,
        'description': 'Thinai structure'
    },
    {
        'name': 'Ainthinai Ezhubathu',
        'tamil': 'ஐந்திணை எழுபது',
        'function': import_ainthinai_ezhubathu,
        'verses': 68,
        'description': 'Thinai structure'
    },
    {
        'name': 'Thinaymozhi Aimbathu',
        'tamil': 'திணைமொழி ஐம்பது',
        'function': import_thinaymozhi_aimbathu,
        'verses': 50,
        'description': 'Thinai structure'
    },
    {
        'name': 'Thinaimalai Noorraimpathu',
        'tamil': 'திணைமாலை நூற்றைம்பது',
        'function': import_thinaimalai_noorraimpathu,
        'verses': 154,
        'description': 'Thinai structure'
    },
    {
        'name': 'Thirigadugam',
        'tamil': 'திரிகடுகம்',
        'function': import_thirigadugam,
        'verses': 103,
        'description': 'Flat structure'
    },
    {
        'name': 'Asarakkovai',
        'tamil': 'ஆசாரக்கோவை',
        'function': import_asarakkovai,
        'verses': 101,
        'description': 'Flat structure'
    },
    {
        'name': 'Pazhamozhi Nanuru',
        'tamil': 'பழமொழி நானூறு',
        'function': import_pazhamozhi_nanuru,
        'verses': 404,
        'description': 'Flat structure'
    },
    {
        'name': 'Sirupanchamoolam',
        'tamil': 'சிறுபஞ்சமூலம்',
        'function': import_sirupanchamoolam,
        'verses': 103,
        'description': 'Flat structure'
    },
    {
        'name': 'Muthumozhikkanchi',
        'tamil': 'முதுமொழிக்காஞ்சி',
        'function': import_muthumozhikkanchi,
        'verses': 110,
        'description': 'Paththu structure'
    },
    {
        'name': 'Elathi',
        'tamil': 'ஏலாதி',
        'function': import_elathi,
        'verses': 82,
        'description': 'Flat structure'
    },
    {
        'name': 'Kainnilai',
        'tamil': 'கைந்நிலை',
        'function': import_kainnilai,
        'verses': 60,
        'description': 'Thinai structure'
    }
]


def print_header():
    """Print script header"""
    print("=" * 80)
    print("EIGHTEEN LESSER TEXTS (பதினெண்கீழ்க்கணக்கு) - BULK IMPORT")
    print("=" * 80)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Total works: {len(EIGHTEEN_WORKS)}")
    print(f"Total verses: {sum(w['verses'] for w in EIGHTEEN_WORKS):,}")
    print("=" * 80)
    print()


def print_work_header(work_num, work):
    """Print header for each work"""
    print()
    print("-" * 80)
    print(f"[{work_num}/{len(EIGHTEEN_WORKS)}] {work['name']} ({work['tamil']})")
    print(f"Expected verses: {work['verses']:,} | {work['description']}")
    print("-" * 80)


def print_summary(results):
    """Print summary of all imports"""
    print()
    print("=" * 80)
    print("IMPORT SUMMARY")
    print("=" * 80)

    successful = [r for r in results if r['success']]
    failed = [r for r in results if not r['success']]

    print(f"Total works: {len(results)}")
    print(f"Successful: {len(successful)}")
    print(f"Failed: {len(failed)}")
    print(f"Total time: {sum(r['duration'] for r in results):.2f}s")
    print()

    if successful:
        print("✓ SUCCESSFUL IMPORTS:")
        for r in successful:
            print(f"  • {r['name']:<30} {r['verses']:>6,} verses in {r['duration']:>6.2f}s")

    if failed:
        print()
        print("✗ FAILED IMPORTS:")
        for r in failed:
            print(f"  • {r['name']:<30} Error: {r['error']}")

    print("=" * 80)
    print(f"Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)


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

    # Track results
    results = []

    # Process each work
    for i, work in enumerate(EIGHTEEN_WORKS, 1):
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
