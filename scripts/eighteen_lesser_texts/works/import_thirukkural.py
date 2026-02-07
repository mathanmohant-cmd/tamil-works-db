#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Atomic import for திருக்குறள் (Thirukkural)
3-level hierarchical structure: Paal → Iyal → Adhikaram → Kurals

Usage:
    # Standalone (links to default collection 201)
    python import_thirukkural.py [database_url]

    # Link to different collection
    python import_thirukkural.py [database_url] --collection-id 201 --position 11

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


class ThirukkuralImporter(BaseWorkImporter):
    """Atomic importer for Thirukkural"""

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
        metadata = WORK_METADATA['thirukkural'].copy()
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
        """Phase 1: Parse text file into memory

        Note: Thirukkural file uses:
        - # N name for adhikaram headers
        - N.text for kural text (first line of kural)
        - No Paal/Iyal markers (must use structure file for hierarchy)
        """
        print("\\nPhase 1: Parsing file...")

        # Load structure file for Paal/Iyal/Adhikaram hierarchy
        structure_file = Path(text_file_path).parent.parent.parent / "data" / "thirukkural_structure.json"
        if not structure_file.exists():
            raise FileNotFoundError(f"Structure file not found: {structure_file}")

        with open(structure_file, 'r', encoding='utf-8') as f:
            structure = json.load(f)

        # Build kural to hierarchy mapping
        kural_to_hierarchy = {}
        for paal in structure['structure']['paals']:
            for iyal in paal['iyals']:
                for adhikaram in iyal['adhikarams']:
                    start_kural, end_kural = adhikaram['kurals']
                    for kural_num in range(start_kural, end_kural + 1):
                        kural_to_hierarchy[kural_num] = {
                            'paal': paal,
                            'iyal': iyal,
                            'adhikaram': adhikaram
                        }

        with open(text_file_path, 'r', encoding='utf-8') as f:
            lines_text = f.readlines()

        current_kural_lines = []
        current_kural_num = None
        current_adhikaram_section_id = None
        kural_count = 0

        for line in lines_text:
            line = line.strip()
            if not line:
                continue

            # Check for adhikaram header (# N name)
            adhikaram_match = re.match(r'^#\s*(\d+)\s+(.+)$', line)
            if adhikaram_match:
                # Save previous kural if exists
                if current_kural_num is not None and current_kural_lines:
                    self._add_kural(current_kural_num, current_kural_lines, current_adhikaram_section_id)
                    kural_count += 1

                current_kural_lines = []
                current_kural_num = None

                adhikaram_num = int(adhikaram_match.group(1))
                first_kural = (adhikaram_num - 1) * 10 + 1

                if first_kural in kural_to_hierarchy:
                    hierarchy = kural_to_hierarchy[first_kural]

                    # Create Paal if needed
                    paal_id = self._get_or_create_section_id(
                        None, 'Paal', 'பால்',
                        hierarchy['paal']['paal_id'],
                        hierarchy['paal']['paal_name'],
                        hierarchy['paal']['paal_name_tamil']
                    )

                    # Create Iyal if needed
                    iyal_id = self._get_or_create_section_id(
                        paal_id, 'Iyal', 'இயல்',
                        hierarchy['iyal']['iyal_id'],
                        hierarchy['iyal']['iyal_name'],
                        hierarchy['iyal']['iyal_name_tamil']
                    )

                    # Create Adhikaram
                    current_adhikaram_section_id = self._get_or_create_section_id(
                        iyal_id, 'Adhikaram', 'அதிகாரம்',
                        adhikaram_num,
                        hierarchy['adhikaram']['name'],
                        hierarchy['adhikaram']['tamil']
                    )
                continue

            # Check for kural line (N.text)
            kural_line_match = re.match(r'^(\d+)\.(.+)$', line)
            if kural_line_match:
                # Save previous kural if exists
                if current_kural_num is not None and current_kural_lines:
                    self._add_kural(current_kural_num, current_kural_lines, current_adhikaram_section_id)
                    kural_count += 1
                    if kural_count % 100 == 0:
                        print(f"  Parsed {kural_count} kurals...")

                current_kural_num = int(kural_line_match.group(1))
                current_kural_lines = [kural_line_match.group(2).strip()]
            else:
                # Continuation line of current kural
                if current_kural_num is not None:
                    current_kural_lines.append(line)

        # Save last kural
        if current_kural_num is not None and current_kural_lines:
            self._add_kural(current_kural_num, current_kural_lines, current_adhikaram_section_id)
            kural_count += 1

        print(f"[OK] Phase 1 complete: Parsed {kural_count} kurals")
        print(f"  - Sections: {len(self.sections)}")
        print(f"  - Kurals: {len(self.verses)}")
        print(f"  - Lines: {len(self.lines)}")
        print(f"  - Words: {len(self.words)}")

    def _add_kural(self, kural_num, kural_lines, adhikaram_section_id):
        """Add kural to memory"""
        if adhikaram_section_id is None:
            # No adhikaram section yet, skip this kural
            return

        verse_id = self.verse_id
        self.verse_id += 1

        self.verses.append({
            'verse_id': verse_id,
            'work_id': self.work_id,
            'section_id': adhikaram_section_id,
            'verse_number': kural_num,
            'verse_type': 'kural',
            'verse_type_tamil': 'குறள்',
            'total_lines': len(kural_lines),
            'sort_order': kural_num,
            'metadata': None
        })

        for line_num, line_text in enumerate(kural_lines, start=1):
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

    parser = argparse.ArgumentParser(description='Import Thirukkural')
    parser.add_argument('database_url', nargs='?',
                       default=os.getenv('DATABASE_URL',
                                        "postgresql://postgres:postgres@localhost/tamil_literature"))
    parser.add_argument('--collection-id', type=int, help='Collection to link this work to')
    parser.add_argument('--position', type=int, help='Position within collection')
    args = parser.parse_args()

    print("="*70)
    print("Thirukkural Atomic Import")
    print("="*70)
    print(f"Database: {args.database_url[:50]}...")

    importer = ThirukkuralImporter(
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
            "11-திருக்குறள்.txt"
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
        print(f'  python delete_thirukkural.py')
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
