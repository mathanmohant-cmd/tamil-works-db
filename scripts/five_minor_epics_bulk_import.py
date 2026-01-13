#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File Minor Epics (ஐஞ்சிறுகாப்பியங்கள்) Bulk Import
Fast 2-phase import using PostgreSQL COPY

Phase 1: Parse text → Build data structures in memory
Phase 2: Bulk COPY into database (1000x faster than INSERT)

Collection ID: 324 (ஐஞ்சிறுகாப்பியங்கள் - File Minor Epics)

Works (5 Jain minor epics):
1. உதயணகுமார காவியம் (Udayana Kumara Kaviyam) - Kandiyar, 3rd century CE
2. நாககுமார காவியம் (Nagakumara Kaviyam) - Unknown, 5th-10th century CE
3. யசோதர காவியம் (Yasodara Kaviyam) - Unknown, 5th-10th century CE
4. சூளாமணி (Choolamani) - Tholamozhithevar, before 10th century CE
5. நீலகேசி (Nilakesi) - Unknown, 10th century CE

Structure:
- &N Work identifier (N=1-5)
- @N. Kandam/Sarrukkam (Level 1 sections)
- ** Topic/Subsection headings (Level 2 sections)
- #N Verse markers
- 4 lines per verse (typical)
"""

import re
import psycopg2
from pathlib import Path
import csv
import io
import sys
import os
from word_cleaning import split_and_clean_words

# Work metadata for all 5 works
WORK_METADATA = {
    1: {
        'work_name': 'Udayana Kumara Kaviyam',
        'work_name_tamil': 'உதயணகுமார காவியம்',
        'author': 'Kandiyar',
        'author_tamil': 'கண்டியார்',
        'period': '3rd century CE',
        'canonical_order': 324001,
        'position_in_collection': 1,
        'file': '1. உதயணகுமார காவியம்.txt'
    },
    2: {
        'work_name': 'Nagakumara Kaviyam',
        'work_name_tamil': 'நாககுமார காவியம்',
        'author': 'Unknown',
        'author_tamil': 'அறியப்படாத ஆசிரியர்',
        'period': '5th-10th century CE',
        'canonical_order': 324002,
        'position_in_collection': 2,
        'file': '2. நாககுமார காவியம்.txt'
    },
    3: {
        'work_name': 'Yasodara Kaviyam',
        'work_name_tamil': 'யசோதர காவியம்',
        'author': 'Unknown',
        'author_tamil': 'அறியப்படாத ஆசிரியர்',
        'period': '5th-10th century CE',
        'canonical_order': 324003,
        'position_in_collection': 3,
        'file': '3. யசோதர காவியம்.txt'
    },
    4: {
        'work_name': 'Choolamani',
        'work_name_tamil': 'சூளாமணி',
        'author': 'Tholamozhithevar',
        'author_tamil': 'தொலமொழித்தேவர்',
        'period': 'Before 10th century CE',
        'canonical_order': 324004,
        'position_in_collection': 4,
        'file': '4. சூளாமணி.txt'
    },
    5: {
        'work_name': 'Nilakesi',
        'work_name_tamil': 'நீலகேசி',
        'author': 'Unknown',
        'author_tamil': 'அறியப்படாத ஆசிரியர்',
        'period': '10th century CE',
        'canonical_order': 324005,
        'position_in_collection': 5,
        'file': '5. நீலகேசி.txt'
    }
}


class SitrIlakkiyangalBulkImporter:
    """Import all 5 Jain minor epics using 2-phase bulk COPY pattern"""

    def __init__(self, db_connection_string: str):
        """Initialize importer and query MAX IDs from ALL tables"""
        self.conn = psycopg2.connect(db_connection_string)
        self.cursor = self.conn.cursor()
        self.collection_id = 324

        # Data containers
        self.works = []
        self.sections = []
        self.verses = []
        self.lines = []
        self.words = []
        self.work_collections = []

        # Query MAX IDs from ALL tables ONCE at initialization
        # CRITICAL: Query once, increment manually (lessons from 2025-12-05)
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

        print(f"  Starting IDs: work={self.work_id}, section={self.section_id}, "
              f"verse={self.verse_id}, line={self.line_id}, word={self.word_id}")

        # Track current parsing state
        self.current_work_id = None
        self.current_level1_section = None  # @ section
        self.current_level2_section = None  # ** section
        self.level2_section_counter = {}  # Track section numbers per Level 1 section

    def _ensure_collection_exists(self):
        """Create collection 324 if missing"""
        # Check if collection exists
        self.cursor.execute("SELECT collection_id FROM collections WHERE collection_id = %s",
                          (self.collection_id,))
        existing = self.cursor.fetchone()

        if not existing:
            print(f"  Creating ஐஞ்சிறுகாப்பியங்கள் collection (ID: {self.collection_id})...")
            self.cursor.execute("""
                INSERT INTO collections (
                    collection_id, collection_name, collection_name_tamil,
                    collection_type, description, parent_collection_id, sort_order
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                self.collection_id,
                'File Minor Epics',
                'ஐஞ்சிறுகாப்பியங்கள்',
                'period',
                'Five Jain minor epics from the Sangam and post-Sangam period (3rd-10th century CE)',
                1,  # Parent: தமிழ் இலக்கியம் (designated filter collection)
                4   # After Thirumurai=1, NDPD=2, Devotional=3
            ))
            print(f"  [OK] Collection created (will commit with bulk data)")
        else:
            print(f"  Found existing ஐஞ்சிறுகாப்பியங்கள் collection (ID: {self.collection_id})")

    def _create_work(self, work_num: int) -> int:
        """Create work entry from WORK_METADATA and return work_id"""
        if work_num not in WORK_METADATA:
            raise ValueError(f"Invalid work number: {work_num}")

        metadata = WORK_METADATA[work_num]

        # Check if work already exists
        self.cursor.execute("SELECT work_id FROM works WHERE work_name = %s AND work_name_tamil = %s",
                          (metadata['work_name'], metadata['work_name_tamil']))
        existing = self.cursor.fetchone()

        if existing:
            print(f"  [ERROR] Work {metadata['work_name_tamil']} already exists (ID: {existing[0]})")
            return None

        # Use pre-allocated work_id and increment
        work_id = self.work_id
        self.work_id += 1

        self.works.append({
            'work_id': work_id,
            'work_name': metadata['work_name'],
            'work_name_tamil': metadata['work_name_tamil'],
            'author': metadata['author'],
            'author_tamil': metadata['author_tamil'],
            'period': metadata['period'],
            'canonical_order': metadata['canonical_order']
        })

        # Link work to collection 324
        self.work_collections.append({
            'work_id': work_id,
            'collection_id': self.collection_id,
            'position_in_collection': metadata['position_in_collection']
        })

        print(f"  Created work: {metadata['work_name_tamil']} (ID: {work_id}, Canonical: {metadata['canonical_order']})")
        return work_id

    def _add_section(self, work_id: int, parent_id: int or None,
                    level_type: str, level_type_tamil: str,
                    section_num: int, section_name: str, section_name_tamil: str = None) -> int:
        """Add section to in-memory list and return section_id"""
        section_id = self.section_id
        self.section_id += 1  # Manual increment

        # Use section_name for Tamil if not provided separately
        if section_name_tamil is None:
            section_name_tamil = section_name

        self.sections.append({
            'section_id': section_id,
            'work_id': work_id,
            'parent_section_id': parent_id,
            'level_type': level_type,
            'level_type_tamil': level_type_tamil,
            'section_number': section_num,
            'section_name': section_name,
            'section_name_tamil': section_name_tamil,
            'sort_order': section_num
        })

        return section_id

    def _add_verse(self, work_id: int, section_id: int, verse_num: int, verse_lines: list):
        """Add verse, lines, and words to in-memory lists"""
        if not verse_lines:
            return

        # Create verse
        verse_id = self.verse_id
        self.verse_id += 1

        self.verses.append({
            'verse_id': verse_id,
            'work_id': work_id,
            'section_id': section_id,
            'verse_number': verse_num,
            'verse_type': 'Verse',
            'verse_type_tamil': 'பாடல்',
            'total_lines': len(verse_lines),
            'sort_order': verse_num
        })

        # Create lines and words
        for line_num, line_text in enumerate(verse_lines, start=1):
            line_id = self.line_id
            self.line_id += 1

            # Clean line text (remove markers)
            cleaned_line = line_text.strip()

            self.lines.append({
                'line_id': line_id,
                'verse_id': verse_id,
                'line_number': line_num,
                'line_text': cleaned_line
            })

            # Split into words
            words = split_and_clean_words(cleaned_line)
            for word_position, word_text in enumerate(words, start=1):
                word_id = self.word_id
                self.word_id += 1

                self.words.append({
                    'word_id': word_id,
                    'line_id': line_id,
                    'word_position': word_position,
                    'word_text': word_text,
                    'sandhi_split': None
                })

    def parse_file(self, file_path: str, work_num: int):
        """
        Parse one work file (Phase 1: Parse into memory)

        Structure:
        - &N Work identifier
        - @N. Level 1 section (Kandam)
        - ** Level 2 section (Topic) under current Level 1
        - #N Verse marker
        - Lines accumulate until blank line or next marker
        """
        print(f"\nParsing File {work_num}: {Path(file_path).name}")

        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        # State tracking
        current_work_id = None
        current_level1_section = None
        current_level2_section = None
        current_verse_num = None
        current_verse_lines = []
        level2_counter = 0  # Counter for ** sections within current @ section

        for line in lines:
            line = line.strip()

            # Empty line - triggers verse save (but verse save also happens on markers)
            if not line:
                if current_verse_num is not None and current_verse_lines:
                    self._add_verse(current_work_id,
                                  current_level2_section if current_level2_section else current_level1_section,
                                  current_verse_num, current_verse_lines)
                    current_verse_num = None
                    current_verse_lines = []
                continue

            # &N Work identifier
            if line.startswith('&'):
                # Save previous verse
                if current_verse_num is not None and current_verse_lines:
                    self._add_verse(current_work_id,
                                  current_level2_section if current_level2_section else current_level1_section,
                                  current_verse_num, current_verse_lines)

                # Extract work number from &N pattern (may or may not have dot)
                match = re.match(r'&(\d+)\.?\s*(.*)', line)
                if match:
                    file_work_num = int(match.group(1))
                    if file_work_num != work_num:
                        print(f"  [WARNING] File work number {file_work_num} doesn't match expected {work_num}")

                    # Create work
                    current_work_id = self._create_work(work_num)
                    current_level1_section = None
                    current_level2_section = None
                    current_verse_num = None
                    current_verse_lines = []
                    level2_counter = 0

            # @N. Level 1 section (Kandam)
            elif line.startswith('@'):
                # Save previous verse
                if current_verse_num is not None and current_verse_lines:
                    self._add_verse(current_work_id,
                                  current_level2_section if current_level2_section else current_level1_section,
                                  current_verse_num, current_verse_lines)
                    current_verse_num = None
                    current_verse_lines = []

                # Extract section number and name from @N. pattern
                match = re.match(r'@(\d+)\.\s*(.*)', line)
                if match:
                    section_num = int(match.group(1))
                    section_name = match.group(2).strip()

                    current_level1_section = self._add_section(
                        current_work_id,
                        parent_id=None,
                        level_type='Kandam',
                        level_type_tamil='காண்டம்',
                        section_num=section_num,
                        section_name=section_name,
                        section_name_tamil=section_name
                    )
                    current_level2_section = None  # Reset Level 2
                    level2_counter = 0  # Reset counter for new Level 1 section

            # ** Level 2 section (Topic)
            elif line.startswith('**'):
                # Save previous verse
                if current_verse_num is not None and current_verse_lines:
                    self._add_verse(current_work_id,
                                  current_level2_section if current_level2_section else current_level1_section,
                                  current_verse_num, current_verse_lines)
                    current_verse_num = None
                    current_verse_lines = []

                # Extract topic name (remove ** markers)
                section_name = line.replace('**', '').strip()
                level2_counter += 1

                current_level2_section = self._add_section(
                    current_work_id,
                    parent_id=current_level1_section,
                    level_type='Topic',
                    level_type_tamil='தலைப்பு',
                    section_num=level2_counter,
                    section_name=section_name,
                    section_name_tamil=section_name
                )

            # #N Verse marker
            elif line.startswith('#'):
                # Save previous verse
                if current_verse_num is not None and current_verse_lines:
                    self._add_verse(current_work_id,
                                  current_level2_section if current_level2_section else current_level1_section,
                                  current_verse_num, current_verse_lines)

                # Extract verse number
                match = re.match(r'#(\d+)', line)
                if match:
                    current_verse_num = int(match.group(1))
                    current_verse_lines = []

            # Regular line (verse content)
            elif current_verse_num is not None:
                # Accumulate verse line
                current_verse_lines.append(line)

        # Save final verse if any
        if current_verse_num is not None and current_verse_lines:
            self._add_verse(current_work_id,
                          current_level2_section if current_level2_section else current_level1_section,
                          current_verse_num, current_verse_lines)

    def bulk_insert(self):
        """
        Phase 2: Bulk insert using PostgreSQL COPY

        Order (critical for foreign keys):
        1. works
        2. work_collections
        3. sections
        4. verses
        5. lines
        6. words
        """
        print("\nPhase 2: Bulk inserting into database...")

        # 1. Insert works
        print(f"  Inserting {len(self.works)} works...")
        self._bulk_copy('works', self.works,
                       ['work_id', 'work_name', 'work_name_tamil', 'author',
                        'author_tamil', 'period', 'canonical_order'])

        # 2. Insert work_collections
        print(f"  Inserting {len(self.work_collections)} work-collection links...")
        self._bulk_copy('work_collections', self.work_collections,
                       ['work_id', 'collection_id', 'position_in_collection'])

        # 3. Insert sections
        print(f"  Inserting {len(self.sections)} sections...")
        self._bulk_copy('sections', self.sections,
                       ['section_id', 'work_id', 'parent_section_id', 'level_type',
                        'level_type_tamil', 'section_number', 'section_name',
                        'section_name_tamil', 'sort_order'])

        # 4. Insert verses
        print(f"  Inserting {len(self.verses)} verses...")
        self._bulk_copy('verses', self.verses,
                       ['verse_id', 'work_id', 'section_id', 'verse_number',
                        'verse_type', 'verse_type_tamil', 'total_lines', 'sort_order'])

        # 5. Insert lines
        print(f"  Inserting {len(self.lines)} lines...")
        self._bulk_copy('lines', self.lines,
                       ['line_id', 'verse_id', 'line_number', 'line_text'])

        # 6. Insert words
        print(f"  Inserting {len(self.words)} words...")
        self._bulk_copy('words', self.words,
                       ['word_id', 'line_id', 'word_position', 'word_text', 'sandhi_split'])

        # Single commit after all data inserted
        self.conn.commit()
        print("✓ Phase 2 complete: All data inserted")

    def _bulk_copy(self, table_name: str, data: list, columns: list):
        """
        Copy data to table using psycopg2.cursor.copy_from()
        Use '\\N' for NULL values, tab-delimited CSV format
        """
        if not data:
            return

        # Create StringIO buffer
        buffer = io.StringIO()
        writer = csv.writer(buffer, delimiter='\t')

        for row in data:
            writer.writerow([row.get(col) if row.get(col) is not None else '\\N'
                           for col in columns])

        buffer.seek(0)

        # Use COPY command
        self.cursor.copy_from(buffer, table_name, columns=columns, null='\\N')

    def close(self):
        """Close database connection"""
        self.cursor.close()
        self.conn.close()


def print_header():
    """Print banner"""
    print("=" * 70)
    print("ஐஞ்சிறுகாப்பியங்கள் (File Minor Epics) - Bulk Import")
    print("Collection 324: Five Jain Minor Epics (3rd-10th century CE)")
    print("=" * 70)


def print_summary(importer):
    """Print import summary"""
    print("\n" + "=" * 70)
    print("IMPORT SUMMARY")
    print("=" * 70)
    print(f"  Works: {len(importer.works)}")
    print(f"  Sections: {len(importer.sections)}")
    print(f"  Verses: {len(importer.verses)}")
    print(f"  Lines: {len(importer.lines)}")
    print(f"  Words: {len(importer.words)}")
    print("=" * 70)


def main():
    """
    Main execution:
    1. Get database URL
    2. Initialize importer
    3. Create collection 324
    4. Parse all 5 files
    5. Bulk insert
    6. Print summary
    """
    # Get database URL from command line or environment
    if len(sys.argv) > 1:
        db_url = sys.argv[1]
    else:
        db_url = os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@localhost/tamil_literature')

    print_header()

    # Base directory for source files
    base_dir = Path(__file__).parent.parent / 'Tamil-Source-TamilConcordence' / '9_ஐஞ்சிறுகாப்பியங்கள்'

    # Check if directory exists
    if not base_dir.exists():
        print(f"\n✗ Error: Source directory not found: {base_dir}")
        print("  Please ensure Tamil-Source-TamilConcordence/9_ஐஞ்சிறுகாப்பியங்கள்/ exists")
        sys.exit(1)

    try:
        # Initialize importer
        importer = SitrIlakkiyangalBulkImporter(db_url)

        # Create collection 324
        importer._ensure_collection_exists()

        # Parse all 5 files in order
        for work_num in range(1, 6):
            file_path = base_dir / WORK_METADATA[work_num]['file']

            if not file_path.exists():
                print(f"  ✗ File not found: {file_path}")
                continue

            importer.parse_file(str(file_path), work_num)

        # Bulk insert
        importer.bulk_insert()

        # Print summary
        print_summary(importer)

        print("\n✓ Import complete! All 5 works imported successfully.")
        print("\nVerification queries:")
        print("  psql -U postgres -d tamil_literature")
        print("  SELECT work_name_tamil FROM works WHERE work_id IN")
        print("    (SELECT work_id FROM work_collections WHERE collection_id = 324);")

    except psycopg2.IntegrityError as e:
        print(f"\n✗ Database integrity error: {e}")
        print("  Possible causes:")
        print("  - Work already exists (run delete script first)")
        print("  - Duplicate IDs (check ID allocation logic)")
        importer.conn.rollback()
        sys.exit(1)

    except FileNotFoundError as e:
        print(f"\n✗ File error: {e}")
        print("  Check Tamil-Source-TamilConcordence/9_ஐஞ்சிறுகாப்பியங்கள்/ directory")
        sys.exit(1)

    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        importer.conn.rollback()
        sys.exit(1)

    finally:
        importer.close()


if __name__ == '__main__':
    main()
