#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Naalayira Divya Prabandham Collection Metadata
==============================================

Collection: Naalayira Divya Prabandham (நாலாயிரத் திவ்விய பிரபந்தம்) - Collection ID: 322
4 Ayiram (thousand) subcollections (322.1 - 322.4) under Devotional Literature (323)
25 works total by 12 Azhvaars spanning 6th-9th century CE

Structure:
- File 13: First Ayiram (முதல் ஆயிரம்) - 10 works
- File 14: Second Ayiram (இரண்டாம் ஆயிரம்) - 3 works
- File 15: Third Ayiram (மூன்றாம் ஆயிரம்) - 11 works
- File 16: Fourth Ayiram (நான்காம் ஆயிரம்) - 1 work (Thiruvaaymozhi)

Import Script: naalayira_divya_prabandham_bulk_import.py
Delete Script: delete_naalayira_divya_prabandham.py
"""

COLLECTION_ID = 322
COLLECTION_NAME = 'Naalayira Divya Prabandham'
COLLECTION_NAME_TAMIL = 'நாலாயிரத் திவ்விய பிரபந்தம்'

# 4 Ayiram subcollections (under Devotional Literature 323)
SUBCOLLECTIONS = {
    1: {'id': 3221, 'name': 'முதல் ஆயிரம்', 'name_en': 'First Ayiram'},
    2: {'id': 3222, 'name': 'இரண்டாம் ஆயிரம்', 'name_en': 'Second Ayiram'},
    3: {'id': 3223, 'name': 'மூன்றாம் ஆயிரம்', 'name_en': 'Third Ayiram'},
    4: {'id': 3224, 'name': 'நான்காம் ஆயிரம்', 'name_en': 'Fourth Ayiram'},
}

WORK_METADATA = {
    'file13_1': {
        'work_name': 'திருப்பல்லாண்டு',
        'work_name_tamil': 'திருப்பல்லாண்டு',
        'author': 'பெரியாழ்வார்',
        'author_tamil': 'பெரியாழ்வார்',
        'chronology_start_year': 700,
        'chronology_end_year': 800,
        'chronology_confidence': 'high',
        'chronology_notes': 'Composed by Periyazhvaar, foster father of Andal, 8th century CE',
        'canonical_order': 322001,
        'position_in_collection': 1,
        'file': '13.நாலாயிரத் திவ்விய பிரபந்தம்-முதல் ஆயிரம்.txt',
        'subcollection_id': 3221
    },
    'file13_2': {
        'work_name': 'திருமொழி',
        'work_name_tamil': 'திருமொழி',
        'author': 'பெரியாழ்வார்',
        'author_tamil': 'பெரியாழ்வார்',
        'chronology_start_year': 700,
        'chronology_end_year': 800,
        'chronology_confidence': 'high',
        'chronology_notes': 'Composed by Periyazhvaar, foster father of Andal, 8th century CE',
        'canonical_order': 322002,
        'position_in_collection': 2,
        'file': '13.நாலாயிரத் திவ்விய பிரபந்தம்-முதல் ஆயிரம்.txt',
        'subcollection_id': 3221
    },
    'file13_3': {
        'work_name': 'திருப்பாவை',
        'work_name_tamil': 'திருப்பாவை',
        'author': 'ஆண்டாள்',
        'author_tamil': 'ஆண்டாள்',
        'chronology_start_year': 700,
        'chronology_end_year': 800,
        'chronology_confidence': 'high',
        'chronology_notes': 'Composed by Andal, the only female Azhvaar, 8th century CE',
        'canonical_order': 322003,
        'position_in_collection': 3,
        'file': '13.நாலாயிரத் திவ்விய பிரபந்தம்-முதல் ஆயிரம்.txt',
        'subcollection_id': 3221
    },
    'file13_4': {
        'work_name': 'நாச்சியார் திருமொழி',
        'work_name_tamil': 'நாச்சியார் திருமொழி',
        'author': 'ஆண்டாள்',
        'author_tamil': 'ஆண்டாள்',
        'chronology_start_year': 700,
        'chronology_end_year': 800,
        'chronology_confidence': 'high',
        'chronology_notes': 'Composed by Andal, the only female Azhvaar, 8th century CE',
        'canonical_order': 322004,
        'position_in_collection': 4,
        'file': '13.நாலாயிரத் திவ்விய பிரபந்தம்-முதல் ஆயிரம்.txt',
        'subcollection_id': 3221
    },
    'file13_5': {
        'work_name': 'பெருமாள் திருமொழி',
        'work_name_tamil': 'பெருமாள் திருமொழி',
        'author': 'குலசேகர ஆழ்வார்',
        'author_tamil': 'குலசேகர ஆழ்வார்',
        'chronology_start_year': 600,
        'chronology_end_year': 900,
        'chronology_confidence': 'medium',
        'chronology_notes': 'Part of Naalayira Divya Prabandham, composed by குலசேகர ஆழ்வார்',
        'canonical_order': 322005,
        'position_in_collection': 5,
        'file': '13.நாலாயிரத் திவ்விய பிரபந்தம்-முதல் ஆயிரம்.txt',
        'subcollection_id': 3221
    },
    'file13_6': {
        'work_name': 'திருச்சந்த விருத்தம்',
        'work_name_tamil': 'திருச்சந்த விருத்தம்',
        'author': 'திருமழிசை ஆழ்வார்',
        'author_tamil': 'திருமழிசை ஆழ்வார்',
        'chronology_start_year': 600,
        'chronology_end_year': 900,
        'chronology_confidence': 'medium',
        'chronology_notes': 'Part of Naalayira Divya Prabandham, composed by திருமழிசை ஆழ்வார்',
        'canonical_order': 322006,
        'position_in_collection': 6,
        'file': '13.நாலாயிரத் திவ்விய பிரபந்தம்-முதல் ஆயிரம்.txt',
        'subcollection_id': 3221
    },
    'file13_7': {
        'work_name': 'திருமாலை',
        'work_name_tamil': 'திருமாலை',
        'author': 'தொண்டரடிப்பொடி ஆழ்வார்',
        'author_tamil': 'தொண்டரடிப்பொடி ஆழ்வார்',
        'chronology_start_year': 600,
        'chronology_end_year': 900,
        'chronology_confidence': 'medium',
        'chronology_notes': 'Part of Naalayira Divya Prabandham, composed by தொண்டரடிப்பொடி ஆழ்வார்',
        'canonical_order': 322007,
        'position_in_collection': 7,
        'file': '13.நாலாயிரத் திவ்விய பிரபந்தம்-முதல் ஆயிரம்.txt',
        'subcollection_id': 3221
    },
    'file13_8': {
        'work_name': 'திருப்பள்ளியெழுச்சி',
        'work_name_tamil': 'திருப்பள்ளியெழுச்சி',
        'author': 'தொண்டரடிப்பொடி ஆழ்வார்',
        'author_tamil': 'தொண்டரடிப்பொடி ஆழ்வார்',
        'chronology_start_year': 600,
        'chronology_end_year': 900,
        'chronology_confidence': 'medium',
        'chronology_notes': 'Part of Naalayira Divya Prabandham, composed by தொண்டரடிப்பொடி ஆழ்வார்',
        'canonical_order': 322008,
        'position_in_collection': 8,
        'file': '13.நாலாயிரத் திவ்விய பிரபந்தம்-முதல் ஆயிரம்.txt',
        'subcollection_id': 3221
    },
    'file13_9': {
        'work_name': 'அமலனாதிபிரான்',
        'work_name_tamil': 'அமலனாதிபிரான்',
        'author': 'திருப்பாணாழ்வார்',
        'author_tamil': 'திருப்பாணாழ்வார்',
        'chronology_start_year': 600,
        'chronology_end_year': 900,
        'chronology_confidence': 'medium',
        'chronology_notes': 'Part of Naalayira Divya Prabandham, composed by திருப்பாணாழ்வார்',
        'canonical_order': 322009,
        'position_in_collection': 9,
        'file': '13.நாலாயிரத் திவ்விய பிரபந்தம்-முதல் ஆயிரம்.txt',
        'subcollection_id': 3221
    },
    'file13_10': {
        'work_name': 'கண்ணிநுண் சிறுத்தாம்பு',
        'work_name_tamil': 'கண்ணிநுண் சிறுத்தாம்பு',
        'author': 'மதுரகவி ஆழ்வார்',
        'author_tamil': 'மதுரகவி ஆழ்வார்',
        'chronology_start_year': 600,
        'chronology_end_year': 900,
        'chronology_confidence': 'medium',
        'chronology_notes': 'Part of Naalayira Divya Prabandham, composed by மதுரகவி ஆழ்வார்',
        'canonical_order': 322010,
        'position_in_collection': 10,
        'file': '13.நாலாயிரத் திவ்விய பிரபந்தம்-முதல் ஆயிரம்.txt',
        'subcollection_id': 3221
    },
    'file14_11': {
        'work_name': 'பெரிய திருமொழி',
        'work_name_tamil': 'பெரிய திருமொழி',
        'author': 'திருமங்கை ஆழ்வார்',
        'author_tamil': 'திருமங்கை ஆழ்வார்',
        'chronology_start_year': 700,
        'chronology_end_year': 800,
        'chronology_confidence': 'high',
        'chronology_notes': 'Composed by Thirumangai Azhvaar, 8th century CE',
        'canonical_order': 322011,
        'position_in_collection': 11,
        'file': '14.நாலாயிரத் திவ்விய பிரபந்தம்-இரண்டாம் ஆயிரம்.txt',
        'subcollection_id': 3222
    },
    'file14_12': {
        'work_name': 'திருக்குறுந்தாண்டகம்',
        'work_name_tamil': 'திருக்குறுந்தாண்டகம்',
        'author': 'திருமங்கை ஆழ்வார்',
        'author_tamil': 'திருமங்கை ஆழ்வார்',
        'chronology_start_year': 700,
        'chronology_end_year': 800,
        'chronology_confidence': 'high',
        'chronology_notes': 'Composed by Thirumangai Azhvaar, 8th century CE',
        'canonical_order': 322012,
        'position_in_collection': 12,
        'file': '14.நாலாயிரத் திவ்விய பிரபந்தம்-இரண்டாம் ஆயிரம்.txt',
        'subcollection_id': 3222
    },
    'file14_13': {
        'work_name': 'திருநெடுந்தாண்டகம்',
        'work_name_tamil': 'திருநெடுந்தாண்டகம்',
        'author': 'திருமங்கை ஆழ்வார்',
        'author_tamil': 'திருமங்கை ஆழ்வார்',
        'chronology_start_year': 700,
        'chronology_end_year': 800,
        'chronology_confidence': 'high',
        'chronology_notes': 'Composed by Thirumangai Azhvaar, 8th century CE',
        'canonical_order': 322013,
        'position_in_collection': 13,
        'file': '14.நாலாயிரத் திவ்விய பிரபந்தம்-இரண்டாம் ஆயிரம்.txt',
        'subcollection_id': 3222
    },
    'file15_14': {
        'work_name': 'முதல் திருவந்தாதி',
        'work_name_tamil': 'முதல் திருவந்தாதி',
        'author': 'பொய்கை ஆழ்வார்',
        'author_tamil': 'பொய்கை ஆழ்வார்',
        'chronology_start_year': 600,
        'chronology_end_year': 900,
        'chronology_confidence': 'medium',
        'chronology_notes': 'Part of Naalayira Divya Prabandham, composed by பொய்கை ஆழ்வார்',
        'canonical_order': 322014,
        'position_in_collection': 14,
        'file': '15.நாலாயிரத் திவ்விய பிரபந்தம்-மூன்றாம் ஆயிரம்.txt',
        'subcollection_id': 3223
    },
    'file15_15': {
        'work_name': 'இரண்டாம் திருவந்தாதி',
        'work_name_tamil': 'இரண்டாம் திருவந்தாதி',
        'author': 'பூதத்தாழ்வார்',
        'author_tamil': 'பூதத்தாழ்வார்',
        'chronology_start_year': 600,
        'chronology_end_year': 900,
        'chronology_confidence': 'medium',
        'chronology_notes': 'Part of Naalayira Divya Prabandham, composed by பூதத்தாழ்வார்',
        'canonical_order': 322015,
        'position_in_collection': 15,
        'file': '15.நாலாயிரத் திவ்விய பிரபந்தம்-மூன்றாம் ஆயிரம்.txt',
        'subcollection_id': 3223
    },
    'file15_16': {
        'work_name': 'மூன்றாம் திருவந்தாதி',
        'work_name_tamil': 'மூன்றாம் திருவந்தாதி',
        'author': 'பேயாழ்வார்',
        'author_tamil': 'பேயாழ்வார்',
        'chronology_start_year': 600,
        'chronology_end_year': 900,
        'chronology_confidence': 'medium',
        'chronology_notes': 'Part of Naalayira Divya Prabandham, composed by பேயாழ்வார்',
        'canonical_order': 322016,
        'position_in_collection': 16,
        'file': '15.நாலாயிரத் திவ்விய பிரபந்தம்-மூன்றாம் ஆயிரம்.txt',
        'subcollection_id': 3223
    },
    'file15_17': {
        'work_name': 'நான்முகன் திருவந்தாதி',
        'work_name_tamil': 'நான்முகன் திருவந்தாதி',
        'author': 'திருமழிசை ஆழ்வார்',
        'author_tamil': 'திருமழிசை ஆழ்வார்',
        'chronology_start_year': 600,
        'chronology_end_year': 900,
        'chronology_confidence': 'medium',
        'chronology_notes': 'Part of Naalayira Divya Prabandham, composed by திருமழிசை ஆழ்வார்',
        'canonical_order': 322017,
        'position_in_collection': 17,
        'file': '15.நாலாயிரத் திவ்விய பிரபந்தம்-மூன்றாம் ஆயிரம்.txt',
        'subcollection_id': 3223
    },
    'file15_18': {
        'work_name': 'திருவிருத்தம்',
        'work_name_tamil': 'திருவிருத்தம்',
        'author': 'நம்மாழ்வார்',
        'author_tamil': 'நம்மாழ்வார்',
        'chronology_start_year': 800,
        'chronology_end_year': 900,
        'chronology_confidence': 'high',
        'chronology_notes': 'Composed by Nammazhvaar, most prominent Azhvaar of 9th century CE',
        'canonical_order': 322018,
        'position_in_collection': 18,
        'file': '15.நாலாயிரத் திவ்விய பிரபந்தம்-மூன்றாம் ஆயிரம்.txt',
        'subcollection_id': 3223
    },
    'file15_19': {
        'work_name': 'திருவாசிரியம்',
        'work_name_tamil': 'திருவாசிரியம்',
        'author': 'நம்மாழ்வார்',
        'author_tamil': 'நம்மாழ்வார்',
        'chronology_start_year': 800,
        'chronology_end_year': 900,
        'chronology_confidence': 'high',
        'chronology_notes': 'Composed by Nammazhvaar, most prominent Azhvaar of 9th century CE',
        'canonical_order': 322019,
        'position_in_collection': 19,
        'file': '15.நாலாயிரத் திவ்விய பிரபந்தம்-மூன்றாம் ஆயிரம்.txt',
        'subcollection_id': 3223
    },
    'file15_20': {
        'work_name': 'பெரியதிருவந்தாதி',
        'work_name_tamil': 'பெரியதிருவந்தாதி',
        'author': 'நம்மாழ்வார்',
        'author_tamil': 'நம்மாழ்வார்',
        'chronology_start_year': 800,
        'chronology_end_year': 900,
        'chronology_confidence': 'high',
        'chronology_notes': 'Composed by Nammazhvaar, most prominent Azhvaar of 9th century CE',
        'canonical_order': 322020,
        'position_in_collection': 20,
        'file': '15.நாலாயிரத் திவ்விய பிரபந்தம்-மூன்றாம் ஆயிரம்.txt',
        'subcollection_id': 3223
    },
    'file15_21': {
        'work_name': 'திருவெழுக்கூற்றிருக்கை',
        'work_name_tamil': 'திருவெழுக்கூற்றிருக்கை',
        'author': 'திருமங்கை ஆழ்வார்',
        'author_tamil': 'திருமங்கை ஆழ்வார்',
        'chronology_start_year': 700,
        'chronology_end_year': 800,
        'chronology_confidence': 'high',
        'chronology_notes': 'Composed by Thirumangai Azhvaar, 8th century CE',
        'canonical_order': 322021,
        'position_in_collection': 21,
        'file': '15.நாலாயிரத் திவ்விய பிரபந்தம்-மூன்றாம் ஆயிரம்.txt',
        'subcollection_id': 3223
    },
    'file15_22': {
        'work_name': 'சிறிய திருமடல்',
        'work_name_tamil': 'சிறிய திருமடல்',
        'author': 'திருமங்கை ஆழ்வார்',
        'author_tamil': 'திருமங்கை ஆழ்வார்',
        'chronology_start_year': 700,
        'chronology_end_year': 800,
        'chronology_confidence': 'high',
        'chronology_notes': 'Composed by Thirumangai Azhvaar, 8th century CE',
        'canonical_order': 322022,
        'position_in_collection': 22,
        'file': '15.நாலாயிரத் திவ்விய பிரபந்தம்-மூன்றாம் ஆயிரம்.txt',
        'subcollection_id': 3223
    },
    'file15_23': {
        'work_name': 'பெரிய திருமடல்',
        'work_name_tamil': 'பெரிய திருமடல்',
        'author': 'திருமங்கை ஆழ்வார்',
        'author_tamil': 'திருமங்கை ஆழ்வார்',
        'chronology_start_year': 700,
        'chronology_end_year': 800,
        'chronology_confidence': 'high',
        'chronology_notes': 'Composed by Thirumangai Azhvaar, 8th century CE',
        'canonical_order': 322023,
        'position_in_collection': 23,
        'file': '15.நாலாயிரத் திவ்விய பிரபந்தம்-மூன்றாம் ஆயிரம்.txt',
        'subcollection_id': 3223
    },
    'file15_24': {
        'work_name': 'இராமானுச நூற்றந்தாதி',
        'work_name_tamil': 'இராமானுச நூற்றந்தாதி',
        'author': 'திருவரங்கத்து அமுதனார்',
        'author_tamil': 'திருவரங்கத்து அமுதனார்',
        'chronology_start_year': 600,
        'chronology_end_year': 900,
        'chronology_confidence': 'medium',
        'chronology_notes': 'Part of Naalayira Divya Prabandham, composed by திருவரங்கத்து அமுதனார்',
        'canonical_order': 322024,
        'position_in_collection': 24,
        'file': '15.நாலாயிரத் திவ்விய பிரபந்தம்-மூன்றாம் ஆயிரம்.txt',
        'subcollection_id': 3223
    },
    'file16_25': {
        'work_name': 'திருவாய்மொழி',
        'work_name_tamil': 'திருவாய்மொழி',
        'author': 'நம்மாழ்வார்',
        'author_tamil': 'நம்மாழ்வார்',
        'chronology_start_year': 800,
        'chronology_end_year': 900,
        'chronology_confidence': 'high',
        'chronology_notes': 'Composed by Nammazhvaar, most prominent Azhvaar of 9th century CE',
        'canonical_order': 322025,
        'position_in_collection': 25,
        'file': '16.நாலாயிரத் திவ்விய பிரபந்தம்-நான்காம் ஆயிரம்.txt',
        'subcollection_id': 3224
    }
}
