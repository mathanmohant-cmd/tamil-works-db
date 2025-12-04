#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sangam Literature Bulk Import - Fast 2-phase import using PostgreSQL COPY
Phase 1: Parse all text files → Build data structures in memory
Phase 2: Bulk COPY into database (1000x faster than INSERT)
"""

import re
import psycopg2
from pathlib import Path
from typing import Dict, List
import csv
import io
import os

class SangamBulkImporter:
    # Map filenames to work information
    SANGAM_WORKS = {
        'குறுந்தொகை.txt': {
            'work_id': 4, 'work_name': 'Kuruntokai', 'work_name_tamil': 'குறுந்தொகை',
            'type': 'thogai', 'description': 'Short poems on love and war'
        },
        'நற்றிணை.txt': {
            'work_id': 5, 'work_name': 'Natrinai', 'work_name_tamil': 'நற்றிணை',
            'type': 'thogai', 'description': 'Collection of 400 poems'
        },
        'ஐங்குறுநூறு.txt': {
            'work_id': 6, 'work_name': 'Ainkurunuru', 'work_name_tamil': 'ஐங்குறுநூறு',
            'type': 'thogai', 'description': 'Five hundred short poems'
        },
        'அகநானூறு.txt': {
            'work_id': 7, 'work_name': 'Akananuru', 'work_name_tamil': 'அகநானூறு',
            'type': 'thogai', 'description': 'Four hundred poems on love'
        },
        'புறநானூறு.txt': {
            'work_id': 8, 'work_name': 'Purananuru', 'work_name_tamil': 'புறநானூறு',
            'type': 'thogai', 'description': 'Four hundred poems on war and ethics'
        },
        'கலித்தொகை.txt': {
            'work_id': 9, 'work_name': 'Kalittokai', 'work_name_tamil': 'கலித்தொகை',
            'type': 'thogai', 'description': 'Collection of Kali meter poems'
        },
        'பதிற்றுப்பத்து.txt': {
            'work_id': 10, 'work_name': 'Patirruppattu', 'work_name_tamil': 'பதிற்றுப்பத்து',
            'type': 'thogai', 'description': 'Ten tens of poems'
        },
        'பரிபாடல்.txt': {
            'work_id': 11, 'work_name': 'Paripadal', 'work_name_tamil': 'பரிபாடல்',
            'type': 'thogai', 'description': 'Songs in Paripadal meter'
        },
        'திருமுருகாற்றுப்படை.txt': {
            'work_id': 12, 'work_name': 'Tirumurukāṟṟuppaṭai', 'work_name_tamil': 'திருமுருகாற்றுப்படை',
            'type': 'padal', 'description': 'Guide to Lord Murugan'
        },
        'பொருநராற்றுப்படை.txt': {
            'work_id': 13, 'work_name': 'Porunarāṟṟuppaṭai', 'work_name_tamil': 'பொருநராற்றுப்படை',
            'type': 'padal', 'description': 'Guide to patron'
        },
        'சிறுபாணாற்றுப்படை.txt': {
            'work_id': 14, 'work_name': 'Sirupāṇāṟṟuppaṭai', 'work_name_tamil': 'சிறுபாணாற்றுப்படை',
            'type': 'padal', 'description': 'Guide to small drum player'
        },
        'பெரும்பாணாற்றுப்படை.txt': {
            'work_id': 15, 'work_name': 'Perumpāṇāṟṟuppaṭai', 'work_name_tamil': 'பெரும்பாணாற்றுப்படை',
            'type': 'padal', 'description': 'Guide to great drum player'
        },
        'முல்லைப்பாட்டு.txt': {
            'work_id': 16, 'work_name': 'Mullaippāṭṭu', 'work_name_tamil': 'முல்லைப்பாட்டு',
            'type': 'padal', 'description': 'Song of Mullai landscape'
        },
        'மதுரைக்காஞ்சி.txt': {
            'work_id': 17, 'work_name': 'Maturaikkāñci', 'work_name_tamil': 'மதுரைக்காஞ்சி',
            'type': 'padal', 'description': 'Description of Madurai city'
        },
        'நெடுநல்வாடை.txt': {
            'work_id': 18, 'work_name': 'Neṭunalvāṭai', 'work_name_tamil': 'நெடுநல்வாடை',
            'type': 'padal', 'description': 'The long north wind'
        },
        'பட்டினப்பாலை.txt': {
            'work_id': 19, 'work_name': 'Paṭṭiṉappālai', 'work_name_tamil': 'பட்டினப்பாலை',
            'type': 'padal', 'description': 'Description of seaport'
        },
        'மலைபடுகடாம்.txt': {
            'work_id': 20, 'work_name': 'Malaippaṭukaṭām', 'work_name_tamil': 'மலைபடுகடாம்',
            'type': 'padal', 'description': 'Mountain-traversing journey'
        },
        'குறிஞ்சிப்பாட்டு.txt': {
            'work_id': 21, 'work_name': 'Kuṟiñcippāṭṭu', 'work_name_tamil': 'குறிஞ்சிப்பாட்டு',
            'type': 'padal', 'description': 'Song of Kurinji landscape'
        }
    }

    def __init__(self, db_connection_string: str):
        """Initialize importer"""
        self.conn = psycopg2.connect(db_connection_string)
        self.cursor = self.conn.cursor()

        # Get existing max IDs from database
        self.cursor.execute("SELECT COALESCE(MAX(section_id), 0) FROM sections")
        self.section_id = self.cursor.fetchone()[0] + 1

        self.cursor.execute("SELECT COALESCE(MAX(verse_id), 0) FROM verses")
        self.verse_id = self.cursor.fetchone()[0] + 1

        self.cursor.execute("SELECT COALESCE(MAX(line_id), 0) FROM lines")
        self.line_id = self.cursor.fetchone()[0] + 1

        self.cursor.execute("SELECT COALESCE(MAX(word_id), 0) FROM words")
        self.word_id = self.cursor.fetchone()[0] + 1

        print(f"  Starting IDs: section={self.section_id}, verse={self.verse_id}, line={self.line_id}, word={self.word_id}")

        # Data containers (reset per work)
        self.sections = []
        self.verses = []
        self.lines = []
        self.words = []
        self.works = []

        # Section cache
        self.section_cache = {}

    def _ensure_works_exist(self):
        """Create all Sangam work entries"""
        print("  Creating Sangam work entries...")

        for filename, work_info in self.SANGAM_WORKS.items():
            self.cursor.execute("SELECT work_id FROM works WHERE work_id = %s", (work_info['work_id'],))
            if not self.cursor.fetchone():
                self.works.append({
                    'work_id': work_info['work_id'],
                    'work_name': work_info['work_name'],
                    'work_name_tamil': work_info['work_name_tamil'],
                    'period': '300 BCE - 300 CE',
                    'author': 'Various',
                    'author_tamil': 'பல்வேறு புலவர்கள்',
                    'description': work_info['description']
                })

        if self.works:
            self._bulk_copy('works', self.works,
                           ['work_id', 'work_name', 'work_name_tamil', 'period',
                            'author', 'author_tamil', 'description'])
            self.conn.commit()
            print(f"  Created {len(self.works)} work entries")

    def _reset_data_containers(self):
        """Clear data containers for next work"""
        self.sections = []
        self.verses = []
        self.lines = []
        self.words = []
        self.section_cache = {}

    def _get_or_create_section_id(self, work_id, parent_id=None):
        """Get or create root section for work"""
        cache_key = (work_id, parent_id)

        if cache_key in self.section_cache:
            return self.section_cache[cache_key]

        section_id = self.section_id
        self.section_id += 1

        self.sections.append({
            'section_id': section_id,
            'work_id': work_id,
            'parent_section_id': parent_id,
            'level_type': 'Poems',
            'level_type_tamil': 'பாடல்கள்',
            'section_number': 1,
            'section_name': 'Main Collection',
            'section_name_tamil': 'முக்கிய தொகுப்பு',
            'sort_order': 1
        })

        self.section_cache[cache_key] = section_id
        return section_id

    def parse_thogai_file(self, file_path: Path, work_info: Dict):
        """Parse Thogai (poetry collection) format"""
        print(f"  Parsing {work_info['work_name_tamil']} (Thogai)...")

        work_id = work_info['work_id']
        section_id = self._get_or_create_section_id(work_id)

        with open(file_path, 'r', encoding='utf-8') as f:
            lines_text = f.readlines()

        current_poem_num = None
        current_poem_lines = []
        poem_count = 0

        for line in lines_text:
            line = line.strip()
            if not line:
                continue

            # Check for poem header: # N theme
            poem_match = re.match(r'^#\s*(\d+)', line)
            if poem_match:
                if current_poem_num and current_poem_lines:
                    self._add_poem(work_id, section_id, current_poem_num, current_poem_lines)
                    poem_count += 1

                current_poem_num = int(poem_match.group(1))
                current_poem_lines = []
                continue

            # Skip author lines
            if line.startswith('*'):
                continue

            # Poem line
            if current_poem_num:
                current_poem_lines.append(line)

        # Save last poem
        if current_poem_num and current_poem_lines:
            self._add_poem(work_id, section_id, current_poem_num, current_poem_lines)
            poem_count += 1

        print(f"    Parsed {poem_count} poems")

    def parse_padal_file(self, file_path: Path, work_info: Dict):
        """Parse Padal (continuous poem) format"""
        print(f"  Parsing {work_info['work_name_tamil']} (Padal)...")

        work_id = work_info['work_id']
        section_id = self._get_or_create_section_id(work_id)

        with open(file_path, 'r', encoding='utf-8') as f:
            lines_text = f.readlines()

        poem_lines = []
        for line in lines_text:
            line = line.strip()
            if line:
                poem_lines.append(line)

        if poem_lines:
            self._add_poem(work_id, section_id, 1, poem_lines)
            print(f"    Parsed 1 continuous poem ({len(poem_lines)} lines)")

    def _add_poem(self, work_id, section_id, poem_num, poem_lines):
        """Add poem to memory"""
        verse_id = self.verse_id
        self.verse_id += 1

        self.verses.append({
            'verse_id': verse_id,
            'work_id': work_id,
            'section_id': section_id,
            'verse_number': poem_num,
            'verse_type': 'poem',
            'verse_type_tamil': 'பாடல்',
            'total_lines': len(poem_lines),
            'sort_order': poem_num
        })

        for line_num, line_text in enumerate(poem_lines, start=1):
            line_id = self.line_id
            self.line_id += 1

            self.lines.append({
                'line_id': line_id,
                'verse_id': verse_id,
                'line_number': line_num,
                'line_text': line_text
            })

            # Parse words
            words = line_text.strip().split()
            for word_position, word_text in enumerate(words, start=1):
                word_id = self.word_id
                self.word_id += 1

                self.words.append({
                    'word_id': word_id,
                    'line_id': line_id,
                    'word_position': word_position,
                    'word_text': word_text.strip('.,;!?'),
                    'sandhi_split': None
                })

    def parse_directory(self, directory_path: Path):
        """Parse and import works one at a time with per-work rollback"""
        print(f"\nParsing Sangam literature files...")

        success_count = 0
        failed_works = []

        for filename, work_info in self.SANGAM_WORKS.items():
            file_path = directory_path / filename
            if not file_path.exists():
                print(f"  Skipping {filename} (not found)")
                continue

            # Check if work already imported
            self.cursor.execute("""
                SELECT COUNT(*) FROM verses WHERE work_id = %s
            """, (work_info['work_id'],))
            existing_count = self.cursor.fetchone()[0]

            if existing_count > 0:
                print(f"  Skipping {work_info['work_name_tamil']} (already imported: {existing_count} verses)")
                continue

            try:
                print(f"\n{'='*70}")
                print(f"Processing: {work_info['work_name_tamil']} (ID: {work_info['work_id']})")
                print(f"{'='*70}")

                # Phase 1: Parse file into memory
                if work_info['type'] == 'thogai':
                    self.parse_thogai_file(file_path, work_info)
                else:
                    self.parse_padal_file(file_path, work_info)

                # Phase 2: Bulk insert for this work
                self._bulk_insert_work(work_info['work_name_tamil'])

                # Commit this work
                self.conn.commit()
                print(f"✓ {work_info['work_name_tamil']} imported successfully")
                success_count += 1

            except Exception as e:
                # Rollback this work
                self.conn.rollback()
                print(f"✗ Failed to import {work_info['work_name_tamil']}: {e}")
                failed_works.append((work_info['work_name_tamil'], str(e)))

            finally:
                # Clear data containers for next work
                self._reset_data_containers()

        # Summary
        print(f"\n{'='*70}")
        print(f"Import Summary:")
        print(f"  ✓ Successfully imported: {success_count} works")
        if failed_works:
            print(f"  ✗ Failed: {len(failed_works)} works")
            for work_name, error in failed_works:
                print(f"    - {work_name}: {error}")
        print(f"{'='*70}")

    def _bulk_insert_work(self, work_name: str):
        """Bulk insert single work using COPY"""
        print(f"  Inserting into database...")

        # Insert sections
        if self.sections:
            print(f"    - {len(self.sections)} sections...")
            self._bulk_copy('sections', self.sections,
                           ['section_id', 'work_id', 'parent_section_id', 'level_type', 'level_type_tamil',
                            'section_number', 'section_name', 'section_name_tamil', 'sort_order'])

        # Insert verses
        if self.verses:
            print(f"    - {len(self.verses)} verses...")
            self._bulk_copy('verses', self.verses,
                           ['verse_id', 'work_id', 'section_id', 'verse_number', 'verse_type',
                            'verse_type_tamil', 'total_lines', 'sort_order'])

        # Insert lines
        if self.lines:
            print(f"    - {len(self.lines)} lines...")
            self._bulk_copy('lines', self.lines,
                           ['line_id', 'verse_id', 'line_number', 'line_text'])

        # Insert words
        if self.words:
            print(f"    - {len(self.words)} words...")
            self._bulk_copy('words', self.words,
                           ['word_id', 'line_id', 'word_position', 'word_text', 'sandhi_split'])

    def _bulk_copy(self, table_name, data, columns):
        """Use COPY for bulk insert"""
        if not data:
            return

        buffer = io.StringIO()
        writer = csv.writer(buffer, delimiter='\t')

        for row in data:
            writer.writerow([row.get(col) if row.get(col) is not None else '\\N' for col in columns])

        buffer.seek(0)
        self.cursor.copy_from(buffer, table_name, columns=columns, null='\\N')

    def close(self):
        """Close connection"""
        self.cursor.close()
        self.conn.close()


def main():
    import sys

    # Get database URL
    db_connection = os.getenv('DATABASE_URL', "postgresql://postgres:password@localhost/tamil_literature")
    if len(sys.argv) > 1:
        db_connection = sys.argv[1]

    # Directory path
    script_dir = Path(__file__).parent
    project_dir = script_dir.parent
    sangam_dir = project_dir / "Tamil-Source-TamilConcordence" / "2_Sangam_Literature"

    print("="*70)
    print("Sangam Literature Bulk Import - Fast 2-Phase Import")
    print("="*70)
    print(f"Database: {db_connection[:50]}...")
    print(f"Directory: {sangam_dir}")

    importer = SangamBulkImporter(db_connection)

    try:
        importer._ensure_works_exist()
        importer.parse_directory(sangam_dir)
        print("\n✓ Import complete!")
    finally:
        importer.close()


if __name__ == '__main__':
    main()
