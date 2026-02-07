#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ethical Literature (நீதிநூல்கள்) Bulk Import
Fast 2-phase import using PostgreSQL COPY

Phase 1: Parse text → Build data structures in memory
Phase 2: Bulk COPY into database (1000x faster than INSERT)

Collection ID: 325 (நீதிநூல்கள் - Ethical Literature)

Works (21 ethical literature texts):
Includes works by Auvaiyar, Siva Prakasar, Bharathiyar, and others
spanning 3rd-20th century CE

Structure:
- &N Work identifier (N=1-21)
- @N Section markers
- ** Verse metadata/topics (NOT Level 2 sections - stored as metadata only)
- #N Verse markers
- File 21 special: Verses renumbered per section (NOT continuous #1-#1332)
"""

import re
import psycopg2
from pathlib import Path
import csv
import io
import sys
import os
from word_cleaning import split_and_clean_words

# Work metadata for all 21 works
WORK_METADATA = {
    1: {
        'work_name': 'Aathichudi',
        'work_name_tamil': 'ஆத்திசூடி',
        'author': 'Auvaiyar II',
        'author_tamil': 'ஔவையார்',
        'period': '12th century CE',
        'canonical_order': 325001,
        'position_in_collection': 1,
        'file': '1.ஆத்திசூடி.txt'
    },
    2: {
        'work_name': 'Konrai Venthan',
        'work_name_tamil': 'கொன்றைவேந்தன்',
        'author': 'Auvaiyar II',
        'author_tamil': 'ஔவையார்',
        'period': '12th century CE',
        'canonical_order': 325002,
        'position_in_collection': 2,
        'file': '2.கொன்றைவேந்தன்.txt'
    },
    3: {
        'work_name': 'Moodhurai (Vaakkundaam)',
        'work_name_tamil': 'மூதுரை (வாக்குண்டாம்)',
        'author': 'Auvaiyar II',
        'author_tamil': 'ஔவையார்',
        'period': '12th century CE',
        'canonical_order': 325003,
        'position_in_collection': 3,
        'file': '3.மூதுரை (வாக்குண்டாம்).txt'
    },
    4: {
        'work_name': 'Nalvazhi',
        'work_name_tamil': 'நல்வழி',
        'author': 'Auvaiyar II',
        'author_tamil': 'ஔவையார்',
        'period': '12th century CE',
        'canonical_order': 325004,
        'position_in_collection': 4,
        'file': '4.நல்வழி.txt'
    },
    5: {
        'work_name': 'Vetri Vetkai (Narunthokai)',
        'work_name_tamil': 'வெற்றி வேற்கை (நறுந்தொகை)',
        'author': 'Unknown',
        'author_tamil': 'அறியப்படாத ஆசிரியர்',
        'period': '3rd-6th century CE',
        'canonical_order': 325005,
        'position_in_collection': 5,
        'file': '5.வெற்றி வேற்கை (நறுந்தொகை).txt'
    },
    6: {
        'work_name': 'Ulaga Neethi',
        'work_name_tamil': 'உலக நீதி',
        'author': 'Unknown',
        'author_tamil': 'அறியப்படாத ஆசிரியர்',
        'period': '6th-10th century CE',
        'canonical_order': 325006,
        'position_in_collection': 6,
        'file': '6.உலக நீதி.txt'
    },
    7: {
        'work_name': 'Neethineeri Vilakkam',
        'work_name_tamil': 'நீதிநெறி விளக்கம்',
        'author': 'Unknown',
        'author_tamil': 'அறியப்படாத ஆசிரியர்',
        'period': '6th-10th century CE',
        'canonical_order': 325007,
        'position_in_collection': 7,
        'file': '7.நீதிநெறி விளக்கம்.txt'
    },
    8: {
        'work_name': 'Araneri Chaaram',
        'work_name_tamil': 'அறநெறிச்சாரம்',
        'author': 'Unknown',
        'author_tamil': 'அறியப்படாத ஆசிரியர்',
        'period': '6th-10th century CE',
        'canonical_order': 325008,
        'position_in_collection': 8,
        'file': '8.அறநெறிச்சாரம்.txt'
    },
    9: {
        'work_name': 'Neethi Nool',
        'work_name_tamil': 'நீதி நூல்',
        'author': 'Munusep Vedhanayagam Pillai',
        'author_tamil': 'முனிசீப் வேதநாயகம் பிள்ளை',
        'period': '19th century CE',
        'canonical_order': 325009,
        'position_in_collection': 9,
        'file': '9.நீதி நூல்.txt'
    },
    10: {
        'work_name': 'Nanneri',
        'work_name_tamil': 'நன்னெறி',
        'author': 'Siva Prakasar',
        'author_tamil': 'சிவப்பிரகாசர்',
        'period': '17th-18th century CE',
        'canonical_order': 325010,
        'position_in_collection': 10,
        'file': '10.நன்னெறி.txt'
    },
    11: {
        'work_name': 'Neethi Chudamani',
        'work_name_tamil': 'நீதி சூடாமணி',
        'author': 'Unknown',
        'author_tamil': 'அறியப்படாத ஆசிரியர்',
        'period': '10th-15th century CE',
        'canonical_order': 325011,
        'position_in_collection': 11,
        'file': '11.நீதி சூடாமணி.txt'
    },
    12: {
        'work_name': 'Muthumozhi Venpa',
        'work_name_tamil': 'முதுமொழி வெண்பா',
        'author': 'Unknown',
        'author_tamil': 'அறியப்படாத ஆசிரியர்',
        'period': '10th-15th century CE',
        'canonical_order': 325012,
        'position_in_collection': 12,
        'file': '12.முதுமொழி வெண்பா.txt'
    },
    13: {
        'work_name': 'Viveka Chinthamani',
        'work_name_tamil': 'விவேக சிந்தாமணி',
        'author': 'Unknown',
        'author_tamil': 'அறியப்படாத ஆசிரியர்',
        'period': '10th-15th century CE',
        'canonical_order': 325013,
        'position_in_collection': 13,
        'file': '13.விவேக.txt'
    },
    14: {
        'work_name': 'Aathichudi Venpa',
        'work_name_tamil': 'ஆத்திசூடி வெண்பா',
        'author': 'Unknown',
        'author_tamil': 'அறியப்படாத ஆசிரியர்',
        'period': '12th-17th century CE',
        'canonical_order': 325014,
        'position_in_collection': 14,
        'file': '14.ஆத்திசூடி வெண்பா.txt'
    },
    15: {
        'work_name': 'Neethi Venpa',
        'work_name_tamil': 'நீதி வெண்பா',
        'author': 'Unknown',
        'author_tamil': 'அறியப்படாத ஆசிரியர்',
        'period': '12th-17th century CE',
        'canonical_order': 325015,
        'position_in_collection': 15,
        'file': '15.நீதி வெண்பா.txt'
    },
    16: {
        'work_name': 'Nanmadhi Venpa',
        'work_name_tamil': 'நன்மதி வெண்பா',
        'author': 'Unknown',
        'author_tamil': 'அறியப்படாத ஆசிரியர்',
        'period': '12th-17th century CE',
        'canonical_order': 325016,
        'position_in_collection': 16,
        'file': '16.நன்மதி வெண்பா.txt'
    },
    17: {
        'work_name': 'Arungalach Cheppu',
        'work_name_tamil': 'அருங்கலச்செப்பு',
        'author': 'Unknown',
        'author_tamil': 'அறியப்படாத ஆசிரியர்',
        'period': '10th-15th century CE',
        'canonical_order': 325017,
        'position_in_collection': 17,
        'file': '17.அருங்கலச்செப்பு.txt'
    },
    18: {
        'work_name': 'Mudhumozhimael Vaippu',
        'work_name_tamil': 'முதுமொழிமேல் வைப்பு',
        'author': 'Unknown',
        'author_tamil': 'அறியப்படாத ஆசிரியர்',
        'period': '10th-15th century CE',
        'canonical_order': 325018,
        'position_in_collection': 18,
        'file': '18.முதுமொழிமேல் வைப்பு.txt'
    },
    19: {
        'work_name': 'Pudhiya Aathichudi',
        'work_name_tamil': 'புதிய ஆத்திசூடி',
        'author': 'Bharathiyar',
        'author_tamil': 'பாரதியார்',
        'period': '20th century CE',
        'canonical_order': 325019,
        'position_in_collection': 19,
        'file': '19.புதிய ஆத்திசூடி.txt'
    },
    20: {
        'work_name': 'Ilaiyaar Aathichudi',
        'work_name_tamil': 'இளையார் ஆத்திசூடி',
        'author': 'Unknown',
        'author_tamil': 'அறியப்படாத ஆசிரியர்',
        'period': '15th-19th century CE',
        'canonical_order': 325020,
        'position_in_collection': 20,
        'file': '20.இளையார் ஆத்திசூடி.txt'
    },
    21: {
        'work_name': 'Thirukkural Kumaresa Venpa',
        'work_name_tamil': 'திருக்குறள் குமரேச வெண்பா',
        'author': 'Kumaresa Guruparar',
        'author_tamil': 'குமரேச குருபரர்',
        'period': '18th-19th century CE',
        'canonical_order': 325021,
        'position_in_collection': 21,
        'file': '21.திருக்குறள் குமரேச வெண்பா.txt'
    }
}


class NeethinoolkalBulkImporter:
    """Import all 21 ethical literature works using 2-phase bulk COPY pattern"""

    def __init__(self, db_connection_string: str):
        """Initialize importer and query MAX IDs from ALL tables"""
        self.conn = psycopg2.connect(db_connection_string)
        self.cursor = self.conn.cursor()
        self.collection_id = 325

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

        # Track current parsing state
        self.current_work_id = None
        self.current_section = None

    def _ensure_collection_exists(self):
        """Create collection 325 if missing"""
        # Check if collection exists
        self.cursor.execute("SELECT collection_id FROM collections WHERE collection_id = %s",
                          (self.collection_id,))
        existing = self.cursor.fetchone()

        if not existing:
            print(f"  Creating நீதிநூல்கள் collection (ID: {self.collection_id})...")
            self.cursor.execute("""
                INSERT INTO collections (
                    collection_id, collection_name, collection_name_tamil,
                    collection_type, description, parent_collection_id, sort_order
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                self.collection_id,
                'Ethical Literature',
                'நீதிநூல்கள்',
                'genre',
                'Twenty-one ethical literature works spanning 3rd-20th century CE, including Auvaiyar\'s didactic poetry and Thirukkural commentaries',
                1,  # Parent: தமிழ் இலக்கியம் (designated filter collection)
                5   # After Thirumurai=1, NDPD=2, Devotional=3, சிற்றிலக்கியங்கள்=4
            ))
            print(f"  [OK] Collection created (will commit with bulk data)")
        else:
            print(f"  Found existing நீதிநூல்கள் collection (ID: {self.collection_id})")

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

        # Link work to collection 325
        self.work_collections.append({
            'work_id': work_id,
            'collection_id': self.collection_id,
            'position_in_collection': metadata['position_in_collection']
        })

        print(f"  Created work: {metadata['work_name_tamil']} (ID: {work_id}, Canonical: {metadata['canonical_order']})")
        return work_id

    def _add_section(self, work_id: int, section_num: int, section_name: str) -> int:
        """Add section to in-memory list and return section_id"""
        section_id = self.section_id
        self.section_id += 1  # Manual increment

        self.sections.append({
            'section_id': section_id,
            'work_id': work_id,
            'parent_section_id': None,  # No parent - all sections are Level 1
            'level_type': 'Section',
            'level_type_tamil': 'பகுதி',
            'section_number': section_num,
            'section_name': section_name,
            'section_name_tamil': section_name,
            'sort_order': section_num
        })

        return section_id

    def _add_verse(self, work_id: int, section_id: int, verse_num: int,
                   verse_lines: list, topic: str = None):
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

        # Note: ** topic metadata is NOT stored in database per plan
        # (schema doesn't have verse metadata column)

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
        """
        Parse one work file (Phase 1: Parse into memory)

        Structure:
        - &N Work identifier
        - @N Section marker
        - ** Verse metadata/topic (NOT a section - just metadata)
        - #N Verse marker
        - Lines accumulate until blank line or next marker
        """
        print(f"\nParsing File {work_num}: {Path(file_path).name}")

        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        # State tracking
        current_work_id = None
        current_section = None
        current_verse_topic = None  # From ** marker
        current_verse_num = None
        current_verse_lines = []
        verse_counter_per_section = 0  # For File 21 renumbering

        for line in lines:
            line = line.strip()

            # Empty line - triggers verse save
            if not line:
                if current_verse_num is not None and current_verse_lines:
                    self._add_verse(current_work_id, current_section,
                                  verse_counter_per_section,  # Renumbered
                                  current_verse_lines, current_verse_topic)
                    current_verse_num = None
                    current_verse_lines = []
                    current_verse_topic = None
                continue

            # &N Work identifier
            if line.startswith('&'):
                # Save previous verse
                if current_verse_num is not None and current_verse_lines:
                    self._add_verse(current_work_id, current_section,
                                  verse_counter_per_section,
                                  current_verse_lines, current_verse_topic)

                # Extract work number from &N pattern (may or may not have dot)
                match = re.match(r'&(\d+)\.?\s*(.*)', line)
                if match:
                    file_work_num = int(match.group(1))
                    if file_work_num != work_num:
                        print(f"  [WARNING] File work number {file_work_num} doesn't match expected {work_num}")

                    # Create work
                    current_work_id = self._create_work(work_num)
                    current_section = None
                    current_verse_num = None
                    current_verse_lines = []
                    current_verse_topic = None
                    verse_counter_per_section = 0

            # @N Section marker
            elif line.startswith('@'):
                # Save previous verse
                if current_verse_num is not None and current_verse_lines:
                    self._add_verse(current_work_id, current_section,
                                  verse_counter_per_section,
                                  current_verse_lines, current_verse_topic)
                    current_verse_num = None
                    current_verse_lines = []
                    current_verse_topic = None

                # Extract section number and name from @N. or @N pattern
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
                    verse_counter_per_section = 0  # Reset for new section (File 21 renumbering)

            # ** Verse metadata/topic marker
            elif line.startswith('**'):
                # Skip collection header "** நீதி நூல்கள்"
                if 'நீதி நூல்கள்' in line:
                    continue

                # Save previous verse if any
                if current_verse_num is not None and current_verse_lines:
                    self._add_verse(current_work_id, current_section,
                                  verse_counter_per_section,
                                  current_verse_lines, current_verse_topic)
                    current_verse_num = None
                    current_verse_lines = []

                # Store topic for next verse (though not persisted to DB per plan)
                current_verse_topic = line.replace('**', '').strip()

            # #N Verse marker
            elif line.startswith('#'):
                # Save previous verse
                if current_verse_num is not None and current_verse_lines:
                    self._add_verse(current_work_id, current_section,
                                  verse_counter_per_section,
                                  current_verse_lines, current_verse_topic)

                # Extract verse number
                match = re.match(r'#(\d+)', line)
                if match:
                    current_verse_num = int(match.group(1))  # Original verse number
                    verse_counter_per_section += 1  # Increment for renumbering
                    current_verse_lines = []
                    # Keep current_verse_topic from ** marker if present

            # Regular line (verse content)
            elif current_verse_num is not None:
                # Skip annotation/glossary lines (start with *)
                if line.startswith('*'):
                    continue
                # Accumulate verse line
                current_verse_lines.append(line)

        # Save final verse if any
        if current_verse_num is not None and current_verse_lines:
            self._add_verse(current_work_id, current_section,
                          verse_counter_per_section,
                          current_verse_lines, current_verse_topic)

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
    print("நீதிநூல்கள் (Ethical Literature) - Bulk Import")
    print("Collection 325: Twenty-one Ethical Literature Works (3rd-20th century CE)")
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
    3. Create collection 325
    4. Parse all 21 files
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
    base_dir = Path(__file__).parent.parent / 'Tamil-Source-TamilConcordence' / '7_நீதிநூல்கள்'

    # Check if directory exists
    if not base_dir.exists():
        print(f"\n✗ Error: Source directory not found: {base_dir}")
        print("  Please ensure Tamil-Source-TamilConcordence/7_நீதிநூல்கள்/ exists")
        sys.exit(1)

    try:
        # Initialize importer
        importer = NeethinoolkalBulkImporter(db_url)

        # Create collection 325
        importer._ensure_collection_exists()

        # Parse all 21 files in order
        for work_num in range(1, 22):  # 1-21 inclusive
            file_path = base_dir / WORK_METADATA[work_num]['file']

            if not file_path.exists():
                print(f"  ✗ File not found: {file_path}")
                continue

            importer.parse_file(str(file_path), work_num)

        # Bulk insert
        importer.bulk_insert()

        # Print summary
        print_summary(importer)

        print("\n✓ Import complete! All 21 works imported successfully.")
        print("\nVerification queries:")
        print("  psql -U postgres -d tamil_literature")
        print("  SELECT work_name_tamil FROM works WHERE work_id IN")
        print("    (SELECT work_id FROM work_collections WHERE collection_id = 325);")

    except psycopg2.IntegrityError as e:
        print(f"\n✗ Database integrity error: {e}")
        print("  Possible causes:")
        print("  - Work already exists (run delete script first)")
        print("  - Duplicate IDs (check ID allocation logic)")
        importer.conn.rollback()
        sys.exit(1)

    except FileNotFoundError as e:
        print(f"\n✗ File error: {e}")
        print("  Check Tamil-Source-TamilConcordence/7_நீதிநூல்கள்/ directory")
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
