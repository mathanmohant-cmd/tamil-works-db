#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Thembavani Bulk Import Script
===============================
Imports Thembavani (தேம்பாவணி) by Veeramaamunivar (Constanzo Giuseppe Beschi)

Work: Thembavani (தேம்பாவணி) - Christian epic poem
Author: Veeramaamunivar (வீரமாமுனிவர்) - also known as Constanzo Giuseppe Beschi
Tradition: Christian devotional literature
Collection: பக்தி இலக்கியம் (Devotional Literature) - Collection 323

Structure:
    வீரமாமுனிவர் (Constanzo Giuseppe Beschi) ^ தேம்பாவணி
    @number section_name
    #verse_number
    verse lines...
    மேல்

Each @section contains multiple #verses.
Each #verse is ONE complete verse with multiple lines.

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
from thembavani_metadata import (
    WORK_METADATA,
    COLLECTION_ID,
    VERSE_METADATA,
    FILE_INFO
)


class ThembavaniBulkImporter(BaseWorkImporter):
    """
    Imports Thembavani using 2-phase bulk COPY pattern.

    Hierarchy:
    - Collection 323: பக்தி இலக்கியம்
      - Work: தேம்பாவணி
        - Sections: @N markers (படலம் - cantos)
          - Verses: #N markers
            - Lines: Individual lines
              - Words: Word segmentation
    """

    def __init__(self, db_connection_string="postgresql://postgres:postgres@localhost/tamil_literature"):
        """Initialize with database connection using BaseWorkImporter"""
        super().__init__(db_connection_string, collection_id=COLLECTION_ID)

        # Current parsing state
        self.current_work_id = None
        self.section_sort_order = 0
        self.verse_sort_order = 0

        print(f"Initialized ThembavaniBulkImporter")
        print(f"  Collection {COLLECTION_ID} will be linked")

    def _setup_collection(self):
        """Ensure collection 323 exists"""
        super()._ensure_collection_exists(
            collection_id=COLLECTION_ID,
            collection_name='Devotional Literature',
            collection_name_tamil='பக்தி இலக்கியம்',
            description='Standalone devotional works from various traditions'
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
            print(f"  To re-import, first delete: python scripts/delete_thembavani.py")
            sys.exit(1)

    def parse_file(self, file_path: str):
        """Parse Thembavani file"""
        print("\n=== PHASE 1: Parsing Thembavani into memory ===")

        # Setup collection and create work
        self._setup_collection()
        self.current_work_id = self._create_work_from_metadata()

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
                    self._create_verse(
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
                section_dict = {
                    'section_id': self.section_id,
                    'work_id': self.current_work_id,
                    'parent_section_id': None,
                    'level_type': 'Padalam',
                    'level_type_tamil': 'படலம்',
                    'section_number': current_section_number,
                    'section_name': current_section_name,
                    'section_name_tamil': current_section_name,
                    'sort_order': self.section_sort_order
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
                    self._create_verse(
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
                    self._create_verse(
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
            self._create_verse(
                current_verse_number,
                current_verse_lines,
                current_section_id
            )

        print(f"  [OK] Parsed {len(self.sections)} sections, {len(self.verses)} verses")
        print(f"       {len(self.lines)} lines, {len(self.words)} words")

    def _create_verse(self, verse_num: int, verse_lines: List[str], section_id: int):
        """Create a verse with lines and words"""
        self.verse_sort_order += 1

        verse_metadata = VERSE_METADATA['default_metadata'].copy()
        verse_metadata['line_count'] = len(verse_lines)

        verse_dict = {
            'verse_id': self.verse_id,
            'work_id': self.current_work_id,
            'section_id': section_id,
            'verse_number': verse_num,
            'verse_type': VERSE_METADATA['verse_type'],
            'verse_type_tamil': VERSE_METADATA['verse_type_tamil'],
            'total_lines': len(verse_lines),
            'sort_order': self.verse_sort_order,
            'metadata': verse_metadata
        }
        self.verses.append(verse_dict)
        current_verse_id = self.verse_id
        self.verse_id += 1

        # Create lines and words
        for line_num, line_text in enumerate(verse_lines, 1):
            self._create_line_and_words(line_text, line_num, current_verse_id)

    def _create_line_and_words(self, line_text: str, line_number: int, verse_id: int):
        """Create a line and segment it into words"""
        # Clean embedded marker references (e.g., "#ஃ31" -> "ஃ31" or remove entirely)
        cleaned_line = re.sub(r'[#@&]\d+', '', line_text).strip()
        # Also remove standalone # followed by non-digit characters like #ஃ
        cleaned_line = re.sub(r'#', '', cleaned_line).strip()

        line_dict = {
            'line_id': self.line_id,
            'verse_id': verse_id,
            'line_number': line_number,
            'line_text': cleaned_line
        }
        self.lines.append(line_dict)
        current_line_id = self.line_id
        self.line_id += 1

        # Segment into words (use cleaned line)
        words = split_and_clean_words(cleaned_line)
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
    """Main entry point"""
    if len(sys.argv) > 1:
        db_url = sys.argv[1]
    else:
        db_url = os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@localhost/tamil_literature')

    file_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        'Tamil-Source-TamilConcordence',
        FILE_INFO['source_directory'],
        FILE_INFO['source_file']
    )

    print("=" * 70)
    print("THEMBAVANI BULK IMPORT")
    print("=" * 70)
    print(f"Database: {db_url}")
    print(f"Source file: {file_path}")

    importer = ThembavaniBulkImporter(db_url)

    try:
        importer.parse_file(file_path)
        importer.bulk_insert()
        print("\n[SUCCESS] Thembavani imported successfully!")
    except Exception as e:
        print(f"\n[ERROR] Import failed: {e}")
        raise
    finally:
        importer.close()


if __name__ == '__main__':
    main()
