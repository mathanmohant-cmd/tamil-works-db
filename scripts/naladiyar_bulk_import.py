#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Naladiyar Bulk Import - Fast 2-phase import using PostgreSQL COPY
Phase 1: Parse text → In-memory data structures
Phase 2: Bulk COPY into database (1000x faster than INSERT)

Structure: 3 Paals → Iyals → 40 Adhikarams → 400 Verses (4 lines each)
"""

import re
import psycopg2
from pathlib import Path
import csv
import io
import sys
from word_cleaning import split_and_clean_words


class NaladiyarBulkImporter:
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

        # Section cache to avoid duplicates
        self.section_cache = {}

        # Current hierarchy context
        self.current_paal_id = None
        self.current_iyal_id = None
        self.current_adhikaram_id = None

    def _ensure_work_exists(self):
        """Ensure work entry exists"""
        work_name_english = 'Naladiyar'
        work_name_tamil = 'நாலடியார்'

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

            print(f"  Creating Naladiyar work entry (ID: {self.work_id})...")
            self.cursor.execute("""
                INSERT INTO works (
                    work_id, work_name, work_name_tamil, period, author, author_tamil, description,
                    chronology_start_year, chronology_end_year,
                    chronology_confidence, chronology_notes, canonical_order
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                self.work_id, work_name_english, work_name_tamil,
                '5th - 10th century CE', 'Unknown (Multiple Jain Authors)', 'அறியப்படாத பல ஜைன கவிஞர்கள்',
                'Collection of 400 four-line ethical verses (நாலடி) organized in 3 Paals and 40 Adhikarams',
                400, 1000, 'low',
                'Estimated 5th-10th century CE. Jain didactic work part of Eighteen Lesser Texts.',
                250  # First of Eighteen Lesser Texts
            ))

            self.conn.commit()
            print("  [OK] Work created. Use collection management utility to assign to collections.")

    def _get_or_create_section_id(self, parent_id, level_type, level_type_tamil, section_number, section_name, section_name_tamil):
        """Get or create section, return section_id"""
        cache_key = (parent_id, level_type, section_number)

        if cache_key in self.section_cache:
            return self.section_cache[cache_key]

        # Create new section
        section_id = self.section_id
        self.section_id += 1

        # Calculate sort_order (simple sequential for now)
        sort_order = section_number

        self.sections.append({
            'section_id': section_id,
            'work_id': self.work_id,
            'parent_section_id': parent_id,
            'level_type': level_type,
            'level_type_tamil': level_type_tamil,
            'section_number': section_number,
            'section_name': section_name,
            'section_name_tamil': section_name_tamil,
            'sort_order': sort_order
        })

        self.section_cache[cache_key] = section_id
        return section_id

    def parse_file(self, text_file_path: str):
        """Phase 1: Parse text file into memory"""
        print("\nPhase 1: Parsing file...")

        with open(text_file_path, 'r', encoding='utf-8') as f:
            lines_text = f.readlines()

        current_verse_lines = []
        current_verse_num = None
        verse_count = 0
        paal_counter = 0
        iyal_counter = 0
        adhikaram_counter = 0

        for line in lines_text:
            line = line.strip()
            if not line:
                continue

            # Check for Paal marker (&)
            if line.startswith('&'):
                # Save previous verse if exists
                if current_verse_num and current_verse_lines:
                    self._add_verse(current_verse_num, current_verse_lines)
                    verse_count += 1
                    current_verse_lines = []
                    current_verse_num = None

                paal_counter += 1
                paal_name_tamil = line[1:].strip()

                # Map Tamil names to English
                paal_name_map = {
                    'அறத்துப்பால்': 'Virtue',
                    'பொருட்பால்': 'Wealth',
                    'காமத்துப்பால்': 'Love'
                }
                paal_name = paal_name_map.get(paal_name_tamil, paal_name_tamil)

                self.current_paal_id = self._get_or_create_section_id(
                    None, 'Paal', 'பால்',
                    paal_counter,
                    paal_name,
                    paal_name_tamil
                )
                continue

            # Check for Iyal marker (number followed by Tamil text)
            iyal_match = re.match(r'^(\d+)\s+([\u0B80-\u0BFF\s]+இயல்)\s*$', line)
            if iyal_match:
                # Save previous verse if exists
                if current_verse_num and current_verse_lines:
                    self._add_verse(current_verse_num, current_verse_lines)
                    verse_count += 1
                    current_verse_lines = []
                    current_verse_num = None

                iyal_counter += 1
                iyal_num = int(iyal_match.group(1))
                iyal_name_tamil = iyal_match.group(2).strip()

                # Extract base name without "இயல்"
                iyal_base_name = iyal_name_tamil.replace('இயல்', '').strip()

                self.current_iyal_id = self._get_or_create_section_id(
                    self.current_paal_id, 'Iyal', 'இயல்',
                    iyal_num,
                    iyal_base_name,  # Use transliteration or same as Tamil for now
                    iyal_name_tamil
                )
                continue

            # Check for Adhikaram marker (@)
            adhikaram_match = re.match(r'^@(\d+)\s+(.+)$', line)
            if adhikaram_match:
                # Save previous verse if exists
                if current_verse_num and current_verse_lines:
                    self._add_verse(current_verse_num, current_verse_lines)
                    verse_count += 1
                    current_verse_lines = []
                    current_verse_num = None

                adhikaram_counter += 1
                adhikaram_num = int(adhikaram_match.group(1))
                adhikaram_name_tamil = adhikaram_match.group(2).strip()

                self.current_adhikaram_id = self._get_or_create_section_id(
                    self.current_iyal_id, 'Adhikaram', 'அதிகாரம்',
                    adhikaram_num,
                    adhikaram_name_tamil,  # Use Tamil name as English for now
                    adhikaram_name_tamil
                )
                continue

            # Check for verse marker (#)
            verse_match = re.match(r'^#(\d+)$', line)
            if verse_match:
                # Save previous verse if exists
                if current_verse_num and current_verse_lines:
                    self._add_verse(current_verse_num, current_verse_lines)
                    verse_count += 1
                    if verse_count % 50 == 0:
                        print(f"  Parsed {verse_count} verses...")

                current_verse_num = int(verse_match.group(1))
                current_verse_lines = []
                continue

            # Skip lines that are section headers with "அதிகாரம்-"
            if line.startswith('அதிகாரம்-'):
                continue

            # Skip "மேல்" separator
            if line == 'மேல்':
                continue

            # Otherwise it's a verse line
            if current_verse_num is not None:
                current_verse_lines.append(line)

        # Save last verse
        if current_verse_num and current_verse_lines:
            self._add_verse(current_verse_num, current_verse_lines)
            verse_count += 1

        print(f"[OK] Phase 1 complete: Parsed {verse_count} verses")
        print(f"  - Sections: {len(self.sections)} (Paals: {paal_counter}, Iyals: {iyal_counter}, Adhikarams: {adhikaram_counter})")
        print(f"  - Verses: {len(self.verses)}")
        print(f"  - Lines: {len(self.lines)}")
        print(f"  - Words: {len(self.words)}")

    def _add_verse(self, verse_num, verse_lines):
        """Add verse to memory"""
        verse_id = self.verse_id
        self.verse_id += 1

        self.verses.append({
            'verse_id': verse_id,
            'work_id': self.work_id,
            'section_id': self.current_adhikaram_id,
            'verse_number': verse_num,
            'verse_type': 'verse',
            'verse_type_tamil': 'பாடல்',
            'total_lines': len(verse_lines),
            'sort_order': verse_num
        })

        for line_num, line_text in enumerate(verse_lines, start=1):
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
    text_file = project_dir / "Tamil-Source-TamilConcordence" / "3_சங்க_இலக்கியம்_பதினெண்கீழ்க்கணக்கு" / "1-நாலடியார்.txt"

    print("="*70)
    print("Naladiyar Bulk Import - Fast 2-Phase Import")
    print("="*70)
    print(f"Database: {db_connection[:50]}...")
    print("Text file: 1-Naladiyar.txt")

    importer = NaladiyarBulkImporter(db_connection)

    try:
        importer._ensure_work_exists()
        importer.parse_file(str(text_file))
        importer.bulk_insert()
        print("\n[OK] Import complete!")
    finally:
        importer.close()


if __name__ == '__main__':
    main()
