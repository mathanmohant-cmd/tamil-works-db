#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sirupanchamoolam Bulk Import - Fast 2-phase import using PostgreSQL COPY
Phase 1: Parse text → In-memory data structures
Phase 2: Bulk COPY into database (1000x faster than INSERT)

Structure: Simple flat - 108 paadals
"""

import re
import psycopg2
from pathlib import Path
import csv
import io
import sys
from word_cleaning import split_and_clean_words


class SirupanchamoolamBulkImporter:
    def __init__(self, db_connection_string: str):
        """Initialize importer"""
        self.conn = psycopg2.connect(db_connection_string)
        self.cursor = self.conn.cursor()

        self.work_id = None  # Will be assigned dynamically

        # Data containers
        self.sections = []
        self.verses = []
        self.lines = []
        self.words = []

        # Get existing max IDs from database
        self.cursor.execute("SELECT COALESCE(MAX(section_id), 0) FROM sections")
        self.section_id = self.cursor.fetchone()[0] + 1

        self.cursor.execute("SELECT COALESCE(MAX(verse_id), 0) FROM verses")
        self.verse_id = self.cursor.fetchone()[0] + 1

        self.cursor.execute("SELECT COALESCE(MAX(line_id), 0) FROM lines")
        self.line_id = self.cursor.fetchone()[0] + 1

        self.cursor.execute("SELECT COALESCE(MAX(word_id), 0) FROM words")
        self.word_id = self.cursor.fetchone()[0] + 1

        print(f"  Starting IDs: section={self.section_id}, verse={self.verse_id}, line={self.line_id}, word={self.word_id}")

        # Default section ID (for flat structure)
        self.default_section_id = None

    def _ensure_work_exists(self):
        """Ensure work entry exists"""
        work_name_english = 'Sirupanchamoolam'
        work_name_tamil = 'சிறுபஞ்சமூலம்'

        # Check if work already exists by name
        self.cursor.execute("SELECT work_id FROM works WHERE work_name = %s", (work_name_english,))
        existing = self.cursor.fetchone()

        if existing:
            self.work_id = existing[0]
            print(f"\n[ERROR] Work {work_name_english} already exists (ID: {self.work_id})")
            print(f"To re-import, first delete the existing work:")
            print(f'  python scripts/delete_work.py "{work_name_english}"')
            self.cursor.close()
            self.conn.close()
            sys.exit(1)
        else:
            # Get next available work_id
            self.cursor.execute("SELECT COALESCE(MAX(work_id), 0) + 1 FROM works")
            self.work_id = self.cursor.fetchone()[0]

            print(f"  Creating Sirupanchamoolam work entry (ID: {self.work_id})...")
            self.cursor.execute("""
                INSERT INTO works (
                    work_id, work_name, work_name_tamil, period, author, author_tamil, description,
                    chronology_start_year, chronology_end_year,
                    chronology_confidence, chronology_notes, canonical_order
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                self.work_id, work_name_english, work_name_tamil,
                'Post-Sangam period', 'Karuvoorar', 'கருவூரார்',
                'Collection of medical and ethical verses, part of Eighteen Lesser Texts',
                300, 600, 'low',
                'Estimated post-Sangam period. Attributed to Karuvoorar.',
                265  # Eighteen Lesser Texts collection
            ))

            self.conn.commit()
            print("  [OK] Work created. Use collection management utility to assign to collections.")

            # Create a default section to hold all paadals
            self.default_section_id = self.section_id
            self.section_id += 1

            self.sections.append({
                'section_id': self.default_section_id,
                'work_id': self.work_id,
                'parent_section_id': None,
                'level_type': 'Collection',
                'level_type_tamil': 'தொகுப்பு',
                'section_number': 1,
                'section_name': None,  # NULL for flat works to avoid redundant hierarchy
                'section_name_tamil': None,
                'sort_order': 1
            })

    def parse_file(self, text_file_path: str):
        """Phase 1: Parse text file into memory"""
        print("\nPhase 1: Parsing file...")

        with open(text_file_path, 'r', encoding='utf-8') as f:
            lines_text = f.readlines()

        current_paadal_lines = []
        current_paadal_num = None
        paadal_count = 0

        for line in lines_text:
            line = line.strip()
            if not line:
                continue

            # Check for paadal marker (# with optional title on same line)
            paadal_match = re.match(r'^#(\d+)', line)
            if paadal_match:
                # Save previous paadal if exists
                if current_paadal_num is not None and current_paadal_lines:
                    self._add_paadal(current_paadal_num, current_paadal_lines)
                    paadal_count += 1
                    if paadal_count % 20 == 0:
                        print(f"  Parsed {paadal_count} paadals...")

                current_paadal_num = int(paadal_match.group(1))
                current_paadal_lines = []
                continue

            # Check for section headers (like "கடவுள் வாழ்த்து")
            # These are just labels, skip them
            if re.match(r'^[^\d#@].*வாழ்த்து', line):
                continue

            # Otherwise it's a paadal line
            if current_paadal_num is not None:
                current_paadal_lines.append(line)

        # Save last paadal
        if current_paadal_num is not None and current_paadal_lines:
            self._add_paadal(current_paadal_num, current_paadal_lines)
            paadal_count += 1

        print(f"[OK] Phase 1 complete: Parsed {paadal_count} paadals")
        print(f"  - Sections: {len(self.sections)}")
        print(f"  - Paadals: {len(self.verses)}")
        print(f"  - Lines: {len(self.lines)}")
        print(f"  - Words: {len(self.words)}")

    def _add_paadal(self, paadal_num, paadal_lines):
        """Add paadal to memory"""
        verse_id = self.verse_id
        self.verse_id += 1

        self.verses.append({
            'verse_id': verse_id,
            'work_id': self.work_id,
            'section_id': self.default_section_id,
            'verse_number': paadal_num,
            'verse_type': 'paadal',
            'verse_type_tamil': 'பாடல்',
            'total_lines': len(paadal_lines),
            'sort_order': paadal_num
        })

        for line_num, line_text in enumerate(paadal_lines, start=1):
            # Clean line: remove dots/periods, markers, and line numbers
            cleaned_line = line_text.replace('.', '').replace('…', '')
            # Remove structural markers
            cleaned_line = re.sub(r'^[#@$&*]+\s*', '', cleaned_line)
            # Remove ** and *** markers
            cleaned_line = re.sub(r'\*\*\*?', '', cleaned_line)
            # Remove trailing line numbers
            cleaned_line = re.sub(r'\s+\d+$', '', cleaned_line)

            line_id = self.line_id
            self.line_id += 1

            self.lines.append({
                'line_id': line_id,
                'verse_id': verse_id,
                'line_number': line_num,
                'line_text': cleaned_line.strip()
            })

            # Parse and clean words using shared utility
            cleaned_words = split_and_clean_words(cleaned_line)
            for word_position, word_text in enumerate(cleaned_words, start=1):
                word_id = self.word_id
                self.word_id += 1

                self.words.append({
                    'word_id': word_id,
                    'line_id': line_id,
                    'word_position': word_position,
                    'word_text': word_text,
                    'sandhi_split': None
                })

    def bulk_insert(self):
        """Phase 2: Bulk insert using COPY"""
        print("\nPhase 2: Bulk inserting into database...")

        # Insert sections
        print(f"  Inserting {len(self.sections)} sections...")
        self._bulk_copy('sections', self.sections,
                       ['section_id', 'work_id', 'parent_section_id', 'level_type', 'level_type_tamil',
                        'section_number', 'section_name', 'section_name_tamil', 'sort_order'])

        # Insert verses
        print(f"  Inserting {len(self.verses)} paadals...")
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
        print("[OK] Phase 2 complete: All data inserted")

    def _bulk_copy(self, table_name, data, columns):
        """Use COPY for bulk insert"""
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
        """Close connection"""
        self.cursor.close()
        self.conn.close()


def main():
    import os

    # Get database URL
    db_connection = os.getenv('DATABASE_URL', "postgresql://postgres:postgres@localhost/tamil_literature")
    if len(sys.argv) > 1:
        db_connection = sys.argv[1]

    # Text file path
    script_dir = Path(__file__).parent
    project_dir = script_dir.parent
    text_file = project_dir / "Tamil-Source-TamilConcordence" / "3_சங்க_இலக்கியம்_பதினெண்கீழ்க்கணக்கு" / "15-சிறுபஞ்சமூலம்.txt"

    print("="*70)
    print("Sirupanchamoolam Bulk Import - Fast 2-Phase Import")
    print("="*70)
    print(f"Database: {db_connection[:50]}...")
    print("Text file: 15-Sirupanchamoolam.txt")

    importer = SirupanchamoolamBulkImporter(db_connection)

    try:
        importer._ensure_work_exists()
        importer.parse_file(str(text_file))
        importer.bulk_insert()
        print("\n[OK] Import complete!")
    finally:
        importer.close()


if __name__ == '__main__':
    main()
