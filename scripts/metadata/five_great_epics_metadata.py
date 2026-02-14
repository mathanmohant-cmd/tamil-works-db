#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Five Great Epics (ஐம்பெரும்காப்பியங்கள்) Work Metadata
Centralized metadata for all 5 great Tamil epics (Collection 251)

The Five Great Epics represent the pinnacle of classical Tamil epic literature,
spanning 5th-10th century CE, including Buddhist, Jain, and secular traditions.
"""

# Collection-level constants
COLLECTION_ID = 251
COLLECTION_NAME = 'Five Great Epics'
COLLECTION_NAME_TAMIL = 'ஐம்பெரும்காப்பியங்கள்'
COLLECTION_DESCRIPTION = 'The Five Great Epics of Tamil Literature (ஐம்பெரும்காப்பியங்கள்) - Classical Tamil epic poetry spanning 5th-10th century CE'

# Work metadata for all 5 epics
WORK_METADATA = {
    'silapathikaram': {
        'work_name': 'Silapathikaram',
        'work_name_tamil': 'சிலப்பதிகாரம்',
        'author': 'Ilango Adigal',
        'author_tamil': 'இளங்கோ அடிகள்',
        'description': 'One of the Five Great Epics of Tamil Literature',
        'chronology_start_year': 400,
        'chronology_end_year': 600,
        'chronology_confidence': 'high',
        'chronology_notes': 'Epic by Iḷaṅkō Aṭikaḷ. References to Gajabahu of Sri Lanka help dating.',
        'canonical_order': 280,
        'position_in_collection': 1,
        'file': 'silapathikaram_conc_full.txt'
    },
    'manimegalai': {
        'work_name': 'Manimegalai',
        'work_name_tamil': 'மணிமேகலை',
        'author': 'Kulavāṇikaṉ Sīthalai Sāttanār',
        'author_tamil': 'குலவாணிகன் சீத்தலைச் சாத்தனார்',
        'description': 'One of the Five Great Epics of Tamil Literature. Buddhist epic by Kulavāṇikaṉ Sīthalai Sāttanār.',
        'chronology_start_year': 500,
        'chronology_end_year': 600,
        'chronology_confidence': 'medium',
        'chronology_notes': 'Twin epic to Silapathikaram. Manimegalai is the daughter of Madhavi and Kovalan.',
        'canonical_order': 290,
        'position_in_collection': 2,
        'file': 'manimegalai_conc_full.txt'
    },
    'seevaka_sinthamani': {
        'work_name': 'Seevaka Sinthamani',
        'work_name_tamil': 'சீவக சிந்தாமணி',
        'author': 'Thiruthakka Thevar (Tirutakkatēvar)',
        'author_tamil': 'திருத்தக்கத் தேவர்',
        'description': 'One of the Five Great Epics of Tamil Literature. Jain epic about Prince Jivaka.',
        'chronology_start_year': 900,
        'chronology_end_year': 1000,
        'chronology_confidence': 'medium',
        'chronology_notes': 'Jain epic in 13 books. Story of Prince Jivaka who renounces worldly life.',
        'canonical_order': 291,
        'position_in_collection': 3,
        'file': 'seevaka_sinthamani_conc_full.txt'
    },
    'valayapathi': {
        'work_name': 'Valayapathi',
        'work_name_tamil': 'வளையாபதி',
        'author': 'Unknown',
        'author_tamil': 'அறியப்படவில்லை',
        'description': 'One of the Five Great Epics of Tamil Literature (fragmentary). Only 72 verses survive.',
        'chronology_start_year': 900,
        'chronology_end_year': 1100,
        'chronology_confidence': 'low',
        'chronology_notes': 'Lost epic, only fragments survive. Attribution and dating uncertain.',
        'canonical_order': 292,
        'position_in_collection': 4,
        'file': 'valayapathi_conc_full.txt'
    },
    'kundalakesi': {
        'work_name': 'Kundalakesi',
        'work_name_tamil': 'குண்டலகேசி',
        'author': 'Unknown',
        'author_tamil': 'அறியப்படவில்லை',
        'description': 'One of the Five Great Epics of Tamil Literature (fragmentary). Only 19 verses survive.',
        'chronology_start_year': 500,
        'chronology_end_year': 700,
        'chronology_confidence': 'low',
        'chronology_notes': 'Lost Buddhist epic, only fragments survive. Attribution and dating uncertain.',
        'canonical_order': 293,
        'position_in_collection': 5,
        'file': 'kundalakesi_conc_full.txt'
    }
}
