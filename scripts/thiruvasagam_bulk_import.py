#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Thiruvasagam Bulk Import Script
=================================
Imports Thiruvasagam (Thirumurai File 8.1) by Manikkavasagar

Collection: Thirumurai (திருமுறை) - Collection ID 321
Work: Thiruvasagam (திருவாசகம்) by Manikkavasagar (மாணிக்கவாசகர்)

Structure:
    மாணிக்கவாசகர் ^ திருவாசகம்
    @number pathigam_name
    continuous lines (line numbers at multiples of 5 on right)
    மேல்

Each pathigam is treated as ONE verse with multiple lines.

Uses 2-phase bulk COPY pattern for optimal performance.
"""

import os
import sys
import re
import json
import io
import csv
import psycopg2
from typing import List, Dict

class ThiruvasagamBulkImporter:
    def __init__(self, db_connection_string: str):
        """Initialize the Thiruvasagam bulk importer"""
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

        # Ensure Thirumurai collection exists
        self.ensure_collection_exists()

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

    def _get_or_create_section_id(self, work_id):
        """
        Get or create a default root section for a work (for works without explicit hierarchy)
        Follows Sangam parser pattern to ensure all verses have a section_id
        """
        section_id = self.section_id
        self.section_id += 1

        self.sections.append({
            'section_id': section_id,
            'work_id': work_id,
            'parent_section_id': None,
            'level_type': 'Chapter',
            'level_type_tamil': 'பகுதி',
            'section_number': 1,
            'section_name': None,  # NULL name to avoid redundant display
            'section_name_tamil': None,
            'sort_order': 1,
            'metadata': {}
        })

        return section_id

    def ensure_collection_exists(self):
        """Ensure the 8th Thirumurai collection exists"""
        # Check if main Thirumurai collection exists (321)
        self.cursor.execute("SELECT collection_id FROM collections WHERE collection_id = 321")
        if not self.cursor.fetchone():
            print("  Creating main Thirumurai collection (321)...")
            self.cursor.execute("""
                INSERT INTO collections (collection_id, collection_name, collection_name_tamil,
                                       collection_type, description, sort_order)
                VALUES (321, 'Thirumurai', 'திருமுறை', 'devotional',
                        'Thirumurai - 12 books of Shaivite devotional literature', 321)
            """)
            self.conn.commit()

        # Check if 8th Thirumurai collection exists (3218)
        self.cursor.execute("SELECT collection_id FROM collections WHERE collection_id = 3218")
        result = self.cursor.fetchone()

        if not result:
            print("  Creating 8th Thirumurai collection (3218)...")
            self.cursor.execute("""
                INSERT INTO collections (collection_id, collection_name, collection_name_tamil,
                                       collection_type, parent_collection_id, description, sort_order)
                VALUES (3218, 'Eighth Thirumurai', 'எட்டாம் திருமுறை', 'devotional', 321,
                        '8th Thirumurai - Thiruvasagam and Thirukovayar by Manikkavasagar', 3218)
            """)
            self.conn.commit()
            print("  [OK] 8th Thirumurai collection created")
        else:
            print("  [OK] 8th Thirumurai collection already exists")

        # Query and return the collection_id
        self.cursor.execute("SELECT collection_id FROM collections WHERE collection_id = 3218")
        self.eighth_thirumurai_collection_id = self.cursor.fetchone()[0]
        return self.eighth_thirumurai_collection_id

    def parse_file(self, file_path: str):
        """Parse Thiruvasagam file"""
        print("\n=== PHASE 1: Parsing Thiruvasagam into memory ===")

        # Create work
        work_metadata = {
            'tradition': 'Shaivite',
            'collection_id': self.eighth_thirumurai_collection_id,
            'collection_name': 'Eighth Thirumurai',
            'collection_name_tamil': 'எட்டாம் திருமுறை',
            'thirumurai_number': 8,
            'file_part': '8.1',
            'saint': 'மாணிக்கவாசகர்',
            'saint_transliteration': 'Manikkavasagar',
            'time_period': '9th century CE',
            'place': 'திருவாதவூர்',
            'deity_focus': 'Shiva (as Nataraja)',
            'musical_tradition': True,
            'liturgical_use': True,
            'philosophical_depth': 'high',
            'emotional_intensity': 'high',
            'themes': ['divine love', 'longing', 'mystical union', 'surrender']
        }

        work_dict = {
            'work_id': self.work_id,
            'work_name': "Thiruvasagam",
            'work_name_tamil': "திருவாசகம்",
            'period': '9th century CE',
            'author': "Manikkavasagar",
            'author_tamil': "மாணிக்கவாசகர்",
            'description': "திருவாசகம் - Shaivite devotional masterpiece",
            'canonical_order': 328,
            'primary_collection_id': self.eighth_thirumurai_collection_id,
            'metadata': work_metadata
        }
        self.works.append(work_dict)
        self.current_work_id = self.work_id
        print(f"  Created work: திருவாசகம் (ID: {self.work_id})")
        self.work_id += 1

        # Parse file
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        # Create a default section for this work (fallback if no pathigams found)
        # This ensures verse_hierarchy and word_details views work correctly
        default_section = self._get_or_create_section_id(self.current_work_id)

        current_pathigam_number = None
        current_pathigam_name = None
        current_pathigam_lines = []
        current_section_id = default_section  # Start with default, update when pathigam found

        for line in lines:
            line_stripped = line.strip()

            # Skip author header
            if '^' in line_stripped:
                continue

            # Pathigam marker: @number pathigam_name
            pathigam_match = re.match(r'^@(\d+)\s+(.+)', line_stripped)
            if pathigam_match:
                # Save previous pathigam
                if current_pathigam_lines:
                    self.create_pathigam_verse(
                        current_pathigam_number,
                        current_pathigam_name,
                        current_pathigam_lines,
                        current_section_id
                    )
                    current_pathigam_lines = []

                current_pathigam_number = int(pathigam_match.group(1))
                current_pathigam_name = pathigam_match.group(2).strip()

                # Create section (pathigam)
                self.section_sort_order += 1
                section_metadata = {
                    'section_type': 'pathigam',
                    'section_type_tamil': 'பதிகம்'
                }

                section_dict = {
                    'section_id': self.section_id,
                    'work_id': self.current_work_id,
                    'parent_section_id': None,
                    'level_type': 'Pathigam',
                    'level_type_tamil': 'பதிகம்',
                    'section_number': current_pathigam_number,
                    'section_name': current_pathigam_name,
                    'section_name_tamil': current_pathigam_name,
                    'sort_order': self.section_sort_order,
                    'metadata': section_metadata
                }
                self.sections.append(section_dict)
                current_section_id = self.section_id
                self.section_id += 1
                continue

            # End of pathigam
            if line_stripped == 'மேல்':
                if current_pathigam_lines:
                    self.create_pathigam_verse(
                        current_pathigam_number,
                        current_pathigam_name,
                        current_pathigam_lines,
                        current_section_id
                    )
                    current_pathigam_lines = []
                continue

            # Collect pathigam lines (remove line numbers on right)
            if line_stripped and current_pathigam_number is not None:
                # Remove trailing line numbers (appear as \t followed by digits)
                clean_line = re.sub(r'\t+\d+\s*$', '', line_stripped)
                if clean_line:
                    current_pathigam_lines.append(clean_line)

        # Handle last pathigam
        if current_pathigam_lines:
            self.create_pathigam_verse(
                current_pathigam_number,
                current_pathigam_name,
                current_pathigam_lines,
                current_section_id
            )

        print(f"  [OK] Parsed {len(self.sections)} pathigams, {len(self.verses)} verses")
        print(f"       {len(self.lines)} lines, {len(self.words)} words")

    def create_pathigam_verse(self, pathigam_num: int, pathigam_name: str,
                             verse_lines: List[str], section_id: int):
        """Create a verse for the pathigam"""
        self.verse_sort_order += 1

        verse_metadata = {
            'saint': 'மாணிக்கவாசகர்',
            'deity': 'Shiva',
            'pathigam_name': pathigam_name,
            'line_count': len(verse_lines),
            'liturgical_use': True,
            'theological_tradition': 'Shaiva Siddhanta',
            'emotional_tone': 'devotional longing'
        }

        verse_dict = {
            'verse_id': self.verse_id,
            'work_id': self.current_work_id,
            'section_id': section_id,
            'verse_number': pathigam_num,
            'verse_type': 'Devotional Hymn',
            'verse_type_tamil': 'பக்தி பாடல்',
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

    def bulk_insert_work_collections(self):
        """Link work to Thiruvasagam collection"""
        if not self.works:
            return

        print(f"  Linking work to Thiruvasagam collection...")

        # Get next available position in this collection
        self.cursor.execute("""
            SELECT COALESCE(MAX(position_in_collection), 0) + 1
            FROM work_collections
            WHERE collection_id = %s
        """, (self.eighth_thirumurai_collection_id,))
        next_position = self.cursor.fetchone()[0]

        buffer = io.StringIO()
        for work in self.works:
            # Link work to 8th Thirumurai collection (dynamic)
            fields = [
                str(work['work_id']),
                str(self.eighth_thirumurai_collection_id),  # collection_id (dynamic)
                str(next_position),     # position_in_collection (dynamic)
                't',     # is_primary (true)
                ''       # notes (NULL)
            ]
            buffer.write('\t'.join(fields) + '\n')
            next_position += 1  # Increment for each work in loop

        buffer.seek(0)
        self.cursor.copy_from(
            buffer, 'work_collections',
            columns=['work_id', 'collection_id', 'position_in_collection', 'is_primary', 'notes'],
            null=''
        )
        print(f"    ✓ Linked work to collection")

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
        """Bulk insert words using PostgreSQL COPY"""
        if not self.words:
            return

        buffer = io.StringIO()
        writer = csv.writer(buffer, delimiter='\t', quoting=csv.QUOTE_MINIMAL, escapechar='\\')

        for word in self.words:
            writer.writerow([
                word['word_id'], word['line_id'], word['word_position'],
                word['word_text'], word.get('sandhi_split', '')
            ])

        buffer.seek(0)
        self.cursor.copy_from(buffer, 'words',
            columns=('word_id', 'line_id', 'word_position', 'word_text', 'sandhi_split'), null='')
        print(f"  [OK] Bulk inserted {len(self.words)} words")

    def import_data(self):
        """Execute bulk imports"""
        print("\n=== PHASE 2: Bulk inserting into database ===")
        try:
            self.bulk_insert_works()
            self.bulk_insert_work_collections()
            self.bulk_insert_sections()
            self.bulk_insert_verses()
            self.bulk_insert_lines()
            self.bulk_insert_words()
            self.conn.commit()
            print("\n[SUCCESS] Thiruvasagam imported successfully!")
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
        '8.1எட்டாம் திருமுறை.txt'
    )

    print("=" * 70)
    print("THIRUVASAGAM BULK IMPORT (Thirumurai File 8.1)")
    print("=" * 70)
    print(f"Database: {db_url}")
    print(f"Source file: {file_path}")

    importer = ThiruvasagamBulkImporter(db_url)

    try:
        importer.connect()
        importer.parse_file(file_path)
        importer.import_data()
    finally:
        importer.close()


if __name__ == '__main__':
    main()
