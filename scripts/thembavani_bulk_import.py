#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Thembavani Bulk Import - Fast 2-phase import using PostgreSQL COPY
Phase 1: Parse text → Generate CSV files
Phase 2: Bulk COPY into database (1000x faster than INSERT)

Thembavani: Christian Tamil epic about St. Joseph
Author: Veeramamunivar (Constantine Joseph Beschi) - 18th century CE
Structure: Padalams (sections) marked with @, verses with #
"""

import re
import psycopg2
from pathlib import Path
import csv
import io
import sys
import os
from word_cleaning import split_and_clean_words

class ThembavaniBulkImporter:
    def __init__(self, db_connection_string: str):
        """Initialize importer"""
        self.conn = psycopg2.connect(db_connection_string)
        self.cursor = self.conn.cursor()

        self.work_id = None

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

        # Section cache
        self.section_cache = {}

    def _ensure_work_exists(self):
        """Ensure work entry exists"""
        work_name = 'Thembavani'
        work_name_tamil = 'தேம்பாவணி'

        # Check if work already exists
        self.cursor.execute("SELECT work_id FROM works WHERE work_name = %s", (work_name,))
        existing = self.cursor.fetchone()

        if existing:
            self.work_id = existing[0]
            print(f"\n[ERROR] Work {work_name_tamil} already exists (ID: {self.work_id})")
            print(f"To re-import, first delete the existing work:")
            print(f'  python scripts/delete_work.py "{work_name}"')
            self.cursor.close()
            self.conn.close()
            sys.exit(1)
        else:
            # Get next available work_id
            self.cursor.execute("SELECT COALESCE(MAX(work_id), 0) + 1 FROM works")
            self.work_id = self.cursor.fetchone()[0]

            print(f"  Creating Thembavani work entry (ID: {self.work_id})...")
            self.cursor.execute("""
                INSERT INTO works (
                    work_id, work_name, work_name_tamil, period, author, author_tamil, description,
                    chronology_start_year, chronology_end_year,
                    chronology_confidence, chronology_notes, canonical_order
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                self.work_id, work_name, work_name_tamil,
                '18th century CE', 'Constantine Joseph Beschi', 'வீரமாமுனிவர்',
                'Christian Tamil epic poem about St. Joseph - blend of Tamil literary tradition and Christian theology',
                1720, 1750, 'high',
                'Written by Italian Jesuit missionary Veeramamunivar (Beschi) in Tamil epic style',
                600  # Colonial period Christian literature
            ))

            self.conn.commit()
            print(f"  [OK] Work created")

    def _get_or_create_section_id(self, section_number, section_name_tamil):
        """Get or create section (Padalam)"""
        cache_key = (section_number, section_name_tamil)

        if cache_key in self.section_cache:
            return self.section_cache[cache_key]

        section_id = self.section_id
        self.section_id += 1

        self.sections.append({
            'section_id': section_id,
            'work_id': self.work_id,
            'parent_section_id': None,
            'level_type': 'Padalam',
            'level_type_tamil': 'படலம்',
            'section_number': section_number,
            'section_name': section_name_tamil,
            'section_name_tamil': section_name_tamil,
            'sort_order': section_number
        })

        self.section_cache[cache_key] = section_id
        return section_id

    def parse_file(self, text_file_path: str):
        """Phase 1: Parse text file into memory"""
        print(f"\nPhase 1: Parsing {Path(text_file_path).name}...")

        with open(text_file_path, 'r', encoding='utf-8') as f:
            lines_text = f.readlines()

        current_section_id = None
        current_section_num = None
        current_verse_lines = []
        current_verse_num = None
        verse_count = 0

        for line in lines_text:
            line = line.strip()
            if not line or line == 'மேல்':
                continue

            # Check for section header: @[number] [section name]
            section_match = re.match(r'^@(\d+)\s+(.+)$', line)
            if section_match:
                # Save previous verse
                if current_verse_num and current_verse_lines and current_section_id:
                    self._add_verse(current_section_id, current_verse_num, current_verse_lines)
                    verse_count += 1

                current_verse_lines = []
                current_verse_num = None

                current_section_num = int(section_match.group(1))
                section_name = section_match.group(2).strip()
                current_section_id = self._get_or_create_section_id(current_section_num, section_name)
                print(f"  Found section: @{current_section_num} {section_name}")
                continue

            # Check for verse number
            verse_match = re.match(r'^#(\d+)$', line)
            if verse_match:
                # Save previous verse
                if current_verse_num and current_verse_lines and current_section_id:
                    self._add_verse(current_section_id, current_verse_num, current_verse_lines)
                    verse_count += 1
                    if verse_count % 100 == 0:
                        print(f"  Parsed {verse_count} verses...")

                current_verse_num = int(verse_match.group(1))
                current_verse_lines = []
                continue

            # Regular verse line
            if current_verse_num is not None:
                cleaned = line.replace('…', '').strip()
                if cleaned:
                    current_verse_lines.append(cleaned)

        # Save last verse
        if current_verse_num and current_verse_lines and current_section_id:
            self._add_verse(current_section_id, current_verse_num, current_verse_lines)
            verse_count += 1

        print(f"[OK] Phase 1 complete: Parsed {verse_count} verses")
        print(f"  - Sections: {len(self.sections)}")
        print(f"  - Verses: {len(self.verses)}")
        print(f"  - Lines: {len(self.lines)}")
        print(f"  - Words: {len(self.words)}")

    def _add_verse(self, section_id, verse_num, verse_lines):
        """Add verse to memory"""
        verse_id = self.verse_id
        self.verse_id += 1

        self.verses.append({
            'verse_id': verse_id,
            'work_id': self.work_id,
            'section_id': section_id,
            'verse_number': verse_num,
            'verse_type': 'verse',
            'verse_type_tamil': 'செய்யுள்',
            'total_lines': len(verse_lines),
            'sort_order': verse_num
        })

        for line_num, line_text in enumerate(verse_lines, start=1):
            line_id = self.line_id
            self.line_id += 1

            # Clean line text: remove trailing numbers, normalize whitespace
            cleaned_line = re.sub(r'\s+\d+\s*$', '', line_text)  # Remove trailing numbers
            cleaned_line = re.sub(r'\s+', ' ', cleaned_line)  # Normalize whitespace
            cleaned_line = cleaned_line.strip()

            self.lines.append({
                'line_id': line_id,
                'verse_id': verse_id,
                'line_number': line_num,
                'line_text': cleaned_line
            })

            # Parse words
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

        buffer = io.StringIO()
        writer = csv.writer(buffer, delimiter='\t')

        for row in data:
            writer.writerow([row.get(col) if row.get(col) is not None else '\\N' for col in columns])

        buffer.seek(0)
        self.cursor.copy_from(buffer, table_name, columns=columns, null='\\N')

    def close(self):
        """Close connection"""
        self.cursor.close()
        self.conn.close()


def main():
    # Get database URL
    db_connection = os.getenv('DATABASE_URL', "postgresql://postgres:postgres@localhost/tamil_literature")
    if len(sys.argv) > 1:
        db_connection = sys.argv[1]

    # Text file path
    script_dir = Path(__file__).parent
    project_dir = script_dir.parent
    text_file = project_dir / "Tamil-Source-TamilConcordence" / "6_பக்தி இலக்கியம்" / "18.தேம்பாவணி.txt"

    print("="*70)
    print("Thembavani Bulk Import - Fast 2-Phase Import")
    print("="*70)
    print(f"Database: {db_connection[:50]}...")
    print(f"Text file: {text_file.name}")

    importer = ThembavaniBulkImporter(db_connection)

    try:
        importer._ensure_work_exists()
        importer.parse_file(str(text_file))
        importer.bulk_insert()

        print("\n" + "="*70)
        print("[OK] Import complete!")
        print(f"  - Sections imported: {len(importer.sections)}")
        print(f"  - Verses imported: {len(importer.verses)}")
        print(f"  - Lines imported: {len(importer.lines)}")
        print(f"  - Words imported: {len(importer.words)}")
        print("="*70)

    except Exception as e:
        print(f"\n[ERROR] Error: {e}")
        import traceback
        traceback.print_exc()
        importer.conn.rollback()
    finally:
        importer.close()


if __name__ == '__main__':
    main()
