#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Atomic import for ஐந்திணை ஐம்பது (Ainthinai Aimbathu)
Thinai structure: Verses organized by thinai (landscape) sections

Usage:
    # Standalone (links to default collection 201)
    python import_ainthinai_aimbathu.py [database_url]

    # Link to different collection
    python import_ainthinai_aimbathu.py [database_url] --collection-id 201 --position 7

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
from work_metadata import WORK_METADATA


class AinthinaiAimbathuImporter(BaseWorkImporter):
    """Atomic importer for Ainthinai Aimbathu"""

    # Default collection for this work
    DEFAULT_COLLECTION_ID = 201
    DEFAULT_COLLECTION_NAME = 'Eighteen Lesser Texts'
    DEFAULT_COLLECTION_NAME_TAMIL = 'பதினெண்கீழ்க்கணக்கு'

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
        metadata = WORK_METADATA['ainthinai_aimbathu'].copy()
        if position:
            metadata['position_in_collection'] = position

        # Create work entry (in memory, not committed)
        self.work_id = self._create_work(
            work_name=metadata['work_name'],
            work_name_tamil=metadata['work_name_tamil'],
            metadata=metadata
        )

        # Thinai structure state
        self.section_cache = {}  # Cache thinai sections
        self.current_thinai_id = None
        self.next_thinai_number = 1

    def _get_or_create_thinai_section(self, thinai_number, thinai_name_tamil):
        """Get or create thinai section"""
        cache_key = (thinai_number, thinai_name_tamil)

        if cache_key in self.section_cache:
            return self.section_cache[cache_key]

        section_id = self.section_id
        self.section_id += 1

        self.sections.append({
            'section_id': section_id,
            'work_id': self.work_id,
            'parent_section_id': None,
            'level_type': 'Thinai',
            'level_type_tamil': 'திணை',
            'section_number': thinai_number,
            'section_name': thinai_name_tamil,
            'section_name_tamil': thinai_name_tamil,
            'sort_order': thinai_number
        })

        self.section_cache[cache_key] = section_id
        return section_id

    def parse_file(self, text_file_path: str):
        """Phase 1: Parse text file into memory"""
        print("\nPhase 1: Parsing file...")

        with open(text_file_path, 'r', encoding='utf-8') as f:
            lines_text = f.readlines()

        current_paadal_lines = []
        current_paadal_num = None
        current_verse_title = None
        paadal_count = 0
        thinai_count = 0

        for line in lines_text:
            line = line.strip()
            if not line:
                continue

            # Check for thinai marker (*@ or @) - number is optional
            thinai_match = re.match(r'^\*?@(\d+)?\s+(.+)$', line)
            if thinai_match:
                # Save previous paadal if exists
                if current_paadal_num is not None and current_paadal_lines:
                    self._add_paadal(current_paadal_num, current_paadal_lines, current_verse_title)
                    paadal_count += 1
                    current_paadal_lines = []
                    current_paadal_num = None
                    current_verse_title = None

                thinai_count += 1
                # Use explicit number if present, otherwise use next sequential number
                if thinai_match.group(1):
                    thinai_num = int(thinai_match.group(1))
                    self.next_thinai_number = thinai_num + 1
                else:
                    thinai_num = self.next_thinai_number
                    self.next_thinai_number += 1

                thinai_name_tamil = thinai_match.group(2).strip()

                self.current_thinai_id = self._get_or_create_thinai_section(thinai_num, thinai_name_tamil)
                continue

            # Check for paadal marker (# or #N TITLE)
            paadal_match = re.match(r'^#(\d+)(?:\s+(.+))?$', line)
            if paadal_match:
                verse_num = int(paadal_match.group(1))
                verse_title = paadal_match.group(2).strip() if paadal_match.group(2) else None

                # Skip duplicate verse numbers
                if verse_num == current_paadal_num:
                    continue

                # Save previous paadal if exists
                if current_paadal_num is not None and current_paadal_lines:
                    self._add_paadal(current_paadal_num, current_paadal_lines, current_verse_title)
                    paadal_count += 1

                current_paadal_num = verse_num
                current_verse_title = verse_title
                current_paadal_lines = []
                continue

            # Otherwise it's a paadal line
            if current_paadal_num is not None:
                current_paadal_lines.append(line)

        # Save last paadal
        if current_paadal_num is not None and current_paadal_lines:
            self._add_paadal(current_paadal_num, current_paadal_lines, current_verse_title)
            paadal_count += 1

        print(f"[OK] Phase 1 complete: Parsed {paadal_count} paadals in {thinai_count} thinai sections")
        print(f"  - Sections: {len(self.sections)}")
        print(f"  - Paadals: {len(self.verses)}")
        print(f"  - Lines: {len(self.lines)}")
        print(f"  - Words: {len(self.words)}")

    def _add_paadal(self, paadal_num, paadal_lines, verse_title=None):
        """Add paadal to memory with optional title metadata"""
        if self.current_thinai_id is None:
            # No thinai section yet, skip this verse
            return

        verse_id = self.verse_id
        self.verse_id += 1

        # Build metadata if title exists
        verse_metadata = None
        if verse_title:
            verse_metadata = {
                "title": verse_title,
                "type": classify_verse_type(verse_title),
                "type_tamil": verse_title
            }

        self.verses.append({
            'verse_id': verse_id,
            'work_id': self.work_id,
            'section_id': self.current_thinai_id,
            'verse_number': paadal_num,
            'verse_type': 'paadal',
            'verse_type_tamil': 'பாடல்',
            'total_lines': len(paadal_lines),
            'sort_order': paadal_num,
            'metadata': json.dumps(verse_metadata, ensure_ascii=False) if verse_metadata else None
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

    parser = argparse.ArgumentParser(description='Import Ainthinai Aimbathu')
    parser.add_argument('database_url', nargs='?',
                       default=os.getenv('DATABASE_URL',
                                        "postgresql://postgres:postgres@localhost/tamil_literature"))
    parser.add_argument('--collection-id', type=int, help='Collection to link this work to')
    parser.add_argument('--position', type=int, help='Position within collection')
    args = parser.parse_args()

    print("="*70)
    print("Ainthinai Aimbathu Atomic Import")
    print("="*70)
    print(f"Database: {args.database_url[:50]}...")

    importer = AinthinaiAimbathuImporter(
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
            "7-ஐந்திணை ஐம்பது.txt"
        )

        if not text_file.exists():
            print(f"\n✗ Error: Text file not found: {text_file}")
            sys.exit(1)

        print(f"Text file: {text_file.name}")

        importer.parse_file(str(text_file))
        importer.bulk_insert()  # Single atomic transaction

        print("\n[OK] Import complete!")

    except ValueError as e:
        print(f"\n✗ Error: {e}")
        print("To re-import, first delete the existing work:")
        print(f'  python delete_ainthinai_aimbathu.py')
        importer.rollback()
        sys.exit(1)

    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        importer.rollback()
        sys.exit(1)

    finally:
        importer.close()


if __name__ == '__main__':
    main()
