#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Kambaramayanam (கம்பராமாயணம்) Work Metadata
Centralized metadata for Kambaramayanam epic (Collection 500)

Kambaramayanam is a Tamil retelling of the Ramayana epic by the medieval poet Kambar,
composed during the 12th century CE during the Chola period. It is considered one of
the greatest Tamil epics and a masterpiece of Tamil literature.
"""

# Collection-level constants
COLLECTION_ID = 500
COLLECTION_NAME = 'Epics'
COLLECTION_NAME_TAMIL = 'காப்பியங்கள்'
COLLECTION_DESCRIPTION = 'Major Tamil epic poetry including medieval retellings of classical epics'

# Work metadata (single work in this collection)
WORK_METADATA = {
    'kambaramayanam': {
        'work_name': 'Kambaramayanam',
        'work_name_tamil': 'கம்பராமாயணம்',
        'author': 'Kambar',
        'author_tamil': 'கம்பர்',
        'description': 'Tamil retelling of the Ramayana epic',
        'chronology_start_year': 1100,
        'chronology_end_year': 1200,
        'chronology_confidence': 'high',
        'chronology_notes': 'Medieval epic by Kambar during Chola period.',
        'canonical_order': 400,
        'position_in_collection': 1,
        'file_pattern': 'கம்பராமாயணம்*.txt'  # Multiple files for different Kandams
    }
}
