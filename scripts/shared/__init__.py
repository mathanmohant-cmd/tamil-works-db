#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Global Shared Utilities for Tamil Literature Import Scripts

This package provides reusable components for all parser scripts:
- BaseWorkImporter: Base class with bulk COPY, ID management, atomicity
- utils: Line cleaning, word segmentation, verse classification

Usage:
    from shared.base_importer import BaseWorkImporter
    from shared.utils import clean_line_text, split_and_clean_words
"""

from .base_importer import BaseWorkImporter
from .utils import clean_line_text, classify_verse_type, split_and_clean_words, clean_tamil_word

__all__ = [
    'BaseWorkImporter',
    'clean_line_text',
    'classify_verse_type',
    'split_and_clean_words',
    'clean_tamil_word'
]
