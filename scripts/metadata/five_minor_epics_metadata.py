#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Five Minor Epics (ஐஞ்சிறுகாப்பியங்கள்) Work Metadata
Centralized metadata for all 5 Jain minor epics (Collection 324)

The Five Minor Epics are smaller-scale Tamil epic works from the Sangam and
post-Sangam period (3rd-10th century CE), primarily from the Jain tradition.
"""

# Collection-level constants
COLLECTION_ID = 324
COLLECTION_NAME = 'Five Minor Epics'
COLLECTION_NAME_TAMIL = 'ஐஞ்சிறுகாப்பியங்கள்'
COLLECTION_DESCRIPTION = 'Five Jain minor epics from the Sangam and post-Sangam period (3rd-10th century CE)'

# Work metadata for all 5 minor epics
WORK_METADATA = {
    'udayana_kumara_kaviyam': {
        'work_name': 'Udayana Kumara Kaviyam',
        'work_name_tamil': 'உதயணகுமார காவியம்',
        'author': 'Kandiyar',
        'author_tamil': 'கண்டியார்',
        'description': 'Jain minor epic about Prince Udayana. One of the five minor epics of Tamil literature.',
        'chronology_start_year': 200,
        'chronology_end_year': 300,
        'chronology_confidence': 'medium',
        'chronology_notes': 'Composed by Kandiyar in the 3rd century CE. Early Jain Tamil epic.',
        'canonical_order': 324001,
        'position_in_collection': 1,
        'file': '1 உதயணகுமார காவியம்.txt',
        'note': None
    },
    'nagakumara_kaviyam': {
        'work_name': 'Nagakumara Kaviyam',
        'work_name_tamil': 'நாககுமார காவியம்',
        'author': 'Unknown',
        'author_tamil': 'அறியப்படாத ஆசிரியர்',
        'description': 'Jain minor epic about Prince Nagakumara. One of the five minor epics of Tamil literature.',
        'chronology_start_year': 400,
        'chronology_end_year': 1000,
        'chronology_confidence': 'low',
        'chronology_notes': 'Attributed to post-Sangam period (5th-10th century CE). Author unknown.',
        'canonical_order': 324002,
        'position_in_collection': 2,
        'file': '2 நாககுமார காவியம்.txt',
        'note': None
    },
    'yasodara_kaviyam': {
        'work_name': 'Yasodara Kaviyam',
        'work_name_tamil': 'யசோதர காவியம்',
        'author': 'Unknown',
        'author_tamil': 'அறியப்படாத ஆசிரியர்',
        'description': 'Jain minor epic about Yasodara. One of the five minor epics of Tamil literature.',
        'chronology_start_year': 400,
        'chronology_end_year': 1000,
        'chronology_confidence': 'low',
        'chronology_notes': 'Attributed to post-Sangam period (5th-10th century CE). Author unknown.',
        'canonical_order': 324003,
        'position_in_collection': 3,
        'file': '3 யசோதர காவியம்.txt',
        'note': None
    },
    'choolamani': {
        'work_name': 'Choolamani',
        'work_name_tamil': 'சூளாமணி',
        'author': 'Tholamozhithevar',
        'author_tamil': 'தொலமொழித்தேவர்',
        'description': 'Jain minor epic by Tholamozhithevar. One of the five minor epics of Tamil literature.',
        'chronology_start_year': 800,
        'chronology_end_year': 1000,
        'chronology_confidence': 'medium',
        'chronology_notes': 'Composed before 10th century CE by Tholamozhithevar.',
        'canonical_order': 324004,
        'position_in_collection': 4,
        'file': '4 சூளாமணி.txt',
        'note': None
    },
    'nilakesi': {
        'work_name': 'Nilakesi',
        'work_name_tamil': 'நீலகேசி',
        'author': 'Unknown',
        'author_tamil': 'அறியப்படாத ஆசிரியர்',
        'description': 'Jain minor epic. One of the five minor epics of Tamil literature. NOTE: Section 9 missing in source file.',
        'chronology_start_year': 900,
        'chronology_end_year': 1000,
        'chronology_confidence': 'medium',
        'chronology_notes': 'Composed in the 10th century CE. Author unknown. Source text has section 9 missing (jumps from @8 to @10).',
        'canonical_order': 324005,
        'position_in_collection': 5,
        'file': '5 நீலகேசி.txt',
        'note': 'Section 9 missing in source file (jumps from @8 to @10)'
    }
}

# File structure information
FILE_INFO = {
    'source_directory': '9_ஐஞ்சிறுகாப்பியங்கள்',
    'structure_markers': {
        'section_level1': '@',  # @N. Kandam/Sarrukkam (காண்டம்/சருக்கம்)
        'section_level2': '**', # ** Topic/Subsection headings (தலைப்பு)
        'verse': '#',           # #N Verse markers (பாடல்)
    },
    'note': 'Files do NOT contain &N work markers. Works are determined by filename matching.'
}

# Section hierarchy (2 levels)
SECTION_HIERARCHY = {
    'level_1': {
        'level_type': 'Kandam',
        'level_type_tamil': 'காண்டம்',
        'description': 'Top-level sections (Kandam or Sarrukkam)'
    },
    'level_2': {
        'level_type': 'Topic',
        'level_type_tamil': 'தலைப்பு',
        'description': 'Subsections under each Kandam (topic headings)'
    }
}

# Verse metadata
VERSE_METADATA = {
    'verse_type': 'Verse',
    'verse_type_tamil': 'பாடல்',
    'default_metadata': {
        'tradition': 'Jain',
        'genre': 'Epic poetry',
        'typical_lines': 4
    }
}

# Import statistics (approximate - filled during import)
IMPORT_STATS = {
    'total_works': 5,
    'total_sections': None,  # Varies by source files
    'total_verses': None,
    'total_lines': None,
    'total_words': None
}
