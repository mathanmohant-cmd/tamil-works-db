#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Word Cleaning Utilities
Shared word cleaning functions for all parsers
"""

import re

def clean_tamil_word(word: str) -> str:
    """
    Clean Tamil word text according to Prof. P. Pandiyaraja's principles:
    - Keep only Tamil characters, hyphens (-), and underscores (_)
    - Remove all numbers (line counts, verse numbers, etc.)
    - Remove dots, punctuation, and English characters

    Tamil Unicode range: \u0B80-\u0BFF

    Examples:
        'அறம்5' → 'அறம்'
        'கடல்10' → 'கடல்'
        'வான்-நிலா' → 'வான்-நிலா' (keeps hyphen)
        'மலை_பெயர்' → 'மலை_பெயர்' (keeps underscore)
        'test123' → '' (no Tamil, returns empty)
    """
    # First, strip trailing numbers (line counts like 5, 10, 15 attached to words)
    word = re.sub(r'\d+$', '', word)

    # Also strip leading numbers
    word = re.sub(r'^\d+', '', word)

    # Remove all non-Tamil characters except - and _
    # Tamil Unicode range: \u0B80-\u0BFF
    cleaned = re.sub(r'[^\u0B80-\u0BFF\-_]', '', word)

    return cleaned.strip()


def is_line_count_token(token: str) -> bool:
    """
    Check if token is a line count number (multiples of 5 or standalone numbers)

    Returns True for: 5, 10, 15, 20, 25, etc.
    Also returns True for standalone numbers: 1, 2, 3, 100, etc.

    Examples:
        is_line_count_token('5') → True
        is_line_count_token('10') → True
        is_line_count_token('15') → True
        is_line_count_token('123') → True
        is_line_count_token('அறம்') → False
        is_line_count_token('அறம்5') → False (has Tamil chars)
    """
    try:
        # If it can be converted to int and is ONLY digits, it's a line count
        int(token)
        return token.isdigit()
    except ValueError:
        return False


def split_and_clean_words(line_text: str) -> list:
    """
    Split line into words and clean each word.

    Process:
    1. Remove common punctuation
    2. Split on whitespace
    3. Skip standalone numbers (line counts)
    4. Clean each word (remove numbers, non-Tamil chars)
    5. Skip empty results

    Args:
        line_text: Tamil text line

    Returns:
        List of cleaned Tamil words

    Examples:
        'அறம் கடல் 5' → ['அறம்', 'கடல்']
        'வான்-நிலா மலை' → ['வான்-நிலா', 'மலை']
        'test அறம் 123 கடல்' → ['அறம்', 'கடல்']
    """
    # Replace common punctuation with spaces (but keep - and _)
    line_text = re.sub(r'[,;!?()।.…*]', ' ', line_text)

    # Split on whitespace
    tokens = line_text.split()

    cleaned_words = []
    for token in tokens:
        # Skip standalone line count numbers
        if is_line_count_token(token):
            continue

        # Clean the word
        cleaned = clean_tamil_word(token)

        # Only keep non-empty cleaned words
        if cleaned:
            cleaned_words.append(cleaned)

    return cleaned_words


# Test function
def test_word_cleaning():
    """Test cases for word cleaning"""
    test_cases = [
        ('அறம்', 'அறம்'),
        ('அறம்5', 'அறம்'),
        ('10', None),  # Line count, should be skipped
        ('கடல்-நிலா', 'கடல்-நிலா'),
        ('வான்_மலை', 'வான்_மலை'),
        ('test123', None),  # No Tamil
        ('அறம் கடல் 5', ['அறம்', 'கடல்']),
        ('வான் 10 மலை 15', ['வான்', 'மலை']),
    ]

    print("Testing word cleaning...")
    for test_input, expected in test_cases:
        if isinstance(expected, list):
            result = split_and_clean_words(test_input)
            status = '✓' if result == expected else '✗'
            print(f"{status} split_and_clean_words('{test_input}') = {result} (expected {expected})")
        else:
            result = clean_tamil_word(test_input)
            if expected is None:
                # Should be empty
                status = '✓' if not result else '✗'
                print(f"{status} clean_tamil_word('{test_input}') = '{result}' (expected empty)")
            else:
                status = '✓' if result == expected else '✗'
                print(f"{status} clean_tamil_word('{test_input}') = '{result}' (expected '{expected}')")


if __name__ == '__main__':
    test_word_cleaning()
