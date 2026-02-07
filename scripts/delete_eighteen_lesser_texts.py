#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Delete all 18 Eighteen Lesser Texts (பதினெண்கீழ்க்கணக்கு) and collection 201

LEGACY WRAPPER: This script now calls the modular architecture.
For direct access, use: scripts/eighteen_lesser_texts/master/delete_all.py

Works deleted (பதினெண்கீழ்க்கணக்கு - 18 works):
1. திருக்குறள் (Thirukkural) - 1,330 verses
2. நாலடியார் (Naladiyar) - 400 verses
3. நான்மணிக்கடிகை (Nanmanikkadigai) - 101 verses
4. இன்னா நாற்பது (Inna Narpathu) - 40 verses
5. இனியவை நாற்பது (Iniyavai Narpathu) - 40 verses
6. கார் நாற்பது (Kar Narpathu) - 40 verses
7. களவழி நாற்பது (Kalavazhi Narpathu) - 40 verses
8. ஐந்திணை ஐம்பது (Ainthinai Aimbathu) - 50 verses
9. ஐந்திணை எழுபது (Ainthinai Ezhubathu) - 70 verses
10. திணைமொழி ஐம்பது (Thinaymozhi Aimbathu) - 50 verses
11. திணைமாலை நூற்றைம்பது (Thinaimalai Noorraimpathu) - 150 verses
12. திரிகடுகம் (Thirigadugam) - 100 verses
13. ஆசாரக்கோவை (Asarakkovai) - 100 verses
14. பழமொழி நானூறு (Pazhamozhi Nanuru) - 400 verses
15. சிறுபஞ்சமூலம் (Sirupanchamoolam) - 100 verses
16. முதுமொழிக் காஞ்சி (Muthumozhikkanchi) - 100 verses
17. ஏலாதி (Elathi) - 80 verses
18. கைந்நிலை (Kainnilai) - 71 verses

Collection: 201 (Eighteen Lesser Texts)

Usage:
    python delete_eighteen_lesser_texts.py [database_url]

Examples:
    python delete_eighteen_lesser_texts.py
    python delete_eighteen_lesser_texts.py postgresql://postgres:postgres@localhost/tamil_literature
"""

import sys
import subprocess
from pathlib import Path


def main():
    """Wrapper that calls the modular delete script"""
    print("\n" + "="*70)
    print("  DELETE EIGHTEEN LESSER TEXTS (Legacy Wrapper)")
    print("="*70)
    print("\nThis script is a backwards-compatible wrapper.")
    print("Calling: eighteen_lesser_texts/master/delete_all.py")
    print("="*70)

    # Get the modular delete script path
    modular_script = Path(__file__).parent / 'eighteen_lesser_texts' / 'master' / 'delete_all.py'

    if not modular_script.exists():
        print(f"\n✗ Error: Modular delete script not found: {modular_script}")
        print("\nPlease ensure the modular architecture is set up:")
        print("  scripts/eighteen_lesser_texts/master/delete_all.py")
        sys.exit(1)

    # Pass through all arguments
    try:
        result = subprocess.run(
            [sys.executable, str(modular_script)] + sys.argv[1:],
            check=False  # Don't raise on non-zero exit
        )
        sys.exit(result.returncode)

    except KeyboardInterrupt:
        print("\n\n✗ Deletion cancelled by user")
        sys.exit(1)

    except Exception as e:
        print(f"\n✗ Error calling modular delete script: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
