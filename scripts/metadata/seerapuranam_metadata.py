#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Seerapuranam Metadata
=====================

Work: Seerapuranam (சீறாப்புராணம்)
Author: Umaruppulavar (உமறுப்புலவர்)
Tradition: Islamic devotional literature
Collection: 323 (பக்தி இலக்கியம் - Devotional Literature)

Import Script: seerapuranam_bulk_import.py
Delete Script: delete_seerapuranam.py
Source File: 6_பக்தி இலக்கியம்/19.சீறாப்புராணம்.txt
"""

WORK_METADATA = {
    'work_id': None,  # Auto-assigned during import
    'work_name': 'Seerapuranam',
    'work_name_tamil': 'சீறாப்புராணம்',
    'author': 'Umaruppulavar',
    'author_tamil': 'உமறுப்புலவர்',
    'description': 'Islamic epic about Prophet Muhammad',
    'canonical_order': 502,
    'position_in_collection': 6,
    'chronology_start_year': 1550,
    'chronology_end_year': 1600,
    'chronology_confidence': 'high',
    'chronology_notes': '16th century CE - Islamic devotional epic by Umaruppulavar',
    'metadata': {
        'tradition': 'Islamic',
        'genre': 'epic',
        'themes': [
            'Prophet Muhammad',
            'Islamic theology',
            'devotional poetry'
        ],
        'literary_significance': 'Major Islamic epic in Tamil literature',
        'language_style': 'Classical Tamil',
        'language': 'Tamil',
        'style': 'Epic poetry with classical Tamil meter'
    }
}

# Collection linkage
COLLECTION_ID = 323  # பக்தி இலக்கியம் (Devotional Literature)
POSITION_IN_COLLECTION = 43  # Seerapuranam in devotional literature

# File structure information
FILE_INFO = {
    'source_directory': '6_பக்தி இலக்கியம்',
    'source_file': '19.சீறாப்புராணம்.txt',
    'file_number': 19,
    'structure_markers': {
        'kandam': '*',         # * N காண்டம் (top level)
        'padalam': '*',        # *N padalam_name (sub level)
        'verse_metadata': '$', # $ verse_id (e.g., $1.0.1)
        'verse': '#',          # #verse_number
        'verse_end': 'மேல்'    # End of verse marker
    }
}

# Section hierarchy (2 levels)
SECTION_HIERARCHY = {
    'level_1': {
        'level_type': 'kandam',
        'level_type_tamil': 'காண்டம்',
        'description': '3 main chapters (Birth, Prophethood, Migration)'
    },
    'level_2': {
        'level_type': 'padalam',
        'level_type_tamil': 'படலம்',
        'parent': 'kandam',
        'description': 'Sub-sections within each kandam'
    }
}

# Verse metadata
VERSE_METADATA = {
    'verse_type': 'verse',
    'verse_type_tamil': 'பாடல்',
    'default_metadata': {}
}

# Import statistics (approximate)
IMPORT_STATS = {
    'total_kandams': 3,
    'total_padalams': None,  # Varies by source file
    'total_verses': None,     # Varies by source file
    'total_lines': None,      # Varies by source file
    'total_words': None       # Varies by source file
}
