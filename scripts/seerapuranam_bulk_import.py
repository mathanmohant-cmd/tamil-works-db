#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Seerapuranam Bulk Import Script
================================
Imports Seerapuranam (சீறாப்புராணம்) by Umaruppulavar

Work: Seerapuranam (சீறாப்புராணம்) - Islamic epic about Prophet Muhammad
Author: Umaruppulavar (உமறுப்புலவர்)
Tradition: Islamic devotional literature
Collection: பக்தி இலக்கியம் (Devotional Literature) - Collection 323

Structure:
- Level 1 (Kandam): 3 chapters marked with "* N காண்டம்"
  - விலாதத்துக் காண்டம் (Vilaadhaththu Kandam) - Birth
  - நுபுவ்வத்துக் காண்டம் (Nupuvvaththu Kandam) - Prophethood
  - இசிறத்துக் காண்டம் (Isiraththu Kandam) - Migration
- Level 2 (Padalam): Subsections marked with *N followed by padalam name
- Verses: Each # section is ONE complete verse
- $ markers contain verse metadata (stored in verse metadata)
- மேல் marks end of verse

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
from seerapuranam_metadata import (
    WORK_METADATA,
    COLLECTION_ID,
    VERSE_METADATA,
    FILE_INFO
)


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


class SeerapuranamBulkImporter(BaseWorkImporter):
    """
    Imports Seerapuranam using 2-phase bulk COPY pattern.

    Hierarchy:
    - Collection 323: பக்தி இலக்கியம்
      - Work: சீறாப்புராணம்
        - Level 1 Sections: Kandams (காண்டம்)
          - Level 2 Sections: Padalams (படலம்)
            - Verses: #N markers
              - Lines: Individual lines
                - Words: Word segmentation
    """

    def __init__(self, db_connection_string="postgresql://postgres:postgres@localhost/tamil_literature"):
        """Initialize with database connection using BaseWorkImporter"""
        super().__init__(db_connection_string, collection_id=COLLECTION_ID)

        # Current parsing state
        self.current_work_id = None

        print(f"Initialized SeerapuranamBulkImporter")
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
            print(f"  To re-import, first delete: python scripts/delete_seerapuranam.py")
            sys.exit(1)

    def parse_file(self, file_path: str):
        """Parse Seerapuranam file"""
        print("\n=== PHASE 1: Parsing Seerapuranam into memory ===")

        # Setup collection and create work
        self._setup_collection()
        self.current_work_id = self._create_work_from_metadata()

        # Parse file
        print(f"  Parsing file: {Path(file_path).name}")

        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        current_kandam_id = None
        current_padalam_id = None
        current_verse_number = None
        current_verse_id = None
        current_verse_lines = []

        for line in lines:
            line = line.rstrip('\n')

            # Skip empty lines
            if not line.strip():
                continue

            # Check for Kandam marker: "* N காண்டம்" or "* N name காண்டம்"
            kandam_match = re.match(r'^\*\s*(\d+)\s+(.+?காண்டம்.*?)$', line)
            if kandam_match:
                # Save previous verse
                if current_verse_lines and current_verse_number is not None:
                    self._create_verse(current_verse_number, current_verse_lines, current_padalam_id)
                    current_verse_lines = []
                    current_verse_number = None

                kandam_number = int(kandam_match.group(1))
                kandam_name = kandam_match.group(2).strip()

                # Create Kandam section
                kandam_section_id = self.section_id
                self.section_id += 1

                self.sections.append({
                    'section_id': kandam_section_id,
                    'work_id': self.current_work_id,
                    'parent_section_id': None,
                    'level_type': 'kandam',
                    'level_type_tamil': 'காண்டம்',
                    'section_number': kandam_number,
                    'section_name': kandam_name,
                    'section_name_tamil': kandam_name,
                    'sort_order': kandam_number
                })

                current_kandam_id = kandam_section_id
                print(f"  Found Kandam {kandam_number}: {kandam_name}")
                continue

            # Check for Padalam marker: "*N படலம்" or "*N. name படலம்"
            padalam_match = re.match(r'^\*(\d+)\.?\s*(.+?)$', line)
            if padalam_match and current_kandam_id is not None:
                # Save previous verse
                if current_verse_lines and current_verse_number is not None:
                    self._create_verse(current_verse_number, current_verse_lines, current_padalam_id)
                    current_verse_lines = []
                    current_verse_number = None

                padalam_number = int(padalam_match.group(1))
                padalam_name = padalam_match.group(2).strip()

                # Create Padalam section
                padalam_section_id = self.section_id
                self.section_id += 1

                self.sections.append({
                    'section_id': padalam_section_id,
                    'work_id': self.current_work_id,
                    'parent_section_id': current_kandam_id,
                    'level_type': 'padalam',
                    'level_type_tamil': 'படலம்',
                    'section_number': padalam_number,
                    'section_name': padalam_name,
                    'section_name_tamil': padalam_name,
                    'sort_order': padalam_number
                })

                current_padalam_id = padalam_section_id
                continue

            # Check for verse metadata: $1.0.1, $1.1.2, etc.
            if line.startswith('$'):
                current_verse_id = line[1:].strip()
                continue

            # Check for verse marker: #N
            verse_match = re.match(r'^#(\d+)$', line)
            if verse_match and current_padalam_id is not None:
                # Save previous verse
                if current_verse_lines and current_verse_number is not None:
                    self._create_verse(current_verse_number, current_verse_lines, current_padalam_id)
                    current_verse_lines = []

                current_verse_number = int(verse_match.group(1))
                continue

            # Check for verse end marker
            if line.strip() == 'மேல்':
                # Verse ends here
                continue

            # Regular content line - add to current verse's lines
            cleaned = clean_line(line)
            if cleaned and current_verse_number is not None:
                current_verse_lines.append(cleaned)

        # Save last verse
        if current_verse_lines and current_verse_number is not None:
            self._create_verse(current_verse_number, current_verse_lines, current_padalam_id)

        print(f"  [OK] Parsed {len(self.sections)} sections, {len(self.verses)} verses")
        print(f"       {len(self.lines)} lines, {len(self.words)} words")

    def _create_verse(self, verse_num: int, verse_lines: List[str], section_id: int):
        """Create a verse with lines and words"""
        if not verse_lines:
            return

        verse_dict = {
            'verse_id': self.verse_id,
            'work_id': self.current_work_id,
            'section_id': section_id,
            'verse_number': verse_num,
            'verse_type': VERSE_METADATA['verse_type'],
            'verse_type_tamil': VERSE_METADATA['verse_type_tamil'],
            'total_lines': len(verse_lines),
            'sort_order': verse_num,
            'metadata': {}
        }
        self.verses.append(verse_dict)
        current_verse_id = self.verse_id
        self.verse_id += 1

        # Process lines
        for line_num, line_text in enumerate(verse_lines, 1):
            line_id = self.line_id
            self.line_id += 1

            self.lines.append({
                'line_id': line_id,
                'verse_id': current_verse_id,
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
    print("SEERAPURANAM BULK IMPORT")
    print("=" * 70)
    print(f"Database: {db_url}")
    print(f"Source file: {file_path}")

    if not Path(file_path).exists():
        print(f"\n✗ Error: Source file not found: {file_path}")
        sys.exit(1)

    importer = SeerapuranamBulkImporter(db_url)

    try:
        importer.parse_file(file_path)
        importer.bulk_insert()
        print("\n[SUCCESS] Seerapuranam imported successfully!")
    except Exception as e:
        print(f"\n[ERROR] Import failed: {e}")
        import traceback
        traceback.print_exc()
        raise
    finally:
        importer.close()


if __name__ == '__main__':
    main()
