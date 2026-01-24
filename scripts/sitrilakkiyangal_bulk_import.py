#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Minor Literary Works (சிற்றிலக்கியங்கள்) Bulk Import
Fast 2-phase import using PostgreSQL COPY

Phase 1: Parse text → Build data structures in memory
Phase 2: Bulk COPY into database (1000x faster than INSERT)

Collection ID: 326 (சிற்றிலக்கியங்கள் - Minor Literary Works)

Works (20 minor literary works):
Diverse literary genres spanning 12th-19th century CE including கலம்பகம்,
பரணி, தூது, கோவை, குறவஞ்சி, and other classical Tamil genres.

Structure Patterns:
- simple: Only #N verse markers (5 works)
- dual_at: @N section markers + #N verses (14 works)
- dual_star: *N. section markers + #N verses (1 work: கலிங்கத்துப்பரணி)
"""

import re
import psycopg2
from pathlib import Path
import csv
import io
import sys
import os
from word_cleaning import split_and_clean_words

# Work metadata for all 20 works
WORK_METADATA = {
    1: {
        'work_name': 'Abhirami Andhadhi',
        'work_name_tamil': 'அபிராமி அந்தாதி',
        'author': 'Abhirami Pattar',
        'author_tamil': 'அபிராமி பட்டர்',
        'period': '18th century CE',
        'canonical_order': 326001,
        'position_in_collection': 1,
        'file': 'அபிராமி அந்தாதி.txt',
        'structure_pattern': 'simple'
    },
    2: {
        'work_name': 'Azhagar Killai Viduthootu',
        'work_name_tamil': 'அழகர் கிள்ளை விடுதூது',
        'author': 'Balapattu Chokkanathar',
        'author_tamil': 'பலபட்டடைச் சொக்கநாதர்',
        'period': '17th-18th century CE',
        'canonical_order': 326002,
        'position_in_collection': 2,
        'file': 'அழகர் கிள்ளை விடுதூது.txt',
        'structure_pattern': 'dual_at'
    },
    3: {
        'work_name': 'Kachchi Kalambagam',
        'work_name_tamil': 'கச்சிக் கலம்பகம்',
        'author': 'Poonthi Aranganatha Mudaliar',
        'author_tamil': 'பூண்டி அரங்கநாத முதலியார்',
        'period': '17th-18th century CE',
        'canonical_order': 326003,
        'position_in_collection': 3,
        'file': 'கச்சிக் கலம்பகம்.txt',
        'structure_pattern': 'dual_at'
    },
    4: {
        'work_name': 'Kalingathu Parani',
        'work_name_tamil': 'கலிங்கத்துப்பரணி',
        'author': 'Cheyangkonttar',
        'author_tamil': 'செயங்கொண்டார்',
        'period': '12th century CE',
        'canonical_order': 326004,
        'position_in_collection': 4,
        'file': 'கலிங்கத்துப்பரணி.txt',
        'structure_pattern': 'dual_star'
    },
    5: {
        'work_name': 'Kasi Kalambagam',
        'work_name_tamil': 'காசிக் கலம்பகம்',
        'author': 'Kumarakuruparar',
        'author_tamil': 'குமரகுருபரர்',
        'period': '17th century CE',
        'canonical_order': 326005,
        'position_in_collection': 5,
        'file': 'காசிக் கலம்பகம்.txt',
        'structure_pattern': 'dual_at'
    },
    6: {
        'work_name': 'Kavadi Chindu',
        'work_name_tamil': 'காவடிச் சிந்து',
        'author': 'Annamalai Rettiyar',
        'author_tamil': 'அண்ணாமலை ரெட்டியார்',
        'period': '19th century CE',
        'canonical_order': 326006,
        'position_in_collection': 6,
        'file': 'காவடிச் சிந்து.txt',
        'structure_pattern': 'dual_at'
    },
    7: {
        'work_name': 'Kuselopakyanam',
        'work_name_tamil': 'குசேலோபாக்கியானம்',
        'author': 'Vallur Devaraja Pillai',
        'author_tamil': 'வல்லூர் தேவராச பிள்ளை',
        'period': '18th-19th century CE',
        'canonical_order': 326007,
        'position_in_collection': 7,
        'file': 'குசேலோபாக்கியானம்.txt',
        'structure_pattern': 'dual_at'
    },
    8: {
        'work_name': 'Kumaresa Sadhagam',
        'work_name_tamil': 'குமரேச சதகம்',
        'author': 'Gurubatha Dasar',
        'author_tamil': 'குருபாத தாசர்',
        'period': '18th-19th century CE',
        'canonical_order': 326008,
        'position_in_collection': 8,
        'file': 'குமரேச சதகம்.txt',
        'structure_pattern': 'simple'
    },
    9: {
        'work_name': 'Thakayaga Parani',
        'work_name_tamil': 'தக்கயாகப்பரணி',
        'author': 'Ottakkuttar',
        'author_tamil': 'ஒட்டக்கூத்தர்',
        'period': '12th century CE',
        'canonical_order': 326009,
        'position_in_collection': 9,
        'file': 'தக்கயாகப்பரணி.txt',
        'structure_pattern': 'dual_at'
    },
    10: {
        'work_name': 'Thanjai Vanan Kovai',
        'work_name_tamil': 'தஞ்சைவாணன் கோவை',
        'author': 'Poyyamozhipulavar',
        'author_tamil': 'பொய்யாமொழிப்புலவர்',
        'period': '15th-16th century CE',
        'canonical_order': 326010,
        'position_in_collection': 10,
        'file': 'தஞ்சைவாணன் கோவை.txt',
        'structure_pattern': 'dual_at'
    },
    11: {
        'work_name': 'Thamizh Vidu Thootu',
        'work_name_tamil': 'தமிழ்விடு தூது',
        'author': 'Madurai Chokkanathar',
        'author_tamil': 'மதுரைச் சொக்கநாதர்',
        'period': '17th century CE',
        'canonical_order': 326011,
        'position_in_collection': 11,
        'file': 'தமிழ்விடு தூது.txt',
        'structure_pattern': 'dual_at'
    },
    12: {
        'work_name': 'Thirukkutrala Kuravanji',
        'work_name_tamil': 'திருக்குற்றாலக் குறவஞ்சி',
        'author': 'Unknown',
        'author_tamil': 'அறியப்படாத ஆசிரியர்',
        'period': '17th-18th century CE',
        'canonical_order': 326012,
        'position_in_collection': 12,
        'file': 'திருக்குற்றாலக் குறவஞ்சி.txt',
        'structure_pattern': 'dual_at'
    },
    13: {
        'work_name': 'Nandhi Kalambagam',
        'work_name_tamil': 'நந்திக் கலம்பகம்',
        'author': 'Unknown',
        'author_tamil': 'அறியப்படாத ஆசிரியர்',
        'period': '17th-18th century CE',
        'canonical_order': 326013,
        'position_in_collection': 13,
        'file': 'நந்திக் கலம்பகம்.txt',
        'structure_pattern': 'dual_at'
    },
    14: {
        'work_name': 'Nala Venba',
        'work_name_tamil': 'நளவெண்பா',
        'author': 'Pugazhenthi Pulavar',
        'author_tamil': 'புகழேந்திப் புலவர்',
        'period': '16th-17th century CE',
        'canonical_order': 326014,
        'position_in_collection': 14,
        'file': 'நளவெண்பா.txt',
        'structure_pattern': 'simple'
    },
    15: {
        'work_name': 'Pandi Kovai',
        'work_name_tamil': 'பாண்டிக்கோவை',
        'author': 'Unknown',
        'author_tamil': 'அறியப்படாத ஆசிரியர்',
        'period': '15th-16th century CE',
        'canonical_order': 326015,
        'position_in_collection': 15,
        'file': 'பாண்டிக்கோவை.txt',
        'structure_pattern': 'dual_at'
    },
    16: {
        'work_name': 'Bethlakema Kuravanji',
        'work_name_tamil': 'பெத்லகேம் குறவஞ்சி',
        'author': 'Vedhanayaga Sasthriyar',
        'author_tamil': 'வேதநாயக சாஸ்திரியார்',
        'period': '19th century CE',
        'canonical_order': 326016,
        'position_in_collection': 16,
        'file': 'பெத்லகேம் குறவஞ்சி.txt',
        'structure_pattern': 'dual_at'
    },
    17: {
        'work_name': 'Madurai Meenakshiyammai Pillai Thamizh',
        'work_name_tamil': 'மதுரை மீனாட்சியம்மை பிள்ளைத் தமிழ்',
        'author': 'Kumarakuruparar',
        'author_tamil': 'குமரகுருபரர்',
        'period': '17th century CE',
        'canonical_order': 326017,
        'position_in_collection': 17,
        'file': 'மதுரை மீனாட்சியம்மை பிள்ளைத் தமிழ்.txt',
        'structure_pattern': 'dual_at'
    },
    18: {
        'work_name': 'Madurai Kalambagam',
        'work_name_tamil': 'மதுரைக் கலம்பகம்',
        'author': 'Kumarakuruparar',
        'author_tamil': 'குமரகுருபரர்',
        'period': '17th century CE',
        'canonical_order': 326018,
        'position_in_collection': 18,
        'file': 'மதுரைக் கலம்பகம்.txt',
        'structure_pattern': 'dual_at'
    },
    19: {
        'work_name': 'Mukkudal Pallu',
        'work_name_tamil': 'முக்கூடற் பள்ளு',
        'author': 'Unknown',
        'author_tamil': 'அறியப்படாத ஆசிரியர்',
        'period': '18th-19th century CE',
        'canonical_order': 326019,
        'position_in_collection': 19,
        'file': 'முக்கூடற் பள்ளு.txt',
        'structure_pattern': 'simple'
    },
    20: {
        'work_name': 'Muvarula',
        'work_name_tamil': 'மூவருலா',
        'author': 'Kavichakravarthi Ottakkuttar',
        'author_tamil': 'கவிச்சக்கரவர்த்தி ஒட்டக்கூத்தர்',
        'period': '12th century CE',
        'canonical_order': 326020,
        'position_in_collection': 20,
        'file': 'மூவருலா.txt',
        'structure_pattern': 'dual_at'
    }
}


class SitrilakkiyangalBulkImporter:
    """Import all 20 minor literary works using 2-phase bulk COPY pattern"""

    def __init__(self, db_connection_string: str):
        """Initialize importer and query MAX IDs from ALL tables"""
        self.conn = psycopg2.connect(db_connection_string)
        self.cursor = self.conn.cursor()
        self.collection_id = 326

        # Data containers
        self.works = []
        self.sections = []
        self.verses = []
        self.lines = []
        self.words = []
        self.work_collections = []

        # Query MAX IDs from ALL tables ONCE at initialization
        # CRITICAL: Query once, increment manually (lessons from 2025-12-05)
        self.cursor.execute("SELECT COALESCE(MAX(work_id), 0) FROM works")
        self.work_id = self.cursor.fetchone()[0] + 1

        self.cursor.execute("SELECT COALESCE(MAX(section_id), 0) FROM sections")
        self.section_id = self.cursor.fetchone()[0] + 1

        self.cursor.execute("SELECT COALESCE(MAX(verse_id), 0) FROM verses")
        self.verse_id = self.cursor.fetchone()[0] + 1

        self.cursor.execute("SELECT COALESCE(MAX(line_id), 0) FROM lines")
        self.line_id = self.cursor.fetchone()[0] + 1

        self.cursor.execute("SELECT COALESCE(MAX(word_id), 0) FROM words")
        self.word_id = self.cursor.fetchone()[0] + 1

        print(f"  Starting IDs: work={self.work_id}, section={self.section_id}, "
              f"verse={self.verse_id}, line={self.line_id}, word={self.word_id}")

    def _ensure_collection_exists(self):
        """Create collection 324 if missing"""
        # Check if collection exists
        self.cursor.execute("SELECT collection_id FROM collections WHERE collection_id = %s",
                          (self.collection_id,))
        existing = self.cursor.fetchone()

        if not existing:
            print(f"  Creating சிற்றிலக்கியங்கள் collection (ID: {self.collection_id})...")
            self.cursor.execute("""
                INSERT INTO collections (
                    collection_id, collection_name, collection_name_tamil,
                    collection_type, description, parent_collection_id, sort_order
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                self.collection_id,
                'Minor Literary Works',
                'சிற்றிலக்கியங்கள்',
                'genre',
                'Twenty minor literary works spanning கலம்பகம், பரணி, தூது, கோவை, குறவஞ்சி, and other classical Tamil genres from 12th-19th centuries CE',
                1,  # Parent: தமிழ் இலக்கியம் (designated filter collection)
                6   # After நீதிநூல்கள்=5
            ))
            print(f"  [OK] Collection created (will commit with bulk data)")
        else:
            print(f"  Found existing சிற்றிலக்கியங்கள் collection (ID: {self.collection_id})")

    def _create_work(self, work_num: int) -> int:
        """Create work entry from WORK_METADATA and return work_id"""
        if work_num not in WORK_METADATA:
            raise ValueError(f"Invalid work number: {work_num}")

        metadata = WORK_METADATA[work_num]

        # Check if work already exists
        self.cursor.execute("SELECT work_id FROM works WHERE work_name = %s AND work_name_tamil = %s",
                          (metadata['work_name'], metadata['work_name_tamil']))
        existing = self.cursor.fetchone()

        if existing:
            print(f"  [ERROR] Work {metadata['work_name_tamil']} already exists (ID: {existing[0]})")
            return None

        # Use pre-allocated work_id and increment
        work_id = self.work_id
        self.work_id += 1

        self.works.append({
            'work_id': work_id,
            'work_name': metadata['work_name'],
            'work_name_tamil': metadata['work_name_tamil'],
            'author': metadata['author'],
            'author_tamil': metadata['author_tamil'],
            'period': metadata['period'],
            'canonical_order': metadata['canonical_order']
        })

        # Link work to collection 324
        self.work_collections.append({
            'work_id': work_id,
            'collection_id': self.collection_id,
            'position_in_collection': metadata['position_in_collection']
        })

        print(f"  Created work: {metadata['work_name_tamil']} (ID: {work_id}, Canonical: {metadata['canonical_order']})")
        return work_id

    def _add_section(self, work_id: int, section_num: int, section_name: str,
                    parent_section_id: int = None, level_type: str = 'Section') -> int:
        """Add section to in-memory list and return section_id"""
        section_id = self.section_id
        self.section_id += 1  # Manual increment

        self.sections.append({
            'section_id': section_id,
            'work_id': work_id,
            'parent_section_id': parent_section_id,
            'level_type': level_type,
            'level_type_tamil': 'பகுதி' if level_type == 'Section' else level_type,
            'section_number': section_num,
            'section_name': section_name,
            'section_name_tamil': section_name,
            'sort_order': section_num
        })

        return section_id

    def _add_verse(self, work_id: int, section_id: int, verse_num: int, verse_lines: list):
        """Add verse, lines, and words to in-memory lists"""
        if not verse_lines:
            return

        # Create verse
        verse_id = self.verse_id
        self.verse_id += 1

        self.verses.append({
            'verse_id': verse_id,
            'work_id': work_id,
            'section_id': section_id,
            'verse_number': verse_num,
            'verse_type': 'Verse',
            'verse_type_tamil': 'பாடல்',
            'total_lines': len(verse_lines),
            'sort_order': verse_num
        })

        # Create lines and words
        for line_num, line_text in enumerate(verse_lines, start=1):
            line_id = self.line_id
            self.line_id += 1

            # Clean line text
            cleaned_line = line_text.strip()

            self.lines.append({
                'line_id': line_id,
                'verse_id': verse_id,
                'line_number': line_num,
                'line_text': cleaned_line
            })

            # Split into words
            words = split_and_clean_words(cleaned_line)
            for word_position, word_text in enumerate(words, start=1):
                word_id = self.word_id
                self.word_id += 1

                self.words.append({
                    'word_id': word_id,
                    'line_id': line_id,
                    'word_position': word_position,
                    'word_text': word_text,
                    'sandhi_split': None
                })

    def parse_file(self, file_path: str, work_num: int):
        """Route to appropriate parser based on structure_pattern"""
        pattern = WORK_METADATA[work_num]['structure_pattern']

        print(f"\nParsing File {work_num}: {Path(file_path).name} (Pattern: {pattern})")

        if pattern == 'simple':
            self._parse_simple_pattern(file_path, work_num)
        elif pattern == 'dual_at':
            self._parse_dual_at_pattern(file_path, work_num)
        elif pattern == 'dual_star':
            self._parse_dual_star_pattern(file_path, work_num)
        else:
            raise ValueError(f"Unknown structure pattern: {pattern}")

    def _parse_simple_pattern(self, file_path: str, work_num: int):
        """
        Parse files with simple #N verse numbering (no sections)

        Pattern:
        ** [Work Title]
        #N [Optional Topic]
        [verse lines]
        [blank line]

        Create single default section with NULL name to avoid redundant hierarchy
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        # Create work
        current_work_id = self._create_work(work_num)
        if not current_work_id:
            return

        # Create default section with NULL name (avoids redundant hierarchy in UI)
        default_section = self._add_section(
            current_work_id,
            section_num=1,
            section_name=None,
            level_type='Section'
        )

        # State tracking
        current_verse_num = None
        current_verse_lines = []
        verse_counter = 0

        for line in lines:
            line = line.strip()

            # Skip work title and metadata markers
            if line.startswith('**'):
                continue

            # Empty line - triggers verse save
            if not line:
                if current_verse_num is not None and current_verse_lines:
                    self._add_verse(current_work_id, default_section,
                                  verse_counter, current_verse_lines)
                    current_verse_num = None
                    current_verse_lines = []
                continue

            # #N Verse marker
            if line.startswith('#'):
                # Save previous verse
                if current_verse_num is not None and current_verse_lines:
                    self._add_verse(current_work_id, default_section,
                                  verse_counter, current_verse_lines)
                    current_verse_lines = []

                # Extract verse number (ignore topic on same line)
                match = re.match(r'#(\d+)', line)
                if match:
                    current_verse_num = int(match.group(1))
                    verse_counter += 1
                    current_verse_lines = []

            # Regular line (verse content)
            elif current_verse_num is not None:
                # Skip continuation markers
                if line == 'மேல்':
                    continue
                current_verse_lines.append(line)

        # Save final verse
        if current_verse_num is not None and current_verse_lines:
            self._add_verse(current_work_id, default_section,
                          verse_counter, current_verse_lines)

    def _parse_dual_at_pattern(self, file_path: str, work_num: int):
        """
        Parse files with @N section markers

        Pattern:
        ** [Work Title]
        @N [Section Name]
        ** [Optional Verse Metadata]
        #N [Verse]
        [verse lines]
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        # Create work
        current_work_id = self._create_work(work_num)
        if not current_work_id:
            return

        # State tracking
        current_section = None
        current_verse_num = None
        current_verse_lines = []
        verse_counter = 0
        seen_work_title = False

        for line in lines:
            line = line.strip()

            # Empty line - triggers verse save
            if not line:
                if current_verse_num is not None and current_verse_lines:
                    self._add_verse(current_work_id, current_section,
                                  verse_counter, current_verse_lines)
                    current_verse_num = None
                    current_verse_lines = []
                continue

            # ** Work title or verse metadata (skip)
            if line.startswith('**'):
                if not seen_work_title:
                    seen_work_title = True
                # Skip all ** lines (work title, verse topics, etc.)
                continue

            # @N Section marker
            if line.startswith('@'):
                # Save previous verse
                if current_verse_num is not None and current_verse_lines:
                    self._add_verse(current_work_id, current_section,
                                  verse_counter, current_verse_lines)
                    current_verse_num = None
                    current_verse_lines = []

                # Extract section number and name
                match = re.match(r'@(\d+)\.?\s*(.*)', line)
                if match:
                    section_num = int(match.group(1))
                    section_name = match.group(2).strip()
                    if not section_name:
                        section_name = f"Section {section_num}"

                    current_section = self._add_section(
                        current_work_id,
                        section_num,
                        section_name
                    )
                    verse_counter = 0  # Reset for new section

            # #N Verse marker
            elif line.startswith('#'):
                # Save previous verse
                if current_verse_num is not None and current_verse_lines:
                    self._add_verse(current_work_id, current_section,
                                  verse_counter, current_verse_lines)

                # Extract verse number (ignore topic)
                match = re.match(r'#(\d+)', line)
                if match:
                    current_verse_num = int(match.group(1))
                    verse_counter += 1
                    current_verse_lines = []

            # Regular line (verse content)
            elif current_verse_num is not None:
                # Skip continuation markers
                if line == 'மேல்':
                    continue
                current_verse_lines.append(line)

        # Save final verse
        if current_verse_num is not None and current_verse_lines:
            self._add_verse(current_work_id, current_section,
                          verse_counter, current_verse_lines)

    def _parse_dual_star_pattern(self, file_path: str, work_num: int):
        """
        Parse files with *N. section markers (கலிங்கத்துப்பரணி only)

        Pattern:
        ** [Work Title]
        *N. [Level 1 Section]
        *[Level 2 Subsection]
        #N [Verse]

        Build 2-level hierarchy: sections → subsections
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        # Create work
        current_work_id = self._create_work(work_num)
        if not current_work_id:
            return

        # State tracking
        current_level1_section = None
        current_level2_section = None
        current_verse_num = None
        current_verse_lines = []
        verse_counter = 0
        level1_counter = 0
        level2_counter = 0

        for line in lines:
            line = line.strip()

            # Empty line - triggers verse save
            if not line:
                if current_verse_num is not None and current_verse_lines:
                    # Save to current subsection or Level 1 section
                    target_section = current_level2_section if current_level2_section else current_level1_section
                    self._add_verse(current_work_id, target_section,
                                  verse_counter, current_verse_lines)
                    current_verse_num = None
                    current_verse_lines = []
                continue

            # ** Work title (skip)
            if line.startswith('**'):
                continue

            # *N. Level 1 section marker (numbered)
            if re.match(r'\*\d+\.', line):
                # Save previous verse
                if current_verse_num is not None and current_verse_lines:
                    target_section = current_level2_section if current_level2_section else current_level1_section
                    self._add_verse(current_work_id, target_section,
                                  verse_counter, current_verse_lines)
                    current_verse_num = None
                    current_verse_lines = []

                # Extract section number and name
                match = re.match(r'\*(\d+)\.\s*(.*)', line)
                if match:
                    level1_counter += 1
                    section_name = match.group(2).strip()
                    if not section_name:
                        section_name = f"Section {level1_counter}"

                    current_level1_section = self._add_section(
                        current_work_id,
                        level1_counter,
                        section_name,
                        parent_section_id=None,
                        level_type='Section'
                    )
                    current_level2_section = None  # Reset subsection
                    verse_counter = 0
                    level2_counter = 0

            # *[name] Level 2 subsection marker (not numbered)
            elif line.startswith('*') and not re.match(r'\*\d+\.', line):
                # Save previous verse
                if current_verse_num is not None and current_verse_lines:
                    target_section = current_level2_section if current_level2_section else current_level1_section
                    self._add_verse(current_work_id, target_section,
                                  verse_counter, current_verse_lines)
                    current_verse_num = None
                    current_verse_lines = []

                # Extract subsection name
                subsection_name = line[1:].strip()
                if subsection_name:
                    level2_counter += 1
                    current_level2_section = self._add_section(
                        current_work_id,
                        level2_counter,
                        subsection_name,
                        parent_section_id=current_level1_section,
                        level_type='Subsection'
                    )
                    verse_counter = 0

            # #N Verse marker
            elif line.startswith('#'):
                # Save previous verse
                if current_verse_num is not None and current_verse_lines:
                    target_section = current_level2_section if current_level2_section else current_level1_section
                    self._add_verse(current_work_id, target_section,
                                  verse_counter, current_verse_lines)

                # Extract verse number
                match = re.match(r'#(\d+)', line)
                if match:
                    current_verse_num = int(match.group(1))
                    verse_counter += 1
                    current_verse_lines = []

            # Regular line (verse content)
            elif current_verse_num is not None:
                # Skip continuation markers
                if line == 'மேல்':
                    continue
                current_verse_lines.append(line)

        # Save final verse
        if current_verse_num is not None and current_verse_lines:
            target_section = current_level2_section if current_level2_section else current_level1_section
            self._add_verse(current_work_id, target_section,
                          verse_counter, current_verse_lines)

    def bulk_insert(self):
        """
        Phase 2: Bulk insert using PostgreSQL COPY

        Order (critical for foreign keys):
        1. works
        2. work_collections
        3. sections
        4. verses
        5. lines
        6. words
        """
        print("\nPhase 2: Bulk inserting into database...")

        # 1. Insert works
        print(f"  Inserting {len(self.works)} works...")
        self._bulk_copy('works', self.works,
                       ['work_id', 'work_name', 'work_name_tamil', 'author',
                        'author_tamil', 'period', 'canonical_order'])

        # 2. Insert work_collections
        print(f"  Inserting {len(self.work_collections)} work-collection links...")
        self._bulk_copy('work_collections', self.work_collections,
                       ['work_id', 'collection_id', 'position_in_collection'])

        # 3. Insert sections
        print(f"  Inserting {len(self.sections)} sections...")
        self._bulk_copy('sections', self.sections,
                       ['section_id', 'work_id', 'parent_section_id', 'level_type',
                        'level_type_tamil', 'section_number', 'section_name',
                        'section_name_tamil', 'sort_order'])

        # 4. Insert verses
        print(f"  Inserting {len(self.verses)} verses...")
        self._bulk_copy('verses', self.verses,
                       ['verse_id', 'work_id', 'section_id', 'verse_number',
                        'verse_type', 'verse_type_tamil', 'total_lines', 'sort_order'])

        # 5. Insert lines
        print(f"  Inserting {len(self.lines)} lines...")
        self._bulk_copy('lines', self.lines,
                       ['line_id', 'verse_id', 'line_number', 'line_text'])

        # 6. Insert words
        print(f"  Inserting {len(self.words)} words...")
        self._bulk_copy('words', self.words,
                       ['word_id', 'line_id', 'word_position', 'word_text', 'sandhi_split'])

        # Single commit after all data inserted
        self.conn.commit()
        print("✓ Phase 2 complete: All data inserted")

    def _bulk_copy(self, table_name: str, data: list, columns: list):
        """
        Copy data to table using psycopg2.cursor.copy_from()
        Use '\\N' for NULL values, tab-delimited CSV format
        """
        if not data:
            return

        # Create StringIO buffer
        buffer = io.StringIO()
        writer = csv.writer(buffer, delimiter='\t')

        for row in data:
            writer.writerow([row.get(col) if row.get(col) is not None else '\\N'
                           for col in columns])

        buffer.seek(0)

        # Use COPY command
        self.cursor.copy_from(buffer, table_name, columns=columns, null='\\N')

    def close(self):
        """Close database connection"""
        self.cursor.close()
        self.conn.close()


def print_header():
    """Print banner"""
    print("=" * 70)
    print("சிற்றிலக்கியங்கள் (Minor Literary Works) - Bulk Import")
    print("Collection 326: Twenty Minor Literary Works (12th-19th century CE)")
    print("=" * 70)


def print_summary(importer):
    """Print import summary"""
    print("\n" + "=" * 70)
    print("IMPORT SUMMARY")
    print("=" * 70)
    print(f"  Works: {len(importer.works)}")
    print(f"  Sections: {len(importer.sections)}")
    print(f"  Verses: {len(importer.verses)}")
    print(f"  Lines: {len(importer.lines)}")
    print(f"  Words: {len(importer.words)}")
    print("=" * 70)


def main():
    """
    Main execution:
    1. Get database URL
    2. Initialize importer
    3. Create collection 324
    4. Parse all 20 files
    5. Bulk insert
    6. Print summary
    """
    # Get database URL from command line or environment
    if len(sys.argv) > 1:
        db_url = sys.argv[1]
    else:
        db_url = os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@localhost/tamil_literature')

    # Set stdout to UTF-8 for Windows console (Tamil text support)
    if sys.platform == 'win32':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

    print_header()

    # Base directory for source files
    base_dir = Path(__file__).parent.parent / 'Tamil-Source-TamilConcordence' / '8_சிற்றிலக்கியங்கள்'

    # Check if directory exists
    if not base_dir.exists():
        print(f"\n✗ Error: Source directory not found: {base_dir}")
        print("  Please ensure Tamil-Source-TamilConcordence/8_சிற்றிலக்கியங்கள்/ exists")
        sys.exit(1)

    try:
        # Initialize importer
        importer = SitrilakkiyangalBulkImporter(db_url)

        # Create collection 324
        importer._ensure_collection_exists()

        # Parse all 20 files in order
        for work_num in range(1, 21):  # 1-20 inclusive
            file_path = base_dir / WORK_METADATA[work_num]['file']

            if not file_path.exists():
                print(f"  ✗ File not found: {file_path}")
                continue

            importer.parse_file(str(file_path), work_num)

        # Bulk insert
        importer.bulk_insert()

        # Print summary
        print_summary(importer)

        print("\n✓ Import complete! All 20 works imported successfully.")
        print("\nVerification queries:")
        print("  psql -U postgres -d tamil_literature")
        print("  SELECT work_name_tamil FROM works WHERE work_id IN")
        print("    (SELECT work_id FROM work_collections WHERE collection_id = 324);")

    except psycopg2.IntegrityError as e:
        print(f"\n✗ Database integrity error: {e}")
        print("  Possible causes:")
        print("  - Work already exists (run delete script first)")
        print("  - Duplicate IDs (check ID allocation logic)")
        importer.conn.rollback()
        sys.exit(1)

    except FileNotFoundError as e:
        print(f"\n✗ File error: {e}")
        print("  Check Tamil-Source-TamilConcordence/8_சிற்றிலக்கியங்கள்/ directory")
        sys.exit(1)

    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        importer.conn.rollback()
        sys.exit(1)

    finally:
        importer.close()


if __name__ == '__main__':
    main()
