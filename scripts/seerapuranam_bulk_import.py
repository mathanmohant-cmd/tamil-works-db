#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Seerapuranam Parser for Tamil Literature Database - Bulk COPY Import

This script parses Seerapuranam text file and imports it into the database.
Uses 2-phase bulk import for high performance.

Structure:
- Work: Seerapuranam (சீறாப்புராணம்)
- Level 1 (Kandam): 3 chapters marked with "* N காண்டம்"
  - விலாதத்துக் காண்டம் (Vilaadhaththu Kandam) - Birth
  - நுபுவ்வத்துக் காண்டம் (Nupuvvaththu Kandam) - Prophethood
  - இசிறத்துக் காண்டம் (Isiraththu Kandam) - Migration
- Level 2 (Padalam): Subsections marked with *N followed by padalam name
- Verses: Each # section is ONE complete verse
- $ markers contain verse metadata (stored in verse metadata)
- மேல் marks end of verse
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
    - Removing structural markers ($, #, மேல்)
    - Removing ** markers
    - Removing line numbers
    - Removing dots used for alignment
    - Stripping whitespace
    """
    # Skip verse end marker
    if line.strip() == 'மேல்':
        return ''

    # Remove structural markers at the beginning
    line = re.sub(r'^[$#]+\s*', '', line)

    # Remove anything after ** (including **)
    if '**' in line:
        line = line.split('**')[0]

    # Remove ** and *** markers anywhere
    line = re.sub(r'\*\*\*?', '', line)

    # Remove dots used for alignment
    line = line.replace('.', '').replace('…', '')

    # Remove trailing numbers
    line = re.sub(r'\s+\d+$', '', line)

    return line.strip()


def parse_seerapuranam_file(file_path):
    """
    Parse Seerapuranam file and extract structure.

    Structure:
    - * N காண்டம் = Kandam (top level)
    - *N படலம் = Padalam (sub level)
    - $ = verse metadata (e.g., $1.0.1, $1.1.2)
    - # = verse number
    - மேல் = end of verse

    Returns:
    {
        'kandams': [
            {
                'number': int,
                'name': str,
                'padalams': [
                    {
                        'number': int,
                        'name': str,
                        'verses': [
                            {
                                'verse_number': int,
                                'verse_id': str,  # from $ marker
                                'lines': [str, str, ...]
                            },
                            ...
                        ]
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

    kandams = []
    current_kandam = None
    current_padalam = None
    current_verse = None
    current_verse_id = None

    for line in lines:
        line = line.rstrip('\n')

        # Skip empty lines
        if not line.strip():
            continue

        # Check for Kandam marker: "* N காண்டம்" or "* N name காண்டம்"
        kandam_match = re.match(r'^\*\s*(\d+)\s+(.+?காண்டம்.*?)$', line)
        if kandam_match:
            # Save previous padalam and kandam
            if current_padalam is not None and current_kandam is not None:
                if current_verse is not None:
                    current_padalam['verses'].append(current_verse)
                    current_verse = None
                current_kandam['padalams'].append(current_padalam)
                current_padalam = None
            if current_kandam is not None:
                kandams.append(current_kandam)

            kandam_number = int(kandam_match.group(1))
            kandam_name = kandam_match.group(2).strip()

            current_kandam = {
                'number': kandam_number,
                'name': kandam_name,
                'padalams': []
            }
            print(f"  Found Kandam {kandam_number}: {kandam_name}")
            continue

        # Check for Padalam marker: "*N படலம்" or "*N. name படலம்"
        # Examples: "*0 காப்பு", "*1கடவுள் வாழ்த்துப் படலம்", "*2. நாட்டுப்படலம்"
        padalam_match = re.match(r'^\*(\d+)\.?\s*(.+?)$', line)
        if padalam_match and current_kandam is not None:
            # Save previous padalam
            if current_padalam is not None:
                if current_verse is not None:
                    current_padalam['verses'].append(current_verse)
                    current_verse = None
                current_kandam['padalams'].append(current_padalam)

            padalam_number = int(padalam_match.group(1))
            padalam_name = padalam_match.group(2).strip()

            current_padalam = {
                'number': padalam_number,
                'name': padalam_name,
                'verses': []
            }
            continue

        # Check for verse metadata: $1.0.1, $1.1.2, etc.
        if line.startswith('$'):
            current_verse_id = line[1:].strip()
            continue

        # Check for verse marker: #N
        verse_match = re.match(r'^#(\d+)$', line)
        if verse_match and current_padalam is not None:
            # Save previous verse
            if current_verse is not None:
                current_padalam['verses'].append(current_verse)

            verse_number = int(verse_match.group(1))
            current_verse = {
                'verse_number': verse_number,
                'verse_id': current_verse_id or '',
                'lines': []
            }
            current_verse_id = None
            continue

        # Check for verse end marker
        if line.strip() == 'மேல்':
            # Verse ends here, but we'll append it when we hit the next verse or padalam
            continue

        # Regular content line - add to current verse's lines
        cleaned = clean_line(line)
        if cleaned and current_verse is not None:
            current_verse['lines'].append(cleaned)

    # Save last verse, padalam, and kandam
    if current_verse is not None and current_padalam is not None:
        current_padalam['verses'].append(current_verse)
    if current_padalam is not None and current_kandam is not None:
        current_kandam['padalams'].append(current_padalam)
    if current_kandam is not None:
        kandams.append(current_kandam)

    return {'kandams': kandams}


class SeerapuranamBulkImporter:
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
        """Ensure Seerapuranam work exists"""
        work_name_tamil = 'சீறாப்புராணம்'
        work_name_english = 'Seerapuranam'

        # Check if work already exists by name
        self.cursor.execute("SELECT work_id FROM works WHERE work_name = %s", (work_name_english,))
        existing = self.cursor.fetchone()

        if existing:
            self.work_id = existing[0]
            print(f"\n✗ Work {work_name_tamil} already exists (ID: {self.work_id})")
            print(f"To re-import, first delete the existing work:")
            print(f'  python scripts/delete_seerapuranam.py')
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
                    chronology_confidence, chronology_notes, canonical_order,
                    primary_collection_id
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                self.work_id,
                work_name_english,
                work_name_tamil,
                'Islamic epic about Prophet Muhammad',
                '16th century CE',
                'Umaruppulavar',
                'உமறுப்புலவர்',
                1550, 1600, 'high',
                'Islamic devotional epic by Umaruppulavar',
                502,  # Devotional Literature standalone
                None  # Standalone work, no collection
            ))
            self.conn.commit()
            print(f"  ✓ Work created (ID: {self.work_id}). Standalone work, no collection assignment needed.")

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

        # Parse the file
        data = parse_seerapuranam_file(self.source_file)

        # Process each Kandam
        for kandam_data in data['kandams']:
            kandam_name = kandam_data['name']
            kandam_number = kandam_data['number']

            print(f"\nProcessing Kandam {kandam_number}: {kandam_name}")

            # Create Kandam section
            kandam_section_id = self.section_id
            self.section_id += 1

            self.sections.append({
                'section_id': kandam_section_id,
                'work_id': self.work_id,
                'parent_section_id': None,
                'level_type': 'kandam',
                'level_type_tamil': 'காண்டம்',
                'section_number': kandam_number,
                'section_name': kandam_name,
                'section_name_tamil': kandam_name,
                'sort_order': kandam_number
            })

            # Process each Padalam (subsection)
            for padalam_data in kandam_data['padalams']:
                padalam_name = padalam_data['name']
                padalam_number = padalam_data['number']

                # Create Padalam section
                padalam_section_id = self.section_id
                self.section_id += 1

                self.sections.append({
                    'section_id': padalam_section_id,
                    'work_id': self.work_id,
                    'parent_section_id': kandam_section_id,
                    'level_type': 'padalam',
                    'level_type_tamil': 'படலம்',
                    'section_number': padalam_number,
                    'section_name': padalam_name,
                    'section_name_tamil': padalam_name,
                    'sort_order': padalam_number
                })

                verse_count = len(padalam_data['verses'])
                total_lines = sum(len(v['lines']) for v in padalam_data['verses'])
                print(f"  Padalam #{padalam_number}: {padalam_name} ({verse_count} verses, {total_lines} lines)")

                # Process each verse
                for verse_data in padalam_data['verses']:
                    verse_number = verse_data['verse_number']
                    verse_lines = verse_data['lines']

                    if not verse_lines:
                        continue

                    # Create verse
                    verse_id = self.verse_id
                    self.verse_id += 1

                    # Note: $ verse_id markers in source file are for reference only, not stored

                    self.verses.append({
                        'verse_id': verse_id,
                        'work_id': self.work_id,
                        'section_id': padalam_section_id,
                        'verse_number': verse_number,
                        'verse_type': 'verse',
                        'verse_type_tamil': 'பாடல்',
                        'total_lines': len(verse_lines),
                        'sort_order': verse_number,
                        'metadata': {}
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

                        # Process words
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
        self._bulk_copy_with_jsonb('verses', self.verses,
                       ['verse_id', 'work_id', 'section_id', 'verse_number', 'verse_type',
                        'verse_type_tamil', 'total_lines', 'sort_order', 'metadata'])

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

    def _bulk_copy_with_jsonb(self, table_name, data, columns):
        """Use PostgreSQL COPY for bulk insert with JSONB support"""
        if not data:
            return

        import json

        # Create StringIO buffer - manual TSV construction (NO csv.writer)
        buffer = io.StringIO()

        for row in data:
            row_data = []
            for col in columns:
                val = row.get(col)
                if val is None:
                    row_data.append('')
                elif col == 'metadata' and isinstance(val, dict):
                    # Convert dict to JSON string
                    row_data.append(json.dumps(val, ensure_ascii=False))
                else:
                    # Clean text fields - escape tabs and newlines
                    if isinstance(val, str):
                        val = str(val).replace('\t', ' ').replace('\n', ' ').replace('\r', '')
                    row_data.append(str(val))

            # Manual TSV construction
            buffer.write('\t'.join(row_data) + '\n')

        buffer.seek(0)

        # Use COPY command
        self.cursor.copy_from(buffer, table_name, columns=columns, null='')

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
    source_file = project_dir / "Tamil-Source-TamilConcordence" / "6_பக்தி இலக்கியம்" / "19.சீறாப்புராணம்.txt"

    # Allow database URL as command line argument
    if len(sys.argv) > 1:
        db_connection = sys.argv[1]

    print("=" * 70)
    print("Seerapuranam Parser - Bulk COPY Import")
    print("=" * 70)
    print(f"Database: {db_connection.split('@')[-1] if '@' in db_connection else db_connection}")
    print(f"Source: {source_file}")
    print("=" * 70)

    if not source_file.exists():
        print(f"\n✗ Error: Source file not found: {source_file}")
        sys.exit(1)

    # Create importer
    importer = SeerapuranamBulkImporter(db_connection, source_file)

    try:
        importer._ensure_work_exists()
        importer.parse_file()
        importer.bulk_insert()
        print("\n" + "=" * 70)
        print("✓ Seerapuranam import completed successfully!")
        print("=" * 70)
    finally:
        importer.close()
        print("\n✓ Database connection closed")


if __name__ == '__main__':
    main()
