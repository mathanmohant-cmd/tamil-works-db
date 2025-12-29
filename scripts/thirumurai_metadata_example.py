#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Example: How to add metadata to Thirumurai bulk import
This shows the key changes needed to integrate JSONB metadata

Key changes from original thirumurai_bulk_import.py:
1. Import json module
2. Add metadata field when creating work/section/verse dictionaries
3. Update bulk_insert methods to include metadata column in COPY
"""

import json  # NEW: Import json module for serialization

# Saint metadata (for Devaram works in Files 1-7)
DEVARAM_SAINTS = {
    1: {
        'saint': 'திருஞானசம்பந்தர்',
        'transliteration': 'Thirugnanasambandar',
        'period': '7th century CE',
        'pathigam_count': 384,
        'place': 'சீர்காழி'
    },
    2: {
        'saint': 'திருநாவுக்கரசர்',
        'transliteration': 'Thirunavukkarasar (Appar)',
        'period': '7th century CE',
        'pathigam_count': 311,
        'place': 'திருவாமூர்'
    },
    3: {
        'saint': 'சுந்தரர்',
        'transliteration': 'Sundarar',
        'period': '8th century CE',
        'pathigam_count': 100,
        'place': 'திருநாவலூர்'
    }
}

# Example: Creating a work with metadata
def create_work_with_metadata(self, file_number, work_name, work_name_tamil, author, author_tamil):
    """Create work dictionary with rich metadata"""

    # Get saint info for Devaram works
    saint_info = DEVARAM_SAINTS.get(file_number)

    # Build metadata dictionary
    metadata = {
        'tradition': 'Shaivite',
        'collection_id': 321,
        'collection_name': 'Thirumurai',
        'collection_name_tamil': 'திருமுறை',
        'file_number': file_number,
        'musical_tradition': True,
        'performance_context': 'temple worship',
        'deity_focus': 'Shiva',
        'liturgical_use': True,
        'language_style': 'devotional',
        'verse_form': 'pathigam'  # Groups of 10-11 verses
    }

    # Add saint-specific metadata for Devaram works
    if saint_info:
        metadata.update({
            'sub_collection': 'Devaram',
            'sub_collection_tamil': 'தேவாரம்',
            'saint': saint_info['saint'],
            'saint_transliteration': saint_info['transliteration'],
            'time_period': saint_info['period'],
            'pathigam_count': saint_info['pathigam_count'],
            'birthplace': saint_info['place']
        })

    work_dict = {
        'work_id': self.work_id,
        'work_name': work_name,
        'work_name_tamil': work_name_tamil,
        'author': author,
        'author_tamil': author_tamil,
        'description': f"{work_name_tamil} from Thirumurai Collection",
        'metadata': metadata  # NEW: Add metadata field
    }

    self.works.append(work_dict)
    print(f"    Created work: {work_name_tamil} (ID: {self.work_id}) with metadata")
    self.work_id += 1

# Example: Creating a section (pathigam) with metadata
def create_section_with_metadata(self, section_name, section_name_tamil, pann=None, temple=None, location=None):
    """Create section (pathigam) with metadata"""

    # Build section metadata
    metadata = {
        'section_type': 'pathigam',
        'section_type_tamil': 'பதிகம்'
    }

    # Add musical mode (pann) if known
    if pann:
        metadata['pann'] = pann  # e.g., 'குறிஞ்சி'
        metadata['musical_mode'] = True

    # Add temple/location if known
    if temple:
        metadata['temple'] = temple  # e.g., 'காபாலீச்சுவரம்'
        metadata['temple_location'] = location  # e.g., 'Mylapore, Chennai'
        metadata['deity_location'] = f"Shiva at {temple}"

    section_dict = {
        'section_id': self.section_id,
        'work_id': self.current_work_id,
        'parent_section_id': None,
        'level_type': 'Pathigam',
        'level_type_tamil': 'பதிகம்',
        'section_number': self.pathigam_number,
        'section_name': section_name,
        'section_name_tamil': section_name_tamil,
        'sort_order': self.pathigam_number,
        'metadata': metadata  # NEW: Add metadata field
    }

    self.sections.append(section_dict)
    self.section_id += 1

# Example: Creating a verse with metadata
def create_verse_with_metadata(self, verse_number, total_lines, raga=None, talam=None, themes=None):
    """Create verse with metadata"""

    # Build verse metadata
    metadata = {
        'meter': 'venba',  # Common meter in Devaram
        'line_count': total_lines,
        'saint': self.current_saint,  # Track from work metadata
        'deity': 'Shiva'
    }

    # Add musical metadata if known
    if raga:
        metadata['raga'] = raga  # e.g., 'பைரவி'
    if talam:
        metadata['talam'] = talam  # e.g., 'ஆதி'

    # Add thematic tags if known
    if themes:
        metadata['themes'] = themes  # e.g., ['divine grace', 'devotion', 'surrender']

    # Add common devotional metadata
    metadata.update({
        'liturgical_use': True,
        'performance_context': 'temple worship',
        'theological_tradition': 'Shaiva Siddhanta'
    })

    verse_dict = {
        'verse_id': self.verse_id,
        'work_id': self.current_work_id,
        'section_id': self.current_section_id,
        'verse_number': verse_number,
        'verse_type': 'Devotional Hymn',
        'verse_type_tamil': 'பக்தி பாடல்',
        'total_lines': total_lines,
        'sort_order': self.verse_sort_order,
        'metadata': metadata  # NEW: Add metadata field
    }

    self.verses.append(verse_dict)
    self.verse_id += 1

# Example: Updated bulk_insert_works with metadata
def bulk_insert_works(self):
    """Bulk insert works with metadata using PostgreSQL COPY"""
    if not self.works:
        return

    import csv
    import io

    buffer = io.StringIO()
    writer = csv.writer(buffer, delimiter='\t', quoting=csv.QUOTE_MINIMAL, escapechar='\\')

    for work in self.works:
        # NEW: Serialize metadata to JSON string
        metadata_json = json.dumps(work.get('metadata', {}), ensure_ascii=False) if work.get('metadata') else None

        writer.writerow([
            work['work_id'],
            work['work_name'],
            work['work_name_tamil'],
            work.get('period', ''),
            work.get('author', ''),
            work.get('author_tamil', ''),
            work.get('description', ''),
            work.get('chronology_start_year', ''),
            work.get('chronology_end_year', ''),
            work.get('chronology_confidence', ''),
            work.get('chronology_notes', ''),
            work.get('canonical_order', ''),
            work.get('primary_collection_id', ''),
            metadata_json  # NEW: Include metadata column
        ])

    buffer.seek(0)

    # NEW: Include 'metadata' in columns list
    self.cursor.copy_from(
        buffer,
        'works',
        columns=('work_id', 'work_name', 'work_name_tamil', 'period', 'author',
                'author_tamil', 'description', 'chronology_start_year',
                'chronology_end_year', 'chronology_confidence', 'chronology_notes',
                'canonical_order', 'primary_collection_id', 'metadata'),
        null=''
    )

    print(f"  [OK] Bulk inserted {len(self.works)} works with metadata")

# Example: Updated bulk_insert_sections with metadata
def bulk_insert_sections(self):
    """Bulk insert sections with metadata using PostgreSQL COPY"""
    if not self.sections:
        return

    import csv
    import io

    buffer = io.StringIO()
    writer = csv.writer(buffer, delimiter='\t', quoting=csv.QUOTE_MINIMAL, escapechar='\\')

    for section in self.sections:
        # NEW: Serialize metadata to JSON string
        metadata_json = json.dumps(section.get('metadata', {}), ensure_ascii=False) if section.get('metadata') else None

        writer.writerow([
            section['section_id'],
            section['work_id'],
            section.get('parent_section_id', ''),
            section.get('level_type', ''),
            section.get('level_type_tamil', ''),
            section.get('section_number', ''),
            section.get('section_name', ''),
            section.get('section_name_tamil', ''),
            section['sort_order'],
            metadata_json  # NEW: Include metadata column
        ])

    buffer.seek(0)

    # NEW: Include 'metadata' in columns list
    self.cursor.copy_from(
        buffer,
        'sections',
        columns=('section_id', 'work_id', 'parent_section_id', 'level_type',
                'level_type_tamil', 'section_number', 'section_name',
                'section_name_tamil', 'sort_order', 'metadata'),
        null=''
    )

    print(f"  [OK] Bulk inserted {len(self.sections)} sections with metadata")

# Example: Updated bulk_insert_verses with metadata
def bulk_insert_verses(self):
    """Bulk insert verses with metadata using PostgreSQL COPY"""
    if not self.verses:
        return

    import csv
    import io

    buffer = io.StringIO()
    writer = csv.writer(buffer, delimiter='\t', quoting=csv.QUOTE_MINIMAL, escapechar='\\')

    for verse in self.verses:
        # NEW: Serialize metadata to JSON string
        metadata_json = json.dumps(verse.get('metadata', {}), ensure_ascii=False) if verse.get('metadata') else None

        writer.writerow([
            verse['verse_id'],
            verse['work_id'],
            verse.get('section_id', ''),
            verse['verse_number'],
            verse.get('verse_type', ''),
            verse.get('verse_type_tamil', ''),
            verse['total_lines'],
            verse['sort_order'],
            metadata_json  # NEW: Include metadata column
        ])

    buffer.seek(0)

    # NEW: Include 'metadata' in columns list
    self.cursor.copy_from(
        buffer,
        'verses',
        columns=('verse_id', 'work_id', 'section_id', 'verse_number',
                'verse_type', 'verse_type_tamil', 'total_lines', 'sort_order',
                'metadata'),
        null=''
    )

    print(f"  [OK] Bulk inserted {len(self.verses)} verses with metadata")


# Example metadata for specific Thirumurai works:

# File 8.1: Thiruvasagam (திருவாசகம்)
THIRUVASAGAM_METADATA = {
    'tradition': 'Shaivite',
    'collection_id': 321,
    'collection_name': 'Thirumurai',
    'file_number': 8,
    'sub_collection': 'Thiruvasagam',
    'saint': 'மாணிக்கவாசகர்',
    'saint_transliteration': 'Manikkavasagar',
    'time_period': '9th century CE',
    'place': 'திருவாதவூர்',
    'deity_focus': 'Shiva (as Nataraja)',
    'musical_tradition': True,
    'liturgical_use': True,
    'philosophical_depth': 'high',
    'emotional_intensity': 'high',
    'themes': ['divine love', 'longing', 'mystical union', 'surrender'],
    'notable_sections': ['திருவெம்பாவை்', 'திருப்பள்ளியெழுச்சி்']
}

# File 10: Thirumanthiram (திருமந்திரம்)
THIRUMANTHIRAM_METADATA = {
    'tradition': 'Shaivite',
    'collection_id': 321,
    'collection_name': 'Thirumurai',
    'file_number': 10,
    'sub_collection': 'Thirumanthiram',
    'saint': 'திருமூலர்',
    'saint_transliteration': 'Thirumoolar',
    'time_period': '2nd-6th century CE (disputed)',
    'verse_count': 3000,
    'verse_type': 'tantra',
    'deity_focus': 'Shiva',
    'philosophical_tradition': 'Shaiva Siddhanta',
    'genre': 'philosophical-devotional',
    'topics': ['yoga', 'tantra', 'philosophy', 'ethics', 'cosmology'],
    'structure': '9 tantras, each with chapters',
    'meter': 'venba',
    'musical_tradition': False,  # More philosophical than musical
    'influence': 'foundational text for Tamil Shaiva philosophy'
}

# File 12: Periya Puranam (பெரியபுராணம்)
PERIYA_PURANAM_METADATA = {
    'tradition': 'Shaivite',
    'collection_id': 321,
    'collection_name': 'Thirumurai',
    'file_number': 12,
    'sub_collection': 'Periya Puranam',
    'saint': 'சேக்கிழார்',
    'saint_transliteration': 'Sekkizhar',
    'time_period': '12th century CE',
    'genre': 'hagiography',
    'genre_tamil': 'வரலாற்றுக் காப்பியம்',
    'subject': 'Lives of 63 Nayanmars',
    'verse_count': 4286,
    'structure': '13 chapters (திருமுறைகள்)',
    'meter': 'viruttam',
    'deity_focus': 'Shiva (through devotees)',
    'narrative_type': 'biographical anthology',
    'musical_tradition': False,
    'literary_significance': 'Defines Tamil Shaiva identity',
    'cultural_impact': 'high'
}
