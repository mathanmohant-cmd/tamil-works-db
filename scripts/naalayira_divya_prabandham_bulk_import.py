#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Naalayira Divya Prabandham Bulk Import - Fast 2-phase import using PostgreSQL COPY
Phase 1: Parse text → Generate CSV files
Phase 2: Bulk COPY into database (1000x faster than INSERT)

This collection contains 24 works by 12 Alvars (Vaishnavite saints)
Spread across 4 files (முதல் ஆயிரம், இரண்டாம் ஆயிரம், மூன்றாம் ஆயிரம், நான்காம் ஆயிரம்)
"""

import re
import psycopg2
from pathlib import Path
from typing import Dict, List
import csv
import io
import sys
import os
from word_cleaning import split_and_clean_words

class NaalayiraDivyaPrabandhamBulkImporter:
    def __init__(self, db_connection_string: str):
        """Initialize importer"""
        self.conn = psycopg2.connect(db_connection_string)
        self.cursor = self.conn.cursor()

        self.work_ids = {}  # Map work_name to work_id

        # Data containers
        self.works = []
        self.sections = []
        self.verses = []
        self.lines = []
        self.words = []

        # Get existing max IDs from database
        self.cursor.execute("SELECT COALESCE(MAX(work_id), 0) FROM works")
        self.work_id = self.cursor.fetchone()[0] + 1

        self.cursor.execute("SELECT COALESCE(MAX(section_id), 0) FROM sections")
        self.section_id = self.cursor.fetchone()[0] + 1

        self.cursor.execute("SELECT COALESCE(MAX(verse_id), 0) FROM verses")
        self.verse_id = self.cursor.fetchone()[0] + 1

        self.cursor.execute("SELECT COALESCE(MAX(line_id), 0) FROM lines")
        self.line_id = self.cursor.fetchone()[0] + 1

        self.cursor.execute("SELECT COALESCE(MAX(word_id), 0) FROM words")
        self.word_id = self.cursor.fetchone()[0] + 1

        print(f"  Starting IDs: work={self.work_id}, section={self.section_id}, verse={self.verse_id}, line={self.line_id}, word={self.word_id}")

    def _create_default_section(self, work_id: int, work_name_tamil: str):
        """Create default root section for flat-structure works"""
        section_id = self.section_id
        self.section_id += 1

        self.sections.append({
            'section_id': section_id,
            'work_id': work_id,
            'parent_section_id': None,
            'level_type': 'Collection',
            'level_type_tamil': 'தொகுப்பு',
            'section_number': 1,
            'section_name': work_name_tamil,
            'section_name_tamil': work_name_tamil,
            'sort_order': 1
        })

        return section_id

    def _create_work(self, work_name: str, work_name_tamil: str, author: str, author_tamil: str, canonical_order: int):
        """Create a work entry in memory"""
        # Check if work already exists
        self.cursor.execute("SELECT work_id FROM works WHERE work_name = %s AND work_name_tamil = %s",
                          (work_name, work_name_tamil))
        existing = self.cursor.fetchone()

        if existing:
            work_id = existing[0]
            print(f"  [ERROR] Work {work_name_tamil} already exists (ID: {work_id})")
            return None

        # Use pre-allocated work_id and increment
        work_id = self.work_id
        self.work_id += 1

        self.works.append({
            'work_id': work_id,
            'work_name': work_name,
            'work_name_tamil': work_name_tamil,
            'author': author,
            'author_tamil': author_tamil,
            'period': '7th-9th century CE',
            'canonical_order': canonical_order
        })

        print(f"  Created work: {work_name_tamil} (ID: {work_id}, Canonical: {canonical_order})")

        # Create default section for flat-structure works
        section_id = self._create_default_section(work_id, work_name_tamil)

        self.work_ids[work_name_tamil] = work_id
        return work_id, section_id

    def parse_file(self, text_file_path: str, file_section_name: str):
        """Phase 1: Parse text file into memory"""
        print(f"\nParsing {Path(text_file_path).name}...")

        with open(text_file_path, 'r', encoding='utf-8') as f:
            lines_text = f.readlines()

        current_work_id = None
        current_section_id = None
        current_work_name = None
        current_author = None
        current_verse_lines = []
        current_verse_num = None
        verse_count = 0
        work_position = len(self.work_ids) + 1
        base_canonical_order = 301  # Starting canonical order for NDP works
        section_map = {}  # Map work_id to section_id

        for line in lines_text:
            line = line.strip()
            if not line or line == 'மேல்':
                continue

            # Check for work header: @[Author] - [Work Name]
            work_match = re.match(r'^@(.+?)\s*-\s*(.+)$', line)
            if work_match:
                # Save previous verse if exists
                if current_verse_num and current_verse_lines and current_work_id and current_section_id:
                    self._add_verse(current_work_id, current_section_id, current_verse_num, current_verse_lines)
                    verse_count += 1

                current_verse_lines = []
                current_verse_num = None

                current_author = work_match.group(1).strip()
                current_work_name = work_match.group(2).strip()

                # Create work key
                work_key = f"{current_author} - {current_work_name}"

                if work_key not in self.work_ids:
                    # Create new work
                    result = self._create_work(
                        work_name=current_work_name,
                        work_name_tamil=current_work_name,
                        author=current_author.replace('ஆழ்வார்', 'Alvar').replace('ஆண்டாள்', 'Andal'),
                        author_tamil=current_author,
                        canonical_order=base_canonical_order + work_position - 1
                    )
                    if result:
                        work_id, section_id = result
                        self.work_ids[work_key] = work_id
                        section_map[work_id] = section_id
                        current_work_id = work_id
                        current_section_id = section_id
                        print(f"    Created work: {current_work_name} by {current_author} (ID: {work_id})")
                        work_position += 1
                    else:
                        current_work_id = None
                        current_section_id = None
                else:
                    current_work_id = self.work_ids[work_key]
                    current_section_id = section_map.get(current_work_id)

                continue

            # Check for verse number
            verse_match = re.match(r'^#(\d+)$', line)
            if verse_match:
                # Save previous verse
                if current_verse_num and current_verse_lines and current_work_id and current_section_id:
                    self._add_verse(current_work_id, current_section_id, current_verse_num, current_verse_lines)
                    verse_count += 1
                    if verse_count % 100 == 0:
                        print(f"      Parsed {verse_count} verses...")

                current_verse_num = int(verse_match.group(1))
                current_verse_lines = []
                continue

            # Regular verse line
            if current_verse_num is not None:
                # Clean line
                cleaned = line.replace('…', '').strip()
                if cleaned:
                    current_verse_lines.append(cleaned)

        # Save last verse
        if current_verse_num and current_verse_lines and current_work_id and current_section_id:
            self._add_verse(current_work_id, current_section_id, current_verse_num, current_verse_lines)
            verse_count += 1

        print(f"  [OK] Parsed {verse_count} verses from {len(self.work_ids)} works")

    def _add_verse(self, work_id, section_id, verse_num, verse_lines):
        """Add verse to memory"""
        verse_id = self.verse_id
        self.verse_id += 1

        self.verses.append({
            'verse_id': verse_id,
            'work_id': work_id,
            'section_id': section_id,
            'verse_number': verse_num,
            'verse_type': 'pasuram',
            'verse_type_tamil': 'பாசுரம்',
            'total_lines': len(verse_lines),
            'sort_order': verse_num
        })

        for line_num, line_text in enumerate(verse_lines, start=1):
            line_id = self.line_id
            self.line_id += 1

            # Clean line text: remove trailing numbers, normalize whitespace
            cleaned_line = re.sub(r'\s+\d+\s*$', '', line_text)  # Remove trailing numbers
            cleaned_line = re.sub(r'\s+', ' ', cleaned_line)  # Normalize whitespace
            cleaned_line = cleaned_line.strip()

            self.lines.append({
                'line_id': line_id,
                'verse_id': verse_id,
                'line_number': line_num,
                'line_text': cleaned_line
            })

            # Parse words
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

    def bulk_insert(self):
        """Phase 2: Bulk insert using COPY"""
        print("\nPhase 2: Bulk inserting into database...")

        # Insert works
        if self.works:
            print(f"  Inserting {len(self.works)} works...")
            self._bulk_copy('works', self.works,
                           ['work_id', 'work_name', 'work_name_tamil', 'period', 'author',
                            'author_tamil', 'canonical_order'])

        # Insert sections
        if self.sections:
            print(f"  Inserting {len(self.sections)} sections...")
            self._bulk_copy('sections', self.sections,
                           ['section_id', 'work_id', 'parent_section_id', 'level_type', 'level_type_tamil',
                            'section_number', 'section_name', 'section_name_tamil', 'sort_order'])

        # Insert verses
        print(f"  Inserting {len(self.verses)} verses...")
        self._bulk_copy('verses', self.verses,
                       ['verse_id', 'work_id', 'section_id', 'verse_number', 'verse_type',
                        'verse_type_tamil', 'total_lines', 'sort_order'])

        # Insert lines
        print(f"  Inserting {len(self.lines)} lines...")
        self._bulk_copy('lines', self.lines,
                       ['line_id', 'verse_id', 'line_number', 'line_text'])

        # Insert words
        print(f"  Inserting {len(self.words)} words...")
        self._bulk_copy('words', self.words,
                       ['word_id', 'line_id', 'word_position', 'word_text', 'sandhi_split'])

        self.conn.commit()
        print("[OK] Phase 2 complete: All data inserted")

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
    # Get database URL
    db_connection = os.getenv('DATABASE_URL', "postgresql://postgres:postgres@localhost/tamil_literature")
    if len(sys.argv) > 1:
        db_connection = sys.argv[1]

    # Text file paths
    script_dir = Path(__file__).parent
    project_dir = script_dir.parent
    base_dir = project_dir / "Tamil-Source-TamilConcordence" / "6_பக்தி இலக்கியம்"

    files = [
        (base_dir / "13.நாலாயிரத் திவ்விய பிரபந்தம்-முதல் ஆயிரம்.txt", "முதல் ஆயிரம்"),
        (base_dir / "14.நாலாயிரத் திவ்விய பிரபந்தம்-இரண்டாம் ஆயிரம்.txt", "இரண்டாம் ஆயிரம்"),
        (base_dir / "15.நாலாயிரத் திவ்விய பிரபந்தம்-மூன்றாம் ஆயிரம்.txt", "மூன்றாம் ஆயிரம்"),
        (base_dir / "16.நாலாயிரத் திவ்விய பிரபந்தம்-நான்காம் ஆயிரம்.txt", "நான்காம் ஆயிரம்"),
    ]

    print("="*70)
    print("Naalayira Divya Prabandham Bulk Import - Fast 2-Phase Import")
    print("="*70)
    print(f"Database: {db_connection[:50]}...")
    print(f"Files: 4 (முதல் ஆயிரம் through நான்காம் ஆயிரம்)")

    importer = NaalayiraDivyaPrabandhamBulkImporter(db_connection)

    try:
        # Parse all files
        for file_path, section_name in files:
            if file_path.exists():
                importer.parse_file(str(file_path), section_name)
            else:
                print(f"  [ERROR] File not found: {file_path}")

        # Bulk insert
        importer.bulk_insert()

        print("\n" + "="*70)
        print("[OK] Import complete!")
        print(f"  - Works created: {len(importer.work_ids)}")
        print(f"  - Verses imported: {len(importer.verses)}")
        print(f"  - Lines imported: {len(importer.lines)}")
        print(f"  - Words imported: {len(importer.words)}")
        print("="*70)

    except Exception as e:
        print(f"\n[ERROR] Error: {e}")
        import traceback
        traceback.print_exc()
        importer.conn.rollback()
    finally:
        importer.close()


if __name__ == '__main__':
    main()
