#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Thirukkural Bulk Import - Fast 2-phase import using PostgreSQL COPY
Phase 1: Parse text → Generate CSV files
Phase 2: Bulk COPY into database (1000x faster than INSERT)
"""

import json
import re
import psycopg2
from pathlib import Path
from typing import Dict, List
import csv
import io

class ThirukkuralBulkImporter:
    def __init__(self, db_connection_string: str):
        """Initialize importer"""
        self.conn = psycopg2.connect(db_connection_string)
        self.cursor = self.conn.cursor()

        # Load structure
        structure_file = Path(__file__).parent.parent / "data" / "thirukkural_structure.json"
        with open(structure_file, 'r', encoding='utf-8') as f:
            self.structure = json.load(f)

        self.kural_to_hierarchy = self._build_kural_mapping()
        self.work_id = None  # Will be assigned dynamically

        # Data containers
        self.sections = []
        self.verses = []
        self.lines = []
        self.words = []

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

        # Section cache to avoid duplicates
        self.section_cache = {}

    def _build_kural_mapping(self) -> Dict:
        """Build kural number to hierarchy mapping"""
        mapping = {}
        for paal in self.structure['structure']['paals']:
            for iyal in paal['iyals']:
                for adhikaram in iyal['adhikarams']:
                    start_kural, end_kural = adhikaram['kurals']
                    for kural_num in range(start_kural, end_kural + 1):
                        mapping[kural_num] = {
                            'paal': paal,
                            'iyal': iyal,
                            'adhikaram': adhikaram
                        }
        return mapping

    def _ensure_work_exists(self):
        """Ensure work entry exists"""
        work_name_english = 'Thirukkural'
        work_name_tamil = 'திருக்குறள்'

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

            print(f"  Creating Thirukkural work entry (ID: {self.work_id})...")
            self.cursor.execute("""
                INSERT INTO works (work_id, work_name, work_name_tamil, period, author, author_tamil, description)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                self.work_id, work_name_english, work_name_tamil,
                '4th - 5th century CE', 'Thiruvalluvar', 'திருவள்ளுவர்',
                'Classic Tamil text on ethics, politics, and love - 1,330 couplets'
            ))
            self.conn.commit()

    def _get_or_create_section_id(self, parent_id, level_type, section_number, section_name, section_name_tamil):
        """Get or create section, return section_id"""
        cache_key = (parent_id, level_type, section_number)

        if cache_key in self.section_cache:
            return self.section_cache[cache_key]

        # Create new section
        section_id = self.section_id
        self.section_id += 1

        # Calculate sort_order (simple sequential for now)
        sort_order = section_number

        self.sections.append({
            'section_id': section_id,
            'work_id': self.work_id,
            'parent_section_id': parent_id,
            'level_type': level_type,
            'level_type_tamil': level_type + '_tamil',
            'section_number': section_number,
            'section_name': section_name,
            'section_name_tamil': section_name_tamil,
            'sort_order': sort_order
        })

        self.section_cache[cache_key] = section_id
        return section_id

    def parse_file(self, text_file_path: str):
        """Phase 1: Parse text file into memory"""
        print(f"\nPhase 1: Parsing {text_file_path}...")

        with open(text_file_path, 'r', encoding='utf-8') as f:
            lines_text = f.readlines()

        current_adhikaram_section_id = None
        current_kural_num = None
        current_kural_lines = []

        verse_count = 0

        for line in lines_text:
            line = line.strip()
            if not line:
                continue

            # Check for adhikaram header
            adhikaram_match = re.match(r'^#\s*(\d+)\s+(.+)$', line)
            if adhikaram_match:
                # Save previous kural
                if current_kural_num and current_kural_lines:
                    self._add_kural(current_kural_num, current_kural_lines, current_adhikaram_section_id)
                    verse_count += 1

                current_kural_lines = []
                current_kural_num = None

                adhikaram_num = int(adhikaram_match.group(1))
                first_kural = (adhikaram_num - 1) * 10 + 1

                if first_kural in self.kural_to_hierarchy:
                    hierarchy = self.kural_to_hierarchy[first_kural]

                    # Create hierarchy
                    paal_id = self._get_or_create_section_id(
                        None, 'Paal',
                        hierarchy['paal']['paal_id'],
                        hierarchy['paal']['paal_name'],
                        hierarchy['paal']['paal_name_tamil']
                    )

                    iyal_id = self._get_or_create_section_id(
                        paal_id, 'Iyal',
                        hierarchy['iyal']['iyal_id'],
                        hierarchy['iyal']['iyal_name'],
                        hierarchy['iyal']['iyal_name_tamil']
                    )

                    current_adhikaram_section_id = self._get_or_create_section_id(
                        iyal_id, 'Adhikaram',
                        adhikaram_num,
                        hierarchy['adhikaram']['name'],
                        hierarchy['adhikaram']['tamil']
                    )
                continue

            # Check for kural number line
            kural_line_match = re.match(r'^(\d+)\.\s*(.+)$', line)
            if kural_line_match:
                if current_kural_num and current_kural_lines:
                    self._add_kural(current_kural_num, current_kural_lines, current_adhikaram_section_id)
                    verse_count += 1
                    if verse_count % 100 == 0:
                        print(f"  Parsed {verse_count} kurals...")

                current_kural_num = int(kural_line_match.group(1))
                current_kural_lines = [kural_line_match.group(2).strip()]
            else:
                if current_kural_num:
                    current_kural_lines.append(line)

        # Save last kural
        if current_kural_num and current_kural_lines:
            self._add_kural(current_kural_num, current_kural_lines, current_adhikaram_section_id)
            verse_count += 1

        print(f"✓ Phase 1 complete: Parsed {verse_count} kurals")
        print(f"  - Sections: {len(self.sections)}")
        print(f"  - Verses: {len(self.verses)}")
        print(f"  - Lines: {len(self.lines)}")
        print(f"  - Words: {len(self.words)}")

    def _add_kural(self, kural_num, kural_lines, section_id):
        """Add kural to memory"""
        verse_id = self.verse_id
        self.verse_id += 1

        self.verses.append({
            'verse_id': verse_id,
            'work_id': self.work_id,
            'section_id': section_id,
            'verse_number': kural_num,
            'verse_type': 'kural',
            'verse_type_tamil': 'குறள்',
            'total_lines': len(kural_lines),
            'sort_order': kural_num
        })

        for line_num, line_text in enumerate(kural_lines, start=1):
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

    def bulk_insert(self):
        """Phase 2: Bulk insert using COPY"""
        print("\nPhase 2: Bulk inserting into database...")

        # Insert sections
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
        print("✓ Phase 2 complete: All data inserted")

    def _bulk_copy(self, table_name, data, columns):
        """Use COPY for bulk insert"""
        if not data:
            return

        # Create StringIO buffer
        buffer = io.StringIO()
        writer = csv.writer(buffer, delimiter='\t')

        for row in data:
            writer.writerow([row.get(col) if row.get(col) is not None else '\\N' for col in columns])

        buffer.seek(0)

        # Use COPY command
        self.cursor.copy_from(buffer, table_name, columns=columns, null='\\N')

    def close(self):
        """Close connection"""
        self.cursor.close()
        self.conn.close()


def main():
    import sys
    import os

    # Get database URL
    db_connection = os.getenv('DATABASE_URL', "postgresql://postgres:password@localhost/tamil_literature")
    if len(sys.argv) > 1:
        db_connection = sys.argv[1]

    # Text file path
    script_dir = Path(__file__).parent
    project_dir = script_dir.parent
    text_file = project_dir / "Tamil-Source-TamilConcordence" / "3_சங்க_இலக்கியம்_பதினெண்கீழ்க்கணக்கு" / "திருக்குறள்.txt"

    print("="*70)
    print("Thirukkural Bulk Import - Fast 2-Phase Import")
    print("="*70)
    print(f"Database: {db_connection[:50]}...")
    print(f"Text file: {text_file.name}")

    importer = ThirukkuralBulkImporter(db_connection)

    try:
        importer._ensure_work_exists()
        importer.parse_file(str(text_file))
        importer.bulk_insert()
        print("\n✓ Import complete!")
    finally:
        importer.close()


if __name__ == '__main__':
    main()
