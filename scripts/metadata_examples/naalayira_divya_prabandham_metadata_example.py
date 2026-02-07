#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Example: Metadata for Naalayira Divya Prabandham (நாலாயிரத் திவ்விய பிரபந்தம்)
Vaishnavite collection - 24 works by 12 Alvars
Collection ID: 322
"""

# Alvar metadata (12 Alvars who composed the 24 works)
ALVARS = {
    'பொய்கையாழ்வார்': {
        'transliteration': 'Poigai Alvar',
        'period': '7th century CE',
        'position': 1,  # First of the Alvars
        'works': ['முதல் திருவந்தாதி'],
        'place': 'காஞ்சிபுரம்',
        'deity_focus': 'Vishnu at Kanchipuram'
    },
    'பூதத்தாழ்வார்': {
        'transliteration': 'Bhoothathalvar',
        'period': '7th century CE',
        'position': 2,
        'works': ['இரண்டாம் திருவந்தாதி'],
        'place': 'மகாபலிபுரம்',
        'deity_focus': 'Vishnu at Mamallapuram'
    },
    'பேயாழ்வார்': {
        'transliteration': 'Pey Alvar',
        'period': '7th century CE',
        'position': 3,
        'works': ['மூன்றாம் திருவந்தாதி'],
        'place': 'மயிலாப்பூர்',
        'deity_focus': 'Vishnu at Mylapore'
    },
    'திருமழிசையாழ்வார்': {
        'transliteration': 'Thirumalisai Alvar',
        'period': '7th century CE',
        'position': 4,
        'works': ['திருச்சந்த விருத்தம்', 'நான்முகன் திருவந்தாதி'],
        'place': 'திருமழிசை',
        'deity_focus': 'Vishnu at Thirumalisai'
    },
    'நம்மாழ்வார்': {
        'transliteration': 'Nammalvar',
        'period': '9th century CE',
        'position': 5,
        'status': 'chief Alvar',
        'works': ['திருவாய்மொழி', 'திருவாசிரியம்', 'பெரிய திருவந்தாதி'],
        'place': 'திருக்குருகூர்',
        'verse_count': 1296,  # Most prolific
        'deity_focus': 'Ranganatha at Srirangam',
        'philosophical_depth': 'highest',
        'influence': 'Foundational theologian of Sri Vaishnavism'
    },
    'பெரியாழ்வார்': {
        'transliteration': 'Periyalvar',
        'period': '9th century CE',
        'position': 6,
        'works': ['பெரியாழ்வார் திருமொழி'],
        'place': 'ஸ்ரீவில்லிபுத்தூர்',
        'deity_focus': 'Vadapatrasayi at Srivilliputtur',
        'relationship': 'Father of Andal'
    },
    'ஆண்டாள்': {
        'transliteration': 'Andal',
        'period': '9th century CE',
        'position': 7,
        'gender': 'female',
        'status': 'only female Alvar',
        'works': ['திருப்பாவை', 'நாச்சியார் திருமொழி'],
        'place': 'ஸ்ரீவில்லிபுத்தூர்',
        'deity_focus': 'Krishna',
        'literary_form': 'bridal mysticism',
        'cultural_significance': 'Extremely high - Thiruppavai recited daily in temples',
        'relationship': 'Daughter of Periyalvar'
    },
    'தொண்டரடிப்பொடியாழ்வார்': {
        'transliteration': 'Thondaradippodi Alvar',
        'period': '9th century CE',
        'position': 8,
        'works': ['திருமாலை', 'திருப்பள்ளியெழுச்சி'],
        'place': 'திருமண்டங்குடி',
        'deity_focus': 'Ranganatha at Srirangam',
        'theme': 'service and surrender'
    },
    'திருப்பாணாழ்வார்': {
        'transliteration': 'Thiruppan Alvar',
        'period': '9th century CE',
        'position': 9,
        'works': ['அமலனாதிபிரான்'],
        'place': 'உறையூர்',
        'deity_focus': 'Ranganatha at Srirangam',
        'verse_count': 10,
        'social_background': 'outcaste - emphasizes bhakti transcends caste'
    },
    'குலசேகராழ்வார்': {
        'transliteration': 'Kulasekara Alvar',
        'period': '9th century CE',
        'position': 10,
        'works': ['பெருமாள் திருமொழி'],
        'place': 'திருவஞ்சிக்களம்',
        'social_status': 'king of Travancore',
        'deity_focus': 'Rama and Krishna',
        'emotional_tone': 'longing and devotion'
    },
    'திருமங்கையாழ்வார்': {
        'transliteration': 'Thirumangai Alvar',
        'period': '9th century CE',
        'position': 11,
        'works': ['பெரிய திருமொழி', 'திருக்குறுந்தாண்டகம்', 'திருநெடுந்தாண்டகம்', 'முதல் திருவந்தாதி', 'இரண்டாம் திருவந்தாதி', 'மூன்றாம் திருவந்தாதி'],
        'verse_count': 1253,  # Second most prolific
        'place': 'திருக்குறையலூர்',
        'social_status': 'chieftain',
        'deity_focus': 'Vishnu at various divya desams',
        'contribution': 'Identified 106 of 108 divya desams'
    },
    'மதுரகவியாழ்வார்': {
        'transliteration': 'Madhurakavi Alvar',
        'period': '9th century CE',
        'position': 12,
        'works': ['கண்ணிநுண் சிறுத்தாம்பு'],
        'deity_focus': 'Nammalvar (unique - devotion to Alvar, not Vishnu)',
        'verse_count': 11,
        'theme': 'guru bhakti',
        'relationship': 'Disciple of Nammalvar'
    }
}

# Divya Desam metadata (108 sacred Vishnu temples)
# Sample - you can expand this to all 108
DIVYA_DESAMS = {
    'திருவரங்கம்': {
        'transliteration': 'Srirangam',
        'location': 'Trichy, Tamil Nadu',
        'deity': 'Ranganatha',
        'posture': 'reclining',
        'significance': 'Most important Vishnu temple',
        'verses_count': 247,  # Most sung temple
        'region': 'Tamil Nadu'
    },
    'திருவேங்கடம்': {
        'transliteration': 'Tirupati',
        'location': 'Tirupati, Andhra Pradesh',
        'deity': 'Venkateswara',
        'posture': 'standing',
        'significance': 'Richest temple in the world',
        'verses_count': 202,
        'region': 'Andhra Pradesh'
    },
    'திருக்குருகூர்': {
        'transliteration': 'Thirukurugur (Alvar Thirunagari)',
        'location': 'Tirunelveli, Tamil Nadu',
        'deity': 'Nammalvar shrine + Nambi',
        'significance': 'Birthplace of Nammalvar',
        'verses_count': 100,
        'region': 'Tamil Nadu'
    }
    # ... Add all 108 divya desams as needed
}

# Work metadata examples for Naalayira Divya Prabandham

# Thiruppavai (திருப்பாவை்) - Most famous work
THIRUPPAVAI_METADATA = {
    'tradition': 'Vaishnavite',
    'collection_id': 322,
    'collection_name': 'Naalayira Divya Prabandham',
    'collection_name_tamil': 'நாலாயிரத் திவ்விய பிரபந்தம்',
    'file_number': 14,  # Assuming file structure
    'alvar': 'ஆண்டாள்',
    'alvar_transliteration': 'Andal',
    'alvar_gender': 'female',
    'time_period': '9th century CE',
    'place': 'ஸ்ரீவில்லிபுத்தூர்',
    'deity': 'Krishna',
    'deity_location': 'Srivilliputtur',
    'verse_count': 30,
    'month': 'Margazhi (December-January)',
    'meter': 'kali viruttam',
    'genre': 'bridal mysticism',
    'genre_tamil': 'மங்கள நோன்பு',
    'occasion': 'Pavai Nonbu (dawn prayers)',
    'themes': ['divine love', 'longing for union', 'surrender', 'communal worship'],
    'literary_devices': ['metaphor', 'nature imagery', 'dialogue'],
    'cultural_significance': 'Recited daily in temples during Margazhi month',
    'liturgical_use': True,
    'musical_tradition': True,
    'influence': 'Inspired later pavai literature',
    'language_style': 'simple, accessible Tamil',
    'emotional_tone': 'joyful longing',
    'theological_concepts': ['prapatti (surrender)', 'bhakti', 'divine grace']
}

# Thiruvoimozhi (திருவாய்மொழி்) - Nammalvar's magnum opus
THIRUVAYMOZHI_METADATA = {
    'tradition': 'Vaishnavite',
    'collection_id': 322,
    'collection_name': 'Naalayira Divya Prabandham',
    'file_number': 15,
    'alvar': 'நம்மாழ்வார்',
    'alvar_transliteration': 'Nammalvar',
    'status': 'Chief Alvar composition',
    'time_period': '9th century CE',
    'place': 'திருக்குருகூர்',
    'deity': 'Vishnu (especially Ranganatha)',
    'verse_count': 1102,
    'structure': '10 centums (100 verses each + 2)',
    'meter': 'viruttam',
    'genre': 'philosophical-devotional',
    'themes': ['divine love', 'separation', 'union', 'theology', 'cosmology'],
    'philosophical_tradition': 'Visistadvaita precursor',
    'theological_depth': 'highest',
    'liturgical_status': 'Tamil Veda',
    'alternative_name': 'Dravida Veda',
    'commentaries': ['by Ramanuja and successors'],
    'emotional_range': 'wide - from despair to ecstasy',
    'mystical_content': 'high',
    'influence': 'Foundation of Sri Vaishnava theology',
    'divya_desams_covered': 40,  # Covers many temples
    'theological_concepts': [
        'paratva (transcendence)',
        'sulabhatva (accessibility)',
        'ananya prayojana bhakti',
        'divine grace',
        'surrender'
    ]
}

# Example: Creating work with Divya Prabandham metadata
def create_divya_prabandham_work(work_name_tamil, alvar_name, verse_count):
    """Create work metadata for a Divya Prabandham text"""

    alvar_info = ALVARS.get(alvar_name)

    metadata = {
        'tradition': 'Vaishnavite',
        'collection_id': 322,
        'collection_name': 'Naalayira Divya Prabandham',
        'collection_name_tamil': 'நாலாயிரத் திவ்விய பிரபந்தம்',
        'total_verses_in_collection': 4000,
        'alvar': alvar_name,
        'alvar_transliteration': alvar_info['transliteration'],
        'alvar_period': alvar_info['period'],
        'alvar_position': alvar_info['position'],
        'alvar_place': alvar_info['place'],
        'time_period': alvar_info['period'],
        'deity_focus': 'Vishnu',
        'verse_count': verse_count,
        'liturgical_use': True,
        'musical_tradition': True,
        'performance_context': 'temple worship',
        'theological_tradition': 'Sri Vaishnavism',
        'language_style': 'devotional Tamil',
        'divya_desam_references': True,  # All works reference sacred temples
        'emotional_tone': 'bhakti (devotion)',
        'canonical_status': 'Tamil Veda equivalent'
    }

    # Add gender if female (Andal)
    if alvar_info.get('gender') == 'female':
        metadata['alvar_gender'] = 'female'
        metadata['significance'] = 'Only female Alvar'

    # Add special status for Nammalvar
    if alvar_info.get('status') == 'chief Alvar':
        metadata['alvar_status'] = 'Chief Alvar'
        metadata['philosophical_importance'] = 'Foundational'

    return metadata

# Example: Verse metadata for Divya Prabandham
def create_verse_metadata(alvar, deity, divya_desam, themes, meter='viruttam'):
    """Create verse-level metadata for Divya Prabandham verses"""

    divya_desam_info = DIVYA_DESAMS.get(divya_desam, {})

    metadata = {
        'alvar': alvar,
        'deity': deity,
        'deity_form': divya_desam_info.get('deity'),
        'deity_posture': divya_desam_info.get('posture'),
        'divya_desam': divya_desam,
        'divya_desam_location': divya_desam_info.get('location'),
        'divya_desam_region': divya_desam_info.get('region'),
        'themes': themes,
        'meter': meter,
        'liturgical_use': True,
        'theological_tradition': 'Sri Vaishnavism',
        'emotional_tone': 'devotional',
        'language': 'Tamil'
    }

    return metadata

# Example usage in bulk import:
"""
# In parse_divya_prabandham_file():
for work_section in file:
    alvar = extract_alvar_name(work_section)
    work_name = extract_work_name(work_section)
    verses = extract_verses(work_section)

    # Create work with metadata
    work_metadata = create_divya_prabandham_work(
        work_name_tamil=work_name,
        alvar_name=alvar,
        verse_count=len(verses)
    )

    work_dict = {
        'work_id': self.work_id,
        'work_name': transliterate(work_name),
        'work_name_tamil': work_name,
        'author': alvar,
        'author_tamil': alvar,
        'metadata': work_metadata  # Include rich metadata
    }
    self.works.append(work_dict)

    # For each verse, add verse metadata
    for verse in verses:
        divya_desam = extract_temple_reference(verse)
        themes = extract_themes(verse)

        verse_metadata = create_verse_metadata(
            alvar=alvar,
            deity='Vishnu',
            divya_desam=divya_desam,
            themes=themes,
            meter='viruttam'
        )

        verse_dict = {
            'verse_id': self.verse_id,
            'work_id': self.current_work_id,
            'verse_number': verse_number,
            'total_lines': len(verse.lines),
            'metadata': verse_metadata  # Include rich metadata
        }
        self.verses.append(verse_dict)
"""
