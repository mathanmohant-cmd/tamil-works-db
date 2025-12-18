#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Silapathikaram Parser for Tamil Literature Database - Bulk COPY Import

This script parses Silapathikaram text files and imports them into the database.
Uses 2-phase bulk import for high performance.

Structure:
- Work: Silapathikaram (சிலப்பதிகாரம்)
- Level 1 (Kandam): 3 chapters
  - புகார்க் காண்டம் (Pukar Kandam)
  - மதுரைக் காண்டம் (Madurai Kandam)
  - வஞ்சிக் காண்டம் (Vanci Kandam)
- Level 2 (Kaathai): Subsections marked with # (e.g., #1 மங்கல வாழ்த்துப் பாடல்)
- IMPORTANT: Each Kaathai is ONE complete verse (not multiple verses)
- Lines: Individual lines within each Kaathai verse
- Note: Blank lines in input files are just for readability, NOT verse boundaries
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

# Kandam files (ordered)
KANDAM_FILES = [
    ('சிலப்பதிகாரம் – புகார்க் காண்டம்.txt', 'புகார்க் காண்டம்', 'Pukar Kandam', 1),
    ('சிலப்பதிகாரம் – மதுரைக் காண்டம்.txt', 'மதுரைக் காண்டம்', 'Madurai Kandam', 2),
    ('சிலப்பதிகாரம் – வஞ்சிக் காண்டம்.txt', 'வஞ்சிக் காண்டம்', 'Vanci Kandam', 3),
]


def clean_line(line):
    """
    Clean a line by:
    - Removing line numbers (multiples of 5) at the end
    - Removing anything after **
    - Stripping whitespace
    """
    # Remove anything after ** (including **)
    if '**' in line:
        line = line.split('**')[0]

    # Remove trailing numbers (multiples of 5)
    line = re.sub(r'\s+\d+$', '', line)

    return line.strip()


def parse_kandam_file(file_path):
    """
    Parse a single Kandam file and extract structure.

    IMPORTANT: Each Kaathai (section marked with #) is ONE complete verse.
    Blank lines are just for readability, NOT verse boundaries.

    Returns:
    {
        'kandam_name_tamil': str,
        'sections': [
            {
                'number': int,
                'name': str,
                'lines': [str, str, ...]  # All lines in this Kaathai (ONE verse)
            },
            ...
        ]
    }
    """
    print(f"  Parsing file: {file_path.name}")

    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    kandam_info = {
        'sections': []
    }

    current_section = None

    for line in lines:
        line = line.rstrip('\n')

        # Skip empty lines (they are just for readability)
        if not line.strip():
            continue

        # Check for Kandam marker ($)
        if line.startswith('$'):
            # Extract kandam info (format: $புகார்க் காண்டம் or $2 மதுரைக் காண்டம்)
            kandam_text = line[1:].strip()
            # Remove leading number if present
            kandam_text = re.sub(r'^\d+\s+', '', kandam_text)
            kandam_info['kandam_name_tamil'] = kandam_text
            continue

        # Check for section marker (#) - This starts a NEW Kaathai (ONE verse)
        if line.startswith('#'):
            # Save previous section if exists
            if current_section is not None:
                kandam_info['sections'].append(current_section)

            # Parse section header (format: #0 பதிகம் or #11 காடுகாண் காதை)
            match = re.match(r'^#(\d+)\s+(.+)$', line)
            if match:
                section_number = int(match.group(1))
                section_name = match.group(2).strip()

                current_section = {
                    'number': section_number,
                    'name': section_name,
                    'lines': []  # All lines belong to ONE verse
                }
            continue

        # Regular content line - add to current section's lines
        cleaned = clean_line(line)
        if cleaned and current_section is not None:
            current_section['lines'].append(cleaned)

    # Save last section
    if current_section is not None:
        kandam_info['sections'].append(current_section)

    return kandam_info


# Note: Removed simple_word_split function - now using shared word_cleaning utility


class SilapathikaramBulkImporter:
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

    def _ensure_work_exists(self):
        """Ensure Silapathikaram work exists"""
        work_name_tamil = 'சிலப்பதிகாரம்'
        work_name_english = 'Silapathikaram'

        # Check if work already exists by name
        self.cursor.execute("SELECT work_id FROM works WHERE work_name = %s", (work_name_english,))
        existing = self.cursor.fetchone()

        if existing:
            self.work_id = existing[0]
            print(f"Work {work_name_tamil} already exists (ID: {self.work_id})")
        else:
            # Get next available work_id
            self.cursor.execute("SELECT COALESCE(MAX(work_id), 0) + 1 FROM works")
            self.work_id = self.cursor.fetchone()[0]

            print(f"Creating work entry for {work_name_tamil}...")
            self.cursor.execute("""
                INSERT INTO works (
                    work_id, work_name, work_name_tamil, description, period, author, author_tamil,
                    chronology_start_year, chronology_end_year,
                    chronology_confidence, chronology_notes
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                self.work_id,
                work_name_english,
                work_name_tamil,
                'One of the Five Great Epics of Tamil Literature',
                '5th-6th century CE',
                'Ilango Adigal',
                'இளங்கோ அடிகள்',
                400, 600, 'high',
                'Epic by Iḷaṅkō Aṭikaḷ. References to Gajabahu of Sri Lanka help dating.'
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

            # Create Kandam section
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

            # Process each Kaathai (subsection) - each Kaathai is ONE verse
            for section_data in kandam_data['sections']:
                section_name = section_data['name']
                section_number = section_data['number']
                kaathai_lines = section_data['lines']

                if not kaathai_lines:
                    continue

                # Create Kaathai section
                kaathai_section_id = self.section_id
                self.section_id += 1

                self.sections.append({
                    'section_id': kaathai_section_id,
                    'work_id': self.work_id,
                    'parent_section_id': kandam_section_id,
                    'level_type': 'kaathai',
                    'level_type_tamil': 'காதை',
                    'section_number': section_number,
                    'section_name': section_name,
                    'section_name_tamil': section_name,
                    'sort_order': section_number
                })

                line_count = len(kaathai_lines)
                print(f"  Kaathai #{section_number}: {section_name} ({line_count} lines in 1 verse)")

                # Create ONE verse for this entire Kaathai
                # verse_type stores the specific name (e.g., 'மங்கல வாழ்த்துப் பாடல்', 'கானல் வரி')
                verse_id = self.verse_id
                self.verse_id += 1

                self.verses.append({
                    'verse_id': verse_id,
                    'work_id': self.work_id,
                    'section_id': kaathai_section_id,
                    'verse_number': 1,  # Always 1 - one verse per Kaathai
                    'verse_type': section_name,  # Use the actual section name (includes காதை/வரி/பாடல்/etc.)
                    'verse_type_tamil': section_name,  # Same as section_name since it's already in Tamil
                    'total_lines': line_count,
                    'sort_order': 1
                })

                # Process all lines in this Kaathai (which is one verse)
                for line_num, line_text in enumerate(kaathai_lines, 1):
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
    source_dir = project_dir / "Tamil-Source-TamilConcordence" / "4_ஐம்பெருங்காப்பியங்கள்" / "சிலப்பதிகாரம்"

    # Allow database URL as command line argument
    if len(sys.argv) > 1:
        db_connection = sys.argv[1]

    print("=" * 70)
    print("Silapathikaram Parser - Bulk COPY Import")
    print("=" * 70)
    print(f"Database: {db_connection.split('@')[-1] if '@' in db_connection else db_connection}")
    print(f"Source: {source_dir}")
    print("=" * 70)

    # Create importer
    importer = SilapathikaramBulkImporter(db_connection, source_dir)

    try:
        importer._ensure_work_exists()
        importer.parse_all_files()
        importer.bulk_insert()
        print("\n" + "=" * 70)
        print("✓ Silapathikaram import completed successfully!")
        print("=" * 70)
    finally:
        importer.close()
        print("\n✓ Database connection closed")


if __name__ == '__main__':
    main()
