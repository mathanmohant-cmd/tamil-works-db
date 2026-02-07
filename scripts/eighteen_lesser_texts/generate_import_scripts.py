#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generator script to create all 18 individual import scripts for Eighteen Lesser Texts.

Generates scripts from templates based on structure type:
- Flat structure (10 works)
- Thinai structure (5 works)
- Paththu structure (1 work)
- Adhikaram structure (1 work)
- Thirukkural structure (1 work)
"""

import sys
from pathlib import Path

# Add shared directory to path
sys.path.insert(0, str(Path(__file__).parent / 'shared'))
from work_metadata import WORK_METADATA


# Template for flat structure imports
FLAT_TEMPLATE = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Atomic import for {work_name_tamil} ({work_name})
Flat structure: Single section, all verses directly under it

Usage:
    # Standalone (links to default collection 201)
    python import_{work_key}.py [database_url]

    # Link to different collection
    python import_{work_key}.py [database_url] --collection-id 201 --position {position}

    # Via master orchestrator (recommended)
    cd ../master && python import_all.py
"""

import sys
import json
from pathlib import Path

# Add shared utilities to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'shared'))
from base_importer import BaseWorkImporter
from work_metadata import WORK_METADATA
from utils import clean_line_text, classify_verse_type, split_and_clean_words


class {class_name}Importer(BaseWorkImporter):
    """Atomic importer for {work_name}"""

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
        metadata = WORK_METADATA['{work_key}'].copy()
        if position:
            metadata['position_in_collection'] = position

        # Create work entry (in memory, not committed)
        self.work_id = self._create_work(
            work_name=metadata['work_name'],
            work_name_tamil=metadata['work_name_tamil'],
            metadata=metadata
        )

        # Create default section to hold all verses
        self.default_section_id = self.section_id
        self.section_id += 1

    def parse_file(self, text_file_path: str):
        """Phase 1: Parse text file into memory"""
        print("\\nPhase 1: Parsing file...")

        # Create default section
        self.sections.append({{
            'section_id': self.default_section_id,
            'work_id': self.work_id,
            'parent_section_id': None,
            'level_type': 'Collection',
            'level_type_tamil': 'தொகுப்பு',
            'section_number': 1,
            'section_name': None,  # NULL for flat works
            'section_name_tamil': None,
            'sort_order': 1
        }})

        # Parse verses
        with open(text_file_path, 'r', encoding='utf-8') as f:
            lines_text = f.readlines()

        current_paadal_lines = []
        current_paadal_num = None
        current_verse_title = None
        paadal_count = 0

        for line in lines_text:
            line = line.strip()
            if not line:
                continue

            # Check for paadal marker (# or #N TITLE)
            import re
            paadal_match = re.match(r'^#(\\d+)(?:\\s+(.+))?$', line)
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

        print(f"[OK] Phase 1 complete: Parsed {{paadal_count}} paadals")
        print(f"  - Sections: {{len(self.sections)}}")
        print(f"  - Paadals: {{len(self.verses)}}")
        print(f"  - Lines: {{len(self.lines)}}")
        print(f"  - Words: {{len(self.words)}}")

    def _add_paadal(self, paadal_num, paadal_lines, verse_title=None):
        """Add paadal to memory with optional title metadata"""
        verse_id = self.verse_id
        self.verse_id += 1

        # Build metadata if title exists
        verse_metadata = None
        if verse_title:
            verse_metadata = {{
                "title": verse_title,
                "type": classify_verse_type(verse_title),
                "type_tamil": verse_title
            }}

        self.verses.append({{
            'verse_id': verse_id,
            'work_id': self.work_id,
            'section_id': self.default_section_id,
            'verse_number': paadal_num,
            'verse_type': 'paadal',
            'verse_type_tamil': 'பாடல்',
            'total_lines': len(paadal_lines),
            'sort_order': paadal_num,
            'metadata': json.dumps(verse_metadata, ensure_ascii=False) if verse_metadata else None
        }})

        for line_num, line_text in enumerate(paadal_lines, start=1):
            # Clean line
            cleaned_line = clean_line_text(line_text)

            line_id = self.line_id
            self.line_id += 1

            self.lines.append({{
                'line_id': line_id,
                'verse_id': verse_id,
                'line_number': line_num,
                'line_text': cleaned_line
            }})

            # Parse and clean words
            cleaned_words = split_and_clean_words(cleaned_line)
            for word_position, word_text in enumerate(cleaned_words, start=1):
                word_id = self.word_id
                self.word_id += 1

                self.words.append({{
                    'word_id': word_id,
                    'line_id': line_id,
                    'word_position': word_position,
                    'word_text': word_text,
                    'sandhi_split': None
                }})


def main():
    import os
    import argparse

    parser = argparse.ArgumentParser(description='Import {work_name}')
    parser.add_argument('database_url', nargs='?',
                       default=os.getenv('DATABASE_URL',
                                        "postgresql://postgres:postgres@localhost/tamil_literature"))
    parser.add_argument('--collection-id', type=int, help='Collection to link this work to')
    parser.add_argument('--position', type=int, help='Position within collection')
    args = parser.parse_args()

    print("="*70)
    print("{work_name} Atomic Import")
    print("="*70)
    print(f"Database: {{args.database_url[:50]}}...")

    importer = {class_name}Importer(
        args.database_url,
        collection_id=args.collection_id,
        position=args.position
    )

    try:
        # Get text file path
        text_file = Path(__file__).parent.parent.parent.parent / \\
                   "Tamil-Source-TamilConcordence" / \\
                   "{folder}" / \\
                   "{filename}.txt"

        if not text_file.exists():
            print(f"\\n✗ Error: Text file not found: {{text_file}}")
            sys.exit(1)

        print(f"Text file: {{text_file.name}}")

        importer.parse_file(str(text_file))
        importer.bulk_insert()  # Single atomic transaction

        print("\\n[OK] Import complete!")

    except ValueError as e:
        print(f"\\n✗ Error: {{e}}")
        print("To re-import, first delete the existing work:")
        print(f'  python delete_{work_key}.py')
        importer.rollback()
        sys.exit(1)

    except Exception as e:
        print(f"\\n✗ Unexpected error: {{e}}")
        import traceback
        traceback.print_exc()
        importer.rollback()
        sys.exit(1)

    finally:
        importer.close()


if __name__ == '__main__':
    main()
'''


def generate_script(work_key, metadata):
    """Generate import script for a work"""
    # Create class name from work key (e.g., 'inna_narpathu' -> 'InnaNarpathu')
    class_name = ''.join(word.capitalize() for word in work_key.split('_'))

    # Fill template
    script_content = FLAT_TEMPLATE.format(
        work_key=work_key,
        work_name=metadata['work_name'],
        work_name_tamil=metadata['work_name_tamil'],
        class_name=class_name,
        position=metadata['position_in_collection'],
        folder=metadata['folder'],
        filename=metadata['filename']
    )

    # Write to file
    output_path = Path(__file__).parent / 'works' / f"import_{work_key}.py"
    output_path.write_text(script_content, encoding='utf-8')
    print(f"  ✓ Generated {output_path.name}")


def main():
    print("="*70)
    print("  Generating 18 Individual Import Scripts")
    print("="*70)

    # Generate scripts for all flat structure works first
    flat_works = [
        'nanmanikkadigai', 'inna_narpathu', 'iniyavai_narpathu',
        'kar_narpathu', 'kalavazhi_narpathu', 'thirigadugam',
        'asarakkovai', 'pazhamozhi_nanuru', 'sirupanchamoolam', 'elathi'
    ]

    print("\\nGenerating flat structure imports (10 works)...")
    for work_key in flat_works:
        if work_key in WORK_METADATA:
            generate_script(work_key, WORK_METADATA[work_key])

    print(f"\\n[OK] Generated {{len(flat_works)}} flat structure import scripts")
    print("\\nNote: Thinai, paththu, adhikaram, and thirukkural structures")
    print("      require custom parsing logic and will be generated separately.")


if __name__ == '__main__':
    main()
