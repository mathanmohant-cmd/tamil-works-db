#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tolkappiyam Bulk Import - Fast 2-phase import using PostgreSQL COPY
Phase 1: Parse all text files → Build data structures in memory
Phase 2: Bulk COPY into database (1000x faster than INSERT)

Structure:
- 3 Adhikarams (major divisions) - each in separate file
  - *** marks Adhikaram
  - @ marks Iyal (chapter)
  - # marks Nurpaa (verse/rule)

IMPROVEMENTS:
- Ignore dots/periods used for text alignment
- Ignore line count numbers (multiples of 5: 5, 10, 15, etc.)
- Keep only Tamil characters, hyphens (-), and underscores (_) in words
- Single-character words logged separately for later review
"""

import re
import psycopg2
from pathlib import Path
from typing import Dict, List
import csv
import io
import os
import json

class TolkappiyamBulkImporter:
    # Tolkappiyam has 3 Adhikarams (major divisions)
    TOLKAPPIYAM_FILES = {
        'தொல்காப்பியம்-எழுத்ததிகாரம்.txt': {
            'adhikaram_num': 1,
            'adhikaram_name': 'Ezhuttatikaram',
            'adhikaram_name_tamil': 'எழுத்ததிகாரம்',
            'description': 'Phonology and Orthography'
        },
        'தொல்காப்பியம்-சொல்லதிகாரம்.txt': {
            'adhikaram_num': 2,
            'adhikaram_name': 'Sollatikaram',
            'adhikaram_name_tamil': 'சொல்லதிகாரம்',
            'description': 'Morphology and Etymology'
        },
        'தொல்காப்பியம்-பொருளதிகாரம்.txt': {
            'adhikaram_num': 3,
            'adhikaram_name': 'Porulatikaram',
            'adhikaram_name_tamil': 'பொருளதிகாரம்',
            'description': 'Semantics and Poetics'
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

        # Data containers
        self.sections = []
        self.verses = []
        self.lines = []
        self.words = []

        # Track single-character words for later review
        self.single_char_words = []

        # Section cache for hierarchy
        self.section_cache = {}

        # Work ID (assigned dynamically)
        self.work_id = None

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

    def _is_single_tamil_char(self, word: str) -> bool:
        """Check if word is a single Tamil character (excluding - and _)"""
        # Remove - and _ to check actual Tamil characters
        tamil_only = word.replace('-', '').replace('_', '')
        return len(tamil_only) == 1

    def _log_single_char_word(self, word: str, context: Dict):
        """Log single-character word for later review"""
        self.single_char_words.append({
            'word': word,
            'adhikaram': context.get('adhikaram'),
            'iyal': context.get('iyal'),
            'nurpaa': context.get('nurpaa'),
            'line_num': context.get('line_num'),
            'line_text': context.get('line_text')
        })

    def _ensure_work_exists(self):
        """Create Tolkappiyam work entry if it doesn't exist"""
        work_name_english = 'Tolkappiyam'
        work_name_tamil = 'தொல்காப்பியம்'

        # Check if work already exists by name
        self.cursor.execute("SELECT work_id FROM works WHERE work_name = %s", (work_name_english,))
        existing = self.cursor.fetchone()

        if existing:
            self.work_id = existing[0]
            print(f"  Work {work_name_tamil} already exists (ID: {self.work_id})")
        else:
            # Get next available work_id
            self.cursor.execute("SELECT COALESCE(MAX(work_id), 0) + 1 FROM works")
            self.work_id = self.cursor.fetchone()[0]

            print(f"  Creating Tolkappiyam work entry (ID: {self.work_id})...")
            work_data = [{
                'work_id': self.work_id,
                'work_name': work_name_english,
                'work_name_tamil': work_name_tamil,
                'period': '3rd century BCE - 5th century CE',
                'author': 'Tolkappiyar',
                'author_tamil': 'தொல்காப்பியர்',
                'description': 'Ancient Tamil grammar text covering phonology, morphology, and poetics'
            }]

            self._bulk_copy('works', work_data,
                           ['work_id', 'work_name', 'work_name_tamil', 'period',
                            'author', 'author_tamil', 'description'])
            self.conn.commit()
            print(f"  Created Tolkappiyam work entry")

    def _get_or_create_adhikaram_section(self, adhikaram_num: int, adhikaram_info: Dict):
        """Get or create Adhikaram (top-level section)"""
        cache_key = ('adhikaram', adhikaram_num)

        if cache_key in self.section_cache:
            return self.section_cache[cache_key]

        section_id = self.section_id
        self.section_id += 1

        self.sections.append({
            'section_id': section_id,
            'work_id': self.work_id,
            'parent_section_id': None,
            'level_type': 'Adhikaram',
            'level_type_tamil': 'அதிகாரம்',
            'section_number': adhikaram_num,
            'section_name': adhikaram_info['adhikaram_name'],
            'section_name_tamil': adhikaram_info['adhikaram_name_tamil'],
            'sort_order': adhikaram_num
        })

        self.section_cache[cache_key] = section_id
        return section_id

    def _get_or_create_iyal_section(self, adhikaram_id: int, iyal_num: int, iyal_name: str):
        """Get or create Iyal (chapter section under Adhikaram)"""
        cache_key = ('iyal', adhikaram_id, iyal_num)

        if cache_key in self.section_cache:
            return self.section_cache[cache_key]

        section_id = self.section_id
        self.section_id += 1

        self.sections.append({
            'section_id': section_id,
            'work_id': self.work_id,
            'parent_section_id': adhikaram_id,
            'level_type': 'Iyal',
            'level_type_tamil': 'இயல்',
            'section_number': iyal_num,
            'section_name': iyal_name,
            'section_name_tamil': iyal_name,
            'sort_order': iyal_num
        })

        self.section_cache[cache_key] = section_id
        return section_id

    def parse_tolkappiyam_file(self, file_path: Path, file_info: Dict):
        """Parse single Tolkappiyam Adhikaram file"""
        print(f"\n  Parsing {file_info['adhikaram_name_tamil']}...")

        adhikaram_num = file_info['adhikaram_num']
        adhikaram_section_id = self._get_or_create_adhikaram_section(adhikaram_num, file_info)

        with open(file_path, 'r', encoding='utf-8') as f:
            lines_text = f.readlines()

        current_iyal_id = None
        current_iyal_num = None
        current_iyal_name = None
        current_nurpaa_num = None
        current_nurpaa_lines = []
        nurpaa_count = 0

        for line in lines_text:
            line = line.strip()
            if not line:
                continue

            # Skip *** markers (Adhikaram markers)
            if line.startswith('***'):
                continue

            # Check for Iyal marker: @ N <name>
            iyal_match = re.match(r'^@\s*(\d+)\s+(.+)$', line)
            if iyal_match:
                # Save previous nurpaa if exists
                if current_nurpaa_num and current_nurpaa_lines:
                    self._add_nurpaa(adhikaram_section_id, current_iyal_id,
                                    current_nurpaa_num, current_nurpaa_lines,
                                    file_info['adhikaram_name_tamil'], current_iyal_name)
                    nurpaa_count += 1
                    current_nurpaa_num = None
                    current_nurpaa_lines = []

                # Create new Iyal section
                current_iyal_num = int(iyal_match.group(1))
                current_iyal_name = iyal_match.group(2).strip()
                current_iyal_id = self._get_or_create_iyal_section(
                    adhikaram_section_id, current_iyal_num, current_iyal_name
                )
                continue

            # Check for Nurpaa marker: #N
            nurpaa_match = re.match(r'^#(\d+)$', line)
            if nurpaa_match:
                # Save previous nurpaa if exists
                if current_nurpaa_num and current_nurpaa_lines:
                    self._add_nurpaa(adhikaram_section_id, current_iyal_id,
                                    current_nurpaa_num, current_nurpaa_lines,
                                    file_info['adhikaram_name_tamil'], current_iyal_name)
                    nurpaa_count += 1

                # Start new nurpaa
                current_nurpaa_num = int(nurpaa_match.group(1))
                current_nurpaa_lines = []
                continue

            # Nurpaa line content
            if current_nurpaa_num is not None:
                current_nurpaa_lines.append(line)

        # Save last nurpaa
        if current_nurpaa_num and current_nurpaa_lines:
            self._add_nurpaa(adhikaram_section_id, current_iyal_id,
                            current_nurpaa_num, current_nurpaa_lines,
                            file_info['adhikaram_name_tamil'], current_iyal_name)
            nurpaa_count += 1

        print(f"    Parsed {nurpaa_count} nurpaas")

    def _add_nurpaa(self, adhikaram_id, iyal_id, nurpaa_num, nurpaa_lines,
                    adhikaram_name, iyal_name):
        """Add nurpaa (verse) to memory"""
        verse_id = self.verse_id
        self.verse_id += 1

        self.verses.append({
            'verse_id': verse_id,
            'work_id': self.work_id,
            'section_id': iyal_id if iyal_id else adhikaram_id,
            'verse_number': nurpaa_num,
            'verse_type': 'nurpaa',
            'verse_type_tamil': 'நூற்பா',
            'total_lines': len(nurpaa_lines),
            'sort_order': nurpaa_num
        })

        for line_num, line_text in enumerate(nurpaa_lines, start=1):
            # Clean line: remove dots/periods (used for spacing/alignment)
            cleaned_line = line_text.replace('.', '').replace('…', '')

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

                # Log single-character words (grammar references to letters)
                if self._is_single_tamil_char(word_text):
                    self._log_single_char_word(word_text, {
                        'adhikaram': adhikaram_name,
                        'iyal': iyal_name,
                        'nurpaa': nurpaa_num,
                        'line_num': line_num,
                        'line_text': cleaned_line.strip()
                    })
                    # Skip adding to database for now
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

    def parse_all_files(self, tolkappiyam_dir: Path):
        """Parse all 3 Tolkappiyam Adhikaram files"""
        print(f"\nParsing Tolkappiyam files from {tolkappiyam_dir}...")

        # Check if already imported
        self.cursor.execute("""
            SELECT COUNT(*) FROM verses WHERE work_id = %s
        """, (self.work_id,))
        existing_count = self.cursor.fetchone()[0]

        if existing_count > 0:
            print(f"  Tolkappiyam already imported ({existing_count} nurpaas exist)")
            print(f"  Skipping import. Delete existing data first if you want to re-import.")
            return False

        # Parse each file in order
        for filename in sorted(self.TOLKAPPIYAM_FILES.keys()):
            file_path = tolkappiyam_dir / filename
            if not file_path.exists():
                print(f"  ERROR: File not found: {filename}")
                continue

            file_info = self.TOLKAPPIYAM_FILES[filename]
            self.parse_tolkappiyam_file(file_path, file_info)

        return True

    def bulk_insert(self):
        """Phase 2: Bulk insert using PostgreSQL COPY"""
        print("\nPhase 2: Bulk inserting into database...")

        # Insert sections (Adhikarams and Iyals)
        if self.sections:
            print(f"  - {len(self.sections)} sections...")
            self._bulk_copy('sections', self.sections,
                           ['section_id', 'work_id', 'parent_section_id', 'level_type', 'level_type_tamil',
                            'section_number', 'section_name', 'section_name_tamil', 'sort_order'])

        # Insert verses (Nurpaas)
        if self.verses:
            print(f"  - {len(self.verses)} nurpaas...")
            self._bulk_copy('verses', self.verses,
                           ['verse_id', 'work_id', 'section_id', 'verse_number', 'verse_type',
                            'verse_type_tamil', 'total_lines', 'sort_order'])

        # Insert lines
        if self.lines:
            print(f"  - {len(self.lines)} lines...")
            self._bulk_copy('lines', self.lines,
                           ['line_id', 'verse_id', 'line_number', 'line_text'])

        # Insert words
        if self.words:
            print(f"  - {len(self.words)} words...")
            self._bulk_copy('words', self.words,
                           ['word_id', 'line_id', 'word_position', 'word_text', 'sandhi_split'])

    def _bulk_copy(self, table_name, data, columns):
        """Use PostgreSQL COPY for bulk insert"""
        if not data:
            return

        buffer = io.StringIO()
        writer = csv.writer(buffer, delimiter='\t', quoting=csv.QUOTE_MINIMAL)

        for row in data:
            # Replace tabs and newlines in text fields to avoid CSV issues
            values = []
            for col in columns:
                val = row.get(col)
                if val is None:
                    values.append('\\N')
                elif isinstance(val, str):
                    # Replace tabs and newlines that could break COPY format
                    val = val.replace('\t', ' ').replace('\n', ' ').replace('\r', ' ')
                    values.append(val)
                else:
                    values.append(val)
            writer.writerow(values)

        buffer.seek(0)
        self.cursor.copy_from(buffer, table_name, columns=columns, null='\\N')

    def save_single_char_words(self, output_path: Path):
        """Save single-character words to JSON file for later review"""
        if not self.single_char_words:
            print("\n  No single-character words found")
            return

        print(f"\n  Saving {len(self.single_char_words)} single-character words to {output_path}")

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.single_char_words, f, ensure_ascii=False, indent=2)

        print(f"  ✓ Single-character words saved for later review")

    def close(self):
        """Close connection"""
        self.cursor.close()
        self.conn.close()


def main():
    import sys
    import io

    # Fix Windows console encoding for Tamil characters
    if sys.platform == 'win32':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

    # Get database URL
    db_connection = os.getenv('DATABASE_URL', "postgresql://postgres:password@localhost/tamil_literature")
    if len(sys.argv) > 1:
        db_connection = sys.argv[1]

    # Directory path
    script_dir = Path(__file__).parent
    project_dir = script_dir.parent
    tolkappiyam_dir = project_dir / "Tamil-Source-TamilConcordence" / "1_இலக்கண_நூல்கள்" / "தொல்காப்பியம்"
    single_char_output = script_dir / "tolkappiyam_single_char_words.json"

    print("="*70)
    print("Tolkappiyam Bulk Import - Fast 2-Phase Import")
    print("="*70)
    print(f"Database: {db_connection[:50]}...")
    print(f"Directory: {tolkappiyam_dir}")

    importer = TolkappiyamBulkImporter(db_connection)

    try:
        # Ensure work exists
        importer._ensure_work_exists()

        # Phase 1: Parse files
        if importer.parse_all_files(tolkappiyam_dir):
            # Phase 2: Bulk insert
            importer.bulk_insert()

            # Commit transaction
            importer.conn.commit()
            print("\n✓ Tolkappiyam import complete!")

            # Save single-character words for review
            importer.save_single_char_words(single_char_output)
        else:
            print("\n✗ Import skipped")

    except Exception as e:
        importer.conn.rollback()
        print(f"\n✗ Import failed: {e}")
        raise
    finally:
        importer.close()


if __name__ == '__main__':
    main()
