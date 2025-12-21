#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Manimegalai Parser for Tamil Literature Database - Bulk COPY Import

This script parses Manimegalai text file and imports it into the database.
Uses 2-phase bulk import for high performance.

Structure:
- Work: Manimegalai (மணிமேகலை) - One of the Five Great Epics
- Level 1 Sections (31 total):
  - Pathigam (பதிகம்) - Introduction section (#0)
  - 30 Kathais (காதை) - Main chapters (#1-#30)
- Verses: Multiple verses per section, separated by blank lines
- Lines: Individual lines within each verse
- Line numbers (multiples of 5) are removed during cleaning
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
    - Removing section markers (#)
    - Removing trailing line numbers (multiples of 5)
    - Removing dots used for alignment
    - Stripping whitespace
    """
    # Remove section marker at the beginning
    line = re.sub(r'^#\d*\s*', '', line)

    # Remove trailing numbers (multiples of 5)
    line = re.sub(r'\s+\d+$', '', line)

    # Remove dots used for alignment
    line = line.replace('.', '').replace('…', '')

    return line.strip()


def parse_manimegalai_file(file_path):
    """
    Parse the Manimegalai file and extract structure.

    IMPORTANT: Each section (Pathigam or Kathai) is ONE complete paadal (verse).
    Blank lines are just for readability, NOT verse boundaries.

    Returns:
    {
        'sections': [
            {
                'number': int,         # 0 for Pathigam, 1-30 for Kathais
                'name': str,           # Section name in Tamil
                'lines': [str, str, ...]  # All lines in this section (ONE verse)
            },
            ...
        ]
    }
    """
    print(f"  Parsing file: {file_path.name}")

    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    data = {
        'sections': []
    }

    current_section = None

    for line in lines:
        line = line.rstrip('\n')

        # Check for section marker (format: #0 பதிகம் or # 1 விழாவறை காதை)
        section_match = re.match(r'^#\s*(\d+)\s+(.+)$', line)
        if section_match:
            # Save previous section if exists
            if current_section is not None:
                data['sections'].append(current_section)

            # Start new section
            section_number = int(section_match.group(1))
            section_name = section_match.group(2).strip()

            current_section = {
                'number': section_number,
                'name': section_name,
                'lines': []  # All lines belong to ONE verse
            }
            continue

        # Skip if no current section yet
        if current_section is None:
            continue

        # Clean the line
        cleaned = clean_line(line)

        # Skip blank lines (they are just for readability)
        if not cleaned:
            continue

        # Add line to current section's lines
        current_section['lines'].append(cleaned)

    # Save last section
    if current_section is not None:
        data['sections'].append(current_section)

    return data


class ManimegalaiBulkImporter:
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
        """Ensure Manimegalai work exists"""
        work_name_tamil = 'மணிமேகலை'
        work_name_english = 'Manimegalai'

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
                'One of the Five Great Epics of Tamil Literature. Buddhist epic by Kulavāṇikaṉ Sīthalai Sāttanār.',
                '6th century CE',
                'Kulavāṇikaṉ Sīthalai Sāttanār',
                'குலவாணிகன் சீத்தலைச் சாத்தனார்',
                500, 600, 'medium',
                'Twin epic to Silapathikaram. Manimegalai is the daughter of Madhavi and Kovalan.',
                290  # Post-Silapathikaram epic
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

        print(f"\nProcessing Manimegalai...")

        # Parse the file
        data = parse_manimegalai_file(self.source_file)

        # Process each section (Pathigam or Kathai) - each is ONE verse
        for section_data in data['sections']:
            section_number = section_data['number']
            section_name = section_data['name']
            section_lines = section_data['lines']

            if not section_lines:
                continue

            # Determine level type
            if section_number == 0:
                level_type = 'pathigam'
                level_type_tamil = 'பதிகம்'
            else:
                level_type = 'kathai'
                level_type_tamil = 'காதை'

            # Create section
            section_id = self.section_id
            self.section_id += 1

            self.sections.append({
                'section_id': section_id,
                'work_id': self.work_id,
                'parent_section_id': None,
                'level_type': level_type,
                'level_type_tamil': level_type_tamil,
                'section_number': section_number,
                'section_name': section_name,
                'section_name_tamil': section_name,
                'sort_order': section_number
            })

            line_count = len(section_lines)
            print(f"  Section #{section_number}: {section_name} ({line_count} lines in 1 verse)")

            # Create ONE verse for this entire section
            verse_id = self.verse_id
            self.verse_id += 1

            self.verses.append({
                'verse_id': verse_id,
                'work_id': self.work_id,
                'section_id': section_id,
                'verse_number': 1,  # Always 1 - one verse per section
                'verse_type': section_name,  # Use the section name as verse type
                'verse_type_tamil': section_name,
                'total_lines': line_count,
                'sort_order': 1
            })

            # Process all lines in this section (which is one verse)
            for line_num, line_text in enumerate(section_lines, 1):
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
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

    # Database connection - check for environment variable or use default
    db_connection = os.getenv('DATABASE_URL',
                             "postgresql://postgres:postgres@localhost/tamil_literature")

    # Source file path
    script_dir = Path(__file__).parent
    project_dir = script_dir.parent
    source_file = project_dir / "Tamil-Source-TamilConcordence" / "4_ஐம்பெருங்காப்பியங்கள்" / "மணிமேகலை" / "மணிமேகலை.txt"

    # Allow database URL as command line argument
    if len(sys.argv) > 1:
        db_connection = sys.argv[1]

    print("=" * 70)
    print("Manimegalai Parser - Bulk COPY Import")
    print("=" * 70)
    print(f"Database: {db_connection.split('@')[-1] if '@' in db_connection else db_connection}")
    print(f"Source: {source_file}")
    print("=" * 70)

    # Create importer
    importer = ManimegalaiBulkImporter(db_connection, source_file)

    try:
        importer._ensure_work_exists()
        importer.parse_file()
        importer.bulk_insert()
        print("\n" + "=" * 70)
        print("✓ Manimegalai import completed successfully!")
        print("=" * 70)
    finally:
        importer.close()
        print("\n✓ Database connection closed")


if __name__ == '__main__':
    main()
