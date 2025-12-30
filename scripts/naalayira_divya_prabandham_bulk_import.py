#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Naalayira Divya Prabandham Bulk Import Script
==============================================
Imports Naalayira Divya Prabandham (நாலாயிரத் திவ்விய பிரபந்தம்)
24 Vaishnavite works by 12 Alvars (~4000 verses)

Collection: Naalayira Divya Prabandham - Collection ID 322

Structure:
    File 13: முதல் ஆயிரம் (First Thousand) - 10 works
    File 14: இரண்டாம் ஆயிரம் (Second Thousand) - 3 works
    File 15: மூன்றாம் ஆயிரம் (Third Thousand) - 11 works
    File 16: நான்காம் ஆயிரம் (Fourth Thousand) - 1 work (Thiruvaimozhi)

File Format:
    1. Collection_name (first line)
    @Alvar_name ^ Work_name
    #verse_number
    lines...
    மேல் (end of work)

Uses 2-phase bulk COPY pattern for optimal performance.
"""

import os
import sys
import re
import json
import io
import psycopg2
from typing import List, Dict, Optional

class NaalayiraDivyaPrabandhamImporter:
    def __init__(self, db_connection_string: str):
        """Initialize the Naalayira Divya Prabandham bulk importer"""
        self.db_connection_string = db_connection_string
        self.conn = None
        self.cursor = None

        # Data containers
        self.works = []
        self.sections = []
        self.verses = []
        self.lines = []
        self.words = []

        # ID counters - CRITICAL: Query MAX IDs from database
        self.work_id = 1
        self.section_id = 1
        self.verse_id = 1
        self.line_id = 1
        self.word_id = 1

        # Current state tracking
        self.current_work_id = None
        self.current_section_id = None
        self.current_verse_id = None
        self.section_sort_order = 0
        self.verse_sort_order = 0

        # File mappings
        self.file_mappings = [
            {
                'file': '13.நாலாயிரத் திவ்விய பிரபந்தம்-முதல் ஆயிரம்.txt',
                'collection_name': 'முதல் ஆயிரம்',
                'collection_name_english': 'First Thousand',
                'sub_collection_id': 3221,
                'position_start': 1
            },
            {
                'file': '14.நாலாயிரத் திவ்விய பிரபந்தம்-இரண்டாம் ஆயிரம்.txt',
                'collection_name': 'இரண்டாம் ஆயிரம்',
                'collection_name_english': 'Second Thousand',
                'sub_collection_id': 3222,
                'position_start': 11
            },
            {
                'file': '15.நாலாயிரத் திவ்விய பிரபந்தம்-மூன்றாம் ஆயிரம்.txt',
                'collection_name': 'மூன்றாம் ஆயிரம்',
                'collection_name_english': 'Third Thousand',
                'sub_collection_id': 3223,
                'position_start': 14
            },
            {
                'file': '16.நாலாயிரத் திவ்விய பிரபந்தம்-நான்காம் ஆயிரம்.txt',
                'collection_name': 'நான்காம் ஆயிரம்',
                'collection_name_english': 'Fourth Thousand',
                'sub_collection_id': 3224,
                'position_start': 25
            }
        ]

        # Alvar metadata (for enriching work metadata)
        self.alvars = {
            'பெரியாழ்வார்': {
                'transliteration': 'Periyalvar',
                'period': '9th century CE',
                'place': 'ஸ்ரீவில்லிபுத்தூர்'
            },
            'ஆண்டாள்': {
                'transliteration': 'Andal',
                'period': '9th century CE',
                'place': 'ஸ்ரீவில்லிபுத்தூர்',
                'gender': 'female',
                'significance': 'Only female Alvar'
            },
            'குலசேகர ஆழ்வார்': {
                'transliteration': 'Kulasekara Alvar',
                'period': '9th century CE',
                'place': 'திருவஞ்சிக்களம்'
            },
            'குலசேகரன்': {
                'transliteration': 'Kulasekara Alvar',
                'period': '9th century CE',
                'place': 'திருவஞ்சிக்களம்'
            },
            'திருமழிசை ஆழ்வார்': {
                'transliteration': 'Thirumalisai Alvar',
                'period': '7th century CE',
                'place': 'திருமழிசை'
            },
            'தொண்டரடிப்பொடி ஆழ்வார்': {
                'transliteration': 'Thondaradippodi Alvar',
                'period': '9th century CE',
                'place': 'திருமண்டங்குடி'
            },
            'திருப்பாணாழ்வார்': {
                'transliteration': 'Thiruppan Alvar',
                'period': '9th century CE',
                'place': 'உறையூர்'
            },
            'மதுரகவி ஆழ்வார்': {
                'transliteration': 'Madhurakavi Alvar',
                'period': '9th century CE',
                'place': 'திருக்குருகூர்'
            },
            'திருமங்கை ஆழ்வார்': {
                'transliteration': 'Thirumangai Alvar',
                'period': '9th century CE',
                'place': 'திருக்குறையலூர்'
            },
            'பொய்கை ஆழ்வார்': {
                'transliteration': 'Poigai Alvar',
                'period': '7th century CE',
                'place': 'காஞ்சிபுரம்'
            },
            'பூதத்தாழ்வார்': {
                'transliteration': 'Bhoothathalvar',
                'period': '7th century CE',
                'place': 'மகாபலிபுரம்'
            },
            'பேயாழ்வார்': {
                'transliteration': 'Pey Alvar',
                'period': '7th century CE',
                'place': 'மயிலாப்பூர்'
            },
            'நம்மாழ்வார்': {
                'transliteration': 'Nammalvar',
                'period': '9th century CE',
                'place': 'திருக்குருகூர்',
                'status': 'Chief Alvar'
            },
            'திருவரங்கத்து அமுதனார்': {
                'transliteration': 'Thiruvrangatthu Amudhanar',
                'period': '12th century CE',
                'place': 'திருவரங்கம்',
                'note': 'Disciple of Ramanuja'
            }
        }

    def connect(self):
        """Connect to the database and get MAX IDs"""
        print("Connecting to database...")
        self.conn = psycopg2.connect(self.db_connection_string)
        self.cursor = self.conn.cursor()

        # Ensure collections exist
        self.ensure_collections_exist()

        # CRITICAL: Get MAX IDs from database
        self.cursor.execute("SELECT COALESCE(MAX(work_id), 0) + 1 FROM works")
        self.work_id = self.cursor.fetchone()[0]

        self.cursor.execute("SELECT COALESCE(MAX(section_id), 0) + 1 FROM sections")
        self.section_id = self.cursor.fetchone()[0]

        self.cursor.execute("SELECT COALESCE(MAX(verse_id), 0) + 1 FROM verses")
        self.verse_id = self.cursor.fetchone()[0]

        self.cursor.execute("SELECT COALESCE(MAX(line_id), 0) + 1 FROM lines")
        self.line_id = self.cursor.fetchone()[0]

        self.cursor.execute("SELECT COALESCE(MAX(word_id), 0) + 1 FROM words")
        self.word_id = self.cursor.fetchone()[0]

        print(f"  Starting IDs: work={self.work_id}, section={self.section_id}, verse={self.verse_id}, line={self.line_id}, word={self.word_id}")

    def ensure_collections_exist(self):
        """Ensure the Naalayira Divya Prabandham collection and sub-collections exist"""
        # Main collection 322
        self.cursor.execute("SELECT collection_id FROM collections WHERE collection_id = 322")
        result = self.cursor.fetchone()

        if not result:
            print("  Creating Naalayira Divya Prabandham collection (322)...")
            self.cursor.execute("""
                INSERT INTO collections (collection_id, collection_name, collection_name_tamil,
                                       collection_type, description, sort_order)
                VALUES (322, 'Naalayira Divya Prabandham', 'நாலாயிரத் திவ்விய பிரபந்தம்', 'devotional',
                        'Naalayira Divya Prabandham - 4000 verses by 12 Alvars', 322)
            """)
            self.conn.commit()
            print("  [OK] Naalayira Divya Prabandham collection created")
        else:
            print("  [OK] Naalayira Divya Prabandham collection already exists")

        # Sub-collections (3221-3224)
        sub_collections = [
            (3221, 'First Thousand', 'முதல் ஆயிரம்', 322, 1),
            (3222, 'Second Thousand', 'இரண்டாம் ஆயிரம்', 322, 2),
            (3223, 'Third Thousand', 'மூன்றாம் ஆயிரம்', 322, 3),
            (3224, 'Fourth Thousand', 'நான்காம் ஆயிரம்', 322, 4)
        ]

        for coll_id, name, name_tamil, parent_id, sort_order in sub_collections:
            self.cursor.execute("SELECT collection_id FROM collections WHERE collection_id = %s", (coll_id,))
            if not self.cursor.fetchone():
                print(f"  Creating sub-collection: {name_tamil} ({coll_id})...")
                self.cursor.execute("""
                    INSERT INTO collections (collection_id, collection_name, collection_name_tamil,
                                           collection_type, parent_collection_id, sort_order)
                    VALUES (%s, %s, %s, 'devotional', %s, %s)
                """, (coll_id, name, name_tamil, parent_id, sort_order))

        self.conn.commit()

        # Query and store collection IDs as instance variables
        self.cursor.execute("SELECT collection_id FROM collections WHERE collection_id = 322")
        self.main_collection_id = self.cursor.fetchone()[0]

        self.cursor.execute("SELECT collection_id FROM collections WHERE collection_id = 3221")
        self.first_thousand_collection_id = self.cursor.fetchone()[0]

        self.cursor.execute("SELECT collection_id FROM collections WHERE collection_id = 3222")
        self.second_thousand_collection_id = self.cursor.fetchone()[0]

        self.cursor.execute("SELECT collection_id FROM collections WHERE collection_id = 3223")
        self.third_thousand_collection_id = self.cursor.fetchone()[0]

        self.cursor.execute("SELECT collection_id FROM collections WHERE collection_id = 3224")
        self.fourth_thousand_collection_id = self.cursor.fetchone()[0]

    def _get_or_create_section_id(self, work_id):
        """
        Get or create a default root section for a work (for works without explicit hierarchy)
        Follows Sangam parser pattern to ensure all verses have a section_id
        """
        section_id = self.section_id
        self.section_id += 1

        self.sections.append({
            'section_id': section_id,
            'work_id': work_id,
            'parent_section_id': None,
            'level_type': 'Chapter',
            'level_type_tamil': 'பகுதி',
            'section_number': 1,
            'section_name': None,  # NULL name to avoid redundant display
            'section_name_tamil': None,
            'sort_order': 1,
            'metadata': {}
        })

        return section_id

    def parse_all_files(self, base_dir: str):
        """Parse all 4 Naalayira Divya Prabandham files"""
        print("\n=== PHASE 1: Parsing Naalayira Divya Prabandham files into memory ===")

        position_in_main_collection = 1  # Global position across all 24 works

        for file_info in self.file_mappings:
            file_path = os.path.join(base_dir, file_info['file'])
            if not os.path.exists(file_path):
                print(f"  [SKIP] File not found: {file_path}")
                continue

            print(f"\n  Processing: {file_info['collection_name']}")
            position_in_main_collection = self.parse_file(file_path, file_info, position_in_main_collection)

        print(f"\n  [OK] Parsed {len(self.works)} works, {len(self.sections)} sections, {len(self.verses)} verses")
        print(f"       {len(self.lines)} lines, {len(self.words)} words")

    def parse_file(self, file_path: str, file_info: Dict, position_in_main_collection: int) -> int:
        """Parse a single Naalayira Divya Prabandham file"""
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        current_alvar = None
        current_work_name = None
        current_verse_lines = []
        verse_number = 0
        in_verse = False
        position_in_sub_collection = 1

        for line in lines:
            line = line.strip()

            # Skip empty lines
            if not line:
                continue

            # Skip first line (collection name marker like "1. முதலாம் ஆயிரம்")
            if re.match(r'^\d+\.\s*\S+\s+ஆயிரம்', line):
                continue

            # Work marker: @Alvar ^ Work_name
            work_match = re.match(r'^@(.+?)\s*\^\s*(.+)', line)
            if work_match:
                # Save previous work's last verse if any
                if current_verse_lines:
                    self.create_verse(current_verse_lines, verse_number)
                    current_verse_lines = []

                current_alvar = work_match.group(1).strip()
                current_work_name = work_match.group(2).strip()

                # Create work
                alvar_info = self.alvars.get(current_alvar, {})

                # Get sub-collection ID dynamically
                sub_coll_id_map = {
                    'முதல் ஆயிரம்': self.first_thousand_collection_id,
                    'இரண்டாம் ஆயிரம்': self.second_thousand_collection_id,
                    'மூன்றாம் ஆயிரம்': self.third_thousand_collection_id,
                    'நான்காம் ஆயிரம்': self.fourth_thousand_collection_id
                }
                sub_collection_id = sub_coll_id_map.get(file_info['collection_name'], file_info['sub_collection_id'])

                work_metadata = {
                    'tradition': 'Vaishnavite',
                    'collection_id': self.main_collection_id,
                    'collection_name': 'Naalayira Divya Prabandham',
                    'collection_name_tamil': 'நாலாயிரத் திவ்விய பிரபந்தம்',
                    'sub_collection': file_info['collection_name'],
                    'sub_collection_id': sub_collection_id,
                    'alvar': current_alvar,
                    'alvar_transliteration': alvar_info.get('transliteration', ''),
                    'time_period': alvar_info.get('period', ''),
                    'place': alvar_info.get('place', ''),
                    'deity_focus': 'Vishnu',
                    'musical_tradition': True,
                    'performance_context': 'temple worship',
                    'liturgical_use': True,
                    'theological_tradition': 'Sri Vaishnavism'
                }

                # Add special metadata for Andal
                if alvar_info.get('gender') == 'female':
                    work_metadata['alvar_gender'] = 'female'
                    work_metadata['significance'] = alvar_info.get('significance', '')

                # Add special metadata for Nammalvar
                if alvar_info.get('status'):
                    work_metadata['alvar_status'] = alvar_info['status']

                work_dict = {
                    'work_id': self.work_id,
                    'work_name': current_work_name,
                    'work_name_tamil': current_work_name,
                    'period': alvar_info.get('period', '7th-12th century CE'),
                    'author': alvar_info.get('transliteration', current_alvar),
                    'author_tamil': current_alvar,
                    'description': f"{current_work_name} by {current_alvar} - Part of {file_info['collection_name']}",
                    'canonical_order': 400 + position_in_main_collection,  # 401-424
                    'metadata': work_metadata,
                    'position_in_main_collection': position_in_main_collection,
                    'position_in_sub_collection': position_in_sub_collection,
                    'sub_collection_id': sub_collection_id  # Store for work_collections linking
                }
                self.works.append(work_dict)
                self.current_work_id = self.work_id
                print(f"    Work {position_in_main_collection}: {current_work_name} ({current_alvar})")
                self.work_id += 1

                # Create a default section for this work
                self.current_section_id = self._get_or_create_section_id(self.current_work_id)

                # Reset verse tracking
                verse_number = 0
                position_in_main_collection += 1
                position_in_sub_collection += 1
                continue

            # End of work marker
            if line == 'மேல்':
                if current_verse_lines:
                    self.create_verse(current_verse_lines, verse_number)
                    current_verse_lines = []
                in_verse = False
                continue

            # Verse marker: #number
            verse_match = re.match(r'^#(\d+)', line)
            if verse_match:
                # Save previous verse if any
                if current_verse_lines:
                    self.create_verse(current_verse_lines, verse_number)
                    current_verse_lines = []

                verse_number = int(verse_match.group(1))
                in_verse = True
                continue

            # Verse content lines
            if in_verse:
                current_verse_lines.append(line)

        # Handle last verse
        if current_verse_lines:
            self.create_verse(current_verse_lines, verse_number)

        return position_in_main_collection

    def create_verse(self, verse_lines: List[str], verse_number: int):
        """Create a verse with its lines and words"""
        self.verse_sort_order += 1

        # Verse metadata
        current_work = self.works[-1]
        verse_metadata = {
            'alvar': current_work['author_tamil'],
            'deity': 'Vishnu',
            'meter': 'viruttam',
            'line_count': len(verse_lines),
            'liturgical_use': True,
            'theological_tradition': 'Sri Vaishnavism'
        }

        verse_dict = {
            'verse_id': self.verse_id,
            'work_id': self.current_work_id,
            'section_id': self.current_section_id,
            'verse_number': verse_number,
            'verse_type': 'Pasuram',
            'verse_type_tamil': 'பாசுரம்',
            'total_lines': len(verse_lines),
            'sort_order': self.verse_sort_order,
            'metadata': verse_metadata
        }
        self.verses.append(verse_dict)
        self.current_verse_id = self.verse_id
        self.verse_id += 1

        # Create lines and words
        for line_num, line_text in enumerate(verse_lines, 1):
            self.create_line_and_words(line_text, line_num)

    def create_line_and_words(self, line_text: str, line_number: int):
        """Create a line and segment it into words"""
        # Create line
        line_dict = {
            'line_id': self.line_id,
            'verse_id': self.current_verse_id,
            'line_number': line_number,
            'line_text': line_text
        }
        self.lines.append(line_dict)
        current_line_id = self.line_id
        self.line_id += 1

        # Segment into words
        words = self.segment_line(line_text)
        for word_position, word_text in enumerate(words, 1):
            word_dict = {
                'word_id': self.word_id,
                'line_id': current_line_id,
                'word_position': word_position,
                'word_text': word_text,
                'sandhi_split': None  # TODO: Implement sandhi analysis
            }
            self.words.append(word_dict)
            self.word_id += 1

    def segment_line(self, line_text: str) -> List[str]:
        """
        Segment a line into words following Tamil grammar rules.
        Uses basic space-based segmentation with underscore handling.
        """
        # Replace underscores with spaces (compound word markers)
        line_text = line_text.replace('_', ' ')

        # Split by whitespace
        words = line_text.split()

        # Remove empty strings
        words = [w for w in words if w.strip()]

        return words

    def bulk_insert_works(self):
        """Bulk insert works using PostgreSQL COPY"""
        if not self.works:
            return

        buffer = io.StringIO()

        for work in self.works:
            metadata_json = json.dumps(work.get('metadata', {}), ensure_ascii=False) if work.get('metadata') else ''

            # Manually construct TSV line to avoid CSV escaping issues with JSON
            fields = [
                str(work['work_id']),
                work['work_name'],
                work['work_name_tamil'],
                work.get('period', ''),
                work.get('author', ''),
                work.get('author_tamil', ''),
                work.get('description', ''),
                str(work['chronology_start_year']) if work.get('chronology_start_year') is not None else '',
                str(work['chronology_end_year']) if work.get('chronology_end_year') is not None else '',
                work.get('chronology_confidence', ''),
                work.get('chronology_notes', ''),
                str(work['canonical_order']) if work.get('canonical_order') is not None else '',
                metadata_json
            ]

            # Replace any literal tabs or newlines in fields (except JSON which is last)
            cleaned_fields = []
            for i, field in enumerate(fields):
                if field is None:
                    cleaned_fields.append('')
                else:
                    # For non-JSON fields, escape tabs and newlines
                    if i < len(fields) - 1:
                        field = str(field).replace('\t', ' ').replace('\n', ' ').replace('\r', '')
                    cleaned_fields.append(field)

            buffer.write('\t'.join(cleaned_fields) + '\n')

        buffer.seek(0)

        self.cursor.copy_from(
            buffer,
            'works',
            columns=('work_id', 'work_name', 'work_name_tamil', 'period', 'author',
                    'author_tamil', 'description', 'chronology_start_year',
                    'chronology_end_year', 'chronology_confidence', 'chronology_notes',
                    'canonical_order', 'metadata'),
            null=''
        )

        print(f"  [OK] Bulk inserted {len(self.works)} works")

    def bulk_insert_work_collections(self):
        """Link all works to their sub-collections and main collection"""
        if not self.works:
            return

        print(f"  Linking {len(self.works)} works to collections...")

        # Get next available position in main collection
        self.cursor.execute("""
            SELECT COALESCE(MAX(position_in_collection), 0) + 1
            FROM work_collections
            WHERE collection_id = %s
        """, (self.main_collection_id,))
        next_position = self.cursor.fetchone()[0]

        buffer = io.StringIO()
        for work in self.works:
            # Get the sub-collection ID from work metadata
            sub_collection_id = work.get('sub_collection_id')

            # Link to sub-collection (primary)
            fields = [
                str(work['work_id']),
                str(sub_collection_id),  # collection_id
                str(work['position_in_sub_collection']),  # position_in_collection
                't',  # is_primary (true)
                ''  # notes (NULL)
            ]
            buffer.write('\t'.join(fields) + '\n')

            # Link to main collection (dynamic)
            fields = [
                str(work['work_id']),
                str(self.main_collection_id),  # collection_id (dynamic)
                str(next_position),     # position_in_collection (dynamic)
                'f',  # is_primary (false - sub-collection is primary)
                ''  # notes (NULL)
            ]
            buffer.write('\t'.join(fields) + '\n')
            next_position += 1  # Increment for each work in loop

        buffer.seek(0)
        self.cursor.copy_from(
            buffer, 'work_collections',
            columns=['work_id', 'collection_id', 'position_in_collection', 'is_primary', 'notes'],
            null=''
        )
        print(f"    ✓ Linked {len(self.works)} works to collections")

    def bulk_insert_sections(self):
        """Bulk insert sections using PostgreSQL COPY"""
        if not self.sections:
            return

        buffer = io.StringIO()

        for section in self.sections:
            metadata_json = json.dumps(section.get('metadata', {}), ensure_ascii=False) if section.get('metadata') else ''

            fields = [
                str(section['section_id']),
                str(section['work_id']),
                str(section['parent_section_id']) if section.get('parent_section_id') is not None else '',
                section.get('level_type', ''),
                section.get('level_type_tamil', ''),
                str(section['section_number']) if section.get('section_number') is not None else '',
                section.get('section_name', ''),
                section.get('section_name_tamil', ''),
                str(section['sort_order']),
                metadata_json
            ]

            # Clean fields (escape tabs/newlines except in JSON)
            cleaned_fields = []
            for i, field in enumerate(fields):
                if field is None:
                    cleaned_fields.append('')
                else:
                    if i < len(fields) - 1:
                        field = str(field).replace('\t', ' ').replace('\n', ' ').replace('\r', '')
                    cleaned_fields.append(field)

            buffer.write('\t'.join(cleaned_fields) + '\n')

        buffer.seek(0)

        self.cursor.copy_from(
            buffer,
            'sections',
            columns=('section_id', 'work_id', 'parent_section_id', 'level_type',
                    'level_type_tamil', 'section_number', 'section_name',
                    'section_name_tamil', 'sort_order', 'metadata'),
            null=''
        )

        print(f"  [OK] Bulk inserted {len(self.sections)} sections")

    def bulk_insert_verses(self):
        """Bulk insert verses using PostgreSQL COPY"""
        if not self.verses:
            return

        buffer = io.StringIO()

        for verse in self.verses:
            metadata_json = json.dumps(verse.get('metadata', {}), ensure_ascii=False) if verse.get('metadata') else ''

            fields = [
                str(verse['verse_id']),
                str(verse['work_id']),
                str(verse['section_id']) if verse.get('section_id') is not None else '',
                str(verse['verse_number']),
                verse.get('verse_type', ''),
                verse.get('verse_type_tamil', ''),
                str(verse['total_lines']),
                str(verse['sort_order']),
                metadata_json
            ]

            # Clean fields
            cleaned_fields = []
            for i, field in enumerate(fields):
                if field is None:
                    cleaned_fields.append('')
                else:
                    if i < len(fields) - 1:
                        field = str(field).replace('\t', ' ').replace('\n', ' ').replace('\r', '')
                    cleaned_fields.append(field)

            buffer.write('\t'.join(cleaned_fields) + '\n')

        buffer.seek(0)

        self.cursor.copy_from(
            buffer,
            'verses',
            columns=('verse_id', 'work_id', 'section_id', 'verse_number',
                    'verse_type', 'verse_type_tamil', 'total_lines', 'sort_order',
                    'metadata'),
            null=''
        )

        print(f"  [OK] Bulk inserted {len(self.verses)} verses")

    def bulk_insert_lines(self):
        """Bulk insert lines using PostgreSQL COPY"""
        if not self.lines:
            return

        buffer = io.StringIO()

        for line in self.lines:
            fields = [
                str(line['line_id']),
                str(line['verse_id']),
                str(line['line_number']),
                line['line_text']
            ]

            # Clean fields - escape tabs and newlines in line_text
            cleaned_fields = []
            for i, field in enumerate(fields):
                if field is None:
                    cleaned_fields.append('')
                else:
                    # For line_text (last field), escape tabs and newlines but preserve all other characters
                    if i == len(fields) - 1:
                        field = str(field).replace('\t', ' ').replace('\n', ' ').replace('\r', '')
                    cleaned_fields.append(field)

            buffer.write('\t'.join(cleaned_fields) + '\n')

        buffer.seek(0)

        self.cursor.copy_from(
            buffer,
            'lines',
            columns=('line_id', 'verse_id', 'line_number', 'line_text'),
            null=''
        )

        print(f"  [OK] Bulk inserted {len(self.lines)} lines")

    def bulk_insert_words(self):
        """Bulk insert words using PostgreSQL COPY"""
        if not self.words:
            return

        buffer = io.StringIO()

        for word in self.words:
            fields = [
                str(word['word_id']),
                str(word['line_id']),
                str(word['word_position']),
                word['word_text'],
                word.get('sandhi_split', '') or ''
            ]

            # Clean fields - escape tabs and newlines
            cleaned_fields = []
            for i, field in enumerate(fields):
                if field is None:
                    cleaned_fields.append('')
                else:
                    # For text fields (word_text and sandhi_split), escape tabs and newlines
                    if i >= 3:
                        field = str(field).replace('\t', ' ').replace('\n', ' ').replace('\r', '')
                    cleaned_fields.append(field)

            buffer.write('\t'.join(cleaned_fields) + '\n')

        buffer.seek(0)

        self.cursor.copy_from(
            buffer,
            'words',
            columns=('word_id', 'line_id', 'word_position', 'word_text', 'sandhi_split'),
            null=''
        )

        print(f"  [OK] Bulk inserted {len(self.words)} words")

    def import_data(self):
        """Execute bulk imports in correct order"""
        print("\n=== PHASE 2: Bulk inserting into database ===")

        try:
            self.bulk_insert_works()
            self.bulk_insert_work_collections()
            self.bulk_insert_sections()
            self.bulk_insert_verses()
            self.bulk_insert_lines()
            self.bulk_insert_words()

            self.conn.commit()
            print("\n[SUCCESS] All Naalayira Divya Prabandham data imported successfully!")

        except Exception as e:
            self.conn.rollback()
            print(f"\n[ERROR] Import failed: {e}")
            raise

    def close(self):
        """Close database connection"""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
        print("\nDatabase connection closed.")


def main():
    """Main entry point"""
    # Get database connection string
    if len(sys.argv) > 1:
        db_url = sys.argv[1]
    else:
        db_url = os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@localhost/tamil_literature')

    # Base directory for Naalayira Divya Prabandham files
    base_dir = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        'Tamil-Source-TamilConcordence',
        '6_பக்தி இலக்கியம்'
    )

    print("=" * 70)
    print("NAALAYIRA DIVYA PRABANDHAM BULK IMPORT")
    print("நாலாயிரத் திவ்விய பிரபந்தம் - 24 Works by 12 Alvars")
    print("=" * 70)
    print(f"Database: {db_url}")
    print(f"Source directory: {base_dir}")

    importer = NaalayiraDivyaPrabandhamImporter(db_url)

    try:
        importer.connect()
        importer.parse_all_files(base_dir)
        importer.import_data()
    finally:
        importer.close()


if __name__ == '__main__':
    main()
