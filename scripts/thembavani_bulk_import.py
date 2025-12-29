#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Thembavani Bulk Import Script
===============================
Imports Thembavani (தேம்பாவணி) by Veeramaamunivar (Constanzo Giuseppe Beschi)

Work: Thembavani (தேம்பாவணி) - Christian epic poem
Author: Veeramaamunivar (வீரமாமுனிவர்) - also known as Constanzo Giuseppe Beschi
Period: 18th century CE
Tradition: Christian devotional literature
Standalone work (no collection)

Structure:
    வீரமாமுனிவர் (Constanzo Giuseppe Beschi) ^ தேம்பாவணி
    @number section_name
    #verse_number
    verse lines...
    மேல்

Each @section contains multiple #verses.
Each #verse is ONE complete verse with multiple lines.

Uses 2-phase bulk COPY pattern for optimal performance.
"""

import os
import sys
import re
import json
import io
import psycopg2
from typing import List, Dict

class ThembavaniBulkImporter:
    def __init__(self, db_connection_string: str):
        """Initialize the Thembavani bulk importer"""
        self.db_connection_string = db_connection_string
        self.conn = None
        self.cursor = None

        # Data containers
        self.works = []
        self.sections = []
        self.verses = []
        self.lines = []
        self.words = []

        # ID counters
        self.work_id = 1
        self.section_id = 1
        self.verse_id = 1
        self.line_id = 1
        self.word_id = 1

        # Current state
        self.current_work_id = None
        self.section_sort_order = 0
        self.verse_sort_order = 0

    def connect(self):
        """Connect to the database and get MAX IDs"""
        print("Connecting to database...")
        self.conn = psycopg2.connect(self.db_connection_string)
        self.cursor = self.conn.cursor()

        # Get MAX IDs
        self.cursor.execute("SELECT COALESCE(MAX(work_id), 0) + 1 FROM works")
        self.work_id = self.cursor.fetchone()[0]

        self.cursor.execute("SELECT COALESCE(MAX(section_id), 0) + 1 FROM sections")
        self.section_id = self.cursor.fetchone()[0]

        self.cursor.execute("SELECT COALESCE(MAX(verse_id), 0) + 1 FROM verses")
        self.verse_id = self.cursor.fetchone()[0]

        self.cursor.execute("SELECT COALESCE(MAX(line_id), 0) + 1 FROM lines")
        self.line_id = self.cursor.fetchone()[0]

        self.cursor.execute("SELECT COALESCE(MAX(word_id), 0) + 1 FROM words")
        self.word_id = self.cursor.fetchone()[0]

        print(f"  Starting IDs: work={self.work_id}, section={self.section_id}, verse={self.verse_id}")

    def parse_file(self, file_path: str):
        """Parse Thembavani file"""
        print("\n=== PHASE 1: Parsing Thembavani into memory ===")

        # Create work
        work_metadata = {
            'tradition': 'Christian',
            'author_western_name': 'Constanzo Giuseppe Beschi',
            'author_tamil_name': 'வீரமாமுனிவர்',
            'time_period': '18th century CE',
            'genre': 'epic',
            'themes': ['Christian theology', 'Joseph narrative', 'devotional poetry'],
            'literary_significance': 'First major Christian epic in Tamil',
            'language_style': 'Classical Tamil',
            'composition_date': '1726 CE',
            'verses_count': 3615
        }

        work_dict = {
            'work_id': self.work_id,
            'work_name': "Thembavani",
            'work_name_tamil': "தேம்பாவணி",
            'period': '18th century CE',
            'author': "Veeramaamunivar",
            'author_tamil': "வீரமாமுனிவர்",
            'description': "தேம்பாவணி - Christian epic by Veeramaamunivar (Constanzo Giuseppe Beschi)",
            'canonical_order': 501,
            'primary_collection_id': None,  # Standalone work
            'metadata': work_metadata
        }
        self.works.append(work_dict)
        self.current_work_id = self.work_id
        print(f"  Created work: தேம்பாவணி (ID: {self.work_id})")
        self.work_id += 1

        # Parse file
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        current_section_number = None
        current_section_name = None
        current_section_id = None
        current_verse_number = None
        current_verse_lines = []

        for line in lines:
            line_stripped = line.strip()

            # Skip author header
            if '^' in line_stripped:
                continue

            # Section marker: @number section_name
            section_match = re.match(r'^@(\d+)\s+(.+)', line_stripped)
            if section_match:
                # Save previous verse if exists
                if current_verse_lines and current_verse_number is not None:
                    self.create_verse(
                        current_verse_number,
                        current_verse_lines,
                        current_section_id
                    )
                    current_verse_lines = []
                    current_verse_number = None

                current_section_number = int(section_match.group(1))
                current_section_name = section_match.group(2).strip()

                # Create section
                self.section_sort_order += 1
                section_metadata = {
                    'section_type': 'padalam',
                    'section_type_tamil': 'படலம்'
                }

                section_dict = {
                    'section_id': self.section_id,
                    'work_id': self.current_work_id,
                    'parent_section_id': None,
                    'level_type': 'Padalam',
                    'level_type_tamil': 'படலம்',
                    'section_number': current_section_number,
                    'section_name': current_section_name,
                    'section_name_tamil': current_section_name,
                    'sort_order': self.section_sort_order,
                    'metadata': section_metadata
                }
                self.sections.append(section_dict)
                current_section_id = self.section_id
                self.section_id += 1
                continue

            # Verse marker: #number
            verse_match = re.match(r'^#(\d+)', line_stripped)
            if verse_match:
                # Save previous verse if exists
                if current_verse_lines and current_verse_number is not None:
                    self.create_verse(
                        current_verse_number,
                        current_verse_lines,
                        current_section_id
                    )
                    current_verse_lines = []

                current_verse_number = int(verse_match.group(1))
                continue

            # End of section
            if line_stripped == 'மேல்':
                # Save last verse
                if current_verse_lines and current_verse_number is not None:
                    self.create_verse(
                        current_verse_number,
                        current_verse_lines,
                        current_section_id
                    )
                    current_verse_lines = []
                    current_verse_number = None
                continue

            # Collect verse lines
            if line_stripped and current_verse_number is not None:
                current_verse_lines.append(line_stripped)

        # Handle last verse if file doesn't end with மேல்
        if current_verse_lines and current_verse_number is not None:
            self.create_verse(
                current_verse_number,
                current_verse_lines,
                current_section_id
            )

        print(f"  [OK] Parsed {len(self.sections)} sections, {len(self.verses)} verses")
        print(f"       {len(self.lines)} lines, {len(self.words)} words")

    def create_verse(self, verse_num: int, verse_lines: List[str], section_id: int):
        """Create a verse with lines and words"""
        self.verse_sort_order += 1

        verse_metadata = {
            'author': 'வீரமாமுனிவர்',
            'tradition': 'Christian',
            'line_count': len(verse_lines),
            'epic_type': 'Christian devotional epic'
        }

        verse_dict = {
            'verse_id': self.verse_id,
            'work_id': self.current_work_id,
            'section_id': section_id,
            'verse_number': verse_num,
            'verse_type': 'Epic Verse',
            'verse_type_tamil': 'காப்பிய செய்யுள்',
            'total_lines': len(verse_lines),
            'sort_order': self.verse_sort_order,
            'metadata': verse_metadata
        }
        self.verses.append(verse_dict)
        current_verse_id = self.verse_id
        self.verse_id += 1

        # Create lines and words
        for line_num, line_text in enumerate(verse_lines, 1):
            self.create_line_and_words(line_text, line_num, current_verse_id)

    def create_line_and_words(self, line_text: str, line_number: int, verse_id: int):
        """Create a line and segment it into words"""
        line_dict = {
            'line_id': self.line_id,
            'verse_id': verse_id,
            'line_number': line_number,
            'line_text': line_text
        }
        self.lines.append(line_dict)
        current_line_id = self.line_id
        self.line_id += 1

        # Segment into words
        words = self.segment_line(line_text)
        for word_position, word_text in enumerate(words, 1):
            word_dict = {
                'word_id': self.word_id,
                'line_id': current_line_id,
                'word_position': word_position,
                'word_text': word_text,
                'sandhi_split': None
            }
            self.words.append(word_dict)
            self.word_id += 1

    def segment_line(self, line_text: str) -> List[str]:
        """Segment a line into words"""
        line_text = line_text.replace('_', ' ')
        line_text = line_text.replace('-', ' ')
        words = line_text.split()
        words = [w for w in words if w.strip()]
        return words

    def bulk_insert_works(self):
        """Bulk insert works using PostgreSQL COPY"""
        if not self.works:
            return

        buffer = io.StringIO()

        for work in self.works:
            metadata_json = json.dumps(work.get('metadata', {}), ensure_ascii=False) if work.get('metadata') else ''

            fields = [
                str(work['work_id']), work['work_name'], work['work_name_tamil'],
                work.get('period', ''), work.get('author', ''), work.get('author_tamil', ''),
                work.get('description', ''),
                str(work['chronology_start_year']) if work.get('chronology_start_year') is not None else '',
                str(work['chronology_end_year']) if work.get('chronology_end_year') is not None else '',
                work.get('chronology_confidence', ''),
                work.get('chronology_notes', ''),
                str(work['canonical_order']) if work.get('canonical_order') is not None else '',
                str(work['primary_collection_id']) if work.get('primary_collection_id') is not None else '',
                metadata_json
            ]

            # Clean fields
            cleaned_fields = []
            for i, field in enumerate(fields):
                if field is None:
                    cleaned_fields.append('')
                else:
                    if i < len(fields) - 1:
                        field = str(field).replace('\t', ' ').replace('\n', ' ').replace('\r', '')
                    cleaned_fields.append(field)

            buffer.write('\t'.join(cleaned_fields) + '\n')

        buffer.seek(0)
        self.cursor.copy_from(buffer, 'works',
            columns=('work_id', 'work_name', 'work_name_tamil', 'period', 'author',
                    'author_tamil', 'description', 'chronology_start_year',
                    'chronology_end_year', 'chronology_confidence', 'chronology_notes',
                    'canonical_order', 'primary_collection_id', 'metadata'),
            null='')
        print(f"  [OK] Bulk inserted {len(self.works)} works")

    def bulk_insert_sections(self):
        """Bulk insert sections using PostgreSQL COPY"""
        if not self.sections:
            return

        buffer = io.StringIO()

        for section in self.sections:
            metadata_json = json.dumps(section.get('metadata', {}), ensure_ascii=False) if section.get('metadata') else ''

            fields = [
                str(section['section_id']), str(section['work_id']),
                str(section['parent_section_id']) if section.get('parent_section_id') is not None else '',
                section.get('level_type', ''), section.get('level_type_tamil', ''),
                str(section['section_number']) if section.get('section_number') is not None else '',
                section.get('section_name', ''),
                section.get('section_name_tamil', ''), str(section['sort_order']), metadata_json
            ]

            # Clean fields
            cleaned_fields = []
            for i, field in enumerate(fields):
                if field is None:
                    cleaned_fields.append('')
                else:
                    if i < len(fields) - 1:
                        field = str(field).replace('\t', ' ').replace('\n', ' ').replace('\r', '')
                    cleaned_fields.append(field)

            buffer.write('\t'.join(cleaned_fields) + '\n')

        buffer.seek(0)
        self.cursor.copy_from(buffer, 'sections',
            columns=('section_id', 'work_id', 'parent_section_id', 'level_type',
                    'level_type_tamil', 'section_number', 'section_name',
                    'section_name_tamil', 'sort_order', 'metadata'),
            null='')
        print(f"  [OK] Bulk inserted {len(self.sections)} sections")

    def bulk_insert_verses(self):
        """Bulk insert verses using PostgreSQL COPY"""
        if not self.verses:
            return

        buffer = io.StringIO()

        for verse in self.verses:
            metadata_json = json.dumps(verse.get('metadata', {}), ensure_ascii=False) if verse.get('metadata') else ''

            fields = [
                str(verse['verse_id']), str(verse['work_id']),
                str(verse['section_id']) if verse.get('section_id') is not None else '',
                str(verse['verse_number']), verse.get('verse_type', ''),
                verse.get('verse_type_tamil', ''), str(verse['total_lines']),
                str(verse['sort_order']), metadata_json
            ]

            # Clean fields
            cleaned_fields = []
            for i, field in enumerate(fields):
                if field is None:
                    cleaned_fields.append('')
                else:
                    if i < len(fields) - 1:
                        field = str(field).replace('\t', ' ').replace('\n', ' ').replace('\r', '')
                    cleaned_fields.append(field)

            buffer.write('\t'.join(cleaned_fields) + '\n')

        buffer.seek(0)
        self.cursor.copy_from(buffer, 'verses',
            columns=('verse_id', 'work_id', 'section_id', 'verse_number',
                    'verse_type', 'verse_type_tamil', 'total_lines', 'sort_order', 'metadata'),
            null='')
        print(f"  [OK] Bulk inserted {len(self.verses)} verses")

    def bulk_insert_lines(self):
        """Bulk insert lines using PostgreSQL COPY"""
        if not self.lines:
            return

        buffer = io.StringIO()

        for line in self.lines:
            # Clean line_text to remove tabs and newlines
            line_text = str(line['line_text']).replace('\t', ' ').replace('\n', ' ').replace('\r', '')

            fields = [
                str(line['line_id']),
                str(line['verse_id']),
                str(line['line_number']),
                line_text
            ]

            buffer.write('\t'.join(fields) + '\n')

        buffer.seek(0)
        self.cursor.copy_from(buffer, 'lines',
            columns=('line_id', 'verse_id', 'line_number', 'line_text'), null='')
        print(f"  [OK] Bulk inserted {len(self.lines)} lines")

    def bulk_insert_words(self):
        """Bulk insert words using PostgreSQL COPY (manual TSV construction)"""
        if not self.words:
            return

        buffer = io.StringIO()

        for word in self.words:
            # Manual TSV construction (no csv.writer)
            word_text = str(word['word_text']).replace('\t', ' ').replace('\n', ' ').replace('\r', '')
            sandhi_split = str(word.get('sandhi_split', '')).replace('\t', ' ').replace('\n', ' ').replace('\r', '') if word.get('sandhi_split') else ''

            fields = [
                str(word['word_id']),
                str(word['line_id']),
                str(word['word_position']),
                word_text,
                sandhi_split
            ]

            buffer.write('\t'.join(fields) + '\n')

        buffer.seek(0)
        self.cursor.copy_from(buffer, 'words',
            columns=('word_id', 'line_id', 'word_position', 'word_text', 'sandhi_split'), null='')
        print(f"  [OK] Bulk inserted {len(self.words)} words")

    def import_data(self):
        """Execute bulk imports"""
        print("\n=== PHASE 2: Bulk inserting into database ===")
        try:
            self.bulk_insert_works()
            self.bulk_insert_sections()
            self.bulk_insert_verses()
            self.bulk_insert_lines()
            self.bulk_insert_words()
            self.conn.commit()
            print("\n[SUCCESS] Thembavani imported successfully!")
        except Exception as e:
            self.conn.rollback()
            print(f"\n[ERROR] Import failed: {e}")
            raise

    def close(self):
        """Close database connection"""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
        print("\nDatabase connection closed.")


def main():
    """Main entry point"""
    if len(sys.argv) > 1:
        db_url = sys.argv[1]
    else:
        db_url = os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@localhost/tamil_literature')

    file_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        'Tamil-Source-TamilConcordence',
        '6_பக்தி இலக்கியம்',
        '18.தேம்பாவணி.txt'
    )

    print("=" * 70)
    print("THEMBAVANI BULK IMPORT")
    print("=" * 70)
    print(f"Database: {db_url}")
    print(f"Source file: {file_path}")

    importer = ThembavaniBulkImporter(db_url)

    try:
        importer.connect()
        importer.parse_file(file_path)
        importer.import_data()
    finally:
        importer.close()


if __name__ == '__main__':
    main()
