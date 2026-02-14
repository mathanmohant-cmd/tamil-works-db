#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Master Orchestrator: Import all Eighteen Lesser Texts
Coordinates individual work scripts with proper collection linking.

Usage:
    python import_all.py [database_url]

Note: Each work import is atomic (separate transaction).
      Collection 201 created by first work if needed.
"""

import os
import sys
from pathlib import Path
import subprocess

# Import from centralized metadata
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'metadata'))
from eighteen_lesser_texts_metadata import COLLECTION_ID, COLLECTION_NAME, COLLECTION_NAME_TAMIL

# Legacy aliases for compatibility
COLLECTION_NAME_ENGLISH = COLLECTION_NAME

# Work orchestration order (matches canonical ordering)
# Format: (script_name, position_in_collection, work_display_name)
WORKS = [
    # Work 1: Naladiyar (adhikaram structure - READY)
    ('import_naladiyar.py', 1, 'Naladiyar'),

    # Work 2: Nanmanikkadigai (flat structure - READY)
    ('import_nanmanikkadigai.py', 2, 'Nanmanikkadigai'),

    # Work 3: Inna Narpathu (flat structure - READY)
    ('import_inna_narpathu.py', 3, 'Inna Narpathu'),

    # Work 4: Iniyavai Narpathu (flat structure - READY)
    ('import_iniyavai_narpathu.py', 4, 'Iniyavai Narpathu'),

    # Work 5: Kar Narpathu (flat structure - READY)
    ('import_kar_narpathu.py', 5, 'Kar Narpathu'),

    # Work 6: Kalavazhi Narpathu (flat structure - READY)
    ('import_kalavazhi_narpathu.py', 6, 'Kalavazhi Narpathu'),

    # Work 7-11: Thinai structure (READY)
    ('import_ainthinai_aimbathu.py', 7, 'Ainthinai Aimbathu'),
    ('import_ainthinai_ezhubathu.py', 8, 'Ainthinai Ezhubathu'),
    ('import_thinaymozhi_aimbathu.py', 9, 'Thinaymozhi Aimbathu'),
    ('import_thinaimalai_noorraimpathu.py', 10, 'Thinaimalai Noorraimpathu'),

    # Work 11: Thirigadugam (flat structure - READY)
    ('import_thirigadugam.py', 11, 'Thirigadugam'),

    # Work 12: Asarakkovai (flat structure - READY)
    ('import_asarakkovai.py', 12, 'Asarakkovai'),

    # Work 13: Pazhamozhi Nanuru (flat structure - READY)
    ('import_pazhamozhi_nanuru.py', 13, 'Pazhamozhi Nanuru'),

    # Work 14: Sirupanchamoolam (flat structure - READY)
    ('import_sirupanchamoolam.py', 14, 'Sirupanchamoolam'),

    # Work 15: Muthumozhikkanchi (paththu structure - READY)
    ('import_muthumozhikkanchi.py', 15, 'Muthumozhikkanchi'),

    # Work 16: Elathi (flat structure - READY)
    ('import_elathi.py', 16, 'Elathi'),

    # Work 17: Kainnilai (thinai structure - READY)
    ('import_kainnilai.py', 17, 'Kainnilai'),

    # Work 18: Thirukkural (special 3-level hierarchy - READY)
    ('import_thirukkural.py', 18, 'Thirukkural'),
]


def import_all_works(database_url):
    """Import all works by calling individual scripts

    Note: Individual scripts manage collection creation. Master just orchestrates.
    """
    total_works = len(WORKS)

    print("\n" + "="*70)
    print(f"  MASTER IMPORT: Eighteen Lesser Texts ({total_works} works ready)")
    print("="*70)
    print("\nNote: Each work import is atomic (separate transaction)")
    print(f"      Collection {COLLECTION_ID} created by first work if needed")
    print(f"\nImporting {total_works} works...")

    # Import each work sequentially
    works_dir = Path(__file__).parent.parent / 'works'

    success_count = 0
    failed_works = []

    for i, (script_name, position, work_name) in enumerate(WORKS, 1):
        script_path = works_dir / script_name

        if not script_path.exists():
            print(f"\n[{i}/{total_works}] Skipping {work_name}...")
            print(f"  ✗ Script not found: {script_name}")
            failed_works.append(work_name)
            continue

        print(f"\n[{i}/{total_works}] Importing {work_name}...")

        try:
            result = subprocess.run([
                sys.executable,
                str(script_path),
                database_url,
                '--collection-id', str(COLLECTION_ID),
                '--position', str(position)
            ], check=True, capture_output=True, text=True, encoding='utf-8')

            # Show condensed output (just summary lines)
            for line in result.stdout.split('\n'):
                if 'Phase' in line or '[OK]' in line or 'Inserting' in line:
                    print(f"    {line}")

            success_count += 1

        except subprocess.CalledProcessError as e:
            print(f"  ✗ Failed to import {work_name}")
            if e.stderr:
                # Show only first few lines of error
                error_lines = e.stderr.split('\n')[:5]
                for line in error_lines:
                    if line.strip():
                        print(f"    {line}")
            failed_works.append(work_name)

        except Exception as e:
            print(f"  ✗ Unexpected error importing {work_name}: {e}")
            failed_works.append(work_name)

    # Summary
    print("\n" + "="*70)
    print("  IMPORT SUMMARY")
    print("="*70)
    print(f"  ✓ Successfully imported: {success_count}/{total_works} works")

    if failed_works:
        print(f"  ✗ Failed: {len(failed_works)} work(s)")
        for work in failed_works:
            print(f"    - {work}")
        return False
    else:
        print(f"\n✓ All {total_works} works imported successfully!")
        return True


def main():
    db_connection = os.getenv('DATABASE_URL',
                              "postgresql://postgres:postgres@localhost/tamil_literature")
    if len(sys.argv) > 1:
        db_connection = sys.argv[1]

    print(f"Database: {db_connection[:50]}...")

    if import_all_works(db_connection):
        print("\n✓ Master import complete")
        print(f"\nNote: Successfully imported all {len(WORKS)} Eighteen Lesser Texts works")
        sys.exit(0)
    else:
        print("\n✗ Master import incomplete (see errors above)")
        sys.exit(1)


if __name__ == '__main__':
    main()
