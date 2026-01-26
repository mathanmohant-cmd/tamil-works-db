#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Bharathiyar Poetry (பாரதியார் கவிதைகள்) Bulk Import
Fast 2-phase import using PostgreSQL COPY

Phase 1: Parse text → Build data structures in memory
Phase 2: Bulk COPY into database (1000x faster than INSERT)

Collection ID: 328 (இருபதாம் நூற்றாண்டு தமிழ் இலக்கியம் - 20th Century Tamil Literature)

Works (4 thematic groups of Bharathiyar's poetry):
Poetry of Subramania Bharathiyar (சுப்பிரமணிய பாரதியார்)
spanning 1882-1921 CE

Thematic Organization:
- Work 1: National & Social Reform Poetry (Files 1, 4, 5)
- Work 2: Devotional & Spiritual Poetry (Files 2, 3, 7)
- Work 3: Epic & Narrative Poetry (Files 6, 8, 9)
- Work 4: Modern Free Verse Poetry (File 10)

Structure:
- ** மகாகவி பாரதியார் கவிதைகள் (collection header)
- &N Subsection marker (optional)
- @N Poem identifier
- ** Metadata markers (ராகம், தாளம், பல்லவி, சரணங்கள், song type, notes)
- #N Verse markers (can start from #0 for pallavi)
- Verse lines (variable length, separated by blank lines)

IMPORTANT: This parser stores metadata in JSONB columns:
- sections.metadata: Musical notation (ராகம், தாளம்), song type, meter, translation notes
- verses.metadata: Verse type (பல்லவி/சரணங்கள்), special numbers (#0)
"""

import re
import psycopg2
from pathlib import Path
import csv
import io
import sys
import os
import json
from word_cleaning import split_and_clean_words

# Work metadata for all 4 thematic groups
WORK_METADATA = {
    1: {
        'work_name': 'Bharathiyar National and Social Reform Poetry',
        'work_name_tamil': 'பாரதியார் தேசிய மற்றும் சமூகச் சீர்திருத்தக் கவிதைகள்',
        'author': 'Subramania Bharathiyar',
        'author_tamil': 'சுப்பிரமணிய பாரதியார்',
        'period': '1882-1921 CE',
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
        'period': '1882-1921 CE',
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
        'period': '1882-1921 CE',
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
        'period': '1882-1921 CE',
        'canonical_order': 328004,
        'position_in_collection': 4,
        'files': [10],
        'file_names': {
            10: '10.வசன கவிதை.txt'
        },
        'description': 'Modern free verse poetry by Bharathiyar'
    }
}

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


class BharathiyarBulkImporter:
    """
    Imports Bharathiyar poetry using 2-phase bulk COPY pattern with JSONB metadata.

    Hierarchy:
    - Collection 328: பாரதியார் படைப்புகள்
      - Work 1-4: Thematic groups
        - Section L1: &N markers (தேசீய கீதங்கள், பல்வகைப் பாடல்கள், etc.)
          - Section L2 (Poem): @N markers (with JSONB metadata)
            - Verses: #N markers (with JSONB metadata for verse types)
              - Lines: Individual lines
                - Words: Word segmentation

    Note: File-level sections are NOT created because every file starts with a &N marker
    that duplicates the filename. The &N sections are created directly under the work.
    """

    def __init__(self, db_connection_string="postgresql://postgres:postgres@localhost/tamil_literature"):
        """Initialize with database connection and query MAX IDs"""
        self.conn = psycopg2.connect(db_connection_string)
        self.cursor = self.conn.cursor()

        # Query MAX IDs from ALL tables ONCE (critical pattern from CLAUDE.md)
        # NEVER query inside loops - causes duplicate IDs!

        self.cursor.execute("SELECT COALESCE(MAX(collection_id), 0) FROM collections")
        self.collection_id = self.cursor.fetchone()[0] + 1

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

        # In-memory data structures (lists of dicts)
        self.collections_to_create = []
        self.works = []
        self.work_collections = []
        self.sections = []
        self.verses = []
        self.lines = []
        self.words = []

        # Counters for progress reporting
        self.section_counter = 0
        self.verse_counter = 0
        self.line_counter = 0
        self.word_counter = 0

        print(f"Initialized BharathiyarBulkImporter")
        print(f"  Next IDs: work={self.work_id}, section={self.section_id}, verse={self.verse_id}")
        print(f"  Collection 328 will be created if not exists")

    def _ensure_collection_exists(self):
        """Check if collection 328 exists, create if not"""
        self.cursor.execute("SELECT collection_id FROM collections WHERE collection_id = 328")
        existing = self.cursor.fetchone()

        if not existing:
            print(f"\nCreating Collection 328 (இருபதாம் நூற்றாண்டு தமிழ் இலக்கியம் - Modern Tamil Literature)")
            self.collections_to_create.append((
                328,
                'Bharathiyar Works',
                'பாரதியார் படைப்புகள்',
                'period',
                'Poetry of Subramania Bharathiyar (1882-1921 CE) - National, devotional, and social reform poetry',
                1,  # Parent: தமிழ் இலக்கியம் (designated filter collection)
                7   # After Thirumurai=1, NDPD=2, Devotional=3, Five Minor Epics=4, நீதிநூல்கள்=5, சித்தர் பாடல்கள்=6
            ))
            self.collection_id = 328
            print(f"  [OK] Collection 328 will be created")
        else:
            print(f"  Found existing collection 328")
            self.collection_id = 328

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
            print(f"  [ERROR] Work {metadata['work_name']} already exists (ID: {existing[0]})")
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
            'description': metadata.get('description', ''),
            'canonical_order': metadata['canonical_order']
        })

        # Link work to collection 328
        self.work_collections.append({
            'work_id': work_id,
            'collection_id': self.collection_id,
            'position_in_collection': metadata['position_in_collection']
        })

        print(f"  Created work: {metadata['work_name_tamil']} (ID: {work_id}, Canonical: {metadata['canonical_order']})")
        return work_id

    def _parse_metadata_line(self, line: str, poem_metadata: dict, verse_metadata: dict):
        """Parse ** metadata markers and accumulate into metadata dicts"""
        content = line.replace('**', '').strip()

        # Skip main header
        if 'மகாகவி பாரதியார்' in content:
            return

        # Musical metadata
        if 'ராகம்' in content:
            # Extract: "ராகம் - நாதநாமக்கிரியை" or "ராகம்: நாதநாமக்கிரியை"
            match = re.search(r'ராகம்\s*[-:]\s*(.+)', content)
            if match:
                poem_metadata['raagam'] = match.group(1).strip()

        elif 'தாளம்' in content:
            # Extract: "தாளம் - ஆதி" or "தாளம்: ஆதி"
            match = re.search(r'தாளம்\s*[-:]\s*(.+)', content)
            if match:
                poem_metadata['thaalam'] = match.group(1).strip()

        # Verse structure markers
        elif content == 'பல்லவி':
            verse_metadata['verse_type'] = 'pallavi'

        elif content == 'சரணங்கள்' or content == 'சரணம்':
            verse_metadata['verse_type'] = 'charanam'

        elif content == 'அனுபல்லவி':
            verse_metadata['verse_type'] = 'anupallavi'

        # Song type (in parentheses)
        elif content.startswith('(') and content.endswith(')'):
            poem_metadata['song_type'] = content[1:-1].replace('"', "'")

        # Translation notes (in square brackets)
        elif content.startswith('['):
            poem_metadata['notes'] = content.replace('"', "'")

        # Generic meter/descriptive metadata
        else:
            # Could be meter like "நொண்டிச் சிந்து" or other descriptive text
            # Escape double quotes to prevent JSON syntax errors
            if 'meter' not in poem_metadata:
                poem_metadata['meter'] = content.replace('"', "'")  # Replace double quotes with single quotes

    def _add_section(self, work_id: int, level_type: str, level_type_tamil: str,
                     section_number: int, section_name: str, section_name_tamil: str,
                     parent_section_id: int = None, metadata: dict = None) -> int:
        """Add section with optional metadata to in-memory list and return section_id"""
        section_id = self.section_id
        self.section_id += 1  # Manual increment
        self.section_counter += 1

        self.sections.append({
            'section_id': section_id,
            'work_id': work_id,
            'parent_section_id': parent_section_id,
            'level_type': level_type,
            'level_type_tamil': level_type_tamil,
            'section_number': section_number,
            'section_name': section_name,
            'section_name_tamil': section_name_tamil,
            'sort_order': self.section_counter,
            'metadata': metadata if metadata else None
        })

        return section_id

    def _add_verse(self, work_id: int, section_id: int, verse_number: int,
                   verse_lines: list, verse_metadata: dict = None):
        """Add verse with lines and words to in-memory lists

        Note: verse_number is now a sequential counter, not the original #N from file
        """
        if not verse_lines:
            return

        verse_id = self.verse_id
        self.verse_id += 1  # Manual increment
        self.verse_counter += 1

        # Check if this was originally verse #0 (pallavi/refrain) from metadata
        if verse_metadata and verse_metadata.get('original_verse_num') == 0:
            if 'verse_type' not in verse_metadata:
                verse_metadata['verse_type'] = 'pallavi'

        self.verses.append({
            'verse_id': verse_id,
            'work_id': work_id,
            'section_id': section_id,
            'verse_number': verse_number,
            'verse_type': None,  # Not used for poetry
            'verse_type_tamil': None,
            'total_lines': len(verse_lines),
            'sort_order': self.verse_counter,
            'metadata': verse_metadata if verse_metadata else None
        })

        # Add lines and words
        for line_num, line_text in enumerate(verse_lines, start=1):
            if not line_text.strip():
                continue

            line_id = self.line_id
            self.line_id += 1
            self.line_counter += 1

            self.lines.append({
                'line_id': line_id,
                'verse_id': verse_id,
                'line_number': line_num,
                'line_text': line_text.strip()
            })

            # Word segmentation
            words = split_and_clean_words(line_text)
            for word_pos, word_text in enumerate(words, start=1):
                word_id = self.word_id
                self.word_id += 1
                self.word_counter += 1

                self.words.append({
                    'word_id': word_id,
                    'line_id': line_id,
                    'word_position': word_pos,
                    'word_text': word_text,
                    'sandhi_split': None  # Future enhancement
                })

    def parse_file(self, file_path: Path, work_id: int, file_num: int):
        """Parse one Bharathiyar poetry file with state machine

        Note: File-level sections are NOT created because every file starts with
        a &N marker that has the same name as the filename (creating redundant duplicates).
        The &N sections are created directly under the work instead.
        """
        print(f"\n  Parsing file {file_num}: {file_path.name}")

        # State variables
        level1_section_id = None  # &N section (directly under work)
        level2_section_id = None  # @N poem
        current_verse_num = None
        current_verse_lines = []

        # Metadata accumulators
        poem_metadata = {}      # For next poem
        verse_metadata = {}     # For current verse

        # Parsing state
        in_verse = False
        poem_counter = 0
        verse_counter_in_poem = 0
        verse_sequential_num = 0  # Sequential counter for unique verse numbers

        with open(file_path, 'r', encoding='utf-8') as f:
            for line_raw in f:
                line = line_raw.strip()

                # EMPTY LINE → Save current verse
                if not line:
                    if in_verse and current_verse_lines:
                        verse_sequential_num += 1
                        self._add_verse(work_id, level2_section_id, verse_sequential_num,
                                      current_verse_lines, verse_metadata.copy())
                        current_verse_lines = []
                        verse_metadata = {}  # Reset verse metadata after use
                        in_verse = False
                    continue

                # &N MARKER → Create Level 1 section (directly under work)
                if line.startswith('&'):
                    # Save any pending verse first
                    if in_verse and current_verse_lines:
                        verse_sequential_num += 1
                        self._add_verse(work_id, level2_section_id, verse_sequential_num,
                                      current_verse_lines, verse_metadata.copy())
                        current_verse_lines = []
                        verse_metadata = {}
                        in_verse = False

                    # Extract section number and name
                    match = re.match(r'&(\d+)\s+(.*)', line)
                    if match:
                        section_num = int(match.group(1))
                        section_name = match.group(2).strip()

                        level1_section_id = self._add_section(
                            work_id=work_id,
                            level_type='Section',
                            level_type_tamil='பிரிவு',
                            section_number=section_num,
                            section_name=section_name,
                            section_name_tamil=section_name,
                            parent_section_id=None  # Directly under work
                        )
                    continue

                # @N MARKER → Create Level 2 poem (under &N section)
                if line.startswith('@'):
                    # Save any pending verse first
                    if in_verse and current_verse_lines:
                        verse_sequential_num += 1
                        self._add_verse(work_id, level2_section_id, verse_sequential_num,
                                      current_verse_lines, verse_metadata.copy())
                        current_verse_lines = []
                        verse_metadata = {}
                        in_verse = False

                    # Extract poem number and title
                    match = re.match(r'@(\d+)\s*(.*)', line)
                    if match:
                        poem_num = int(match.group(1))
                        poem_title = match.group(2).strip()
                        poem_counter += 1

                        # Create Level 2 section (poem) with accumulated metadata
                        # Parent is the &N section (level1_section_id), or None if no &N section
                        parent = level1_section_id

                        # Add poem_number to metadata
                        if poem_metadata:
                            poem_metadata['poem_number'] = poem_num
                        else:
                            poem_metadata = {'poem_number': poem_num}

                        level2_section_id = self._add_section(
                            work_id=work_id,
                            level_type='Poem',
                            level_type_tamil='கவிதை',
                            section_number=poem_num,
                            section_name=poem_title,
                            section_name_tamil=poem_title,
                            parent_section_id=parent,
                            metadata=poem_metadata.copy()
                        )

                        # Reset poem metadata for next poem
                        poem_metadata = {}
                        verse_counter_in_poem = 0
                        verse_sequential_num = 0  # Reset for new poem
                    continue

                # ** MARKER → Accumulate metadata
                if line.startswith('**'):
                    self._parse_metadata_line(line, poem_metadata, verse_metadata)
                    continue

                # #N MARKER → Start new verse
                if line.startswith('#'):
                    # Save any pending verse first
                    if in_verse and current_verse_lines:
                        verse_sequential_num += 1
                        self._add_verse(work_id, level2_section_id, verse_sequential_num,
                                      current_verse_lines, verse_metadata.copy())
                        current_verse_lines = []
                        # Don't reset verse_metadata here - might still be accumulating

                    # Extract verse number (for metadata only, use sequential for database)
                    match = re.match(r'#(\d+)', line)
                    if match:
                        current_verse_num = int(match.group(1))
                        verse_counter_in_poem += 1
                        in_verse = True
                        current_verse_lines = []

                        # Store original verse number in metadata if it's special (#0)
                        if current_verse_num == 0 and 'special_number' not in verse_metadata:
                            verse_metadata['original_verse_num'] = 0
                    continue

                # REGULAR LINE → Accumulate verse content
                if in_verse:
                    current_verse_lines.append(line)

        # Save final pending verse
        if in_verse and current_verse_lines:
            verse_sequential_num += 1
            self._add_verse(work_id, level2_section_id, verse_sequential_num,
                          current_verse_lines, verse_metadata.copy())

        print(f"    Parsed {poem_counter} poems")

    def bulk_insert(self):
        """Phase 2: Bulk COPY all data into database"""
        print(f"\n{'='*60}")
        print(f"Phase 2: Bulk inserting into database")
        print(f"{'='*60}")

        try:
            # 1. Insert collections
            if self.collections_to_create:
                print(f"\n1. Inserting {len(self.collections_to_create)} collection(s)...")
                for collection_data in self.collections_to_create:
                    self.cursor.execute("""
                        INSERT INTO collections
                        (collection_id, collection_name, collection_name_tamil, collection_type, description, parent_collection_id, sort_order)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """, collection_data)
                print(f"  [OK] Collections inserted")

            # 2. Insert works
            print(f"\n2. Inserting {len(self.works)} work(s)...")
            works_buffer = io.StringIO()
            writer = csv.writer(works_buffer, delimiter='\t')
            for work in self.works:
                writer.writerow([
                    work['work_id'],
                    work['work_name'],
                    work['work_name_tamil'],
                    work['author'],
                    work['author_tamil'],
                    work['period'],
                    work.get('description', ''),
                    work['canonical_order']
                ])
            works_buffer.seek(0)
            self.cursor.copy_from(works_buffer, 'works',
                                columns=['work_id', 'work_name', 'work_name_tamil', 'author',
                                        'author_tamil', 'period', 'description', 'canonical_order'],
                                null='')
            print(f"  [OK] {len(self.works)} works inserted")

            # 3. Insert work_collections
            print(f"\n3. Inserting {len(self.work_collections)} work-collection links...")
            wc_buffer = io.StringIO()
            writer = csv.writer(wc_buffer, delimiter='\t')
            for wc in self.work_collections:
                writer.writerow([wc['work_id'], wc['collection_id'], wc['position_in_collection']])
            wc_buffer.seek(0)
            self.cursor.copy_from(wc_buffer, 'work_collections',
                                columns=['work_id', 'collection_id', 'position_in_collection'],
                                null='')
            print(f"  [OK] Work-collection links inserted")

            # 4. Insert sections (with JSONB metadata)
            print(f"\n4. Inserting {len(self.sections)} section(s) with JSONB metadata...")
            sections_buffer = io.StringIO()
            for section in self.sections:
                # Serialize metadata to JSON
                metadata_json = ''
                if section.get('metadata'):
                    metadata_json = json.dumps(section['metadata'], ensure_ascii=False)
                    metadata_json = metadata_json.replace('\t', ' ')  # Remove tabs for COPY

                # Manual row formatting (CSV writer breaks JSONB)
                row = [
                    str(section['section_id']),
                    str(section['work_id']),
                    str(section['parent_section_id']) if section.get('parent_section_id') else '',
                    section['level_type'],
                    section['level_type_tamil'],
                    str(section['section_number']),
                    section.get('section_name', ''),
                    section.get('section_name_tamil', ''),
                    str(section['sort_order']),
                    metadata_json
                ]
                sections_buffer.write('\t'.join(row) + '\n')

            sections_buffer.seek(0)
            self.cursor.copy_from(sections_buffer, 'sections',
                                columns=['section_id', 'work_id', 'parent_section_id', 'level_type',
                                        'level_type_tamil', 'section_number', 'section_name',
                                        'section_name_tamil', 'sort_order', 'metadata'],
                                null='')
            print(f"  [OK] {len(self.sections)} sections inserted")

            # 5. Insert verses (with JSONB metadata)
            print(f"\n5. Inserting {len(self.verses)} verse(s) with JSONB metadata...")
            verses_buffer = io.StringIO()
            for verse in self.verses:
                # Serialize metadata to JSON
                metadata_json = ''
                if verse.get('metadata'):
                    metadata_json = json.dumps(verse['metadata'], ensure_ascii=False)
                    metadata_json = metadata_json.replace('\t', ' ')

                row = [
                    str(verse['verse_id']),
                    str(verse['work_id']),
                    str(verse['section_id']),
                    str(verse['verse_number']),
                    verse.get('verse_type', '') or '',
                    verse.get('verse_type_tamil', '') or '',
                    str(verse['total_lines']),
                    str(verse['sort_order']),
                    metadata_json
                ]
                verses_buffer.write('\t'.join(row) + '\n')

            verses_buffer.seek(0)
            self.cursor.copy_from(verses_buffer, 'verses',
                                columns=['verse_id', 'work_id', 'section_id', 'verse_number',
                                        'verse_type', 'verse_type_tamil', 'total_lines',
                                        'sort_order', 'metadata'],
                                null='')
            print(f"  [OK] {len(self.verses)} verses inserted")

            # 6. Insert lines
            print(f"\n6. Inserting {len(self.lines)} line(s)...")
            lines_buffer = io.StringIO()
            writer = csv.writer(lines_buffer, delimiter='\t')
            for line in self.lines:
                writer.writerow([line['line_id'], line['verse_id'], line['line_number'], line['line_text']])
            lines_buffer.seek(0)
            self.cursor.copy_from(lines_buffer, 'lines',
                                columns=['line_id', 'verse_id', 'line_number', 'line_text'],
                                null='')
            print(f"  [OK] {len(self.lines)} lines inserted")

            # 7. Insert words
            print(f"\n7. Inserting {len(self.words)} word(s)...")
            words_buffer = io.StringIO()
            writer = csv.writer(words_buffer, delimiter='\t')
            for word in self.words:
                writer.writerow([
                    word['word_id'],
                    word['line_id'],
                    word['word_position'],
                    word['word_text'],
                    word.get('sandhi_split', '') or ''
                ])
            words_buffer.seek(0)
            self.cursor.copy_from(words_buffer, 'words',
                                columns=['word_id', 'line_id', 'word_position', 'word_text', 'sandhi_split'],
                                null='')
            print(f"  [OK] {len(self.words)} words inserted")

            # Commit all changes
            self.conn.commit()
            print(f"\n{'='*60}")
            print(f"✓ SUCCESS: All data committed to database")
            print(f"{'='*60}")

        except Exception as e:
            print(f"\n✗ ERROR during bulk insert: {e}")
            self.conn.rollback()
            raise

    def run(self, source_dir: Path):
        """Main execution: Parse all files and bulk insert"""
        print(f"\n{'='*60}")
        print(f"Bharathiyar Poetry Bulk Import")
        print(f"{'='*60}")

        # Ensure collection 328 exists
        self._ensure_collection_exists()

        print(f"\n{'='*60}")
        print(f"Phase 1: Parsing files into memory")
        print(f"{'='*60}")

        # Work 1: National & Social Reform (Files 1, 4, 5, 11)
        print(f"\nWork 1: National & Social Reform Poetry")
        work1_id = self._create_work(1)
        if work1_id:
            for file_num in WORK_METADATA[1]['files']:
                file_path = source_dir / WORK_METADATA[1]['file_names'][file_num]
                if file_path.exists():
                    self.parse_file(file_path, work1_id, file_num)
                else:
                    print(f"  [WARNING] File not found: {file_path}")

        # Work 2: Devotional & Spiritual (Files 2, 3, 7)
        print(f"\nWork 2: Devotional & Spiritual Poetry")
        work2_id = self._create_work(2)
        if work2_id:
            for file_num in WORK_METADATA[2]['files']:
                file_path = source_dir / WORK_METADATA[2]['file_names'][file_num]
                if file_path.exists():
                    self.parse_file(file_path, work2_id, file_num)
                else:
                    print(f"  [WARNING] File not found: {file_path}")

        # Work 3: Epic & Narrative (Files 6, 8, 9)
        print(f"\nWork 3: Epic & Narrative Poetry")
        work3_id = self._create_work(3)
        if work3_id:
            for file_num in WORK_METADATA[3]['files']:
                file_path = source_dir / WORK_METADATA[3]['file_names'][file_num]
                if file_path.exists():
                    self.parse_file(file_path, work3_id, file_num)
                else:
                    print(f"  [WARNING] File not found: {file_path}")

        # Work 4: Modern Free Verse (File 10)
        print(f"\nWork 4: Modern Free Verse Poetry")
        work4_id = self._create_work(4)
        if work4_id:
            for file_num in WORK_METADATA[4]['files']:
                file_path = source_dir / WORK_METADATA[4]['file_names'][file_num]
                if file_path.exists():
                    self.parse_file(file_path, work4_id, file_num)
                else:
                    print(f"  [WARNING] File not found: {file_path}")

        # Summary
        print(f"\n{'='*60}")
        print(f"Parsing Complete - Summary:")
        print(f"{'='*60}")
        print(f"  Works: {len(self.works)}")
        print(f"  Sections: {len(self.sections)}")
        print(f"  Verses: {len(self.verses)}")
        print(f"  Lines: {len(self.lines)}")
        print(f"  Words: {len(self.words)}")

        # Bulk insert
        self.bulk_insert()

        # Close connection
        self.cursor.close()
        self.conn.close()
        print(f"\nDatabase connection closed")


def main():
    """Main entry point"""
    import sys

    # Set stdout to UTF-8 for Windows console (Tamil text support)
    if sys.platform == 'win32':
        import codecs
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, errors='replace')
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, errors='replace')

    # Get database URL from command line or environment or use default
    if len(sys.argv) > 1:
        db_url = sys.argv[1]
    else:
        db_url = os.environ.get('DATABASE_URL', 'postgresql://postgres:postgres@localhost/tamil_literature')

    # Source directory
    source_dir = Path(__file__).parent.parent / 'Tamil-Source-TamilConcordence' / '10_பாரதியார்_கவிதைகள்'

    if not source_dir.exists():
        print(f"ERROR: Source directory not found: {source_dir}")
        sys.exit(1)

    print(f"Database URL: {db_url}")
    print(f"Source directory: {source_dir}")

    # Run import
    try:
        importer = BharathiyarBulkImporter(db_url)
        importer.run(source_dir)
        print(f"\n✓ Import completed successfully!")
    except Exception as e:
        print(f"\n✗ Import failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
