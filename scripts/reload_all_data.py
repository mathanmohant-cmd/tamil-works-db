#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Complete Database Reload Script
Drops all data, recreates schema, and imports all 5 Tamil literary works
"""

import os
import sys
import io
import subprocess
from pathlib import Path

# Fix encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def run_script(script_name, db_url, description):
    """Run a Python script and check for errors"""
    print(f"\n{'='*70}")
    print(f"{description}")
    print(f"{'='*70}")

    script_path = Path(__file__).parent / script_name
    if not script_path.exists():
        print(f"✗ Script not found: {script_name}")
        return False

    try:
        result = subprocess.run(
            [sys.executable, str(script_path), db_url],
            capture_output=True,
            text=True,
            encoding='utf-8'
        )

        # Print output
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(result.stderr, file=sys.stderr)

        if result.returncode != 0:
            print(f"✗ {description} failed with exit code {result.returncode}")
            return False

        print(f"✓ {description} completed successfully")
        return True

    except Exception as e:
        print(f"✗ Error running {script_name}: {e}")
        return False

def main():
    print("="*70)
    print("  COMPLETE DATABASE RELOAD - ALL TAMIL LITERARY WORKS")
    print("="*70)

    # Get database URL
    db_url = os.getenv('DATABASE_URL')
    if len(sys.argv) > 1:
        db_url = sys.argv[1]

    if not db_url:
        print("\n✗ Database URL required")
        print("\nUsage:")
        print("  python reload_all_data.py <database_url>")
        print("\nOr set DATABASE_URL environment variable:")
        print('  export DATABASE_URL="postgresql://user:pass@host:port/dbname"')
        return

    print(f"\nDatabase: {db_url[:50]}...")

    # Confirm reload
    print("\n⚠ WARNING: This will DELETE ALL existing data!")
    response = input("\nProceed with complete reload? (yes/no): ").strip().lower()
    if response not in ['yes', 'y']:
        print("Reload cancelled.")
        return

    # Step 1: Setup database (drops tables and recreates schema)
    if not run_script('setup_railway_db.py', db_url,
                     "Step 1/6: Drop and recreate database schema"):
        print("\n✗ Schema setup failed. Aborting.")
        return

    # Step 2: Import Thirukkural
    if not run_script('thirukkural_bulk_import.py', db_url,
                     "Step 2/6: Import Thirukkural (1,330 kurals)"):
        print("\n✗ Thirukkural import failed. Aborting.")
        return

    # Step 3: Import Tolkappiyam
    if not run_script('tolkappiyam_bulk_import.py', db_url,
                     "Step 3/6: Import Tolkappiyam (3 Adhikarams)"):
        print("\n✗ Tolkappiyam import failed. Continuing with other works...")

    # Step 4: Import Sangam Literature
    if not run_script('sangam_bulk_import.py', db_url,
                     "Step 4/6: Import Sangam Literature (18 works)"):
        print("\n✗ Sangam import failed. Continuing with other works...")

    # Step 5: Import Silapathikaram
    if not run_script('silapathikaram_bulk_import.py', db_url,
                     "Step 5/6: Import Silapathikaram (epic in 3 Kandams)"):
        print("\n✗ Silapathikaram import failed. Continuing with other works...")

    # Step 6: Import Kambaramayanam
    if not run_script('kambaramayanam_bulk_import.py', db_url,
                     "Step 6/6: Import Kambaramayanam (epic in 6 Kandams)"):
        print("\n✗ Kambaramayanam import failed.")

    print("\n" + "="*70)
    print("  DATABASE RELOAD COMPLETE!")
    print("="*70)
    print("\nNext steps:")
    print("1. Verify data:")
    print("   psql <database_url> -c 'SELECT work_name, COUNT(*) FROM verses GROUP BY work_name;'")
    print("\n2. Start backend:")
    print("   cd webapp/backend && python main.py")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nReload cancelled by user.")
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
