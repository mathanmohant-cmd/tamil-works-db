#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Atomic import for முதுமொழிக்காஞ்சி (Muthumozhikkanchi)
Paththu structure: Verses organized in groups of ten (paththu)

Usage:
    # Standalone (links to default collection 201)
    python import_muthumozhikkanchi.py [database_url]

    # Link to different collection
    python import_muthumozhikkanchi.py [database_url] --collection-id 201 --position 16

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


class MuthumozhikkanchiImporter(BaseWorkImporter):
    """Atomic importer for Muthumozhikkanchi"""

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
        metadata = WORK_METADATA['muthumozhikkanchi'].copy()
        if position:
            metadata['position_in_collection'] = position

        # Create work entry (in memory, not committed)
        self.work_id = self._create_work(
            work_name=metadata['work_name'],
            work_name_tamil=metadata['work_name_tamil'],
            metadata=metadata
        )

        # Paththu structure state
        self.section_cache = {}  # Cache paththu sections
        self.current_paththu_id = None
        self.next_paththu_number = 1

    def _get_or_create_paththu_section(self, paththu_number, paththu_name_tamil):
        """Get or create paththu section"""
        cache_key = (paththu_number, paththu_name_tamil)

        if cache_key in self.section_cache:
            return self.section_cache[cache_key]

        section_id = self.section_id
        self.section_id += 1

        self.sections.append({
            'section_id': section_id,
            'work_id': self.work_id,
            'parent_section_id': None,
            'level_type': 'Paththu',
            'level_type_tamil': 'பத்து',
            'section_number': paththu_number,
            'section_name': paththu_name_tamil,
            'section_name_tamil': paththu_name_tamil,
            'sort_order': paththu_number
        })

        self.section_cache[cache_key] = section_id
        return section_id

    def parse_file(self, text_file_path: str):
        """Phase 1: Parse text file into memory"""
        print("\\nPhase 1: Parsing file...")

        with open(text_file_path, 'r', encoding='utf-8') as f:
            lines_text = f.readlines()

        current_paadal_lines = []
        current_paadal_num = None
        paadal_count = 0
        paththu_count = 0

        for line in lines_text:
            line = line.strip()
            if not line:
                continue

            # Check for paththu marker (*@ or @) - number is optional
            paththu_match = re.match(r'^\*?@(\d+)?\s+(.+)$', line)
            if paththu_match:
                # Save previous paadal if exists
                if current_paadal_num is not None and current_paadal_lines:
                    self._add_paadal(current_paadal_num, current_paadal_lines)
                    paadal_count += 1
                    current_paadal_lines = []
                    current_paadal_num = None

                paththu_count += 1
                # Use explicit number if present, otherwise use next sequential number
                if paththu_match.group(1):
                    paththu_num = int(paththu_match.group(1))
                    self.next_paththu_number = paththu_num + 1
                else:
                    paththu_num = self.next_paththu_number
                    self.next_paththu_number += 1

                paththu_name_tamil = paththu_match.group(2).strip()

                self.current_paththu_id = self._get_or_create_paththu_section(paththu_num, paththu_name_tamil)
                continue

            # Check for paadal marker (#N)
            paadal_match = re.match(r'^#(\d+)', line)
            if paadal_match:
                # Save previous paadal if exists
                if current_paadal_num is not None and current_paadal_lines:
                    self._add_paadal(current_paadal_num, current_paadal_lines)
                    paadal_count += 1
                    if paadal_count % 10 == 0:
                        print(f"  Parsed {paadal_count} paadals...")

                current_paadal_num = int(paadal_match.group(1))
                current_paadal_lines = []
                continue

            # Otherwise it's a paadal line
            if current_paadal_num is not None:
                current_paadal_lines.append(line)

        # Save last paadal
        if current_paadal_num is not None and current_paadal_lines:
            self._add_paadal(current_paadal_num, current_paadal_lines)
            paadal_count += 1

        print(f"[OK] Phase 1 complete: Parsed {paadal_count} paadals in {paththu_count} paththu sections")
        print(f"  - Sections: {len(self.sections)}")
        print(f"  - Paadals: {len(self.verses)}")
        print(f"  - Lines: {len(self.lines)}")
        print(f"  - Words: {len(self.words)}")

    def _add_paadal(self, paadal_num, paadal_lines):
        """Add paadal to memory"""
        if self.current_paththu_id is None:
            # No paththu section yet, skip this verse
            return

        verse_id = self.verse_id
        self.verse_id += 1

        self.verses.append({
            'verse_id': verse_id,
            'work_id': self.work_id,
            'section_id': self.current_paththu_id,
            'verse_number': paadal_num,
            'verse_type': 'paadal',
            'verse_type_tamil': 'பாடல்',
            'total_lines': len(paadal_lines),
            'sort_order': paadal_num,
            'metadata': None
        })

        for line_num, line_text in enumerate(paadal_lines, start=1):
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

    parser = argparse.ArgumentParser(description='Import Muthumozhikkanchi')
    parser.add_argument('database_url', nargs='?',
                       default=os.getenv('DATABASE_URL',
                                        "postgresql://postgres:postgres@localhost/tamil_literature"))
    parser.add_argument('--collection-id', type=int, help='Collection to link this work to')
    parser.add_argument('--position', type=int, help='Position within collection')
    args = parser.parse_args()

    print("="*70)
    print("Muthumozhikkanchi Atomic Import")
    print("="*70)
    print(f"Database: {args.database_url[:50]}...")

    importer = MuthumozhikkanchiImporter(
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
            "16-முதுமொழிக்காஞ்சி.txt"
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
        print(f'  python delete_muthumozhikkanchi.py')
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
