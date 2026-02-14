#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Thiruvarutpa Balakrishnapillai Edition Bulk Import Script
=========================================================
Imports Thiruvarutpa (திருவருட்பா) - Balakrishnapillai Edition (File 20)
Author: Ramalinga Swamigal (இராமலிங்க சுவாமிகள்) - Vallalar
Period: 19th century CE
Tradition: Universal spirituality / Shaivite

Structure:
    & = Thirumurai number (top-level section)
    @ = Sub-section name
    # = verse_number

Uses 2-phase bulk COPY pattern with BaseWorkImporter for optimal performance.
"""

import os
import sys
import re
from pathlib import Path
from typing import List

# Import shared utilities
sys.path.insert(0, str(Path(__file__).parent))
from shared.base_importer import BaseWorkImporter
from shared.utils import split_and_clean_words

# Import metadata
sys.path.insert(0, str(Path(__file__).parent / 'metadata'))
from thiruvarutpa_balakrishnapillai_metadata import (
    WORK_METADATA,
    COLLECTION_ID,
    FILE_INFO,
    VERSE_METADATA
)


class ThiruvarutpaBalaImporter(BaseWorkImporter):
    """
    Imports Thiruvarutpa Balakrishnapillai Edition using 2-phase bulk COPY pattern.

    Hierarchy:
    - Collection 323: பக்தி இலக்கியம்
      - Work: திருவருட்பா - பாலகிருஷ்ணபிள்ளை பதிப்பு
        - Thirumurai: & markers (திருமுறை)
          - Sections: @ markers (பகுதி)
            - Verses: # markers
              - Lines: Individual lines
                - Words: Word segmentation
    """

    def __init__(self, db_connection_string="postgresql://postgres:postgres@localhost/tamil_literature"):
        """Initialize with database connection using BaseWorkImporter"""
        super().__init__(db_connection_string, collection_id=COLLECTION_ID)

        # Current parsing state
        self.current_work_id = None
        self.current_thirumurai_section_id = None
        self.current_subsection_id = None
        self.section_sort_order = 0
        self.verse_sort_order = 0

        print(f"Initialized ThiruvarutpaBalaImporter")
        print(f"  Collection {COLLECTION_ID} will be linked")

    def _setup_collection(self):
        """Ensure collection 323 exists"""
        super()._ensure_collection_exists(
            collection_id=COLLECTION_ID,
            collection_name='Devotional Literature',
            collection_name_tamil='பக்தி இலக்கியம்',
            description='Standalone devotional works from various traditions (includes Thiruvarutpa editions, Thiruppugazh, Thembavani, Seerapuranam)'
        )

    def _create_work_from_metadata(self) -> int:
        """Create work entry from WORK_METADATA using parent class method"""
        try:
            work_id = super()._create_work(
                work_name=WORK_METADATA['work_name'],
                work_name_tamil=WORK_METADATA['work_name_tamil'],
                metadata=WORK_METADATA
            )
            print(f"  Created work: {WORK_METADATA['work_name_tamil']} (ID: {work_id})")
            return work_id
        except ValueError as e:
            print(f"  [ERROR] {e}")
            print(f"  To re-import, first delete: python scripts/delete_thiruvarutpa_balakrishnapillai.py")
            sys.exit(1)

    def parse_file(self, file_path: str):
        """Parse Thiruvarutpa Balakrishnapillai Edition file"""
        print("\n=== PHASE 1: Parsing Thiruvarutpa Balakrishnapillai into memory ===")

        # Setup collection and create work
        self._setup_collection()
        self.current_work_id = self._create_work_from_metadata()

        # Parse file
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        # State tracking
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

            # Thirumurai marker: &number name (allow optional space after number)
            thirumurai_match = re.match(r'^&(\d+)\.?\s*(.+)', line)
            if thirumurai_match:
                # Save previous verse if any
                if current_verse_lines and self.current_subsection_id:
                    self._create_verse(current_verse_lines, verse_number)
                    current_verse_lines = []

                thirumurai_num = int(thirumurai_match.group(1))
                thirumurai_name = thirumurai_match.group(2).strip()

                # Create Thirumurai section
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
                    'sort_order': self.section_sort_order
                }
                self.sections.append(section_dict)
                self.current_thirumurai_section_id = self.section_id
                self.section_id += 1
                self.current_subsection_id = None
                in_verse = False
                continue

            # Subsection marker: @number name or @number. name
            subsection_match = re.match(r'^@(\d+)\.?\s*(.+)', line)
            if subsection_match:
                # Save previous verse if any
                if current_verse_lines and self.current_subsection_id:
                    self._create_verse(current_verse_lines, verse_number)
                    current_verse_lines = []

                subsection_num = int(subsection_match.group(1))
                subsection_name = subsection_match.group(2).strip()

                # Create subsection
                self.section_sort_order += 1
                section_dict = {
                    'section_id': self.section_id,
                    'work_id': self.current_work_id,
                    'parent_section_id': self.current_thirumurai_section_id,
                    'level_type': 'Section',
                    'level_type_tamil': 'பகுதி',
                    'section_number': self.section_sort_order,
                    'section_name': subsection_name,
                    'section_name_tamil': subsection_name,
                    'sort_order': self.section_sort_order
                }
                self.sections.append(section_dict)
                self.current_subsection_id = self.section_id
                self.section_id += 1
                in_verse = False
                continue

            # Verse marker: #number or #number.
            verse_match = re.match(r'^#(-?\d+)\.?', line)
            if verse_match:
                # Save previous verse if any
                if current_verse_lines:
                    self._create_verse(current_verse_lines, verse_number)
                    current_verse_lines = []

                verse_number = int(verse_match.group(1))

                # Special case: Create காப்பு subsection for #-1 or #0 (invocatory verses)
                if verse_number <= 0:
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
                        'sort_order': self.section_sort_order
                    }
                    self.sections.append(kappu_section)
                    self.current_subsection_id = self.section_id
                    self.section_id += 1

                in_verse = True
                continue

            # Verse content lines
            if in_verse and self.current_subsection_id:
                # Skip lines that look like section/verse markers
                if re.match(r'^[@#&]\d+', line):
                    continue

                # Clean embedded marker references
                cleaned_line = re.sub(r'[#@&]\d+', '', line).strip()

                # Only add non-empty lines
                if cleaned_line:
                    current_verse_lines.append(cleaned_line)

        # Handle last verse
        if current_verse_lines:
            self._create_verse(current_verse_lines, verse_number)

        print(f"\n  [OK] Parsed 1 work, {len(self.sections)} sections, {len(self.verses)} verses")
        print(f"       {len(self.lines)} lines, {len(self.words)} words")

    def _create_verse(self, verse_lines: List[str], verse_number: int):
        """Create a verse with its lines and words"""
        if not verse_lines:
            return

        self.verse_sort_order += 1

        # Use metadata from metadata file
        verse_metadata = VERSE_METADATA['default_metadata'].copy()
        verse_metadata['line_count'] = len(verse_lines)

        verse_dict = {
            'verse_id': self.verse_id,
            'work_id': self.current_work_id,
            'section_id': self.current_subsection_id,
            'verse_number': self.verse_sort_order,
            'verse_type': VERSE_METADATA['verse_type'],
            'verse_type_tamil': VERSE_METADATA['verse_type_tamil'],
            'total_lines': len(verse_lines),
            'sort_order': self.verse_sort_order
        }
        self.verses.append(verse_dict)
        current_verse_id = self.verse_id
        self.verse_id += 1

        # Create lines and words
        for line_num, line_text in enumerate(verse_lines, 1):
            self._create_line_and_words(line_text, line_num, current_verse_id)

    def _create_line_and_words(self, line_text: str, line_number: int, verse_id: int):
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

        # Segment into words using shared utility
        words = split_and_clean_words(line_text)
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


def main():
    # Get database connection string
    db_connection = os.getenv('DATABASE_URL', "postgresql://postgres:postgres@localhost/tamil_literature")
    if len(sys.argv) > 1:
        db_connection = sys.argv[1]

    print("="*70)
    print("  THIRUVARUTPA - BALAKRISHNAPILLAI EDITION (File 20)")
    print("="*70)
    print(f"Database: {db_connection[:50]}...")

    # File path
    script_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(script_dir, '..', 'Tamil-Source-TamilConcordence',
                             FILE_INFO['source_directory'],
                             FILE_INFO['source_file'])

    try:
        importer = ThiruvarutpaBalaImporter(db_connection)
        importer.parse_file(file_path)
        importer.bulk_insert()
        importer.close()

        print("\n" + "="*70)
        print("  IMPORT COMPLETED SUCCESSFULLY")
        print("="*70)
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
