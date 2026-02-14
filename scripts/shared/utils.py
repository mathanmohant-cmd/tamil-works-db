#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Global Utilities for Tamil Literature Import Scripts

Provides common functions for all Tamil work parsers:
- Line cleaning (removing markers, numbers, punctuation)
- Word splitting and cleaning
- Verse type classification

Used by:
- Eighteen Lesser Texts (18 works)
- Can be used by: Sangam, Five Great Epics, Devotional Literature, etc.

Example Usage:
    from shared.utils import clean_line_text, split_and_clean_words

    cleaned = clean_line_text("அறத்தான் வருவதே இன்பம்...")
    words = split_and_clean_words(cleaned)
"""

import re
import sys
from pathlib import Path

# Add parent directory to path to access word_cleaning module
sys.path.insert(0, str(Path(__file__).parent.parent))
from utilities.word_cleaning import split_and_clean_words, clean_tamil_word


def clean_line_text(line_text):
    """Clean line text by removing markers, dots, and trailing line numbers

    Removes:
    - Dots and ellipsis (. …)
    - Structural markers (#, @, $, &, *)
    - ** and *** markers
    - Trailing line numbers

    Args:
        line_text: Raw line text from concordance file

    Returns:
        Cleaned line text (string)

    Examples:
        'அறத்தான் வருவதே இன்பம்...' → 'அறத்தான் வருவதே இன்பம்'
        '#50 கடலும் மலையும்' → 'கடலும் மலையும்'
        'வானம் குளிர் ***' → 'வானம் குளிர்'
        'மழை பெய்யும் 5' → 'மழை பெய்யும்'
    """
    # Remove dots and ellipsis
    cleaned = line_text.replace('.', '').replace('…', '')

    # Remove structural markers at the start
    cleaned = re.sub(r'^[#@$&*]+\s*', '', cleaned)

    # Remove ** and *** markers anywhere
    cleaned = re.sub(r'\*\*\*?', '', cleaned)

    # Remove trailing line numbers (multiples of 5 typically)
    cleaned = re.sub(r'\s+\d+$', '', cleaned)

    return cleaned.strip()


def classify_verse_type(title):
    """Classify verse type from title text

    Args:
        title: Verse title text (Tamil)

    Returns:
        Verse type classification (string):
        - 'invocation' - கடவுள் வாழ்த்து
        - 'prelim' - பாயிரம்
        - 'surplus' - மிகை
        - 'external' - புறத்திரட்டு
        - 'annotated' - Has title but doesn't match other categories
        - 'regular' - No title

    Examples:
        'கடவுள் வாழ்த்து' → 'invocation'
        'பாயிரம்' → 'prelim'
        'அறம்' → 'annotated'
        None → 'regular'
    """
    if not title:
        return "regular"

    if "கடவுள்" in title or "வாழ்த்து" in title:
        return "invocation"
    elif "பாயிரம்" in title:
        return "prelim"
    elif "மிகை" in title:
        return "surplus"
    elif "புறத்திரட்" in title:
        return "external"
    else:
        return "annotated"


__all__ = [
    'clean_line_text',
    'classify_verse_type',
    'split_and_clean_words',
    'clean_tamil_word'
]
