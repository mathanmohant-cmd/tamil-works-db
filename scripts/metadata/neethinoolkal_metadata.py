#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ethical Literature (நீதிநூல்கள்) Work Metadata
Centralized metadata for all 21 ethical literature works (Collection 325)

Ethical literature represents Tamil didactic and moral poetry spanning
3rd-20th century CE, including Auvaiyar's classic works, Bharathiyar's
modern adaptations, and Thirukkural commentaries.
"""

# Collection-level constants
COLLECTION_ID = 325
COLLECTION_NAME = 'Ethical Literature'
COLLECTION_NAME_TAMIL = 'நீதிநூல்கள்'
COLLECTION_DESCRIPTION = "Twenty-one ethical literature works spanning 3rd-20th century CE, including Auvaiyar's didactic poetry and Thirukkural commentaries"

# Work metadata for all 21 works
WORK_METADATA = {
    1: {
        'work_name': 'Aathichudi',
        'work_name_tamil': 'ஆத்திசூடி',
        'author': 'Auvaiyar II',
        'author_tamil': 'ஔவையார்',
        'chronology_start_year': 1100,
        'chronology_end_year': 1200,
        'chronology_confidence': 'low',
        'chronology_notes': 'Estimated 12th century CE. Dating based on manuscript evidence and historical context.',
        'canonical_order': 325001,
        'position_in_collection': 1,
        'file': '1.ஆத்திசூடி.txt'
    },
    2: {
        'work_name': 'Konrai Venthan',
        'work_name_tamil': 'கொன்றைவேந்தன்',
        'author': 'Auvaiyar II',
        'author_tamil': 'ஔவையார்',
        'chronology_start_year': 1100,
        'chronology_end_year': 1200,
        'chronology_confidence': 'low',
        'chronology_notes': 'Estimated 12th century CE. Dating based on manuscript evidence and historical context.',
        'canonical_order': 325002,
        'position_in_collection': 2,
        'file': '2.கொன்றைவேந்தன்.txt'
    },
    3: {
        'work_name': 'Moodhurai (Vaakkundaam)',
        'work_name_tamil': 'மூதுரை (வாக்குண்டாம்)',
        'author': 'Auvaiyar II',
        'author_tamil': 'ஔவையார்',
        'chronology_start_year': 1100,
        'chronology_end_year': 1200,
        'chronology_confidence': 'low',
        'chronology_notes': 'Estimated 12th century CE. Dating based on manuscript evidence and historical context.',
        'canonical_order': 325003,
        'position_in_collection': 3,
        'file': '3.மூதுரை (வாக்குண்டாம்).txt'
    },
    4: {
        'work_name': 'Nalvazhi',
        'work_name_tamil': 'நல்வழி',
        'author': 'Auvaiyar II',
        'author_tamil': 'ஔவையார்',
        'chronology_start_year': 1100,
        'chronology_end_year': 1200,
        'chronology_confidence': 'low',
        'chronology_notes': 'Estimated 12th century CE. Dating based on manuscript evidence and historical context.',
        'canonical_order': 325004,
        'position_in_collection': 4,
        'file': '4.நல்வழி.txt'
    },
    5: {
        'work_name': 'Vetri Vetkai (Narunthokai)',
        'work_name_tamil': 'வெற்றி வேற்கை (நறுந்தொகை)',
        'author': 'Unknown',
        'author_tamil': 'அறியப்படாத ஆசிரியர்',
        'chronology_start_year': 200,
        'chronology_end_year': 600,
        'chronology_confidence': 'low',
        'chronology_notes': 'Estimated 3rd-6th century CE. Wide date range reflects scholarly uncertainty.',
        'canonical_order': 325005,
        'position_in_collection': 5,
        'file': '5.வெற்றி வேற்கை (நறுந்தொகை).txt'
    },
    6: {
        'work_name': 'Ulaga Neethi',
        'work_name_tamil': 'உலக நீதி',
        'author': 'Unknown',
        'author_tamil': 'அறியப்படாத ஆசிரியர்',
        'chronology_start_year': 500,
        'chronology_end_year': 1000,
        'chronology_confidence': 'low',
        'chronology_notes': 'Estimated 6th-10th century CE. Wide date range reflects scholarly uncertainty.',
        'canonical_order': 325006,
        'position_in_collection': 6,
        'file': '6.உலக நீதி.txt'
    },
    7: {
        'work_name': 'Neethineeri Vilakkam',
        'work_name_tamil': 'நீதிநெறி விளக்கம்',
        'author': 'Unknown',
        'author_tamil': 'அறியப்படாத ஆசிரியர்',
        'chronology_start_year': 500,
        'chronology_end_year': 1000,
        'chronology_confidence': 'low',
        'chronology_notes': 'Estimated 6th-10th century CE. Wide date range reflects scholarly uncertainty.',
        'canonical_order': 325007,
        'position_in_collection': 7,
        'file': '7.நீதிநெறி விளக்கம்.txt'
    },
    8: {
        'work_name': 'Araneri Chaaram',
        'work_name_tamil': 'அறநெறிச்சாரம்',
        'author': 'Unknown',
        'author_tamil': 'அறியப்படாத ஆசிரியர்',
        'chronology_start_year': 500,
        'chronology_end_year': 1000,
        'chronology_confidence': 'low',
        'chronology_notes': 'Estimated 6th-10th century CE. Wide date range reflects scholarly uncertainty.',
        'canonical_order': 325008,
        'position_in_collection': 8,
        'file': '8.அறநெறிச்சாரம்.txt'
    },
    9: {
        'work_name': 'Neethi Nool',
        'work_name_tamil': 'நீதி நூல்',
        'author': 'Munusep Vedhanayagam Pillai',
        'author_tamil': 'முனிசீப் வேதநாயகம் பிள்ளை',
        'chronology_start_year': 1800,
        'chronology_end_year': 1900,
        'chronology_confidence': 'low',
        'chronology_notes': 'Estimated 19th century CE. Dating based on manuscript evidence and historical context.',
        'canonical_order': 325009,
        'position_in_collection': 9,
        'file': '9.நீதி நூல்.txt'
    },
    10: {
        'work_name': 'Nanneri',
        'work_name_tamil': 'நன்னெறி',
        'author': 'Siva Prakasar',
        'author_tamil': 'சிவப்பிரகாசர்',
        'chronology_start_year': 1600,
        'chronology_end_year': 1800,
        'chronology_confidence': 'low',
        'chronology_notes': 'Estimated 17th-18th century CE. Wide date range reflects scholarly uncertainty.',
        'canonical_order': 325010,
        'position_in_collection': 10,
        'file': '10.நன்னெறி.txt'
    },
    11: {
        'work_name': 'Neethi Chudamani',
        'work_name_tamil': 'நீதி சூடாமணி',
        'author': 'Unknown',
        'author_tamil': 'அறியப்படாத ஆசிரியர்',
        'chronology_start_year': 900,
        'chronology_end_year': 1500,
        'chronology_confidence': 'low',
        'chronology_notes': 'Estimated 10th-15th century CE. Wide date range reflects scholarly uncertainty.',
        'canonical_order': 325011,
        'position_in_collection': 11,
        'file': '11.நீதி சூடாமணி.txt'
    },
    12: {
        'work_name': 'Muthumozhi Venpa',
        'work_name_tamil': 'முதுமொழி வெண்பா',
        'author': 'Unknown',
        'author_tamil': 'அறியப்படாத ஆசிரியர்',
        'chronology_start_year': 900,
        'chronology_end_year': 1500,
        'chronology_confidence': 'low',
        'chronology_notes': 'Estimated 10th-15th century CE. Wide date range reflects scholarly uncertainty.',
        'canonical_order': 325012,
        'position_in_collection': 12,
        'file': '12.முதுமொழி வெண்பா.txt'
    },
    13: {
        'work_name': 'Viveka Chinthamani',
        'work_name_tamil': 'விவேக சிந்தாமணி',
        'author': 'Unknown',
        'author_tamil': 'அறியப்படாத ஆசிரியர்',
        'chronology_start_year': 900,
        'chronology_end_year': 1500,
        'chronology_confidence': 'low',
        'chronology_notes': 'Estimated 10th-15th century CE. Wide date range reflects scholarly uncertainty.',
        'canonical_order': 325013,
        'position_in_collection': 13,
        'file': '13.விவேக.txt'
    },
    14: {
        'work_name': 'Aathichudi Venpa',
        'work_name_tamil': 'ஆத்திசூடி வெண்பா',
        'author': 'Unknown',
        'author_tamil': 'அறியப்படாத ஆசிரியர்',
        'chronology_start_year': 1100,
        'chronology_end_year': 1700,
        'chronology_confidence': 'low',
        'chronology_notes': 'Estimated 12th-17th century CE. Wide date range reflects scholarly uncertainty.',
        'canonical_order': 325014,
        'position_in_collection': 14,
        'file': '14.ஆத்திசூடி வெண்பா.txt'
    },
    15: {
        'work_name': 'Neethi Venpa',
        'work_name_tamil': 'நீதி வெண்பா',
        'author': 'Unknown',
        'author_tamil': 'அறியப்படாத ஆசிரியர்',
        'chronology_start_year': 1100,
        'chronology_end_year': 1700,
        'chronology_confidence': 'low',
        'chronology_notes': 'Estimated 12th-17th century CE. Wide date range reflects scholarly uncertainty.',
        'canonical_order': 325015,
        'position_in_collection': 15,
        'file': '15.நீதி வெண்பா.txt'
    },
    16: {
        'work_name': 'Nanmadhi Venpa',
        'work_name_tamil': 'நன்மதி வெண்பா',
        'author': 'Unknown',
        'author_tamil': 'அறியப்படாத ஆசிரியர்',
        'chronology_start_year': 1100,
        'chronology_end_year': 1700,
        'chronology_confidence': 'low',
        'chronology_notes': 'Estimated 12th-17th century CE. Wide date range reflects scholarly uncertainty.',
        'canonical_order': 325016,
        'position_in_collection': 16,
        'file': '16.நன்மதி வெண்பா.txt'
    },
    17: {
        'work_name': 'Arungalach Cheppu',
        'work_name_tamil': 'அருங்கலச்செப்பு',
        'author': 'Unknown',
        'author_tamil': 'அறியப்படாத ஆசிரியர்',
        'chronology_start_year': 900,
        'chronology_end_year': 1500,
        'chronology_confidence': 'low',
        'chronology_notes': 'Estimated 10th-15th century CE. Wide date range reflects scholarly uncertainty.',
        'canonical_order': 325017,
        'position_in_collection': 17,
        'file': '17.அருங்கலச்செப்பு.txt'
    },
    18: {
        'work_name': 'Mudhumozhimael Vaippu',
        'work_name_tamil': 'முதுமொழிமேல் வைப்பு',
        'author': 'Unknown',
        'author_tamil': 'அறியப்படாத ஆசிரியர்',
        'chronology_start_year': 900,
        'chronology_end_year': 1500,
        'chronology_confidence': 'low',
        'chronology_notes': 'Estimated 10th-15th century CE. Wide date range reflects scholarly uncertainty.',
        'canonical_order': 325018,
        'position_in_collection': 18,
        'file': '18.முதுமொழிமேல் வைப்பு.txt'
    },
    19: {
        'work_name': 'Pudhiya Aathichudi',
        'work_name_tamil': 'புதிய ஆத்திசூடி',
        'author': 'Bharathiyar',
        'author_tamil': 'பாரதியார்',
        'chronology_start_year': 1900,
        'chronology_end_year': 2000,
        'chronology_confidence': 'low',
        'chronology_notes': 'Estimated 20th century CE. Dating based on manuscript evidence and historical context.',
        'canonical_order': 325019,
        'position_in_collection': 19,
        'file': '19.புதிய ஆத்திசூடி.txt'
    },
    20: {
        'work_name': 'Ilaiyaar Aathichudi',
        'work_name_tamil': 'இளையார் ஆத்திசூடி',
        'author': 'Unknown',
        'author_tamil': 'அறியப்படாத ஆசிரியர்',
        'chronology_start_year': 1400,
        'chronology_end_year': 1900,
        'chronology_confidence': 'low',
        'chronology_notes': 'Estimated 15th-19th century CE. Wide date range reflects scholarly uncertainty.',
        'canonical_order': 325020,
        'position_in_collection': 20,
        'file': '20.இளையார் ஆத்திசூடி.txt'
    },
    21: {
        'work_name': 'Thirukkural Kumaresa Venpa',
        'work_name_tamil': 'திருக்குறள் குமரேச வெண்பா',
        'author': 'Kumaresa Guruparar',
        'author_tamil': 'குமரேச குருபரர்',
        'chronology_start_year': 1700,
        'chronology_end_year': 1900,
        'chronology_confidence': 'low',
        'chronology_notes': 'Estimated 18th-19th century CE. Wide date range reflects scholarly uncertainty.',
        'canonical_order': 325021,
        'position_in_collection': 21,
        'file': '21.திருக்குறள் குமரேச வெண்பா.txt'
    }
}
