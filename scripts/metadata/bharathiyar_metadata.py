#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Bharathiyar Works (பாரதியார் படைப்புகள்) Work Metadata
Centralized metadata for all 4 thematic groups of Bharathiyar poetry (Collection 328)

Bharathiyar (Subramania Bharathiyar, 1882-1921 CE) was a pioneering Tamil poet,
freedom fighter, and social reformer during the Indian independence movement.
His works span national songs, devotional poetry, social reform, and epic narratives.
"""

# Collection-level constants
COLLECTION_ID = 328
COLLECTION_NAME = 'Bharathiyar Works'
COLLECTION_NAME_TAMIL = 'பாரதியார் படைப்புகள்'
COLLECTION_DESCRIPTION = 'Poetry of Subramania Bharathiyar (1882-1921 CE) - National, devotional, and social reform poetry'

# File-level section names (Level 1 - extracted from filenames)
FILE_SECTION_NAMES = {
    1: 'தேசீய கீதங்கள்',
    2: 'தோத்திரப் பாடல்கள்',
    3: 'வேதாந்தப் பாடல்கள் - ஞானப் பாடல்கள்',
    4: 'பல்வகைப் பாடல்கள்',
    5: 'தனிப் பாடல்கள்',
    6: 'சுயசரிதை',
    7: 'கண்ணன் பாட்டு',
    8: 'பாஞ்சாலி சபதம்',
    9: 'குயில் பாட்டு',
    10: 'வசன கவிதை'
}

# Work metadata for all 4 thematic groups
WORK_METADATA = {
    1: {
        'work_name': 'Bharathiyar National and Social Reform Poetry',
        'work_name_tamil': 'பாரதியார் தேசிய மற்றும் சமூகச் சீர்திருத்தக் கவிதைகள்',
        'author': 'Subramania Bharathiyar',
        'author_tamil': 'சுப்பிரமணிய பாரதியார்',
        'chronology_start_year': 1882,
        'chronology_end_year': 1921,
        'chronology_confidence': 'high',
        'chronology_notes': 'Subramania Bharathiyar lived from 1882 to 1921 CE. Works composed during Indian independence movement.',
        'canonical_order': 328001,
        'position_in_collection': 1,
        'files': [1, 4, 5],
        'file_names': {
            1: '1.தேசீய கீதங்கள்.txt',
            4: '4.பல்வகைப் பாடல்கள்.txt',
            5: '5.தனிப் பாடல்கள்.txt'
        },
        'description': 'National songs, women\'s liberation, education, social reform, and miscellaneous poems by Bharathiyar'
    },
    2: {
        'work_name': 'Bharathiyar Devotional and Spiritual Poetry',
        'work_name_tamil': 'பாரதியார் பக்தி மற்றும் ஆன்மிகக் கவிதைகள்',
        'author': 'Subramania Bharathiyar',
        'author_tamil': 'சுப்பிரமணிய பாரதியார்',
        'chronology_start_year': 1882,
        'chronology_end_year': 1921,
        'chronology_confidence': 'high',
        'chronology_notes': 'Subramania Bharathiyar lived from 1882 to 1921 CE. Works composed during Indian independence movement.',
        'canonical_order': 328002,
        'position_in_collection': 2,
        'files': [2, 3, 7],
        'file_names': {
            2: '2.தோத்திரப் பாடல்கள்.txt',
            3: '3.வேதாந்தப் பாடல்கள் - ஞானப் பாடல்கள்.txt',
            7: '7.கண்ணன் பாட்டு.txt'
        },
        'description': 'Devotional hymns, Vedantic songs, and Krishna devotional poetry by Bharathiyar'
    },
    3: {
        'work_name': 'Bharathiyar Epic and Narrative Poetry',
        'work_name_tamil': 'பாரதியார் காப்பியக் கவிதைகள்',
        'author': 'Subramania Bharathiyar',
        'author_tamil': 'சுப்பிரமணிய பாரதியார்',
        'chronology_start_year': 1882,
        'chronology_end_year': 1921,
        'chronology_confidence': 'high',
        'chronology_notes': 'Subramania Bharathiyar lived from 1882 to 1921 CE. Works composed during Indian independence movement.',
        'canonical_order': 328003,
        'position_in_collection': 3,
        'files': [6, 8, 9],
        'file_names': {
            6: '6.சுயசரிதை.txt',
            8: '8.பாஞ்சாலி சபதம்.txt',
            9: '9.குயில் பாட்டு.txt'
        },
        'description': 'Autobiography, Panchali\'s Oath (Mahabharata epic), and Song of the Koel (narrative poetry) by Bharathiyar'
    },
    4: {
        'work_name': 'Bharathiyar Modern Free Verse Poetry',
        'work_name_tamil': 'பாரதியார் நவீன வசனக் கவிதை',
        'author': 'Subramania Bharathiyar',
        'author_tamil': 'சுப்பிரமணிய பாரதியார்',
        'chronology_start_year': 1882,
        'chronology_end_year': 1921,
        'chronology_confidence': 'high',
        'chronology_notes': 'Subramania Bharathiyar lived from 1882 to 1921 CE. Works composed during Indian independence movement.',
        'canonical_order': 328004,
        'position_in_collection': 4,
        'files': [10],
        'file_names': {
            10: '10.வசன கவிதை.txt'
        },
        'description': 'Modern free verse poetry by Bharathiyar'
    }
}
