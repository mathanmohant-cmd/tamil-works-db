#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Thiruppugazh Metadata
=====================

Work: Thiruppugazh (திருப்புகழ்)
Author: Arunagirinathar (அருணகிரிநாதர்)
Tradition: Shaivite (Murugan worship)
Collection: 323 (பக்தி இலக்கியம் - Devotional Literature)

Import Script: thiruppugazh_bulk_import.py
Delete Script: delete_thiruppugazh.py
Source File: 6_பக்தி இலக்கியம்/17.திருப்புகழ்.txt
"""

WORK_METADATA = {
    'work_id': None,  # Auto-assigned during import
    'work_name': 'Thiruppugazh',
    'work_name_tamil': 'திருப்புகழ்',
    'author': 'Arunagirinathar',
    'author_tamil': 'அருணகிரிநாதர்',
    'description': 'திருப்புகழ் - Shaivite devotional hymns to Lord Murugan',
    'canonical_order': 500,
    'position_in_collection': 3,
    'chronology_start_year': 1400,
    'chronology_end_year': 1500,
    'chronology_confidence': 'medium',
    'chronology_notes': '15th century CE - Arunagirinathar composed hymns during Vijayanagara period',
    'metadata': {
        'tradition': 'Shaivite',
        'deity_focus': 'Murugan (Kartikeya)',
        'time_period': '15th century CE',
        'place': 'திருவண்ணாமலை (Thiruvannamalai)',
        'saint': 'அருணகிரிநாதர்',
        'saint_transliteration': 'Arunagirinathar',
        'musical_tradition': True,
        'liturgical_use': True,
        'philosophical_depth': 'high',
        'emotional_intensity': 'high',
        'themes': [
            'devotion to Murugan',
            'divine grace',
            'spiritual liberation',
            'mystical experience'
        ],
        'verse_count': 1334,
        'language': 'Tamil',
        'style': 'elaborate poetic compositions with complex meter'
    }
}

# Collection linkage
COLLECTION_ID = 323  # பக்தி இலக்கியம் (Devotional Literature)
POSITION_IN_COLLECTION = None  # Auto-assigned as next position

# File structure information
FILE_INFO = {
    'source_directory': '6_பக்தி இலக்கியம்',
    'source_file': '17.திருப்புகழ்.txt',
    'file_number': 17,
    'structure_markers': {
        'author_header': '^',  # அருணகிரிநாதர் ^ திருப்புகழ்
        'section': '@',        # @number section_name
        'verse': '#',          # #verse_number
        'verse_end': 'மேல்'    # End of verse marker
    }
}

# Section hierarchy (1 level)
SECTION_HIERARCHY = {
    'level_1': {
        'level_type': 'Volume',
        'level_type_tamil': 'தொகுதி',
        'section_type': 'thoguthi',
        'section_type_tamil': 'தொகுதி',
        'description': 'Top-level organizational units (volumes/collections)'
    }
}

# Verse metadata
VERSE_METADATA = {
    'verse_type': 'Devotional Hymn',
    'verse_type_tamil': 'பக்தி பாடல்',
    'default_metadata': {
        'saint': 'அருணகிரிநாதர்',
        'deity': 'Murugan',
        'liturgical_use': True,
        'emotional_tone': 'devotional praise'
    }
}

# Import statistics (approximate)
IMPORT_STATS = {
    'total_sections': None,  # Varies by source file
    'total_verses': 1334,
    'total_lines': None,     # Varies by source file
    'total_words': None      # Varies by source file
}
