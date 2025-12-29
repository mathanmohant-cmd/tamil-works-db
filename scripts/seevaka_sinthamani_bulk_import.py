#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Seevaka Sinthamani Parser for Tamil Literature Database - Bulk COPY Import

This script parses Seevaka Sinthamani text file and imports it into the database.
Uses 2-phase bulk import for high performance.

Structure:
- Work: Seevaka Sinthamani (சீவக சிந்தாமணி) - One of the Five Great Epics
- Level 1: Ilampagams (இலம்பகம்) - Major book divisions marked with @
- Level 2: Verses - Individual verses marked with # (each # section = ONE verse)
- Lines: Individual lines within each verse
- Blank lines are just for readability
"""

import os
import re
import sys
import psycopg2
import csv
import io
from pathlib import Path
from word_cleaning import split_and_clean_words


def clean_line(line):
    """
    Clean a line by:
    - Removing section markers (@ and #)
    - Removing trailing line numbers
    - Removing dots used for alignment
    - Stripping whitespace
    """
    # Remove section markers at the beginning
    line = re.sub(r'^[@#]\d*\s*', '', line)

    # Remove trailing numbers
    line = re.sub(r'\s+\d+$', '', line)

    # Remove dots used for alignment
    line = line.replace('.', '').replace('…', '')

    return line.strip()


def parse_seevaka_sinthamani_file(file_path):
    """
    Parse the Seevaka Sinthamani file and extract structure.

    Structure:
    - @ marks Ilampagams (major sections)
    - # marks individual verses (each verse = one complete poem)
    - Blank lines are for readability

    Returns:
    {
        'ilampagams': [
            {
                'number': int,
                'name': str,
                'verses': [
                    {
                        'number': int,
                        'name': str,
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

    data = {
        'ilampagams': []
    }

    current_ilampagam = None
    current_verse = None

    for line in lines:
        line = line.rstrip('\n')

        # Check for Ilampagam marker (format: @0 கடவுள் வாழ்த்து)
        ilampagam_match = re.match(r'^@\s*(\d+)\s+(.+)$', line)
        if ilampagam_match:
            # Save previous verse if exists
            if current_verse is not None and current_ilampagam is not None:
                current_ilampagam['verses'].append(current_verse)
                current_verse = None

            # Save previous ilampagam if exists
            if current_ilampagam is not None:
                data['ilampagams'].append(current_ilampagam)

            # Start new ilampagam
            ilampagam_number = int(ilampagam_match.group(1))
            ilampagam_name = ilampagam_match.group(2).strip()

            current_ilampagam = {
                'number': ilampagam_number,
                'name': ilampagam_name,
                'verses': []
            }
            continue

        # Check for verse marker (format: #1 சித்தர் வணக்கம் or just #5)
        verse_match = re.match(r'^#\s*(\d+)\s*(.*)$', line)
        if verse_match:
            # Save previous verse if exists
            if current_verse is not None and current_ilampagam is not None:
                current_ilampagam['verses'].append(current_verse)

            # Start new verse
            verse_number = int(verse_match.group(1))
            verse_name = verse_match.group(2).strip() if verse_match.group(2) else ""

            current_verse = {
                'number': verse_number,
                'name': verse_name,
                'lines': []
            }
            continue

        # Skip if no current verse yet
        if current_verse is None:
            continue

        # Clean the line
        cleaned = clean_line(line)

        # Skip blank lines
        if not cleaned:
            continue

        # Add line to current verse
        current_verse['lines'].append(cleaned)

    # Save last verse if exists
    if current_verse is not None and current_ilampagam is not None:
        current_ilampagam['verses'].append(current_verse)

    # Save last ilampagam
    if current_ilampagam is not None:
        data['ilampagams'].append(current_ilampagam)

    return data


class SeevakaSinthamaniBulkImporter:
    def __init__(self, db_connection_string: str, source_file: Path):
        """Initialize bulk importer"""
        self.conn = psycopg2.connect(db_connection_string)
        self.cursor = self.conn.cursor()
        self.source_file = source_file

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

    def _ensure_work_exists(self):
        """Ensure Seevaka Sinthamani work exists"""
        work_name_tamil = 'சீவக சிந்தாமணி'
        work_name_english = 'Seevaka Sinthamani'

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
                'One of the Five Great Epics of Tamil Literature. Jain epic about Prince Jivaka.',
                '10th century CE',
                'Thiruthakka Thevar (Tirutakkatēvar)',
                'திருத்தக்கத் தேவர்',
                900, 1000, 'medium',
                'Jain epic in 13 books. Story of Prince Jivaka who renounces worldly life.',
                291  # After Manimegalai (290)
            ))
            self.conn.commit()
            print(f"  ✓ Work created (ID: {self.work_id}). Use collection management utility to assign to collections.")

        # Get starting IDs for batch processing
        self.cursor.execute("SELECT COALESCE(MAX(section_id), 0) FROM sections")
        self.section_id = self.cursor.fetchone()[0] + 1

        self.cursor.execute("SELECT COALESCE(MAX(verse_id), 0) FROM verses")
        self.verse_id = self.cursor.fetchone()[0] + 1

        self.cursor.execute("SELECT COALESCE(MAX(line_id), 0) FROM lines")
        self.line_id = self.cursor.fetchone()[0] + 1

        self.cursor.execute("SELECT COALESCE(MAX(word_id), 0) FROM words")
        self.word_id = self.cursor.fetchone()[0] + 1

    def parse_file(self):
        """Phase 1: Parse file into memory"""
        print("\nPhase 1: Parsing file...")

        if not os.path.exists(self.source_file):
            print(f"Error: File not found: {self.source_file}")
            sys.exit(1)

        print(f"\nProcessing Seevaka Sinthamani...")

        # Parse the file
        data = parse_seevaka_sinthamani_file(self.source_file)

        # Process each Ilampagam
        for ilampagam_data in data['ilampagams']:
            ilampagam_number = ilampagam_data['number']
            ilampagam_name = ilampagam_data['name']
            verses_list = ilampagam_data['verses']

            # Create Ilampagam section
            ilampagam_section_id = self.section_id
            self.section_id += 1

            self.sections.append({
                'section_id': ilampagam_section_id,
                'work_id': self.work_id,
                'parent_section_id': None,
                'level_type': 'ilampagam',
                'level_type_tamil': 'இலம்பகம்',
                'section_number': ilampagam_number,
                'section_name': ilampagam_name,
                'section_name_tamil': ilampagam_name,
                'sort_order': ilampagam_number
            })

            verse_count = len(verses_list)
            line_count = sum(len(v['lines']) for v in verses_list)
            print(f"  Ilampagam #{ilampagam_number}: {ilampagam_name} ({verse_count} verses, {line_count} lines)")

            # Process each verse in this Ilampagam
            for verse_data in verses_list:
                verse_number = verse_data['number']
                verse_name = verse_data['name']
                verse_lines = verse_data['lines']

                if not verse_lines:
                    continue

                # Create verse
                verse_id = self.verse_id
                self.verse_id += 1

                self.verses.append({
                    'verse_id': verse_id,
                    'work_id': self.work_id,
                    'section_id': ilampagam_section_id,
                    'verse_number': verse_number,
                    'verse_type': verse_name if verse_name else 'verse',
                    'verse_type_tamil': verse_name if verse_name else 'செய்யுள்',
                    'total_lines': len(verse_lines),
                    'sort_order': verse_number
                })

                # Process all lines in this verse
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

        print(f"\n✓ Phase 1 complete: Parsed file")
        print(f"  - Sections (Ilampagams): {len(self.sections)}")
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
        os.environ['PYTHONIOENCODING'] = 'utf-8'

    # Database connection - check for environment variable or use default
    db_connection = os.getenv('DATABASE_URL',
                             "postgresql://postgres:postgres@localhost/tamil_literature")

    # Source file path
    script_dir = Path(__file__).parent
    project_dir = script_dir.parent
    source_file = project_dir / "Tamil-Source-TamilConcordence" / "4_ஐம்பெருங்காப்பியங்கள்" / "சீவக சிந்தாமணி" / "சீவக சிந்தாமணி.txt"

    # Allow database URL as command line argument
    if len(sys.argv) > 1:
        db_connection = sys.argv[1]

    print("=" * 70)
    print("Seevaka Sinthamani Parser - Bulk COPY Import")
    print("=" * 70)
    print(f"Database: {db_connection.split('@')[-1] if '@' in db_connection else db_connection}")
    print(f"Source: {source_file}")
    print("=" * 70)

    # Create importer
    importer = SeevakaSinthamaniBulkImporter(db_connection, source_file)

    try:
        importer._ensure_work_exists()
        importer.parse_file()
        importer.bulk_insert()
        print("\n" + "=" * 70)
        print("✓ Seevaka Sinthamani import completed successfully!")
        print("=" * 70)
    finally:
        importer.close()
        print("\n✓ Database connection closed")


if __name__ == '__main__':
    main()
