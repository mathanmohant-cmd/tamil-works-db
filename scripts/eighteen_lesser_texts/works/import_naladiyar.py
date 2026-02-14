#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Atomic import for நாலடியார் (Naladiyar)
3-level hierarchical structure: Paal → Iyal → Adhikaram → Verses

Usage:
    # Standalone (links to default collection 201)
    python import_naladiyar.py [database_url]

    # Link to different collection
    python import_naladiyar.py [database_url] --collection-id 201 --position 1

    # Via master orchestrator (recommended)
    cd ../master && python import_all.py
"""

import sys
import json
import re
from pathlib import Path

# Add paths for global shared utilities and local metadata
sys.path.insert(0, str(Path(__file__).parent.parent.parent))  # scripts/ for global shared
sys.path.insert(0, str(Path(__file__).parent.parent / 'shared'))  # local shared/ for work_metadata
from shared.base_importer import BaseWorkImporter
from shared.utils import clean_line_text, classify_verse_type, split_and_clean_words
# Import from centralized metadata
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'metadata'))
from eighteen_lesser_texts_metadata import WORK_METADATA, COLLECTION_ID, COLLECTION_NAME, COLLECTION_NAME_TAMIL


class NaladiyarImporter(BaseWorkImporter):
    """Atomic importer for Naladiyar"""

    # Default collection for this work
    DEFAULT_COLLECTION_ID = COLLECTION_ID
    DEFAULT_COLLECTION_NAME = COLLECTION_NAME
    DEFAULT_COLLECTION_NAME_TAMIL = COLLECTION_NAME_TAMIL

    def __init__(self, db_connection_string, collection_id=None, position=None):
        # Use default collection if not specified
        collection_id = collection_id or self.DEFAULT_COLLECTION_ID
        super().__init__(db_connection_string, collection_id)

        # Ensure collection exists (idempotent, not committed yet)
        self._ensure_collection_exists(
            collection_id=self.DEFAULT_COLLECTION_ID,
            collection_name=self.DEFAULT_COLLECTION_NAME,
            collection_name_tamil=self.DEFAULT_COLLECTION_NAME_TAMIL,
            description='Classical Tamil didactic literature collection (பதினெண்கீழ்க்கணக்கு)'
        )

        # Get metadata from shared dictionary
        metadata = WORK_METADATA['naladiyar'].copy()
        if position:
            metadata['position_in_collection'] = position

        # Create work entry (in memory, not committed)
        self.work_id = self._create_work(
            work_name=metadata['work_name'],
            work_name_tamil=metadata['work_name_tamil'],
            metadata=metadata
        )

        # Hierarchical structure state (3 levels)
        self.section_cache = {}  # Cache sections to avoid duplicates
        self.current_paal_id = None
        self.current_iyal_id = None
        self.current_adhikaram_id = None

        # Counters for sequential numbering
        self.paal_counter = 0
        self.iyal_counter = 0
        self.adhikaram_counter = 0

    def _get_or_create_section_id(self, parent_id, level_type, level_type_tamil,
                                   section_number, section_name, section_name_tamil):
        """Get or create section, return section_id"""
        cache_key = (parent_id, level_type, section_number)

        if cache_key in self.section_cache:
            return self.section_cache[cache_key]

        section_id = self.section_id
        self.section_id += 1

        self.sections.append({
            'section_id': section_id,
            'work_id': self.work_id,
            'parent_section_id': parent_id,
            'level_type': level_type,
            'level_type_tamil': level_type_tamil,
            'section_number': section_number,
            'section_name': section_name,
            'section_name_tamil': section_name_tamil,
            'sort_order': section_number
        })

        self.section_cache[cache_key] = section_id
        return section_id

    def parse_file(self, text_file_path: str):
        """Phase 1: Parse text file into memory"""
        print("\\nPhase 1: Parsing file...")

        with open(text_file_path, 'r', encoding='utf-8') as f:
            lines_text = f.readlines()

        current_verse_lines = []
        current_verse_num = None
        verse_count = 0

        for line in lines_text:
            line = line.strip()
            if not line:
                continue

            # Check for Paal marker (&)
            if line.startswith('&'):
                # Save previous verse if exists
                if current_verse_num is not None and current_verse_lines:
                    self._add_verse(current_verse_num, current_verse_lines)
                    verse_count += 1
                    current_verse_lines = []
                    current_verse_num = None

                self.paal_counter += 1
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
                    self.paal_counter,
                    paal_name,
                    paal_name_tamil
                )
                continue

            # Check for Iyal marker (number followed by Tamil text ending with "இயல்")
            iyal_match = re.match(r'^(\d+)\s+([\u0B80-\u0BFF\s]+இயல்)\s*$', line)
            if iyal_match:
                # Save previous verse if exists
                if current_verse_num is not None and current_verse_lines:
                    self._add_verse(current_verse_num, current_verse_lines)
                    verse_count += 1
                    current_verse_lines = []
                    current_verse_num = None

                self.iyal_counter += 1
                iyal_num = int(iyal_match.group(1))
                iyal_name_tamil = iyal_match.group(2).strip()

                # Extract base name without "இயல்"
                iyal_base_name = iyal_name_tamil.replace('இயல்', '').strip()

                self.current_iyal_id = self._get_or_create_section_id(
                    self.current_paal_id, 'Iyal', 'இயல்',
                    iyal_num,
                    iyal_base_name,
                    iyal_name_tamil
                )
                continue

            # Check for Adhikaram marker (@N name)
            adhikaram_match = re.match(r'^@(\d+)\s+(.+)$', line)
            if adhikaram_match:
                # Save previous verse if exists
                if current_verse_num is not None and current_verse_lines:
                    self._add_verse(current_verse_num, current_verse_lines)
                    verse_count += 1
                    current_verse_lines = []
                    current_verse_num = None

                self.adhikaram_counter += 1
                adhikaram_num = int(adhikaram_match.group(1))
                adhikaram_name_tamil = adhikaram_match.group(2).strip()

                self.current_adhikaram_id = self._get_or_create_section_id(
                    self.current_iyal_id, 'Adhikaram', 'அதிகாரம்',
                    adhikaram_num,
                    adhikaram_name_tamil,  # Use Tamil name as English for now
                    adhikaram_name_tamil
                )
                continue

            # Check for verse marker (#N)
            verse_match = re.match(r'^#(\d+)$', line)
            if verse_match:
                # Save previous verse if exists
                if current_verse_num is not None and current_verse_lines:
                    self._add_verse(current_verse_num, current_verse_lines)
                    verse_count += 1
                    if verse_count % 50 == 0:
                        print(f"  Parsed {verse_count} verses...")

                current_verse_num = int(verse_match.group(1))
                current_verse_lines = []
                continue

            # Skip section header lines
            if line.startswith('அதிகாரம்-'):
                continue

            # Skip "மேல்" separator
            if line == 'மேல்':
                continue

            # Otherwise it's a verse line
            if current_verse_num is not None:
                current_verse_lines.append(line)

        # Save last verse
        if current_verse_num is not None and current_verse_lines:
            self._add_verse(current_verse_num, current_verse_lines)
            verse_count += 1

        print(f"[OK] Phase 1 complete: Parsed {verse_count} verses")
        print(f"  - Paals: {self.paal_counter}")
        print(f"  - Iyals: {self.iyal_counter}")
        print(f"  - Adhikarams: {self.adhikaram_counter}")
        print(f"  - Sections: {len(self.sections)}")
        print(f"  - Verses: {len(self.verses)}")
        print(f"  - Lines: {len(self.lines)}")
        print(f"  - Words: {len(self.words)}")

    def _add_verse(self, verse_num, verse_lines):
        """Add verse to memory"""
        if self.current_adhikaram_id is None:
            # No adhikaram section yet, skip this verse
            return

        verse_id = self.verse_id
        self.verse_id += 1

        self.verses.append({
            'verse_id': verse_id,
            'work_id': self.work_id,
            'section_id': self.current_adhikaram_id,
            'verse_number': verse_num,
            'verse_type': 'naladiyar',
            'verse_type_tamil': 'நாலடியார்',
            'total_lines': len(verse_lines),
            'sort_order': verse_num,
            'metadata': None
        })

        for line_num, line_text in enumerate(verse_lines, start=1):
            # Clean line
            cleaned_line = clean_line_text(line_text)

            line_id = self.line_id
            self.line_id += 1

            self.lines.append({
                'line_id': line_id,
                'verse_id': verse_id,
                'line_number': line_num,
                'line_text': cleaned_line
            })

            # Parse and clean words
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


def main():
    import os
    import argparse

    parser = argparse.ArgumentParser(description='Import Naladiyar')
    parser.add_argument('database_url', nargs='?',
                       default=os.getenv('DATABASE_URL',
                                        "postgresql://postgres:postgres@localhost/tamil_literature"))
    parser.add_argument('--collection-id', type=int, help='Collection to link this work to')
    parser.add_argument('--position', type=int, help='Position within collection')
    args = parser.parse_args()

    print("="*70)
    print("Naladiyar Atomic Import")
    print("="*70)
    print(f"Database: {args.database_url[:50]}...")

    importer = NaladiyarImporter(
        args.database_url,
        collection_id=args.collection_id,
        position=args.position
    )

    try:
        # Get text file path
        text_file = (
            Path(__file__).parent.parent.parent.parent /
            "Tamil-Source-TamilConcordence" /
            "3_சங்க_இலக்கியம்_பதினெண்கீழ்க்கணக்கு" /
            "1-நாலடியார்.txt"
        )

        if not text_file.exists():
            print(f"\\n✗ Error: Text file not found: {text_file}")
            sys.exit(1)

        print(f"Text file: {text_file.name}")

        importer.parse_file(str(text_file))
        importer.bulk_insert()  # Single atomic transaction

        print("\\n[OK] Import complete!")

    except ValueError as e:
        print(f"\\n✗ Error: {e}")
        print("To re-import, first delete the existing work:")
        print(f'  python delete_naladiyar.py')
        importer.rollback()
        sys.exit(1)

    except Exception as e:
        print(f"\\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        importer.rollback()
        sys.exit(1)

    finally:
        importer.close()


if __name__ == '__main__':
    main()
