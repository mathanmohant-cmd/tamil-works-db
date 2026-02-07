#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generator for Naladiyar adhikaram structure import script.
Creates import/delete pair for hierarchical 3-level structure (Paal→Iyal→Adhikaram).
"""

import sys
from pathlib import Path

# Add shared directory to path
sys.path.insert(0, str(Path(__file__).parent / 'shared'))
from work_metadata import WORK_METADATA


def generate_adhikaram_import_script(work_key, metadata):
    """Generate import script for adhikaram structure work (Naladiyar)"""

    class_name = ''.join(word.capitalize() for word in work_key.split('_'))

    script = f'''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Atomic import for {metadata['work_name_tamil']} ({metadata['work_name']})
3-level hierarchical structure: Paal → Iyal → Adhikaram → Verses

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

        # Hierarchical structure state (3 levels)
        self.section_cache = {{}}  # Cache sections to avoid duplicates
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

        self.sections.append({{
            'section_id': section_id,
            'work_id': self.work_id,
            'parent_section_id': parent_id,
            'level_type': level_type,
            'level_type_tamil': level_type_tamil,
            'section_number': section_number,
            'section_name': section_name,
            'section_name_tamil': section_name_tamil,
            'sort_order': section_number
        }})

        self.section_cache[cache_key] = section_id
        return section_id

    def parse_file(self, text_file_path: str):
        """Phase 1: Parse text file into memory"""
        print("\\\\nPhase 1: Parsing file...")

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
                paal_name_map = {{
                    'அறத்துப்பால்': 'Virtue',
                    'பொருட்பால்': 'Wealth',
                    'காமத்துப்பால்': 'Love'
                }}
                paal_name = paal_name_map.get(paal_name_tamil, paal_name_tamil)

                self.current_paal_id = self._get_or_create_section_id(
                    None, 'Paal', 'பால்',
                    self.paal_counter,
                    paal_name,
                    paal_name_tamil
                )
                continue

            # Check for Iyal marker (number followed by Tamil text ending with "இயல்")
            iyal_match = re.match(r'^(\\\\d+)\\\\s+([\\\\u0B80-\\\\u0BFF\\\\s]+இயல்)\\\\s*$', line)
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
            adhikaram_match = re.match(r'^@(\\\\d+)\\\\s+(.+)$', line)
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
            verse_match = re.match(r'^#(\\\\d+)$', line)
            if verse_match:
                # Save previous verse if exists
                if current_verse_num is not None and current_verse_lines:
                    self._add_verse(current_verse_num, current_verse_lines)
                    verse_count += 1
                    if verse_count % 50 == 0:
                        print(f"  Parsed {{verse_count}} verses...")

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

        print(f"[OK] Phase 1 complete: Parsed {{verse_count}} verses")
        print(f"  - Paals: {{self.paal_counter}}")
        print(f"  - Iyals: {{self.iyal_counter}}")
        print(f"  - Adhikarams: {{self.adhikaram_counter}}")
        print(f"  - Sections: {{len(self.sections)}}")
        print(f"  - Verses: {{len(self.verses)}}")
        print(f"  - Lines: {{len(self.lines)}}")
        print(f"  - Words: {{len(self.words)}}")

    def _add_verse(self, verse_num, verse_lines):
        """Add verse to memory"""
        if self.current_adhikaram_id is None:
            # No adhikaram section yet, skip this verse
            return

        verse_id = self.verse_id
        self.verse_id += 1

        self.verses.append({{
            'verse_id': verse_id,
            'work_id': self.work_id,
            'section_id': self.current_adhikaram_id,
            'verse_number': verse_num,
            'verse_type': 'naladiyar',
            'verse_type_tamil': 'நாலடியார்',
            'total_lines': len(verse_lines),
            'sort_order': verse_num,
            'metadata': None
        }})

        for line_num, line_text in enumerate(verse_lines, start=1):
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
            print(f"\\\\n✗ Error: Text file not found: {{text_file}}")
            sys.exit(1)

        print(f"Text file: {{text_file.name}}")

        importer.parse_file(str(text_file))
        importer.bulk_insert()  # Single atomic transaction

        print("\\\\n[OK] Import complete!")

    except ValueError as e:
        print(f"\\\\n✗ Error: {{e}}")
        print("To re-import, first delete the existing work:")
        print(f'  python delete_{work_key}.py')
        importer.rollback()
        sys.exit(1)

    except Exception as e:
        print(f"\\\\n✗ Unexpected error: {{e}}")
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
    print("\\\\n" + "="*70)
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
            print(f"\\\\n✗ Work '{{WORK_NAME_ENGLISH}}' not found")
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

        print(f"\\\\nThis will delete:")
        print(f"  - 1 work ({{WORK_NAME_TAMIL}})")
        print(f"  - {{stats[0]:,}} sections")
        print(f"  - {{stats[1]:,}} verses")
        print(f"  - {{stats[2]:,}} lines")
        print(f"  - {{stats[3]:,}} words")

        response = input("\\\\nAre you sure? (yes/no): ").strip().lower()
        if response not in ['yes', 'y']:
            print("Deletion cancelled.")
            cursor.close()
            conn.close()
            return False

        print("\\\\nDeleting work data...")

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
        print(f"\\\\n✓ Successfully deleted {{WORK_NAME_TAMIL}}")

        cursor.close()
        conn.close()
        return True

    except Exception as e:
        print(f"\\\\n✗ Error: {{e}}")
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
        print("\\\\n✓ Deletion complete")
        sys.exit(0)
    else:
        print("\\\\n✗ Deletion failed or cancelled")
        sys.exit(1)


if __name__ == '__main__':
    main()
'''

    return script


def main():
    print("="*70)
    print("  Generating Adhikaram Structure Script (Naladiyar)")
    print("="*70)

    works_dir = Path(__file__).parent / 'works'

    work_key = 'naladiyar'
    if work_key in WORK_METADATA:
        metadata = WORK_METADATA[work_key]

        # Generate import script
        import_script = generate_adhikaram_import_script(work_key, metadata)
        import_path = works_dir / f"import_{work_key}.py"
        import_path.write_text(import_script, encoding='utf-8')
        print(f"\n  ✓ Generated import_{work_key}.py")

        # Generate delete script
        delete_script = generate_delete_script(work_key, metadata)
        delete_path = works_dir / f"delete_{work_key}.py"
        delete_path.write_text(delete_script, encoding='utf-8')
        print(f"  ✓ Generated delete_{work_key}.py")

    print(f"\n✓ Generated Naladiyar adhikaram structure script pair (2 scripts)")


if __name__ == '__main__':
    main()
