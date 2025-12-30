#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Devaram Bulk Import Script
===========================
Imports Devaram works (Thirumurai Files 1-7) from the 3 Nayanmars:
- Files 1-3: Sambandar Devaram (திருஞானசம்பந்தர்) - 4,169 verses
- Files 4-6: Appar Devaram (திருநாவுக்கரசர்/அப்பர்) - 3,066 verses
- File 7: Sundarar Devaram (சுந்தரர்) - 101 pathigams

Collection: Thirumurai (திருமுறை) - Collection ID 321
Sub-collection: Devaram (தேவாரம்)

Structure:
    Author ^ Work (verse range)
    Section_number. Section_name : பண் - pann_name
    #verse_number
    lines...
    மேல்

Uses 2-phase bulk COPY pattern for optimal performance.
"""

import os
import sys
import re
import json
import io
import csv
import psycopg2
from typing import List, Dict, Optional

class DevaramBulkImporter:
    def __init__(self, db_connection_string: str):
        """Initialize the Devaram bulk importer"""
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
                'file': '1.முதலாம் திருமுறை.txt',
                'work_name': "Sambandar Devaram 1",
                'work_name_tamil': "சம்பந்தர் தேவாரம் (1-1469)",
                'author': "Thirugnanasambandar",
                'author_tamil': "திருஞானசம்பந்தர்",
                'thirumurai_number': 1,
                'verse_range': (1, 1469)
            },
            {
                'file': '2.இரண்டாம் திருமுறை.txt',
                'work_name': "Sambandar Devaram 2",
                'work_name_tamil': "சம்பந்தர் தேவாரம் (1470-2800)",
                'author': "Thirugnanasambandar",
                'author_tamil': "திருஞானசம்பந்தர்",
                'thirumurai_number': 2,
                'verse_range': (1470, 2800)
            },
            {
                'file': '3.மூன்றாம் திருமுறை.txt',
                'work_name': "Sambandar Devaram 3",
                'work_name_tamil': "சம்பந்தர் தேவாரம் (2801-4169)",
                'author': "Thirugnanasambandar",
                'author_tamil': "திருஞானசம்பந்தர்",
                'thirumurai_number': 3,
                'verse_range': (2801, 4169)
            },
            {
                'file': '4.நான்காம்_திருமுறை.txt',
                'work_name': "Appar Devaram 1",
                'work_name_tamil': "அப்பர் தேவாரம் (1-1070)",
                'author': "Thirunavukkarasar (Appar)",
                'author_tamil': "திருநாவுக்கரசர் (அப்பர்)",
                'thirumurai_number': 4,
                'verse_range': (1, 1070)
            },
            {
                'file': '5.ஐந்தாம் திருமுறை.txt',
                'work_name': "Appar Devaram 2",
                'work_name_tamil': "அப்பர் தேவாரம் (1071-2085)",
                'author': "Thirunavukkarasar (Appar)",
                'author_tamil': "திருநாவுக்கரசர் (அப்பர்)",
                'thirumurai_number': 5,
                'verse_range': (1071, 2085)
            },
            {
                'file': '6.ஆறாம் திருமுறை.txt',
                'work_name': "Appar Devaram 3",
                'work_name_tamil': "அப்பர் தேவாரம் (2086-3066)",
                'author': "Thirunavukkarasar (Appar)",
                'author_tamil': "திருநாவுக்கரசர் (அப்பர்)",
                'thirumurai_number': 6,
                'verse_range': (2086, 3066)
            },
            {
                'file': '7.ஏழாம் திருமுறை.txt',
                'work_name': "Sundarar Devaram",
                'work_name_tamil': "சுந்தரர் தேவாரம் (1-101)",
                'author': "Sundarar",
                'author_tamil': "சுந்தரர்",
                'thirumurai_number': 7,
                'verse_range': (1, 101)
            }
        ]

    def connect(self):
        """Connect to the database and get MAX IDs"""
        print("Connecting to database...")
        self.conn = psycopg2.connect(self.db_connection_string)
        self.cursor = self.conn.cursor()

        # Ensure Thirumurai collection exists
        self.ensure_collection_exists()

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

    def ensure_collection_exists(self):
        """Ensure the Devaram collection and author sub-collections exist"""
        # Check if main Thirumurai collection exists (321)
        self.cursor.execute("SELECT collection_id FROM collections WHERE collection_id = 321")
        if not self.cursor.fetchone():
            print("  Creating main Thirumurai collection (321)...")
            self.cursor.execute("""
                INSERT INTO collections (collection_id, collection_name, collection_name_tamil,
                                       collection_type, description, sort_order)
                VALUES (321, 'Thirumurai', 'திருமுறை', 'devotional',
                        'Thirumurai - 12 books of Shaivite devotional literature', 321)
            """)
            self.conn.commit()

        # Check if Devaram collection exists (3211)
        self.cursor.execute("SELECT collection_id FROM collections WHERE collection_id = 3211")
        if not self.cursor.fetchone():
            print("  Creating Devaram collection (3211)...")
            self.cursor.execute("""
                INSERT INTO collections (collection_id, collection_name, collection_name_tamil,
                                       collection_type, parent_collection_id, description, sort_order)
                VALUES (3211, 'Devaram', 'தேவாரம்', 'devotional', 321,
                        'Devaram - Hymns by Sambandar, Appar, and Sundarar (Thirumurai 1-7)', 3211)
            """)
            self.conn.commit()
            print("  [OK] Devaram collection created")
        else:
            print("  [OK] Devaram collection already exists")

        # Create individual Thirumurai 1-7 collections
        thirumurai_collections = [
            (32111, 'First Thirumurai', 'முதலாம் திருமுறை', 'Sambandar - File 1'),
            (32112, 'Second Thirumurai', 'இரண்டாம் திருமுறை', 'Sambandar - File 2'),
            (32113, 'Third Thirumurai', 'மூன்றாம் திருமுறை', 'Sambandar - File 3'),
            (32114, 'Fourth Thirumurai', 'நான்காம் திருமுறை', 'Appar - File 4'),
            (32115, 'Fifth Thirumurai', 'ஐந்தாம் திருமுறை', 'Appar - File 5'),
            (32116, 'Sixth Thirumurai', 'ஆறாம் திருமுறை', 'Appar - File 6'),
            (32117, 'Seventh Thirumurai', 'ஏழாம் திருமுறை', 'Sundarar - File 7')
        ]

        for coll_id, name, name_tamil, desc in thirumurai_collections:
            self.cursor.execute("SELECT collection_id FROM collections WHERE collection_id = %s", (coll_id,))
            if not self.cursor.fetchone():
                print(f"  Creating {name_tamil} collection ({coll_id})...")
                self.cursor.execute("""
                    INSERT INTO collections (collection_id, collection_name, collection_name_tamil,
                                           collection_type, parent_collection_id, description, sort_order)
                    VALUES (%s, %s, %s, 'devotional', 3211, %s, %s)
                """, (coll_id, name, name_tamil, desc, coll_id))

        # Create author sub-collections
        author_collections = [
            (321111, 'Sambandar Devaram', 'சம்பந்தர் தேவாரம்', 'Thirumurai 1-3: Thirugnanasambandar'),
            (321112, 'Appar Devaram', 'அப்பர் தேவாரம்', 'Thirumurai 4-6: Thirunavukkarasar (Appar)'),
            (321113, 'Sundarar Devaram', 'சுந்தரர் தேவாரம்', 'Thirumurai 7: Sundarar')
        ]

        for coll_id, name, name_tamil, desc in author_collections:
            self.cursor.execute("SELECT collection_id FROM collections WHERE collection_id = %s", (coll_id,))
            if not self.cursor.fetchone():
                print(f"  Creating {name_tamil} collection ({coll_id})...")
                self.cursor.execute("""
                    INSERT INTO collections (collection_id, collection_name, collection_name_tamil,
                                           collection_type, parent_collection_id, description, sort_order)
                    VALUES (%s, %s, %s, 'devotional', 3211, %s, %s)
                """, (coll_id, name, name_tamil, desc, coll_id))

        self.conn.commit()

        # Query and store collection IDs as instance variables
        self.cursor.execute("SELECT collection_id FROM collections WHERE collection_id = 3211")
        self.devaram_collection_id = self.cursor.fetchone()[0]

        # Store individual Thirumurai collection IDs
        self.cursor.execute("SELECT collection_id FROM collections WHERE collection_id = 32111")
        self.first_thirumurai_collection_id = self.cursor.fetchone()[0]

        self.cursor.execute("SELECT collection_id FROM collections WHERE collection_id = 32112")
        self.second_thirumurai_collection_id = self.cursor.fetchone()[0]

        self.cursor.execute("SELECT collection_id FROM collections WHERE collection_id = 32113")
        self.third_thirumurai_collection_id = self.cursor.fetchone()[0]

        self.cursor.execute("SELECT collection_id FROM collections WHERE collection_id = 32114")
        self.fourth_thirumurai_collection_id = self.cursor.fetchone()[0]

        self.cursor.execute("SELECT collection_id FROM collections WHERE collection_id = 32115")
        self.fifth_thirumurai_collection_id = self.cursor.fetchone()[0]

        self.cursor.execute("SELECT collection_id FROM collections WHERE collection_id = 32116")
        self.sixth_thirumurai_collection_id = self.cursor.fetchone()[0]

        self.cursor.execute("SELECT collection_id FROM collections WHERE collection_id = 32117")
        self.seventh_thirumurai_collection_id = self.cursor.fetchone()[0]

        # Store author sub-collection IDs
        self.cursor.execute("SELECT collection_id FROM collections WHERE collection_id = 321111")
        self.sambandar_collection_id = self.cursor.fetchone()[0]

        self.cursor.execute("SELECT collection_id FROM collections WHERE collection_id = 321112")
        self.appar_collection_id = self.cursor.fetchone()[0]

        self.cursor.execute("SELECT collection_id FROM collections WHERE collection_id = 321113")
        self.sundarar_collection_id = self.cursor.fetchone()[0]

    def parse_all_files(self, base_dir: str):
        """Parse all 7 Devaram files"""
        print("\n=== PHASE 1: Parsing Devaram files into memory ===")

        for file_info in self.file_mappings:
            file_path = os.path.join(base_dir, file_info['file'])
            if not os.path.exists(file_path):
                print(f"  [SKIP] File not found: {file_path}")
                continue

            print(f"\n  Processing: {file_info['work_name_tamil']}")
            self.parse_file(file_path, file_info)

        print(f"\n  [OK] Parsed {len(self.works)} works, {len(self.sections)} pathigams, {len(self.verses)} verses")
        print(f"       {len(self.lines)} lines, {len(self.words)} words")

    def parse_file(self, file_path: str, file_info: Dict):
        """Parse a single Devaram file"""
        # Determine author collection and individual Thirumurai collection based on number
        thirumurai_num = file_info['thirumurai_number']

        # Map to individual Thirumurai collection
        thirumurai_collection_map = {
            1: (self.first_thirumurai_collection_id, 'First Thirumurai', 'முதலாம் திருமுறை'),
            2: (self.second_thirumurai_collection_id, 'Second Thirumurai', 'இரண்டாம் திருமுறை'),
            3: (self.third_thirumurai_collection_id, 'Third Thirumurai', 'மூன்றாம் திருமுறை'),
            4: (self.fourth_thirumurai_collection_id, 'Fourth Thirumurai', 'நான்காம் திருமுறை'),
            5: (self.fifth_thirumurai_collection_id, 'Fifth Thirumurai', 'ஐந்தாம் திருமுறை'),
            6: (self.sixth_thirumurai_collection_id, 'Sixth Thirumurai', 'ஆறாம் திருமுறை'),
            7: (self.seventh_thirumurai_collection_id, 'Seventh Thirumurai', 'ஏழாம் திருமுறை')
        }

        thirumurai_collection_id, thirumurai_collection_name, thirumurai_collection_tamil = thirumurai_collection_map[thirumurai_num]

        # Map to author collection
        if thirumurai_num <= 3:
            author_collection_id = self.sambandar_collection_id
            author_collection_name = 'Sambandar Devaram'
            author_collection_name_tamil = 'சம்பந்தர் தேவாரம்'
        elif thirumurai_num <= 6:
            author_collection_id = self.appar_collection_id
            author_collection_name = 'Appar Devaram'
            author_collection_name_tamil = 'அப்பர் தேவாரம்'
        else:  # thirumurai_num == 7
            author_collection_id = self.sundarar_collection_id
            author_collection_name = 'Sundarar Devaram'
            author_collection_name_tamil = 'சுந்தரர் தேவாரம்'

        # Create work with metadata
        work_metadata = {
            'tradition': 'Shaivite',
            'thirumurai_collection_id': thirumurai_collection_id,
            'thirumurai_collection_name': thirumurai_collection_name,
            'thirumurai_collection_tamil': thirumurai_collection_tamil,
            'author_collection_id': author_collection_id,
            'author_collection_name': author_collection_name,
            'author_collection_tamil': author_collection_name_tamil,
            'thirumurai_number': thirumurai_num,
            'saint': file_info['author_tamil'],
            'saint_transliteration': file_info['author'],
            'time_period': '7th-8th century CE',
            'deity_focus': 'Shiva',
            'musical_tradition': True,
            'performance_context': 'temple worship',
            'liturgical_use': True,
            'verse_form': 'pathigam',
            'verse_range': file_info['verse_range']
        }

        work_dict = {
            'work_id': self.work_id,
            'work_name': file_info['work_name'],
            'work_name_tamil': file_info['work_name_tamil'],
            'period': '7th-8th century CE',
            'author': file_info['author'],
            'author_tamil': file_info['author_tamil'],
            'description': f"{file_info['work_name_tamil']} - Part of {thirumurai_collection_tamil}",
            'canonical_order': 320 + thirumurai_num,  # 321-327
            'metadata': work_metadata
        }
        self.works.append(work_dict)
        self.current_work_id = self.work_id
        print(f"    Created work: {file_info['work_name_tamil']} (ID: {self.work_id})")
        self.work_id += 1

        # Parse file content
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        # Create a default section for this work (fallback if no pathigams found)
        # This ensures verse_hierarchy and word_details views work correctly
        default_section = self._get_or_create_section_id(self.current_work_id)

        current_section = default_section  # Start with default, update when pathigam found
        current_pann = None
        current_verse_lines = []
        verse_number = 0
        in_verse = False

        for line in lines:
            line = line.strip()

            if not line or line == 'மேல்':
                # End of verse
                if in_verse and current_verse_lines:
                    self.create_verse(current_verse_lines, verse_number, current_pann)
                    current_verse_lines = []
                    in_verse = False
                continue

            # Skip author line (first line)
            if '^' in line:
                continue

            # Section marker: " 1. Section name : பண் - pann_name" or "பண் : pann_name"
            section_match = re.match(r'^\s*(\d+)\.\s*(.+?)\s*:\s*பண்\s*[-:]\s*(.+)', line)
            if section_match:
                section_num = int(section_match.group(1))
                section_name = section_match.group(2).strip()
                current_pann = section_match.group(3).strip()

                # Create section (pathigam)
                self.section_sort_order += 1
                section_metadata = {
                    'section_type': 'pathigam',
                    'section_type_tamil': 'பதிகம்',
                    'pann': current_pann,
                    'musical_mode': True
                }

                section_dict = {
                    'section_id': self.section_id,
                    'work_id': self.current_work_id,
                    'parent_section_id': None,
                    'level_type': 'Pathigam',
                    'level_type_tamil': 'பதிகம்',
                    'section_number': section_num,
                    'section_name': section_name,
                    'section_name_tamil': section_name,
                    'sort_order': self.section_sort_order,
                    'metadata': section_metadata
                }
                self.sections.append(section_dict)
                current_section = self.section_id
                self.section_id += 1
                continue

            # Verse marker: #number
            verse_match = re.match(r'^#(\d+)', line)
            if verse_match:
                # Save previous verse if any
                if current_verse_lines:
                    self.create_verse(current_verse_lines, verse_number, current_pann)
                    current_verse_lines = []

                verse_number = int(verse_match.group(1))
                in_verse = True
                self.current_section_id = current_section
                continue

            # Verse content lines
            if in_verse:
                current_verse_lines.append(line)

        # Handle last verse
        if current_verse_lines:
            self.create_verse(current_verse_lines, verse_number, current_pann)

    def create_verse(self, verse_lines: List[str], verse_number: int, pann: Optional[str]):
        """Create a verse with its lines and words"""
        self.verse_sort_order += 1

        # Verse metadata
        verse_metadata = {
            'saint': self.works[-1]['author_tamil'],
            'deity': 'Shiva',
            'meter': 'venba',
            'line_count': len(verse_lines),
            'liturgical_use': True,
            'theological_tradition': 'Shaiva Siddhanta'
        }

        if pann:
            verse_metadata['pann'] = pann

        verse_dict = {
            'verse_id': self.verse_id,
            'work_id': self.current_work_id,
            'section_id': self.current_section_id,
            'verse_number': verse_number,
            'verse_type': 'Devotional Hymn',
            'verse_type_tamil': 'பக்தி பாடல்',
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
        """Link works to three collection levels:
        1. Individual Thirumurai (முதலாம் திருமுறை, etc.) - PRIMARY
        2. Author sub-collection (சம்பந்தர், அப்பர், சுந்தரர்) - SECONDARY
        3. Main Devaram collection - TERTIARY
        """
        if not self.works:
            return

        print(f"  Linking {len(self.works)} works to collections (3 levels each)...")

        # Get starting positions for each collection type
        # We'll track positions for each individual Thirumurai and author collection
        thirumurai_positions = {}
        author_positions = {}

        # Query starting position for Devaram main collection
        self.cursor.execute("""
            SELECT COALESCE(MAX(position_in_collection), 0) + 1
            FROM work_collections
            WHERE collection_id = %s
        """, (self.devaram_collection_id,))
        devaram_position = self.cursor.fetchone()[0]

        buffer = io.StringIO()
        for work in self.works:
            thirumurai_coll_id = work['metadata']['thirumurai_collection_id']
            author_coll_id = work['metadata']['author_collection_id']

            # Get position for individual Thirumurai collection
            if thirumurai_coll_id not in thirumurai_positions:
                self.cursor.execute("""
                    SELECT COALESCE(MAX(position_in_collection), 0) + 1
                    FROM work_collections
                    WHERE collection_id = %s
                """, (thirumurai_coll_id,))
                thirumurai_positions[thirumurai_coll_id] = self.cursor.fetchone()[0]

            # Get position for author sub-collection
            if author_coll_id not in author_positions:
                self.cursor.execute("""
                    SELECT COALESCE(MAX(position_in_collection), 0) + 1
                    FROM work_collections
                    WHERE collection_id = %s
                """, (author_coll_id,))
                author_positions[author_coll_id] = self.cursor.fetchone()[0]

            # Link to individual Thirumurai collection (PRIMARY)
            fields = [
                str(work['work_id']),
                str(thirumurai_coll_id),
                str(thirumurai_positions[thirumurai_coll_id]),
                't',  # is_primary = true
                ''
            ]
            buffer.write('\t'.join(fields) + '\n')
            thirumurai_positions[thirumurai_coll_id] += 1

            # Link to author sub-collection (SECONDARY)
            fields = [
                str(work['work_id']),
                str(author_coll_id),
                str(author_positions[author_coll_id]),
                'f',  # is_primary = false
                ''
            ]
            buffer.write('\t'.join(fields) + '\n')
            author_positions[author_coll_id] += 1

            # Link to main Devaram collection (TERTIARY)
            fields = [
                str(work['work_id']),
                str(self.devaram_collection_id),
                str(devaram_position),
                'f',  # is_primary = false
                ''
            ]
            buffer.write('\t'.join(fields) + '\n')
            devaram_position += 1

        buffer.seek(0)
        self.cursor.copy_from(
            buffer, 'work_collections',
            columns=['work_id', 'collection_id', 'position_in_collection', 'is_primary', 'notes'],
            null=''
        )
        print(f"    ✓ Linked {len(self.works)} works to 3 collection levels each")

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
        writer = csv.writer(buffer, delimiter='\t', quoting=csv.QUOTE_MINIMAL, escapechar='\\')

        for line in self.lines:
            writer.writerow([
                line['line_id'],
                line['verse_id'],
                line['line_number'],
                line['line_text']
            ])

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
        writer = csv.writer(buffer, delimiter='\t', quoting=csv.QUOTE_MINIMAL, escapechar='\\')

        for word in self.words:
            writer.writerow([
                word['word_id'],
                word['line_id'],
                word['word_position'],
                word['word_text'],
                word.get('sandhi_split', '')
            ])

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
            print("\n[SUCCESS] All Devaram data imported successfully!")

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

    # Base directory for Devaram files
    base_dir = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        'Tamil-Source-TamilConcordence',
        '6_பக்தி இலக்கியம்'
    )

    print("=" * 70)
    print("DEVARAM BULK IMPORT (Thirumurai Files 1-7)")
    print("=" * 70)
    print(f"Database: {db_url}")
    print(f"Source directory: {base_dir}")

    importer = DevaramBulkImporter(db_url)

    try:
        importer.connect()
        importer.parse_all_files(base_dir)
        importer.import_data()
    finally:
        importer.close()


if __name__ == '__main__':
    main()
