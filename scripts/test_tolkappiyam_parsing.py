#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Tolkappiyam parsing logic without database
"""

import re
import sys
import io
from pathlib import Path

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def _clean_word_text(word: str) -> str:
    """Clean word text"""
    word = re.sub(r'\d+$', '', word)
    cleaned = re.sub(r'[^\u0B80-\u0BFF\-_]', '', word)
    return cleaned.strip()

def _is_single_tamil_char(word: str) -> bool:
    """Check if word is a single Tamil character"""
    tamil_only = word.replace('-', '').replace('_', '')
    return len(tamil_only) == 1

# Test file path
script_dir = Path(__file__).parent
project_dir = script_dir.parent
test_file = project_dir / "Tamil-Source-TamilConcordence" / "1_இலக்கண_நூல்கள்" / "தொல்காப்பியம்" / "தொல்காப்பியம்-எழுத்ததிகாரம்.txt"

print("Testing Tolkappiyam parsing logic:")
print("="*70)
print(f"File: {test_file.name}\n")

with open(test_file, 'r', encoding='utf-8') as f:
    lines_text = f.readlines()

current_adhikaram = None
current_iyal = None
current_nurpaa = None
nurpaa_count = 0
iyal_count = 0
single_char_count = 0
word_count = 0

for line in lines_text[:200]:  # Test first 200 lines
    line = line.strip()
    if not line:
        continue

    # Adhikaram marker
    if line.startswith('***'):
        adhikaram_match = re.match(r'\*\*\*(\d+)\s+(.+)', line)
        if adhikaram_match:
            current_adhikaram = adhikaram_match.group(2).strip()
            print(f"ADHIKARAM: {current_adhikaram}")
        continue

    # Iyal marker
    iyal_match = re.match(r'^@\s*(\d+)\s+(.+)$', line)
    if iyal_match:
        iyal_num = iyal_match.group(1)
        iyal_name = iyal_match.group(2).strip()
        current_iyal = iyal_name
        iyal_count += 1
        print(f"  IYAL {iyal_num}: {iyal_name}")
        continue

    # Nurpaa marker
    nurpaa_match = re.match(r'^#(\d+)$', line)
    if nurpaa_match:
        current_nurpaa = nurpaa_match.group(1)
        nurpaa_count += 1
        print(f"    NURPAA #{current_nurpaa}")
        continue

    # Line content
    if current_nurpaa:
        cleaned_line = line.replace('.', '').replace('…', '')
        tokens = cleaned_line.split()
        line_words = []
        line_singles = []

        for token in tokens:
            word_text = _clean_word_text(token)
            if not word_text:
                continue

            if _is_single_tamil_char(word_text):
                line_singles.append(word_text)
                single_char_count += 1
            else:
                line_words.append(word_text)
                word_count += 1

        if line_words or line_singles:
            print(f"      Line: {cleaned_line[:50]}...")
            if line_words:
                print(f"        Words ({len(line_words)}): {' '.join(line_words[:10])}")
            if line_singles:
                print(f"        Single chars ({len(line_singles)}): {' '.join(line_singles)}")

print("\n" + "="*70)
print("Summary:")
print(f"  Iyals found: {iyal_count}")
print(f"  Nurpaas found: {nurpaa_count}")
print(f"  Multi-char words: {word_count}")
print(f"  Single-char words (skipped): {single_char_count}")
print("\n✓ Test complete!")
