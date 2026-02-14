#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Thembavani Metadata
===================

Work: Thembavani (தேம்பாவணி)
Author: Veeramaamunivar / Constanzo Giuseppe Beschi (வீரமாமுனிவர்)
Tradition: Christian devotional literature
Collection: 323 (பக்தி இலக்கியம் - Devotional Literature)

Import Script: thembavani_bulk_import.py
Delete Script: delete_thembavani.py
Source File: 6_பக்தி இலக்கியம்/18.தேம்பாவணி.txt
"""

WORK_METADATA = {
    'work_id': None,  # Auto-assigned during import
    'work_name': 'Thembavani',
    'work_name_tamil': 'தேம்பாவணி',
    'author': 'Veeramaamunivar',
    'author_tamil': 'வீரமாமுனிவர்',
    'description': 'தேம்பாவணி - Christian epic by Veeramaamunivar (Constanzo Giuseppe Beschi)',
    'canonical_order': 501,
    'position_in_collection': 4,
    'chronology_start_year': 1726,
    'chronology_end_year': 1726,
    'chronology_confidence': 'high',
    'chronology_notes': '1726 CE - Composed by Italian Jesuit missionary Constanzo Giuseppe Beschi in classical Tamil',
    'metadata': {
        'tradition': 'Christian',
        'author_western_name': 'Constanzo Giuseppe Beschi',
        'author_tamil_name': 'வீரமாமுனிவர்',
        'genre': 'epic',
        'themes': [
            'Christian theology',
            'Joseph narrative',
            'devotional poetry'
        ],
        'literary_significance': 'First major Christian epic in Tamil',
        'language_style': 'Classical Tamil',
        'composition_date': '1726 CE',
        'verses_count': 3615,
        'language': 'Tamil',
        'style': 'Epic poetry in classical Tamil meter'
    }
}

# Collection linkage
COLLECTION_ID = 323  # பக்தி இலக்கியம் (Devotional Literature)
POSITION_IN_COLLECTION = None  # Auto-assigned as next position

# File structure information
FILE_INFO = {
    'source_directory': '6_பக்தி இலக்கியம்',
    'source_file': '18.தேம்பாவணி.txt',
    'file_number': 18,
    'structure_markers': {
        'author_header': '^',  # வீரமாமுனிவர் ^ தேம்பாவணி
        'section': '@',        # @number section_name
        'verse': '#',          # #verse_number
        'verse_end': 'மேல்'    # End of verse marker
    }
}

# Section hierarchy (1 level)
SECTION_HIERARCHY = {
    'level_1': {
        'level_type': 'Padalam',
        'level_type_tamil': 'படலம்',
        'section_type': 'padalam',
        'section_type_tamil': 'படலம்',
        'description': 'Cantos or chapters of the epic'
    }
}

# Verse metadata
VERSE_METADATA = {
    'verse_type': 'Epic Verse',
    'verse_type_tamil': 'காப்பிய செய்யுள்',
    'default_metadata': {
        'author': 'வீரமாமுனிவர்',
        'tradition': 'Christian',
        'epic_type': 'Christian devotional epic'
    }
}

# Import statistics (approximate)
IMPORT_STATS = {
    'total_sections': None,  # Varies by source file
    'total_verses': 3615,
    'total_lines': None,     # Varies by source file
    'total_words': None      # Varies by source file
}
