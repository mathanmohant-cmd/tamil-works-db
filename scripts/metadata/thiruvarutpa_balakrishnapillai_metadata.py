#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Thiruvarutpa Balakrishnapillai Edition Metadata
================================================

Work: Thiruvarutpa - Balakrishnapillai Edition (திருவருட்பா - பாலகிருஷ்ணபிள்ளை பதிப்பு)
Author: Ramalinga Swamigal (இராமலிங்க சுவாமிகள்) - Vallalar
Tradition: Universal spirituality / Shaivite
Collection: 323 (பக்தி இலக்கியம் - Devotional Literature)

Import Script: thiruvarutpa_balakrishnapillai_bulk_import.py
Delete Script: delete_thiruvarutpa_balakrishnapillai.py
Source File: 6_பக்தி இலக்கியம்/20.திருவருட்பா - பாலகிருஷ்ணபிள்ளை பதிப்பு.txt
"""

WORK_METADATA = {
    'work_id': None,  # Auto-assigned during import
    'work_name': 'Thiruvarutpa - Balakrishnapillai Edition',
    'work_name_tamil': 'திருவருட்பா - பாலகிருஷ்ணபிள்ளை பதிப்பு',
    'author': 'Ramalinga Swamigal',
    'author_tamil': 'இராமலிங்க சுவாமிகள்',
    'description': 'Thiruvarutpa (Balakrishnapillai Edition) by Ramalinga Swamigal (Vallalar) - Songs of Divine Grace',
    'canonical_order': 503,
    'position_in_collection': 9,  # Position 9 in collection 323
    'chronology_start_year': 1823,  # Vallalar's birth year
    'chronology_end_year': 1874,    # Vallalar's disappearance year
    'chronology_confidence': 'high',
    'chronology_notes': 'Composed by Saint Ramalinga Swamigal (Vallalar) in the 19th century CE',
    'metadata': {
        'author': 'Ramalinga Swamigal',
        'author_tamil': 'இராமலிங்க சுவாமிகள்',
        'alternative_names': ['Vallalar', 'Saint Ramalinga'],
        'tradition': 'Universal spirituality / Shaivite',
        'time_period': '19th century CE',
        'edition': 'Balakrishnapillai Edition',
        'edition_tamil': 'பாலகிருஷ்ணபிள்ளை பதிப்பு',
        'themes': ['Divine Grace', 'Universal Love', 'Compassion', 'Social Reform'],
        'significance': 'Teachings of Vallalar on divine compassion and universal brotherhood',
        'deity_focus': 'Arut Perum Jothi (அருட் பெரும் ஜோதி)',
        'philosophical_depth': 'very high',
        'social_reform': True,
        'universal_message': True
    }
}

# Collection linkage
COLLECTION_ID = 323  # பக்தி இலக்கியம் (Devotional Literature)

# File structure information
FILE_INFO = {
    'source_directory': '6_பக்தி இலக்கியம்',
    'source_file': '20.திருவருட்பா - பாலகிருஷ்ணபிள்ளை பதிப்பு.txt',
    'file_number': 20,
    'structure_markers': {
        'thirumurai': '&',      # &number thirumurai_name (top-level sections)
        'subsection': '@',      # @number subsection_name (under thirumurai)
        'verse': '#',           # #verse_number
        'skip_patterns': ['வள்ளலார் ^', '*']  # Header lines to skip
    }
}

# Section hierarchy (2 levels)
SECTION_HIERARCHY = {
    'level_1': {
        'level_type': 'Thirumurai',
        'level_type_tamil': 'திருமுறை',
        'description': 'Top-level divisions of Thiruvarutpa'
    },
    'level_2': {
        'level_type': 'Section',
        'level_type_tamil': 'பகுதி',
        'description': 'Subsections within each Thirumurai',
        'note': 'காப்பு (Invocatory Verses) sections auto-created for #-1 or #0 verses'
    }
}

# Verse metadata
VERSE_METADATA = {
    'verse_type': 'Poem',
    'verse_type_tamil': 'பாடல்',
    'default_metadata': {
        'author': 'Ramalinga Swamigal',
        'tradition': 'Universal spirituality',
        'deity': 'Arut Perum Jothi',
        'meter': 'Various',
        'themes': ['Divine Grace', 'Compassion']
    }
}

# Import statistics (approximate - filled during import)
IMPORT_STATS = {
    'total_sections': None,  # Varies by source file
    'total_verses': None,
    'total_lines': None,
    'total_words': None
}
