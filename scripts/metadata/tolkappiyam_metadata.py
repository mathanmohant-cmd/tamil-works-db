#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tolkappiyam (தொல்காப்பியம்) Work Metadata
Centralized metadata for Tolkappiyam grammar text (Collection 11)

Tolkappiyam is the oldest extant Tamil grammar text, attributed to Tolkappiyar.
Dating is highly disputed, with estimates ranging from 500 BCE to 500 CE.
Conservative scholarly consensus places it around 3rd century BCE to 1st century CE.
It covers phonology (எழுத்து), morphology (சொல்), and poetics (பொருள்).
"""

# Collection-level constants
COLLECTION_ID = 11
COLLECTION_NAME = 'Tamil Grammar Works'
COLLECTION_NAME_TAMIL = 'தமிழ் இலக்கண நூல்கள்'
COLLECTION_DESCRIPTION = 'Ancient and medieval Tamil grammar and linguistic treatises'

# Work metadata (single work in this collection)
WORK_METADATA = {
    'tolkappiyam': {
        'work_name': 'Tolkappiyam',
        'work_name_tamil': 'தொல்காப்பியம்',
        'author': 'Tolkappiyar',
        'author_tamil': 'தொல்காப்பியர்',
        'description': 'Ancient Tamil grammar text covering phonology, morphology, and poetics',
        'chronology_start_year': -200,
        'chronology_end_year': 100,
        'chronology_confidence': 'low',
        'chronology_notes': 'Dating highly disputed: ranges from 500 BCE to 500 CE. Conservative estimate: 3rd century BCE to 1st century CE.',
        'canonical_order': 100,
        'position_in_collection': 1,
        'file': 'tolkappiyam_conc_full.txt'
    }
}
