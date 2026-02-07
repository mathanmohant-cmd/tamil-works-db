#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generator to create all 18 import and delete scripts based on templates.
Generates scripts for all structure types from the Inna Narpathu template.
"""

import sys
from pathlib import Path

# Add shared directory to path
sys.path.insert(0, str(Path(__file__).parent / 'shared'))
from work_metadata import WORK_METADATA


def generate_flat_import_script(work_key, metadata):
    """Generate import script for flat structure work"""

    class_name = ''.join(word.capitalize() for word in work_key.split('_'))

    script = f'''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Atomic import for {metadata['work_name_tamil']} ({metadata['work_name']})
Flat structure: Single section, all verses directly under it

Usage:
    # Standalone (links to default collection 201)
    python import_{work_key}.py [database_url]

    # Link to different collection
    python import_{work_key}.py [database_url] --collection-id 201 --position {metadata['position_in_collection']}

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


class {class_name}Importer(BaseWorkImporter):
    """Atomic importer for {metadata['work_name']}"""

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

    parser = argparse.ArgumentParser(description='Import {metadata["work_name"]}')
    parser.add_argument('database_url', nargs='?',
                       default=os.getenv('DATABASE_URL',
                                        "postgresql://postgres:postgres@localhost/tamil_literature"))
    parser.add_argument('--collection-id', type=int, help='Collection to link this work to')
    parser.add_argument('--position', type=int, help='Position within collection')
    args = parser.parse_args()

    print("="*70)
    print("{metadata['work_name']} Atomic Import")
    print("="*70)
    print(f"Database: {{args.database_url[:50]}}...")

    importer = {class_name}Importer(
        args.database_url,
        collection_id=args.collection_id,
        position=args.position
    )

    try:
        # Get text file path
        text_file = (
            Path(__file__).parent.parent.parent.parent /
            "Tamil-Source-TamilConcordence" /
            "{metadata['folder']}" /
            "{metadata['filename']}.txt"
        )

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

    return script


def generate_delete_script(work_key, metadata):
    """Generate delete script for any work"""

    script = f'''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Atomic delete for {metadata['work_name_tamil']} ({metadata['work_name']})

Usage:
    python delete_{work_key}.py [database_url]
"""

import os
import sys
import psycopg2

WORK_NAME_ENGLISH = '{metadata['work_name']}'
WORK_NAME_TAMIL = '{metadata['work_name_tamil']}'


def delete_work(connection_string):
    """Delete work and all its data atomically"""
    print("\\n" + "="*70)
    print(f"  DELETE {{WORK_NAME_TAMIL}} ({{WORK_NAME_ENGLISH}})")
    print("="*70)

    try:
        conn = psycopg2.connect(connection_string)
        conn.autocommit = False  # Use transaction
        cursor = conn.cursor()

        # Find work
        cursor.execute(
            "SELECT work_id FROM works WHERE work_name = %s",
            (WORK_NAME_ENGLISH,)
        )
        result = cursor.fetchone()

        if not result:
            print(f"\\n✗ Work '{{WORK_NAME_ENGLISH}}' not found")
            cursor.close()
            conn.close()
            return False

        work_id = result[0]

        # Get deletion stats
        cursor.execute("""
            SELECT
                COUNT(DISTINCT s.section_id) as sections,
                COUNT(DISTINCT v.verse_id) as verses,
                COUNT(DISTINCT l.line_id) as lines,
                COUNT(DISTINCT w.word_id) as words
            FROM works wk
            LEFT JOIN sections s ON wk.work_id = s.work_id
            LEFT JOIN verses v ON wk.work_id = v.work_id
            LEFT JOIN lines l ON v.verse_id = l.verse_id
            LEFT JOIN words w ON l.line_id = w.line_id
            WHERE wk.work_id = %s
        """, (work_id,))
        stats = cursor.fetchone()

        print(f"\\nThis will delete:")
        print(f"  - 1 work ({{WORK_NAME_TAMIL}})")
        print(f"  - {{stats[0]:,}} sections")
        print(f"  - {{stats[1]:,}} verses")
        print(f"  - {{stats[2]:,}} lines")
        print(f"  - {{stats[3]:,}} words")

        response = input("\\nAre you sure? (yes/no): ").strip().lower()
        if response not in ['yes', 'y']:
            print("Deletion cancelled.")
            cursor.close()
            conn.close()
            return False

        print("\\nDeleting work data...")

        # Delete in reverse dependency order
        cursor.execute("""
            DELETE FROM words
            WHERE line_id IN (
                SELECT l.line_id FROM lines l
                JOIN verses v ON l.verse_id = v.verse_id
                WHERE v.work_id = %s
            )
        """, (work_id,))
        print(f"  ✓ Deleted {{cursor.rowcount:,}} words")

        cursor.execute("""
            DELETE FROM lines
            WHERE verse_id IN (SELECT verse_id FROM verses WHERE work_id = %s)
        """, (work_id,))
        print(f"  ✓ Deleted {{cursor.rowcount:,}} lines")

        cursor.execute("DELETE FROM verses WHERE work_id = %s", (work_id,))
        print(f"  ✓ Deleted {{cursor.rowcount:,}} verses")

        cursor.execute("DELETE FROM sections WHERE work_id = %s", (work_id,))
        print(f"  ✓ Deleted {{cursor.rowcount:,}} sections")

        cursor.execute("DELETE FROM work_collections WHERE work_id = %s", (work_id,))
        print(f"  ✓ Unlinked from collections")

        cursor.execute("DELETE FROM works WHERE work_id = %s", (work_id,))
        print(f"  ✓ Deleted work entry")

        conn.commit()
        print(f"\\n✓ Successfully deleted {{WORK_NAME_TAMIL}}")

        cursor.close()
        conn.close()
        return True

    except Exception as e:
        print(f"\\n✗ Error: {{e}}")
        import traceback
        traceback.print_exc()
        if 'conn' in locals():
            conn.rollback()
            conn.close()
        return False


def main():
    db_connection = os.getenv('DATABASE_URL',
                              "postgresql://postgres:postgres@localhost/tamil_literature")
    if len(sys.argv) > 1:
        db_connection = sys.argv[1]

    print(f"Database: {{db_connection[:50]}}...")

    if delete_work(db_connection):
        print("\\n✓ Deletion complete")
        sys.exit(0)
    else:
        print("\\n✗ Deletion failed or cancelled")
        sys.exit(1)


if __name__ == '__main__':
    main()
'''

    return script


def main():
    print("="*70)
    print("  Generating Import and Delete Scripts for Eighteen Lesser Texts")
    print("="*70)

    works_dir = Path(__file__).parent / 'works'

    # Generate scripts for flat structure works
    flat_works = [
        'nanmanikkadigai', 'inna_narpathu', 'iniyavai_narpathu',
        'kar_narpathu', 'kalavazhi_narpathu', 'thirigadugam',
        'asarakkovai', 'pazhamozhi_nanuru', 'sirupanchamoolam', 'elathi'
    ]

    print("\nGenerating flat structure scripts...")
    for work_key in flat_works:
        if work_key in WORK_METADATA:
            metadata = WORK_METADATA[work_key]

            # Generate import script
            import_script = generate_flat_import_script(work_key, metadata)
            import_path = works_dir / f"import_{work_key}.py"
            import_path.write_text(import_script, encoding='utf-8')
            print(f"  ✓ Generated import_{work_key}.py")

            # Generate delete script
            delete_script = generate_delete_script(work_key, metadata)
            delete_path = works_dir / f"delete_{work_key}.py"
            delete_path.write_text(delete_script, encoding='utf-8')
            print(f"  ✓ Generated delete_{work_key}.py")

    print(f"\n✓ Generated {len(flat_works)} flat structure work pairs ({len(flat_works)*2} scripts)")
    print("\nNote: Thinai, paththu, adhikaram, and thirukkural structures")
    print("      need custom parsing logic - will be created separately.")


if __name__ == '__main__':
    main()
