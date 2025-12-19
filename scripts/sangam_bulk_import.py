#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sangam Literature Bulk Import - Fast 2-phase import using PostgreSQL COPY
Phase 1: Parse all text files → Build data structures in memory
Phase 2: Bulk COPY into database (1000x faster than INSERT)

IMPROVEMENTS (2025-12-05):
- Ignore dots/periods used for text alignment (……………………….. or .)
- Ignore line count numbers (multiples of 5: 5, 10, 15, etc.)
- Keep only Tamil characters, hyphens (-), and underscores (_) in words
- Prof. P. Pandiyaraja uses - and _ for specific linguistic segmentation purposes
"""

import re
import psycopg2
from pathlib import Path
from typing import Dict, List
import csv
import io
import os

class SangamBulkImporter:
    # Map filenames to work information (work_id assigned dynamically)
    # Ordered by standard Sangam literature sequence (1-18)
    SANGAM_WORKS = {
        'நற்றிணை.txt': {
            'work_name': 'Natrrinai', 'work_name_tamil': 'நற்றிணை',
            'type': 'thogai', 'description': 'Collection of 400 poems',
            'traditional_order': 2, 'start_year': -100, 'end_year': 100,
            'confidence': 'high', 'notes': 'Considered among the earliest Sangam works'
        },
        'குறுந்தொகை.txt': {
            'work_name': 'Kurunthokai', 'work_name_tamil': 'குறுந்தொகை',
            'type': 'thogai', 'description': 'Short poems on love and war',
            'traditional_order': 3, 'start_year': -100, 'end_year': 100,
            'confidence': 'high', 'notes': 'Early Sangam anthology'
        },
        'ஐங்குறுநூறு.txt': {
            'work_name': 'Ainkurunuru', 'work_name_tamil': 'ஐங்குறுநூறு',
            'type': 'thogai', 'description': 'Five hundred short poems',
            'traditional_order': 4, 'start_year': -100, 'end_year': 200,
            'confidence': 'high', 'notes': 'Sangam anthology of 500 short love poems'
        },
        'பதிற்றுப்பத்து.txt': {
            'work_name': 'Pathitrupathu', 'work_name_tamil': 'பதிற்றுப்பத்து',
            'type': 'thogai', 'description': 'Ten tens of poems',
            'traditional_order': 5, 'start_year': 100, 'end_year': 200,
            'confidence': 'high', 'notes': 'Features Chera kings, slightly later than other anthologies'
        },
        'பரிபாடல்.txt': {
            'work_name': 'Paripaadal', 'work_name_tamil': 'பரிபாடல்',
            'type': 'thogai', 'description': 'Songs in Paripadal meter',
            'traditional_order': 6, 'start_year': 100, 'end_year': 200,
            'confidence': 'high', 'notes': 'Religious hymns to Murugan and Thirumal'
        },
        'கலித்தொகை.txt': {
            'work_name': 'Kalithokai', 'work_name_tamil': 'கலித்தொகை',
            'type': 'thogai', 'description': 'Collection of Kali meter poems',
            'traditional_order': 7, 'start_year': 100, 'end_year': 250,
            'confidence': 'medium', 'notes': 'Some scholars date to later Sangam period'
        },
        'அகநானூறு.txt': {
            'work_name': 'Aganaanuru', 'work_name_tamil': 'அகநானூறு',
            'type': 'thogai', 'description': 'Four hundred poems on love',
            'traditional_order': 8, 'start_year': -100, 'end_year': 200,
            'confidence': 'high', 'notes': '400 love poems from Sangam period'
        },
        'புறநானூறு.txt': {
            'work_name': 'Puranaanuru', 'work_name_tamil': 'புறநானூறு',
            'type': 'thogai', 'description': 'Four hundred poems on war and ethics',
            'traditional_order': 9, 'start_year': -100, 'end_year': 200,
            'confidence': 'high', 'notes': 'Historical references help date some poems precisely'
        },
        'திருமுருகாற்றுப்படை.txt': {
            'work_name': 'Thirumurugaatruppadai', 'work_name_tamil': 'திருமுருகாற்றுப்படை',
            'type': 'padal', 'description': 'Guide to Lord Murugan',
            'traditional_order': 10, 'start_year': 150, 'end_year': 250,
            'confidence': 'high', 'notes': 'Part of Pathupaattu (Ten Idylls)'
        },
        'பொருநராற்றுப்படை.txt': {
            'work_name': 'Porunaraatruppadai', 'work_name_tamil': 'பொருநராற்றுப்படை',
            'type': 'padal', 'description': 'Guide to patron',
            'traditional_order': 11, 'start_year': 150, 'end_year': 250,
            'confidence': 'high', 'notes': 'Part of Pathupaattu (Ten Idylls)'
        },
        'சிறுபாணாற்றுப்படை.txt': {
            'work_name': 'Sirupanaatruppadai', 'work_name_tamil': 'சிறுபாணாற்றுப்படை',
            'type': 'padal', 'description': 'Guide to small drum player',
            'traditional_order': 12, 'start_year': 150, 'end_year': 250,
            'confidence': 'high', 'notes': 'Part of Pathupaattu (Ten Idylls)'
        },
        'பெரும்பாணாற்றுப்படை.txt': {
            'work_name': 'Perumpanaatruppadai', 'work_name_tamil': 'பெரும்பாணாற்றுப்படை',
            'type': 'padal', 'description': 'Guide to great drum player',
            'traditional_order': 13, 'start_year': 150, 'end_year': 250,
            'confidence': 'high', 'notes': 'Part of Pathupaattu (Ten Idylls)'
        },
        'முல்லைப்பாட்டு.txt': {
            'work_name': 'Mullaippaattu', 'work_name_tamil': 'முல்லைப்பாட்டு',
            'type': 'padal', 'description': 'Song of Mullai landscape',
            'traditional_order': 14, 'start_year': 150, 'end_year': 250,
            'confidence': 'high', 'notes': 'Part of Pathupaattu (Ten Idylls)'
        },
        'மதுரைக்காஞ்சி.txt': {
            'work_name': 'Madurai kanchi', 'work_name_tamil': 'மதுரைக்காஞ்சி',
            'type': 'padal', 'description': 'Description of Madurai city',
            'traditional_order': 15, 'start_year': 150, 'end_year': 250,
            'confidence': 'high', 'notes': 'Part of Pathupaattu (Ten Idylls)'
        },
        'நெடுநல்வாடை.txt': {
            'work_name': 'Nedunalvaadai', 'work_name_tamil': 'நெடுநல்வாடை',
            'type': 'padal', 'description': 'The long north wind',
            'traditional_order': 16, 'start_year': 150, 'end_year': 250,
            'confidence': 'high', 'notes': 'Part of Pathupaattu (Ten Idylls)'
        },
        'குறிஞ்சிப்பாட்டு.txt': {
            'work_name': 'Kurinchippaattu', 'work_name_tamil': 'குறிஞ்சிப்பாட்டு',
            'type': 'padal', 'description': 'Song of Kurinji landscape',
            'traditional_order': 17, 'start_year': 150, 'end_year': 250,
            'confidence': 'high', 'notes': 'Part of Pathupaattu (Ten Idylls)'
        },
        'பட்டினப்பாலை.txt': {
            'work_name': 'Pattinappaalai', 'work_name_tamil': 'பட்டினப்பாலை',
            'type': 'padal', 'description': 'Description of seaport',
            'traditional_order': 18, 'start_year': 150, 'end_year': 250,
            'confidence': 'high', 'notes': 'Part of Pathupaattu (Ten Idylls)'
        },
        'மலைபடுகடாம்.txt': {
            'work_name': 'Malaipadukataam', 'work_name_tamil': 'மலைபடுகடாம்',
            'type': 'padal', 'description': 'Mountain-traversing journey',
            'traditional_order': 19, 'start_year': 150, 'end_year': 250,
            'confidence': 'high', 'notes': 'Part of Pathupaattu (Ten Idylls)'
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
        """Create all Sangam work entries with dynamic work_id assignment"""
        print("  Checking/creating Sangam work entries...")

        # First, check if ANY works already exist
        existing_works = []
        for filename, work_info in self.SANGAM_WORKS.items():
            work_name = work_info['work_name']
            self.cursor.execute("SELECT work_id FROM works WHERE work_name = %s", (work_name,))
            existing = self.cursor.fetchone()
            if existing:
                existing_works.append((work_info['work_name'], work_info['work_name_tamil'], existing[0]))

        # If any works exist, exit with error
        if existing_works:
            print(f"\n✗ Found {len(existing_works)} existing Sangam works in database:")
            for name_en, name_ta, work_id in existing_works:
                print(f"  - {name_ta} ({name_en}) - ID: {work_id}")
            print(f"\nTo re-import, first delete the existing work(s):")
            for name_en, name_ta, work_id in existing_works:
                print(f'  python scripts/delete_work.py "{name_en}"')
            print(f"\nNote: You must delete ALL Sangam works before re-importing.")
            self.cursor.close()
            self.conn.close()
            sys.exit(1)

        # Get next available work_id ONCE before the loop
        self.cursor.execute("SELECT COALESCE(MAX(work_id), 0) FROM works")
        next_work_id = self.cursor.fetchone()[0] + 1

        for filename, work_info in self.SANGAM_WORKS.items():
            # Assign next available work_id and increment
            work_info['work_id'] = next_work_id

            # Calculate canonical order: Sangam works are 200-217
            # Map traditional_order (2-19) to canonical_order (200-217)
            canonical_order = 198 + work_info['traditional_order']  # 198 + 2 = 200, 198 + 19 = 217

            self.works.append({
                'work_id': next_work_id,
                'work_name': work_info['work_name'],
                'work_name_tamil': work_info['work_name_tamil'],
                'period': '300 BCE - 300 CE',
                'author': 'Various',
                'author_tamil': 'பல்வேறு புலவர்கள்',
                'description': work_info['description'],
                'chronology_start_year': work_info['start_year'],
                'chronology_end_year': work_info['end_year'],
                'chronology_confidence': work_info['confidence'],
                'chronology_notes': work_info['notes'],
                'canonical_order': canonical_order
            })

            next_work_id += 1  # Increment for next work

        if self.works:
            self._bulk_copy('works', self.works,
                           ['work_id', 'work_name', 'work_name_tamil', 'period',
                            'author', 'author_tamil', 'description',
                            'chronology_start_year', 'chronology_end_year',
                            'chronology_confidence', 'chronology_notes', 'canonical_order'])
            self.conn.commit()
            print(f"  ✓ Created {len(self.works)} new work entries. Use collection management utility to assign to collections.")

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

    def _clean_word_text(self, word: str) -> str:
        """
        Clean word text according to Prof. P. Pandiyaraja's principles:
        - Keep only Tamil characters, hyphens (-), and underscores (_)
        - Remove dots, punctuation, and line count numbers
        """
        # First, strip trailing numbers (line counts like 5, 10, 15 attached to words)
        word = re.sub(r'\d+$', '', word)

        # Remove all non-Tamil characters except - and _
        # Tamil Unicode range: \u0B80-\u0BFF
        cleaned = re.sub(r'[^\u0B80-\u0BFF\-_]', '', word)
        return cleaned.strip()

    def _is_line_count(self, token: str) -> bool:
        """
        Check if token is a line count number (multiples of 5 or 10)
        Returns True for: 5, 10, 15, 20, 25, etc.
        """
        try:
            num = int(token)
            # Common line counts: multiples of 5
            return num % 5 == 0
        except ValueError:
            return False

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
            # Clean line: remove dots/periods, markers, and line numbers
            # Remove alignment dots and ellipsis
            cleaned_line = line_text.replace('.', '').replace('…', '')
            # Remove structural markers
            cleaned_line = re.sub(r'^[#@$&*]+\s*', '', cleaned_line)
            # Remove ** and *** markers
            cleaned_line = re.sub(r'\*\*\*?', '', cleaned_line)
            # Remove trailing line numbers (with or without preceding space)
            # Matches: "text 5", "text5", "text  10", etc.
            cleaned_line = re.sub(r'\s*\d+$', '', cleaned_line)

            line_id = self.line_id
            self.line_id += 1

            self.lines.append({
                'line_id': line_id,
                'verse_id': verse_id,
                'line_number': line_num,
                'line_text': cleaned_line.strip()
            })

            # Parse words
            tokens = cleaned_line.strip().split()
            word_position = 1

            for token in tokens:
                # Skip line count numbers (multiples of 5)
                if self._is_line_count(token):
                    continue

                # Clean word (keep only Tamil, -, and _)
                word_text = self._clean_word_text(token)

                # Skip empty words after cleaning
                if not word_text:
                    continue

                word_id = self.word_id
                self.word_id += 1

                self.words.append({
                    'word_id': word_id,
                    'line_id': line_id,
                    'word_position': word_position,
                    'word_text': word_text,
                    'sandhi_split': None
                })

                word_position += 1

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
