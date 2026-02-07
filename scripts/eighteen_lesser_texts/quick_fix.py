#!/usr/bin/env python3
# Quick fix for path construction in all generators
from pathlib import Path
import re

generators = [
    'generate_all_scripts.py',
    'generate_thinai_scripts.py',
    'generate_adhikaram_script.py',
    'generate_paththu_script.py',
    'generate_thirukkural_script.py'
]

for gen in generators:
    file_path = Path(__file__).parent / gen
    if not file_path.exists():
        continue

    content = file_path.read_text(encoding='utf-8')

    # Replace the problematic multiline path with parenthesized version
    content = re.sub(
        r'text_file = Path\(__file__\)\.parent\.parent\.parent\.parent / \\\\\\\\\s+' +
        r'"Tamil-Source-TamilConcordence" / \\\\\\\\\s+' +
        r'"\{metadata\[\'folder\'\]\}" / \\\\\\\\\s+' +
        r'"\{metadata\[\'filename\'\]\}\.txt"',
        r'''text_file = (
            Path(__file__).parent.parent.parent.parent /
            "Tamil-Source-TamilConcordence" /
            "{metadata['folder']}" /
            "{metadata['filename']}.txt"
        )''',
        content,
        flags=re.MULTILINE
    )

    file_path.write_text(content, encoding='utf-8')
    print(f"✓ Fixed {gen}")

print("\nNow regenerating all scripts...")
