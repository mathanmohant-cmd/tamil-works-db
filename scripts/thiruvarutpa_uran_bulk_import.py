#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Thiruvarutpa Uran Adigal Edition Bulk Import Script
===================================================
Imports Thiruvarutpa (திருவருட்பா) - Uran Adigal Edition (File 21)
Author: Ramalinga Swamigal (இராமலிங்க சுவாமிகள்) - Vallalar
Period: 19th century CE
Tradition: Universal spirituality / Shaivite

Structure:
    & = Thirumurai number (top-level section)
    @ = Sub-section name
    # = verse_number

Uses 2-phase bulk COPY pattern for optimal performance.
"""

import os
import sys
import re
import io
import json
import psycopg2
from typing import List, Dict, Optional

class ThiruvarutpaImporter:
    def __init__(self, db_connection_string: str):
        """Initialize the Thiruvarutpa bulk importer"""
        self.db_connection_string = db_connection_string
        self.conn = None
        self.cursor = None

        # Data containers
        self.works = []
        self.sections = []
        self.verses = []
        self.lines = []
        self.words = []
        self.work_collections = []

        # ID counters - CRITICAL: Query MAX IDs from database
        self.work_id = 1
        self.section_id = 1
        self.verse_id = 1
        self.line_id = 1
        self.word_id = 1

        # Current state tracking
        self.current_work_id = None
        self.current_thirumurai_section_id = None
        self.current_subsection_id = None
        self.section_sort_order = 0
        self.verse_sort_order = 0

        # Collection IDs
        
        # File mappings for both editions
        self.file_mappings = [
            {
                'file': '20.திருவருட்பா - பாலகிருஷ்ணபிள்ளை பதிப்பு.txt',
                'work_name': 'Thiruvarutpa - Balakrishnapillai Edition',
                'work_name_tamil': 'திருவருட்பா - பாலகிருஷ்ணபிள்ளை பதிப்பு',
                'canonical_order': 503,
                'edition': 'Balakrishnapillai'
            },
            {
                'file': '21.திருவருட்பா-ஊரன் அடிகள் பதிப்பு.txt',
                'work_name': 'Thiruvarutpa - Uran Adigal Edition',
                'work_name_tamil': 'திருவருட்பா - ஊரன் அடிகள் பதிப்பு',
                'canonical_order': 504,
                'edition': 'Uran Adigal'
            }
        ]

    def connect(self):
        """Connect to the database and get MAX IDs"""
        print("Connecting to database...")
        self.conn = psycopg2.connect(self.db_connection_string)
        self.cursor = self.conn.cursor()

        # Ensure collections exist
        self.ensure_collection_exists()

        # CRITICAL: Get MAX IDs from database
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

        # Get next available position in collection 323
        self.cursor.execute("SELECT COALESCE(MAX(position_in_collection), 0) + 1 FROM work_collections WHERE collection_id = 323")
        self.position_in_collection = self.cursor.fetchone()[0]

        print(f"  Starting IDs: work={self.work_id}, section={self.section_id}, verse={self.verse_id}, line={self.line_id}, word={self.word_id}")
        print(f"  Next position in collection 323: {self.position_in_collection}")

    def ensure_collection_exists(self):
        """Ensure the Thiruvarutpa & Other Non-Thirumurai Devotional Works collection exists"""
        collection_id = 323
        self.cursor.execute("SELECT collection_id FROM collections WHERE collection_id = %s", (collection_id,))
        result = self.cursor.fetchone()

        if not result:
            print(f"  Creating collection {collection_id} (Thiruvarutpa & Other Non-Thirumurai Devotional Works)...")
            self.cursor.execute("""
                INSERT INTO collections (collection_id, collection_name, collection_name_tamil,
                                       collection_type, description, sort_order)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                collection_id,
                'Thiruvarutpa & Other Non-Thirumurai Devotional Works',
                'திருவருட்பா & பிற பக்தி இலக்கியம்',
                'devotional',
                'Collection of Thiruvarutpa editions and other non-Thirumurai devotional works',
                323
            ))
            self.conn.commit()
            print(f"  [OK] Collection {collection_id} created")
        else:
            print(f"  [OK] Collection {collection_id} already exists")

    def link_work_to_collection(self, work_id: int, position_in_collection: int):
        """Link a work to its collection"""
        work_collection = {
            'work_id': work_id,
            'collection_id': 323,
            'position_in_collection': position_in_collection,
            'is_primary': True,
            'notes': None
        }
        self.work_collections.append(work_collection)

    def parse_file(self, file_path: str, edition_name: str, canonical_order: int):
        """Parse a single Thiruvarutpa edition file"""
        print(f"\n=== PHASE 1: Parsing {edition_name} into memory ===")

        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        # Create work
        work_metadata = {
            'author': 'Ramalinga Swamigal',
            'author_tamil': 'இராமலிங்க சுவாமிகள்',
            'alternative_names': ['Vallalar', 'Saint Ramalinga'],
            'tradition': 'Universal spirituality / Shaivite',
            'period': '19th century CE',
            'edition': edition_name,
            'themes': ['Divine Grace', 'Universal Love', 'Compassion', 'Social Reform'],
            'significance': 'Teachings of Vallalar on divine compassion and universal brotherhood'
        }

        work_dict = {
            'work_id': self.work_id,
            'work_name': f'Thiruvarutpa - {edition_name}',
            'work_name_tamil': f'திருவருட்பா - {edition_name}',
            'period': '19th century CE',
            'author': 'Ramalinga Swamigal',
            'author_tamil': 'இராமலிங்க சுவாமிகள்',
            'description': f"Thiruvarutpa ({edition_name}) by Ramalinga Swamigal (Vallalar)",
            'chronology_start_year': 1823,  # Vallalar's birth year
            'chronology_end_year': 1874,    # Vallalar's disappearance year
            'chronology_confidence': 'high',
            'chronology_notes': 'Composed by Saint Ramalinga Swamigal (Vallalar) in the 19th century',
            'canonical_order': canonical_order,
            'metadata': work_metadata
        }
        self.works.append(work_dict)
        self.current_work_id = self.work_id

        # Link work to collection
        self.link_work_to_collection(self.work_id, self.position_in_collection)
        self.position_in_collection += 1

        self.work_id += 1

        # Reset state for this work
        self.section_sort_order = 0
        self.verse_sort_order = 0

        # Parse content
        current_thirumurai = None
        current_subsection = None
        current_verse_lines = []
        verse_number = 0
        in_verse = False

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Skip header lines
            if line.startswith('வள்ளலார் ^') or line.startswith('*'):
                continue

            # Thirumurai marker: &number name
            thirumurai_match = re.match(r'^&(\d+)\s+(.+)', line)
            if thirumurai_match:
                # Save previous verse if any
                if current_verse_lines and current_subsection:
                    self.create_verse(current_verse_lines, verse_number)
                    current_verse_lines = []

                thirumurai_num = int(thirumurai_match.group(1))
                thirumurai_name = thirumurai_match.group(2).strip()

                self.section_sort_order += 1
                section_dict = {
                    'section_id': self.section_id,
                    'work_id': self.current_work_id,
                    'parent_section_id': None,
                    'level_type': 'Thirumurai',
                    'level_type_tamil': 'திருமுறை',
                    'section_number': thirumurai_num,
                    'section_name': thirumurai_name,
                    'section_name_tamil': thirumurai_name,
                    'sort_order': self.section_sort_order,
                    'metadata': {'thirumurai_number': thirumurai_num}
                }
                self.sections.append(section_dict)
                self.current_thirumurai_section_id = self.section_id
                self.section_id += 1
                current_thirumurai = thirumurai_num
                current_subsection = None
                in_verse = False
                continue

            # Subsection marker: @number name or @number. name
            subsection_match = re.match(r'^@(\d+)\.?\s+(.+)', line)
            if subsection_match:
                # Save previous verse if any
                if current_verse_lines and current_subsection:
                    self.create_verse(current_verse_lines, verse_number)
                    current_verse_lines = []

                subsection_num = int(subsection_match.group(1))
                subsection_name = subsection_match.group(2).strip()

                self.section_sort_order += 1
                section_dict = {
                    'section_id': self.section_id,
                    'work_id': self.current_work_id,
                    'parent_section_id': self.current_thirumurai_section_id,
                    'level_type': 'Section',
                    'level_type_tamil': 'பகுதி',
                    'section_number': self.section_sort_order,  # Use globally unique sort_order
                    'section_name': subsection_name,
                    'section_name_tamil': subsection_name,
                    'sort_order': self.section_sort_order,
                    'metadata': {'original_subsection_number': subsection_num}  # Keep original for reference
                }
                self.sections.append(section_dict)
                self.current_subsection_id = self.section_id
                self.section_id += 1
                current_subsection = subsection_num
                in_verse = False
                continue

            # Verse marker: #number or #number.
            verse_match = re.match(r'^#(-?\d+)\.?', line)
            if verse_match:
                # Save previous verse if any
                if current_verse_lines:
                    self.create_verse(current_verse_lines, verse_number)
                    current_verse_lines = []

                verse_number = int(verse_match.group(1))

                # Special case: Create காப்பு subsection for #-1 or #0 (invocatory verses)
                if verse_number <= 0 and current_subsection != 'kappu':
                    self.section_sort_order += 1
                    kappu_section = {
                        'section_id': self.section_id,
                        'work_id': self.current_work_id,
                        'parent_section_id': self.current_thirumurai_section_id,
                        'level_type': 'Section',
                        'level_type_tamil': 'பகுதி',
                        'section_number': self.section_sort_order,
                        'section_name': 'காப்பு (Invocatory Verses)',
                        'section_name_tamil': 'காப்பு',
                        'sort_order': self.section_sort_order,
                        'metadata': {'type': 'kappu', 'description': 'Invocatory/preliminary verses'}
                    }
                    self.sections.append(kappu_section)
                    self.current_subsection_id = self.section_id
                    self.section_id += 1
                    current_subsection = 'kappu'

                in_verse = True
                continue

            # Verse content lines
            if in_verse and current_subsection:
                current_verse_lines.append(line)

        # Handle last verse
        if current_verse_lines:
            self.create_verse(current_verse_lines, verse_number)

        print(f"\n  [OK] Parsed {len(self.works)} work, {len(self.sections)} sections, {len(self.verses)} verses")
        print(f"       {len(self.lines)} lines, {len(self.words)} words")

    def create_verse(self, verse_lines: List[str], verse_number: int):
        """Create a verse with its lines and words"""
        if not verse_lines:
            return

        self.verse_sort_order += 1

        verse_metadata = {
            'author': 'Ramalinga Swamigal',
            'tradition': 'Universal spirituality',
            'deity': 'Arut Perum Jothi',
            'meter': 'Various',
            'line_count': len(verse_lines),
            'themes': ['Divine Grace', 'Compassion']
        }

        verse_dict = {
            'verse_id': self.verse_id,
            'work_id': self.current_work_id,
            'section_id': self.current_subsection_id,
            'verse_number': self.verse_sort_order,  # Use globally unique sort_order
            'verse_type': 'Poem',
            'verse_type_tamil': 'பாடல்',
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
        # Create line
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
        """
        Segment a line into words following Tamil grammar rules.
        Uses basic space-based segmentation with underscore handling.
        """
        # Replace underscores with spaces (compound word markers)
        line_text = line_text.replace('_', ' ')

        # Split by whitespace
        words = line_text.split()

        # Remove empty strings
        words = [w for w in words if w.strip()]

        return words

    def bulk_insert(self):
        """PHASE 2: Bulk insert using PostgreSQL COPY"""
        print("\n=== PHASE 2: Bulk inserting into database ===")

        try:
            # Insert works
            print(f"  Inserting {len(self.works)} works...")
            works_tsv = io.StringIO()
            for work in self.works:
                metadata_json = json.dumps(work['metadata'], ensure_ascii=False)
                works_tsv.write(f"{work['work_id']}\t{work['work_name']}\t{work['work_name_tamil']}\t"
                              f"{work['period']}\t{work['author']}\t{work['author_tamil']}\t"
                              f"{work['description']}\t{work['chronology_start_year']}\t{work['chronology_end_year']}\t"
                              f"{work['chronology_confidence']}\t{work['chronology_notes']}\t"
                              f"{work['canonical_order']}\t{metadata_json}\n")
            works_tsv.seek(0)
            self.cursor.copy_from(works_tsv, 'works',
                                columns=('work_id', 'work_name', 'work_name_tamil', 'period',
                                       'author', 'author_tamil', 'description',
                                       'chronology_start_year', 'chronology_end_year',
                                       'chronology_confidence', 'chronology_notes',
                                       'canonical_order', 'metadata'))
            print(f"  [OK] Inserted {len(self.works)} works")

            # Link works to collection
            if self.work_collections:
                print(f"  Linking {len(self.work_collections)} works to collections...")
                work_coll_tsv = io.StringIO()
                for work_coll in self.work_collections:
                    work_coll_tsv.write(f"{work_coll['work_id']}\t{work_coll['collection_id']}\t"
                                       f"{work_coll['position_in_collection']}\t"
                                       f"{'t' if work_coll['is_primary'] else 'f'}\t\\N\n")
                work_coll_tsv.seek(0)
                self.cursor.copy_from(work_coll_tsv, 'work_collections',
                                    columns=('work_id', 'collection_id', 'position_in_collection',
                                           'is_primary', 'notes'), null='')
                print(f"  [OK] Linked {len(self.work_collections)} works to collections")

            # Insert sections
            print(f"  Inserting {len(self.sections)} sections...")
            sections_tsv = io.StringIO()
            for section in self.sections:
                parent_id = section['parent_section_id'] if section['parent_section_id'] else '\\N'
                section_name = section['section_name'] if section['section_name'] else '\\N'
                section_name_tamil = section['section_name_tamil'] if section['section_name_tamil'] else '\\N'
                metadata_json = json.dumps(section['metadata'], ensure_ascii=False)
                sections_tsv.write(f"{section['section_id']}\t{section['work_id']}\t{parent_id}\t"
                                 f"{section['level_type']}\t{section['level_type_tamil']}\t"
                                 f"{section['section_number']}\t{section_name}\t{section_name_tamil}\t"
                                 f"{section['sort_order']}\t{metadata_json}\n")
            sections_tsv.seek(0)
            self.cursor.copy_from(sections_tsv, 'sections',
                                columns=('section_id', 'work_id', 'parent_section_id',
                                       'level_type', 'level_type_tamil', 'section_number',
                                       'section_name', 'section_name_tamil', 'sort_order', 'metadata'))
            print(f"  [OK] Inserted {len(self.sections)} sections")

            # Insert verses
            print(f"  Inserting {len(self.verses)} verses...")
            verses_tsv = io.StringIO()
            for verse in self.verses:
                metadata_json = json.dumps(verse['metadata'], ensure_ascii=False)
                verses_tsv.write(f"{verse['verse_id']}\t{verse['work_id']}\t{verse['section_id']}\t"
                               f"{verse['verse_number']}\t{verse['verse_type']}\t{verse['verse_type_tamil']}\t"
                               f"{verse['total_lines']}\t{verse['sort_order']}\t"
                               f"{metadata_json}\n")
            verses_tsv.seek(0)
            self.cursor.copy_from(verses_tsv, 'verses',
                                columns=('verse_id', 'work_id', 'section_id', 'verse_number',
                                       'verse_type', 'verse_type_tamil', 'total_lines',
                                       'sort_order', 'metadata'))
            print(f"  [OK] Inserted {len(self.verses)} verses")

            # Insert lines
            print(f"  Inserting {len(self.lines)} lines...")
            lines_tsv = io.StringIO()
            for line in self.lines:
                # Clean line_text - escape tabs and newlines
                line_text = str(line['line_text']).replace('\t', ' ').replace('\n', ' ').replace('\r', '')
                lines_tsv.write(f"{line['line_id']}\t{line['verse_id']}\t{line['line_number']}\t{line_text}\n")
            lines_tsv.seek(0)
            self.cursor.copy_from(lines_tsv, 'lines',
                                columns=('line_id', 'verse_id', 'line_number', 'line_text'), null='')
            print(f"  [OK] Inserted {len(self.lines)} lines")

            # Insert words
            print(f"  Inserting {len(self.words)} words...")
            words_tsv = io.StringIO()
            for word in self.words:
                # Clean word_text and sandhi_split
                word_text = str(word['word_text']).replace('\t', ' ').replace('\n', ' ').replace('\r', '')
                sandhi = str(word.get('sandhi_split', '') or '').replace('\t', ' ').replace('\n', ' ').replace('\r', '')
                words_tsv.write(f"{word['word_id']}\t{word['line_id']}\t{word['word_position']}\t{word_text}\t{sandhi}\n")
            words_tsv.seek(0)
            self.cursor.copy_from(words_tsv, 'words',
                                columns=('word_id', 'line_id', 'word_position', 'word_text', 'sandhi_split'), null='')
            print(f"  [OK] Inserted {len(self.words)} words")

            # Commit transaction
            self.conn.commit()
            print("\n  [OK] All data committed successfully")

        except Exception as e:
            print(f"\n  [ERROR] Bulk insert failed: {e}")
            self.conn.rollback()
            raise

    def close(self):
        """Close database connection"""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()

def main():
    # Get database connection string
    db_connection = os.getenv('DATABASE_URL', "postgresql://postgres:postgres@localhost/tamil_literature")
    if len(sys.argv) > 1:
        db_connection = sys.argv[1]

    print("="*70)
    print("  THIRUVARUTPA - URAN ADIGAL EDITION (File 21)")
    print("="*70)
    print(f"Database: {db_connection[:50]}...")

    # File path
    script_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(script_dir, '..', 'Tamil-Source-TamilConcordence', '6_பக்தி இலக்கியம்',
                             '21.திருவருட்பா-ஊரன் அடிகள் பதிப்பு.txt')

    try:
        importer = ThiruvarutpaImporter(db_connection)
        importer.connect()
        importer.parse_file(file_path, 'Uran Adigal Edition', 504)
        importer.bulk_insert()
        importer.close()

        print("\n" + "="*70)
        print("  IMPORT COMPLETED SUCCESSFULLY")
        print("="*70)
        print(f"  Imported {len(importer.works)} work")
        print(f"  Total sections: {len(importer.sections)}")
        print(f"  Total verses: {len(importer.verses)}")
        print(f"  Total lines: {len(importer.lines)}")
        print(f"  Total words: {len(importer.words)}")
        print("="*70)

    except Exception as e:
        print(f"\n[ERROR] Import failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
