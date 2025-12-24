#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Quick test for Manimegalai parser parsing logic
"""
import sys
from pathlib import Path

# Fix Windows console encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Import the parse function
sys.path.insert(0, str(Path(__file__).parent))
from manimegalai_bulk_import import parse_manimegalai_file

# Path to source file
script_dir = Path(__file__).parent
project_dir = script_dir.parent
source_file = project_dir / "Tamil-Source-TamilConcordence" / "4_ஐம்பெருங்காப்பியங்கள்" / "மணிமேகலை" / "மணிமேகலை.txt"

print("Testing Manimegalai parser...")
print(f"Source file: {source_file}")
print("=" * 70)

# Parse the file
data = parse_manimegalai_file(source_file)

# Print summary
print(f"\nTotal sections found: {len(data['sections'])}")
print("=" * 70)

for section in data['sections']:
    section_num = section['number']
    section_name = section['name']
    line_count = len(section['lines'])

    print(f"Section #{section_num}: {section_name}")
    print(f"  Lines: {line_count} (1 verse)")

    # Show first 3 lines as sample
    if section['lines']:
        print(f"  First 3 lines:")
        for i, line in enumerate(section['lines'][:3], 1):
            print(f"    {i}. {line}")
        if len(section['lines']) > 3:
            print(f"    ...")
    print()

print("=" * 70)
print("Test complete!")
