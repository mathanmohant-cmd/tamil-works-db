#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Quick fix: Update all generator scripts to use proper path construction
without line continuation characters.
"""

from pathlib import Path

generators = [
    'generate_all_scripts.py',
    'generate_thinai_scripts.py',
    'generate_adhikaram_script.py',
    'generate_paththu_script.py',
    'generate_thirukkural_script.py'
]

# The fix: replace the problematic line continuation with proper path joining
old_pattern = '''        # Get text file path
        text_file = Path(__file__).parent.parent.parent.parent / \\\\
                   "Tamil-Source-TamilConcordence" / \\\\
                   "{metadata['folder']}" / \\\\
                   "{metadata['filename']}.txt"'''

new_pattern = '''        # Get text file path
        text_file = (
            Path(__file__).parent.parent.parent.parent /
            "Tamil-Source-TamilConcordence" /
            "{metadata['folder']}" /
            "{metadata['filename']}.txt"
        )'''

for gen_file in generators:
    file_path = Path(__file__).parent / gen_file
    if file_path.exists():
        content = file_path.read_text(encoding='utf-8')

        # Replace the problematic pattern
        if '\\\\\\\\' in content:  # Check if it has the issue
            content = content.replace(
                'Path(__file__).parent.parent.parent.parent / \\\\\\\\',
                '(\n            Path(__file__).parent.parent.parent.parent /'
            )
            content = content.replace(
                '"{metadata[\'folder\']}" / \\\\\\\\',
                '"{metadata[\'folder\']}" /'
            )
            content = content.replace(
                '"{metadata[\'filename\']}.txt"',
                '"{metadata[\'filename\']}.txt"\n        )'
            )

            file_path.write_text(content, encoding='utf-8')
            print(f"✓ Fixed {gen_file}")
        else:
            print(f"  Skipped {gen_file} (no issues found)")

print("\n✓ All generators fixed!")
