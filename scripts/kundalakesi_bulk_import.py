#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Kundalakesi Parser for Tamil Literature Database - Bulk COPY Import

This script parses Kundalakesi text file and imports it into the database.
Uses 2-phase bulk import for high performance.

Structure:
- Work: Kundalakesi (குண்டலகேசி) - One of the Five Great Epics (fragmentary)
- Verses: 19 verses total (no hierarchical sections)
- Lines: Individual lines within each verse
- Each # marks one complete verse
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
    - Removing verse markers (#)
    - Removing trailing numbers
    - Removing dots used for alignment
    - Stripping whitespace
    """
    # Remove verse marker at the beginning
    line = re.sub(r'^#\d*\s*', '', line)

    # Remove trailing numbers
    line = re.sub(r'\s+\d+$', '', line)

    # Remove dots used for alignment
    line = line.replace('.', '').replace('…', '')

    return line.strip()


def parse_valayapathi_file(file_path):
    """
    Parse the Kundalakesi file and extract structure.

    Structure:
    - # marks individual verses (each verse = one complete poem)
    - No hierarchical sections
    - Blank lines are for readability

    Returns:
    {
        'verses': [
            {
                'number': int,
                'lines': [str, str, ...]
            },
            ...
        ]
    }
    """
    print(f"  Parsing file: {file_path.name}")

    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    data = {
        'verses': []
    }

    current_verse = None

    for line in lines:
        line = line.rstrip('\n')

        # Check for verse marker (format: #1, #2, etc.)
        verse_match = re.match(r'^#(\d+)$', line)
        if verse_match:
            # Save previous verse if exists
            if current_verse is not None:
                data['verses'].append(current_verse)

            # Start new verse
            verse_number = int(verse_match.group(1))

            current_verse = {
                'number': verse_number,
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

    # Save last verse
    if current_verse is not None:
        data['verses'].append(current_verse)

    return data


class KundalakesiBulkImporter:
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
        """Ensure Kundalakesi work exists"""
        work_name_tamil = 'குண்டலகேசி'
        work_name_english = 'Kundalakesi'

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
                'One of the Five Great Epics of Tamil Literature (fragmentary). Only 19 verses survive.',
                'Unknown (possibly 6th century CE)',
                'Unknown',
                'அறியப்படவில்லை',
                500, 700, 'low',
                'Lost Buddhist epic, only fragments survive. Attribution and dating uncertain.',
                293  # After Valayapathi (292)
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

        print(f"\nProcessing Kundalakesi...")

        # Parse the file
        data = parse_valayapathi_file(self.source_file)

        # Create a default section to hold all verses
        default_section_id = self.section_id
        self.section_id += 1

        self.sections.append({
            'section_id': default_section_id,
            'work_id': self.work_id,
            'parent_section_id': None,
            'level_type': 'collection',
            'level_type_tamil': 'தொகுப்பு',
            'section_number': 1,
            'section_name': 'Kundalakesi Collection',
            'section_name_tamil': 'குண்டலகேசி தொகுப்பு',
            'sort_order': 1
        })

        # Process each verse
        for verse_data in data['verses']:
            verse_number = verse_data['number']
            verse_lines = verse_data['lines']

            if not verse_lines:
                continue

            # Create verse
            verse_id = self.verse_id
            self.verse_id += 1

            self.verses.append({
                'verse_id': verse_id,
                'work_id': self.work_id,
                'section_id': default_section_id,  # All verses in default section
                'verse_number': verse_number,
                'verse_type': 'paadal',
                'verse_type_tamil': 'பாடல்',
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
        os.environ['PYTHONIOENCODING'] = 'utf-8'

    # Database connection - check for environment variable or use default
    db_connection = os.getenv('DATABASE_URL',
                             "postgresql://postgres:postgres@localhost/tamil_literature")

    # Source file path
    script_dir = Path(__file__).parent
    project_dir = script_dir.parent
    source_file = project_dir / "Tamil-Source-TamilConcordence" / "4_ஐம்பெருங்காப்பியங்கள்" / "குண்டலகேசி" / "குண்டலகேசி.txt"

    # Allow database URL as command line argument
    if len(sys.argv) > 1:
        db_connection = sys.argv[1]

    print("=" * 70)
    print("Kundalakesi Parser - Bulk COPY Import")
    print("=" * 70)
    print(f"Database: {db_connection.split('@')[-1] if '@' in db_connection else db_connection}")
    print(f"Source: {source_file}")
    print("=" * 70)

    # Create importer
    importer = KundalakesiBulkImporter(db_connection, source_file)

    try:
        importer._ensure_work_exists()
        importer.parse_file()
        importer.bulk_insert()
        print("\n" + "=" * 70)
        print("✓ Kundalakesi import completed successfully!")
        print("=" * 70)
    finally:
        importer.close()
        print("\n✓ Database connection closed")


if __name__ == '__main__':
    main()
