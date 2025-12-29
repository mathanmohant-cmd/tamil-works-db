#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Kambaramayanam Parser for Tamil Literature Database - Bulk COPY Import

This script parses Kambaramayanam text files and imports them into the database.
Uses 2-phase bulk import for high performance.

Structure:
- Work: Kambaramayanam (கம்பராமாயணம்)
- Level 1 (Kandam): 6 chapters (Yuddha Kandam split into 4 parts)
  - & marks Kandam
  - @ marks Padalam (subsection)
  - # marks verse number
- Verses: Individual verses numbered with #
- Lines: Lines within verses
- Clean: Remove ** and *** markers
"""

import os
import re
import sys
import psycopg2
import csv
import io
from pathlib import Path
from word_cleaning import split_and_clean_words

# Kandam files (ordered) - Yuddha Kandam (6) is split across 4 files for convenience
# Note: Section names include "Kandam"/"காண்டம்" and "Padalam"/"படலம்" for natural reading
KANDAM_FILES = [
    ('1-கம்பராமாயணம்-பாலகாண்டம்.txt', 'பால காண்டம்', 'Bala Kandam', 1),
    ('2-கம்பராமாயணம்-அயோத்தியா காண்டம்.txt', 'அயோத்தியா காண்டம்', 'Ayodhya Kandam', 2),
    ('3-கம்பராமாயணம்-ஆரணிய காண்டம்.txt', 'ஆரணிய காண்டம்', 'Aranya Kandam', 3),
    ('4-கம்பராமாயணம்-கிட்கிந்தா காண்டம்.txt', 'கிட்கிந்தா காண்டம்', 'Kishkindha Kandam', 4),
    ('5-கம்பராமாயணம்-சுந்தர காண்டம்.txt', 'சுந்தர காண்டம்', 'Sundara Kandam', 5),
    ('6-கம்பராமாயணம்-யுத்த காண்டம்-1.txt', 'யுத்த காண்டம்', 'Yuddha Kandam', 6),
    ('6-கம்பராமாயணம்-யுத்த காண்டம்-2.txt', 'யுத்த காண்டம்', 'Yuddha Kandam', 6),
    ('6-கம்பராமாயணம்-யுத்த காண்டம்-3.txt', 'யுத்த காண்டம்', 'Yuddha Kandam', 6),
    ('6-கம்பராமாயணம்-யுத்த காண்டம்-4.txt', 'யுத்த காண்டம்', 'Yuddha Kandam', 6),
]


def clean_line(line):
    """
    Clean a line by:
    - Removing structural markers (#, &, @)
    - Removing ** and *** markers
    - Removing line numbers (multiples of 5) at the end
    - Stripping whitespace
    """
    # Remove structural markers that should not appear in line_text
    line = re.sub(r'^[#&@]', '', line)

    # Remove ** and *** markers
    line = re.sub(r'\*\*\*?', '', line)

    # Remove trailing line numbers (multiples of 5)
    line = re.sub(r'\s+\d+$', '', line)

    return line.strip()


def parse_kandam_file(file_path):
    """
    Parse a single Kandam file and extract structure.

    Returns:
    {
        'kandam_name_tamil': str,
        'padalams': [
            {
                'number': int,
                'name': str,
                'verses': [
                    {
                        'number': int,
                        'lines': [str, str, ...]
                    },
                    ...
                ]
            },
            ...
        ]
    }
    """
    print(f"  Parsing file: {file_path.name}")

    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    kandam_info = {
        'padalams': []
    }

    current_padalam = None
    current_verse = None

    for line in lines:
        line = line.rstrip('\n')

        # Check for Kandam marker (&)
        if line.startswith('&'):
            kandam_text = line[1:].strip()
            # Remove leading number if present
            kandam_text = re.sub(r'^\d+\s+', '', kandam_text)
            kandam_info['kandam_name_tamil'] = kandam_text
            continue

        # Check for Padalam marker (@)
        if line.startswith('@'):
            # Save previous verse if exists
            if current_verse and current_padalam:
                current_padalam['verses'].append(current_verse)
                current_verse = None

            # Parse padalam header (format: @1 மங்கல வாழ்த்துப் படலம்)
            match = re.match(r'^@(\d+)\s+(.+)$', line)
            if match:
                padalam_number = int(match.group(1))
                padalam_name = match.group(2).strip()

                # Keep " படலம்" in the name for natural reading
                # If missing, add it
                if not padalam_name.endswith(' படலம்'):
                    padalam_name = padalam_name + ' படலம்'

                current_padalam = {
                    'number': padalam_number,
                    'name': padalam_name,
                    'verses': []
                }
                kandam_info['padalams'].append(current_padalam)
            continue

        # Check for verse marker (#)
        if line.startswith('#'):
            # Save previous verse
            if current_verse and current_padalam:
                current_padalam['verses'].append(current_verse)

            # Parse verse number (format: #1)
            match = re.match(r'^#(\d+)$', line)
            if match:
                verse_number = int(match.group(1))
                current_verse = {
                    'number': verse_number,
                    'lines': []
                }
            continue

        # Regular content line
        cleaned = clean_line(line)
        if cleaned and current_verse is not None:
            current_verse['lines'].append(cleaned)

    # Save last verse
    if current_verse and current_padalam:
        current_padalam['verses'].append(current_verse)

    return kandam_info


# Note: Removed simple_word_split function - now using shared word_cleaning utility


class KambaramayanamBulkImporter:
    def __init__(self, db_connection_string: str, source_dir: Path):
        """Initialize bulk importer"""
        self.conn = psycopg2.connect(db_connection_string)
        self.cursor = self.conn.cursor()
        self.source_dir = source_dir

        # Data containers for bulk insert
        self.sections = []
        self.verses = []
        self.lines = []
        self.words = []

        # ID counters - will be set properly in _ensure_work_exists()
        self.section_id = None
        self.verse_id = None
        self.line_id = None
        self.word_id = None
        self.work_id = None

        # Track Yuddha Kandam parent section
        self.yuddha_kandam_parent_id = None

    def _ensure_work_exists(self):
        """Ensure Kambaramayanam work exists"""
        work_name_tamil = 'கம்பராமாயணம்'
        work_name_english = 'Kambaramayanam'

        # Check if work already exists by name
        self.cursor.execute("SELECT work_id FROM works WHERE work_name = %s", (work_name_english,))
        existing = self.cursor.fetchone()

        if existing:
            self.work_id = existing[0]
            print(f"\n✗ Work {work_name_tamil} already exists (ID: {self.work_id})")
            print(f"To re-import, first delete the existing work:")
            print(f'  python scripts/delete_work.py "{work_name_english}"')
            self.cursor.close()
            self.conn.close()
            sys.exit(1)
        else:
            # Get next available work_id
            self.cursor.execute("SELECT COALESCE(MAX(work_id), 0) + 1 FROM works")
            self.work_id = self.cursor.fetchone()[0]

            print(f"Creating work entry for {work_name_tamil}...")
            self.cursor.execute("""
                INSERT INTO works (
                    work_id, work_name, work_name_tamil, description, period, author, author_tamil,
                    chronology_start_year, chronology_end_year,
                    chronology_confidence, chronology_notes, canonical_order
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                self.work_id,
                work_name_english,
                work_name_tamil,
                'Tamil retelling of the Ramayana epic',
                '12th century CE',
                'Kambar',
                'கம்பர்',
                1100, 1200, 'high',
                'Medieval epic by Kambar during Chola period.',
                400  # Medieval epic
            ))
            self.conn.commit()
            print(f"  ✓ Work created (ID: {self.work_id}).")

            # Create collection and link work to it
            self._create_collection_and_link()

        # Get starting IDs for batch processing
        self.cursor.execute("SELECT COALESCE(MAX(section_id), 0) FROM sections")
        self.section_id = self.cursor.fetchone()[0] + 1

        self.cursor.execute("SELECT COALESCE(MAX(verse_id), 0) FROM verses")
        self.verse_id = self.cursor.fetchone()[0] + 1

        self.cursor.execute("SELECT COALESCE(MAX(line_id), 0) FROM lines")
        self.line_id = self.cursor.fetchone()[0] + 1

        self.cursor.execute("SELECT COALESCE(MAX(word_id), 0) FROM words")
        self.word_id = self.cursor.fetchone()[0] + 1

    def _create_collection_and_link(self):
        """Create காப்பியங்கள் collection and link Kambaramayanam to it"""
        collection_id = 500
        collection_name = 'Epics'
        collection_name_tamil = 'காப்பியங்கள்'

        # Check if collection exists
        self.cursor.execute("SELECT collection_id FROM collections WHERE collection_id = %s", (collection_id,))
        existing = self.cursor.fetchone()

        if not existing:
            print(f"  Creating collection: {collection_name_tamil}")
            self.cursor.execute("""
                INSERT INTO collections (collection_id, collection_name, collection_name_tamil,
                                        collection_type, description, parent_collection_id, sort_order)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (collection_id, collection_name, collection_name_tamil, 'genre',
                  'Tamil Epic Poetry - Major epic works in Tamil literature',
                  None, 500))
            self.conn.commit()
            print(f"  ✓ Created collection {collection_name_tamil}")
        else:
            print(f"  Collection {collection_name_tamil} already exists")

        # Link work to collection
        print(f"  Linking Kambaramayanam to collection...")
        self.cursor.execute("""
            INSERT INTO work_collections (work_id, collection_id, position_in_collection, is_primary, notes)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (work_id, collection_id) DO NOTHING
        """, (self.work_id, collection_id, 1, True, 'Tamil retelling of Ramayana by Kambar'))

        self.conn.commit()
        print(f"  ✓ Linked Kambaramayanam to collection (position 1)")

    def parse_all_files(self):
        """Phase 1: Parse all Kandam files into memory"""
        print("\nPhase 1: Parsing all files...")

        for filename, kandam_tamil, kandam_english, kandam_num in KANDAM_FILES:
            file_path = self.source_dir / filename

            if not os.path.exists(file_path):
                print(f"Warning: File not found: {file_path}")
                continue

            print(f"\nProcessing Kandam {kandam_num}: {kandam_tamil}")

            # Parse the file
            kandam_data = parse_kandam_file(file_path)

            # Handle Yuddha Kandam special case (6) - split across 4 files but ONE section
            if kandam_num == 6:
                if self.yuddha_kandam_parent_id is None:
                    # Create Yuddha Kandam section only once (first time we see kandam_num=6)
                    self.yuddha_kandam_parent_id = self.section_id
                    self.section_id += 1

                    self.sections.append({
                        'section_id': self.yuddha_kandam_parent_id,
                        'work_id': self.work_id,
                        'parent_section_id': None,
                        'level_type': 'kandam',
                        'level_type_tamil': 'காண்டம்',
                        'section_number': 6,
                        'section_name': kandam_english,
                        'section_name_tamil': kandam_tamil,
                        'sort_order': 6
                    })
                    print(f"  Created Yuddha Kandam section (will span multiple files)")

                # Reuse the same Yuddha Kandam section for all 4 files
                kandam_section_id = self.yuddha_kandam_parent_id
            else:
                # Regular Kandam (1-5)
                kandam_section_id = self.section_id
                self.section_id += 1

                self.sections.append({
                    'section_id': kandam_section_id,
                    'work_id': self.work_id,
                    'parent_section_id': None,
                    'level_type': 'kandam',
                    'level_type_tamil': 'காண்டம்',
                    'section_number': kandam_num,
                    'section_name': kandam_english,
                    'section_name_tamil': kandam_tamil,
                    'sort_order': kandam_num
                })

            # Track Padalam sections by (kandam_section_id, padalam_number) to handle duplicates
            padalam_sections = {}  # key: (kandam_section_id, padalam_number), value: section_id

            # Process each Padalam (subsection)
            # Note: Padalam numbers restart for each Kandam part, so use padalam_idx for unique ordering
            for padalam_idx, padalam_data in enumerate(kandam_data['padalams'], 1):
                padalam_name = padalam_data['name']
                padalam_number = padalam_data['number']

                # Check if this Padalam number already exists (e.g., மிகைப் பாடல்கள்)
                padalam_key = (kandam_section_id, padalam_number)
                is_duplicate = padalam_key in padalam_sections

                if is_duplicate:
                    # Reuse existing Padalam section for duplicates (additional verses)
                    padalam_section_id = padalam_sections[padalam_key]
                    print(f"  Padalam #{padalam_number}: {padalam_name} (appending to existing - {len(padalam_data['verses'])} verses)")
                else:
                    # Create new Padalam section
                    padalam_section_id = self.section_id
                    self.section_id += 1

                    # Use padalam_idx for sort_order since padalam_number repeats across Kandam parts
                    self.sections.append({
                        'section_id': padalam_section_id,
                        'work_id': self.work_id,
                        'parent_section_id': kandam_section_id,
                        'level_type': 'padalam',
                        'level_type_tamil': 'படலம்',
                        'section_number': padalam_number,
                        'section_name': padalam_name,
                        'section_name_tamil': padalam_name,
                        'sort_order': padalam_idx  # Use sequential index instead of padalam_number
                    })

                    padalam_sections[padalam_key] = padalam_section_id
                    print(f"  Padalam #{padalam_number}: {padalam_name} ({len(padalam_data['verses'])} verses)")

                verse_count = len(padalam_data['verses'])

                # For duplicate Padalams (மிகைப் பாடல்கள்), find the next available verse number
                if is_duplicate and len(self.verses) > 0:
                    # Find max verse_number for this section
                    existing_verses = [v for v in self.verses if v['section_id'] == padalam_section_id]
                    next_verse_num = len(existing_verses) + 1  # Start from count + 1
                    print(f"    Starting verse numbers at: {next_verse_num} (after {len(existing_verses)} existing verses)")
                else:
                    next_verse_num = 1

                # Process verses - use sequential numbering within Padalam
                for verse_idx, verse_data in enumerate(padalam_data['verses'], start=next_verse_num):
                    verse_number = verse_idx
                    verse_lines = verse_data['lines']

                    if not verse_lines:
                        continue

                    # Add verse
                    verse_id = self.verse_id
                    self.verse_id += 1

                    self.verses.append({
                        'verse_id': verse_id,
                        'work_id': self.work_id,
                        'section_id': padalam_section_id,
                        'verse_number': verse_number,
                        'verse_type': 'poem',
                        'verse_type_tamil': 'பாடல்',
                        'total_lines': len(verse_lines),
                        'sort_order': verse_number
                    })

                    # Process lines
                    for line_num, line_text in enumerate(verse_lines, 1):
                        line_id = self.line_id
                        self.line_id += 1

                        self.lines.append({
                            'line_id': line_id,
                            'verse_id': verse_id,
                            'line_number': line_num,
                            'line_text': line_text
                        })

                        # Process words using shared cleaning utility
                        cleaned_words = split_and_clean_words(line_text)
                        for word_pos, word_text in enumerate(cleaned_words, 1):
                            word_id = self.word_id
                            self.word_id += 1

                            self.words.append({
                                'word_id': word_id,
                                'line_id': line_id,
                                'word_position': word_pos,
                                'word_text': word_text,
                                'sandhi_split': None
                            })

        print(f"\n✓ Phase 1 complete: Parsed all files")
        print(f"  - Sections: {len(self.sections)}")
        print(f"  - Verses: {len(self.verses)}")
        print(f"  - Lines: {len(self.lines)}")
        print(f"  - Words: {len(self.words)}")

    def bulk_insert(self):
        """Phase 2: Bulk insert using PostgreSQL COPY"""
        print("\nPhase 2: Bulk inserting into database...")

        # Insert sections
        print(f"  Inserting {len(self.sections)} sections...")
        self._bulk_copy('sections', self.sections,
                       ['section_id', 'work_id', 'parent_section_id', 'level_type', 'level_type_tamil',
                        'section_number', 'section_name', 'section_name_tamil', 'sort_order'])

        # Insert verses
        print(f"  Inserting {len(self.verses)} verses...")
        self._bulk_copy('verses', self.verses,
                       ['verse_id', 'work_id', 'section_id', 'verse_number', 'verse_type',
                        'verse_type_tamil', 'total_lines', 'sort_order'])

        # Insert lines
        print(f"  Inserting {len(self.lines)} lines...")
        self._bulk_copy('lines', self.lines,
                       ['line_id', 'verse_id', 'line_number', 'line_text'])

        # Insert words
        print(f"  Inserting {len(self.words)} words...")
        self._bulk_copy('words', self.words,
                       ['word_id', 'line_id', 'word_position', 'word_text', 'sandhi_split'])

        self.conn.commit()
        print("✓ Phase 2 complete: All data inserted")

    def _bulk_copy(self, table_name, data, columns):
        """Use PostgreSQL COPY for bulk insert"""
        if not data:
            return

        # Create StringIO buffer
        buffer = io.StringIO()
        writer = csv.writer(buffer, delimiter='\t')

        for row in data:
            writer.writerow([row.get(col) if row.get(col) is not None else '\\N' for col in columns])

        buffer.seek(0)

        # Use COPY command
        self.cursor.copy_from(buffer, table_name, columns=columns, null='\\N')

    def close(self):
        """Close database connection"""
        self.cursor.close()
        self.conn.close()


def main():
    """Main execution function."""
    # Fix Windows console encoding for Tamil characters
    if sys.platform == 'win32':
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

    # Database connection - check for environment variable or use default
    db_connection = os.getenv('DATABASE_URL',
                             "postgresql://postgres:postgres@localhost/tamil_literature")

    # Source directory path
    script_dir = Path(__file__).parent
    project_dir = script_dir.parent
    source_dir = project_dir / "Tamil-Source-TamilConcordence" / "5 _கம்பராமாயணம்"

    # Allow database URL as command line argument
    if len(sys.argv) > 1:
        db_connection = sys.argv[1]

    print("=" * 70)
    print("Kambaramayanam Parser - Bulk COPY Import")
    print("=" * 70)
    print(f"Database: {db_connection.split('@')[-1] if '@' in db_connection else db_connection}")
    print(f"Source: {source_dir}")
    print("=" * 70)

    # Create importer
    importer = KambaramayanamBulkImporter(db_connection, source_dir)

    try:
        importer._ensure_work_exists()
        importer.parse_all_files()
        importer.bulk_insert()
        print("\n" + "=" * 70)
        print("✓ Kambaramayanam import completed successfully!")
        print("=" * 70)
    finally:
        importer.close()
        print("\n✓ Database connection closed")


if __name__ == '__main__':
    main()
