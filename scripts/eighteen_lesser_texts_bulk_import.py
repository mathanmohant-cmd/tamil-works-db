#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Import all 18 Eighteen Lesser Texts (பதினெண்கீழ்க்கணக்கு) into collection 201

LEGACY WRAPPER: This script now calls the modular architecture.
For direct access, use: scripts/eighteen_lesser_texts/master/import_all.py

Works imported (பதினெண்கீழ்க்கணக்கு - 18 works):
1. நாலடியார் (Naladiyar) - 400 verses
2. நான்மணிக்கடிகை (Nanmanikkadigai) - 101 verses
3. இன்னா நாற்பது (Inna Narpathu) - 40 verses
4. இனியவை நாற்பது (Iniyavai Narpathu) - 40 verses
5. கார் நாற்பது (Kar Narpathu) - 40 verses
6. களவழி நாற்பது (Kalavazhi Narpathu) - 40 verses
7. ஐந்திணை ஐம்பது (Ainthinai Aimbathu) - 50 verses
8. ஐந்திணை எழுபது (Ainthinai Ezhubathu) - 70 verses
9. திணைமொழி ஐம்பது (Thinaymozhi Aimbathu) - 50 verses
10. திணைமாலை நூற்றைம்பது (Thinaimalai Noorraimpathu) - 150 verses
11. திரிகடுகம் (Thirigadugam) - 100 verses
12. ஆசாரக்கோவை (Asarakkovai) - 100 verses
13. பழமொழி நானூறு (Pazhamozhi Nanuru) - 400 verses
14. சிறுபஞ்சமூலம் (Sirupanchamoolam) - 100 verses
15. முதுமொழிக் காஞ்சி (Muthumozhikkanchi) - 110 verses
16. ஏலாதி (Elathi) - 80 verses
17. கைந்நிலை (Kainnilai) - 71 verses
18. திருக்குறள் (Thirukkural) - 1,330 verses

Collection: 201 (Eighteen Lesser Texts)

Usage:
    python eighteen_lesser_texts_bulk_import.py [database_url]

Examples:
    python eighteen_lesser_texts_bulk_import.py
    python eighteen_lesser_texts_bulk_import.py postgresql://postgres:postgres@localhost/tamil_literature

Architecture:
    This wrapper calls the modular architecture at:
    scripts/eighteen_lesser_texts/
    ├── master/
    │   ├── import_all.py      # Master orchestrator
    │   └── delete_all.py      # Delete orchestrator
    ├── works/
    │   ├── import_*.py        # 18 individual import scripts
    │   └── delete_*.py        # 18 individual delete scripts
    └── shared/
        ├── base_importer.py   # BaseWorkImporter class
        ├── work_metadata.py   # Metadata for all 18 works
        └── utils.py           # Shared utilities

Benefits:
    - Each work import is atomic (single transaction)
    - Individual works can be imported separately
    - Automatic collection management
    - Robust ID allocation for delete+reimport cycles
    - Hybrid search for orphan detection
"""

import sys
import subprocess
from pathlib import Path


def main():
    """Wrapper that calls the modular import script"""
    print("\n" + "="*70)
    print("  IMPORT EIGHTEEN LESSER TEXTS (Legacy Wrapper)")
    print("="*70)
    print("\nThis script is a backwards-compatible wrapper.")
    print("Calling: eighteen_lesser_texts/master/import_all.py")
    print("="*70)

    # Get the modular import script path
    modular_script = Path(__file__).parent / 'eighteen_lesser_texts' / 'master' / 'import_all.py'

    if not modular_script.exists():
        print(f"\n✗ Error: Modular import script not found: {modular_script}")
        print("\nPlease ensure the modular architecture is set up:")
        print("  scripts/eighteen_lesser_texts/master/import_all.py")
        sys.exit(1)

    # Pass through all arguments
    try:
        result = subprocess.run(
            [sys.executable, str(modular_script)] + sys.argv[1:],
            check=False  # Don't raise on non-zero exit
        )
        sys.exit(result.returncode)

    except KeyboardInterrupt:
        print("\n\n✗ Import cancelled by user")
        sys.exit(1)

    except Exception as e:
        print(f"\n✗ Error calling modular import script: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
