#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Master Import Script for Tamil Devotional Literature (பக்தி இலக்கியம்)

Imports all devotional literature works in the correct order:
1. Thirumurai Collection (321) - 14 works (Files 1-12)
2. Naalayira Divya Prabandham Collection (322) - 24 works (Files 13-16)
3. Standalone Works:
   - Thiruppugazh (File 17)
   - Thembavani (File 18)
   - Seerapuranam (File 19)

Total: ~40 works spanning 6th-19th centuries CE across 5 religions
"""

import sys
import os
from pathlib import Path

# Import all parser modules
try:
    from thirumurai_bulk_import import ThirumuraiBulkImporter
    from naalayira_divya_prabandham_bulk_import import NaalayiraDivyaPrabandhamBulkImporter
    from thiruppugazh_bulk_import import ThiruppugazhBulkImporter
    from thembavani_bulk_import import ThembavaniBulkImporter
    from seerapuranam_bulk_import import SeerapuranamBulkImporter
except ImportError as e:
    print(f"Error importing parser modules: {e}")
    print("Make sure all parser scripts are in the same directory.")
    sys.exit(1)


def import_thirumurai(db_connection):
    """Import all 14 Thirumurai works"""
    print("\n" + "="*70)
    print("STEP 1: Importing Thirumurai Collection (திருமுறை)")
    print("="*70)
    print("Works: 14 (Files 1-12, with File 8 split into 8.1 and 8.2)")
    print("Collection ID: 321")
    print("Canonical Order: 321-334")

    script_dir = Path(__file__).parent
    project_dir = script_dir.parent
    base_dir = project_dir / "Tamil-Source-TamilConcordence" / "6_பக்தி இலக்கியம்"

    files = [
        (1, base_dir / "1.முதலாம் திருமுறை.txt", "devaram"),
        (2, base_dir / "2.இரண்டாம் திருமுறை.txt", "devaram"),
        (3, base_dir / "3.மூன்றாம் திருமுறை.txt", "devaram"),
        (4, base_dir / "4.நான்காம்_திருமுறை.txt", "devaram"),
        (5, base_dir / "5.ஐந்தாம் திருமுறை.txt", "devaram"),
        (6, base_dir / "6.ஆறாம் திருமுறை.txt", "devaram"),
        (7, base_dir / "7.ஏழாம் திருமுறை.txt", "devaram"),
        (8.1, base_dir / "8.1எட்டாம் திருமுறை.txt", "thiruvasagam"),
        (8.2, base_dir / "8.2 எட்டாம் திருமுறை.txt", "thirukkovayar"),
        (9, base_dir / "9.ஒன்பதாம் திருமுறை.txt", "file_9"),
        (10, base_dir / "10.பத்தாம் திருமுறை.txt", "thirumanthiram"),
        (11, base_dir / "11.பதினொன்றாம் திருமுறை.txt", "file_11"),
        (12, base_dir / "12.பன்னிரண்டாம் திருமுறை.txt", "periya_puranam"),
    ]

    importer = ThirumuraiBulkImporter(db_connection)

    try:
        importer._ensure_collection_exists()

        for file_num, file_path, file_type in files:
            if not file_path.exists():
                print(f"  ✗ File not found: {file_path}")
                continue

            if file_type == "devaram":
                importer.parse_devaram_file(str(file_path), int(file_num))
            elif file_type == "thiruvasagam":
                importer.parse_thiruvasagam(str(file_path), int(file_num))
            elif file_type == "thirukkovayar":
                importer.parse_thirukkovayar(str(file_path), int(file_num))
            elif file_type == "file_9":
                importer.parse_file_9(str(file_path), int(file_num))
            elif file_type == "thirumanthiram":
                importer.parse_thirumanthiram(str(file_path), int(file_num))
            elif file_type == "file_11":
                importer.parse_file_11(str(file_path), int(file_num))
            elif file_type == "periya_puranam":
                importer.parse_periya_puranam(str(file_path), int(file_num))

        importer.bulk_insert()

        print(f"\n✓ Thirumurai import complete!")
        print(f"  - Works: {len(importer.works)}")
        print(f"  - Verses: {len(importer.verses)}")
        print(f"  - Words: {len(importer.words)}")

        return True

    except Exception as e:
        print(f"\n✗ Error importing Thirumurai: {e}")
        import traceback
        traceback.print_exc()
        importer.conn.rollback()
        return False
    finally:
        importer.close()


def import_naalayira_divya_prabandham(db_connection):
    """Import all 24 Naalayira Divya Prabandham works"""
    print("\n" + "="*70)
    print("STEP 2: Importing Naalayira Divya Prabandham")
    print("="*70)
    print("Works: 24 (Files 13-16)")
    print("Collection ID: 322 (auto-assigned)")
    print("Canonical Order: 301-324")

    script_dir = Path(__file__).parent
    project_dir = script_dir.parent
    base_dir = project_dir / "Tamil-Source-TamilConcordence" / "6_பக்தி இலக்கியம்"

    files = [
        (base_dir / "13.நாலாயிரத் திவ்விய பிரபந்தம்-முதல் ஆயிரம்.txt", "முதல் ஆயிரம்"),
        (base_dir / "14.நாலாயிரத் திவ்விய பிரபந்தம்-இரண்டாம் ஆயிரம்.txt", "இரண்டாம் ஆயிரம்"),
        (base_dir / "15.நாலாயிரத் திவ்விய பிரபந்தம்-மூன்றாம் ஆயிரம்.txt", "மூன்றாம் ஆயிரம்"),
        (base_dir / "16.நாலாயிரத் திவ்விய பிரபந்தம்-நான்காம் ஆயிரம்.txt", "நான்காம் ஆயிரம்"),
    ]

    importer = NaalayiraDivyaPrabandhamBulkImporter(db_connection)

    try:
        importer._ensure_collection_exists()

        for file_path, section_name in files:
            if file_path.exists():
                importer.parse_file(str(file_path), section_name)
            else:
                print(f"  ✗ File not found: {file_path}")

        importer.bulk_insert()

        print(f"\n✓ Naalayira Divya Prabandham import complete!")
        print(f"  - Works: {len(importer.work_ids)}")
        print(f"  - Verses: {len(importer.verses)}")
        print(f"  - Words: {len(importer.words)}")

        return True

    except Exception as e:
        print(f"\n✗ Error importing Naalayira Divya Prabandham: {e}")
        import traceback
        traceback.print_exc()
        importer.conn.rollback()
        return False
    finally:
        importer.close()


def import_thiruppugazh(db_connection):
    """Import Thiruppugazh"""
    print("\n" + "="*70)
    print("STEP 3: Importing Thiruppugazh (திருப்புகழ்)")
    print("="*70)
    print("Works: 1 (File 17)")
    print("Canonical Order: 500")

    script_dir = Path(__file__).parent
    project_dir = script_dir.parent
    text_file = project_dir / "Tamil-Source-TamilConcordence" / "6_பக்தி இலக்கியம்" / "17.திருப்புகழ்.txt"

    if not text_file.exists():
        print(f"  ✗ File not found: {text_file}")
        return False

    importer = ThiruppugazhBulkImporter(db_connection)

    try:
        importer._ensure_work_exists()
        importer.parse_file(str(text_file))
        importer.bulk_insert()

        print(f"\n✓ Thiruppugazh import complete!")
        print(f"  - Verses: {len(importer.verses)}")
        print(f"  - Words: {len(importer.words)}")

        return True

    except Exception as e:
        print(f"\n✗ Error importing Thiruppugazh: {e}")
        import traceback
        traceback.print_exc()
        importer.conn.rollback()
        return False
    finally:
        importer.close()


def import_thembavani(db_connection):
    """Import Thembavani"""
    print("\n" + "="*70)
    print("STEP 4: Importing Thembavani (தேம்பாவணி)")
    print("="*70)
    print("Works: 1 (File 18)")
    print("Canonical Order: 600")

    script_dir = Path(__file__).parent
    project_dir = script_dir.parent
    text_file = project_dir / "Tamil-Source-TamilConcordence" / "6_பக்தி இலக்கியம்" / "18.தேம்பாவணி.txt"

    if not text_file.exists():
        print(f"  ✗ File not found: {text_file}")
        return False

    importer = ThembavaniBulkImporter(db_connection)

    try:
        importer._ensure_work_exists()
        importer.parse_file(str(text_file))
        importer.bulk_insert()

        print(f"\n✓ Thembavani import complete!")
        print(f"  - Verses: {len(importer.verses)}")
        print(f"  - Words: {len(importer.words)}")

        return True

    except Exception as e:
        print(f"\n✗ Error importing Thembavani: {e}")
        import traceback
        traceback.print_exc()
        importer.conn.rollback()
        return False
    finally:
        importer.close()


def import_seerapuranam(db_connection):
    """Import Seerapuranam"""
    print("\n" + "="*70)
    print("STEP 5: Importing Seerapuranam (சீறாப்புராணம்)")
    print("="*70)
    print("Works: 1 (File 19)")
    print("Canonical Order: 610")

    script_dir = Path(__file__).parent
    project_dir = script_dir.parent
    text_file = project_dir / "Tamil-Source-TamilConcordence" / "6_பக்தி இலக்கியம்" / "19.சீறாப்புராணம்.txt"

    if not text_file.exists():
        print(f"  ✗ File not found: {text_file}")
        return False

    importer = SeerapuranamBulkImporter(db_connection)

    try:
        importer._ensure_work_exists()
        importer.parse_file(str(text_file))
        importer.bulk_insert()

        print(f"\n✓ Seerapuranam import complete!")
        print(f"  - Verses: {len(importer.verses)}")
        print(f"  - Words: {len(importer.words)}")

        return True

    except Exception as e:
        print(f"\n✗ Error importing Seerapuranam: {e}")
        import traceback
        traceback.print_exc()
        importer.conn.rollback()
        return False
    finally:
        importer.close()


def main():
    """Main execution"""
    # Get database URL
    db_connection = os.getenv('DATABASE_URL', "postgresql://postgres:postgres@localhost/tamil_literature")
    if len(sys.argv) > 1:
        db_connection = sys.argv[1]

    print("="*70)
    print("Tamil Devotional Literature (பக்தி இலக்கியம்) - Master Import")
    print("="*70)
    print(f"Database: {db_connection[:50]}...")
    print("\nThis will import:")
    print("  1. Thirumurai (திருமுறை) - 14 works, Collection 321")
    print("  2. Naalayira Divya Prabandham - 24 works, Collection 322")
    print("  3. Thiruppugazh - 1 work")
    print("  4. Thembavani - 1 work")
    print("  5. Seerapuranam - 1 work")
    print("  Total: ~40 works")
    print("="*70)

    results = {
        'Thirumurai': False,
        'Naalayira Divya Prabandham': False,
        'Thiruppugazh': False,
        'Thembavani': False,
        'Seerapuranam': False
    }

    # Import in sequence
    results['Thirumurai'] = import_thirumurai(db_connection)
    results['Naalayira Divya Prabandham'] = import_naalayira_divya_prabandham(db_connection)
    results['Thiruppugazh'] = import_thiruppugazh(db_connection)
    results['Thembavani'] = import_thembavani(db_connection)
    results['Seerapuranam'] = import_seerapuranam(db_connection)

    # Print summary
    print("\n" + "="*70)
    print("IMPORT SUMMARY")
    print("="*70)
    for work, success in results.items():
        status = "✓ SUCCESS" if success else "✗ FAILED"
        print(f"  {work:35} {status}")
    print("="*70)

    # Return success if all imports succeeded
    all_success = all(results.values())
    if all_success:
        print("\n✓ All devotional literature imports completed successfully!")
        sys.exit(0)
    else:
        print("\n✗ Some imports failed. See errors above.")
        sys.exit(1)


if __name__ == '__main__':
    main()
