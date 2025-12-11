#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script to verify Sangam text cleaning logic
"""

import re
import sys
import io

# Fix Windows console encoding for Tamil characters
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def _clean_word_text(word: str) -> str:
    """
    Clean word text according to Prof. P. Pandiyaraja's principles:
    - Keep only Tamil characters, hyphens (-), and underscores (_)
    - Remove dots, punctuation, and line count numbers
    """
    # First, strip trailing numbers (line counts like 5, 10, 15 attached to words)
    word = re.sub(r'\d+$', '', word)

    # Remove all non-Tamil characters except - and _
    # Tamil Unicode range: \u0B80-\u0BFF
    cleaned = re.sub(r'[^\u0B80-\u0BFF\-_]', '', word)
    return cleaned.strip()

def _is_line_count(token: str) -> bool:
    """
    Check if token is a line count number (multiples of 5 or 10)
    Returns True for: 5, 10, 15, 20, 25, etc.
    """
    try:
        num = int(token)
        # Common line counts: multiples of 5
        return num % 5 == 0
    except ValueError:
        return False

# Test cases from actual Sangam text
test_lines = [
    "சேவல் அம் கொடியோன் காப்ப……………………….. 5",
    "நறியவும் உளவோ நீ அறியும் பூவே………………………..5",
    "பல் இதழ் உண்கண் பாடு ஒல்லாவே………………………..5",
    "தாமரை புரையும் காமர் சேவடி",
    "செம் களம் பட கொன்று அவுணர் தேய்த்த"
]

print("Testing Sangam text cleaning logic:")
print("="*70)

for line in test_lines:
    # Clean line: remove dots/periods
    cleaned_line = line.replace('.', '').replace('…', '')
    print(f"\nOriginal: {line}")
    print(f"Cleaned:  {cleaned_line}")

    # Parse words
    tokens = cleaned_line.strip().split()
    word_position = 1
    words = []

    for token in tokens:
        # Skip line count numbers
        if _is_line_count(token):
            print(f"  SKIP line count: {token}")
            continue

        # Clean word
        word_text = _clean_word_text(token)

        # Skip empty words
        if not word_text:
            print(f"  SKIP empty after cleaning: '{token}'")
            continue

        words.append((word_position, word_text))
        word_position += 1

    print(f"  Words ({len(words)}): {[w[1] for w in words]}")

print("\n" + "="*70)
print("✓ Test complete!")
