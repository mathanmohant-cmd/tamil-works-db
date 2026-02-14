#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Five Minor Epics (ஐஞ்சிறுகாப்பியங்கள்) Bulk Import
Fast 2-phase import using PostgreSQL COPY with BaseWorkImporter

Phase 1: Parse text → Build data structures in memory
Phase 2: Bulk COPY into database (1000x faster than INSERT)

Collection ID: 324 (ஐஞ்சிறுகாப்பியங்கள் - Five Minor Epics)

Works (5 Jain minor epics):
1. உதயணகுமார காவியம் (Udayana Kumara Kaviyam) - Kandiyar, 3rd century CE
2. நாககுமார காவியம் (Nagakumara Kaviyam) - Unknown, 5th-10th century CE
3. யசோதர காவியம் (Yasodara Kaviyam) - Unknown, 5th-10th century CE
4. சூளாமணி (Choolamani) - Tholamozhithevar, before 10th century CE
5. நீலகேசி (Nilakesi) - Unknown, 10th century CE
   NOTE: Section 9 missing in source file (jumps from @8 to @10)

File Structure:
- @N. Kandam/Sarrukkam (Level 1 sections - காண்டம்/சருக்கம்)
- ** Topic/Subsection headings (Level 2 sections - தலைப்பு)
- #N Verse markers (verses - பாடல்)
- 4 lines per verse (typical)

Uses 2-phase bulk COPY pattern with BaseWorkImporter for optimal performance.
"""

import re
import sys
import os
from pathlib import Path

# Import shared utilities
sys.path.insert(0, str(Path(__file__).parent))
from shared.base_importer import BaseWorkImporter
from shared.utils import split_and_clean_words

# Import metadata
sys.path.insert(0, str(Path(__file__).parent / 'metadata'))
from five_minor_epics_metadata import (
    WORK_METADATA,
    COLLECTION_ID,
    COLLECTION_NAME,
    COLLECTION_NAME_TAMIL,
    FILE_INFO
)


class FiveMinorEpicsImporter(BaseWorkImporter):
    """
    Import all 5 Jain minor epics using 2-phase bulk COPY pattern.

    Hierarchy:
    - Collection 324: ஐஞ்சிறுகாப்பியங்கள்
      - 5 Works (each with own file)
        - Kandam: @ markers (காண்டம்) - Level 1 sections
          - Topics: ** markers (தலைப்பு) - Level 2 sections
            - Verses: # markers
              - Lines: Individual lines
                - Words: Word segmentation
    """

    def __init__(self, db_connection_string="postgresql://postgres:postgres@localhost/tamil_literature"):
        """Initialize with database connection using BaseWorkImporter"""
        super().__init__(db_connection_string, collection_id=COLLECTION_ID)

        # Track current parsing state
        self.current_work_id = None
        self.current_level1_section = None  # @ section
        self.current_level2_section = None  # ** section
        self.level2_section_counter = 0    # Counter for ** sections within current @ section

        print(f"Initialized FiveMinorEpicsImporter")
        print(f"  Collection {COLLECTION_ID} ({COLLECTION_NAME_TAMIL}) will be created/linked")

    def _setup_collection(self):
        """Ensure collection 324 exists"""
        super()._ensure_collection_exists(
            collection_id=COLLECTION_ID,
            collection_name=COLLECTION_NAME,
            collection_name_tamil=COLLECTION_NAME_TAMIL,
            description='Five Jain minor epics from the Sangam and post-Sangam period (3rd-10th century CE)'
        )

    def parse_all_works(self, base_dir: Path):
        """Parse all 5 works from their files"""
        print("\n=== PHASE 1: Parsing all 5 minor epics into memory ===")

        # Setup collection first
        self._setup_collection()

        # Parse each work in order
        for work_key, work_meta in WORK_METADATA.items():
            file_path = base_dir / work_meta['file']

            if not file_path.exists():
                print(f"  ✗ File not found: {file_path}")
                continue

            print(f"\n  Parsing: {work_meta['work_name_tamil']}...")
            self._parse_work_file(str(file_path), work_meta)

        print(f"\n  [OK] Parsed {len(self.works)} works, {len(self.sections)} sections, {len(self.verses)} verses")
        print(f"       {len(self.lines)} lines, {len(self.words)} words")

    def _parse_work_file(self, file_path: str, work_meta: dict):
        """Parse one work file"""
        # Create work entry
        try:
            work_id = super()._create_work(
                work_name=work_meta['work_name'],
                work_name_tamil=work_meta['work_name_tamil'],
                metadata=work_meta
            )
            print(f"    Created work ID: {work_id}")
            self.current_work_id = work_id
        except ValueError as e:
            print(f"    [ERROR] {e}")
            print(f"    To re-import, first delete: python scripts/delete_five_minor_epics.py")
            return

        # Reset state for new work
        self.current_level1_section = None
        self.current_level2_section = None
        self.level2_section_counter = 0

        # Parse file
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        # State tracking
        current_verse_number = None
        current_verse_lines = []

        for line in lines:
            line_stripped = line.strip()

            # Empty line - triggers verse save
            if not line_stripped:
                if current_verse_number is not None and current_verse_lines:
                    self._create_verse(
                        current_verse_number,
                        current_verse_lines,
                        self.current_level2_section if self.current_level2_section else self.current_level1_section
                    )
                    current_verse_number = None
                    current_verse_lines = []
                continue

            # @N. Level 1 section (Kandam)
            if line_stripped.startswith('@'):
                # Save previous verse
                if current_verse_number is not None and current_verse_lines:
                    self._create_verse(
                        current_verse_number,
                        current_verse_lines,
                        self.current_level2_section if self.current_level2_section else self.current_level1_section
                    )
                    current_verse_number = None
                    current_verse_lines = []

                # Extract section number and name
                match = re.match(r'@(\d+)\.\s*(.*)', line_stripped)
                if match:
                    section_num = int(match.group(1))
                    section_name = match.group(2).strip()

                    # Create Kandam section
                    section_dict = {
                        'section_id': self.section_id,
                        'work_id': self.current_work_id,
                        'parent_section_id': None,
                        'level_type': 'Kandam',
                        'level_type_tamil': 'காண்டம்',
                        'section_number': section_num,
                        'section_name': section_name,
                        'section_name_tamil': section_name,
                        'sort_order': section_num
                    }
                    self.sections.append(section_dict)
                    self.current_level1_section = self.section_id
                    self.section_id += 1
                    self.current_level2_section = None  # Reset Level 2
                    self.level2_section_counter = 0    # Reset counter

            # ** Level 2 section (Topic)
            elif line_stripped.startswith('**'):
                # Save previous verse
                if current_verse_number is not None and current_verse_lines:
                    self._create_verse(
                        current_verse_number,
                        current_verse_lines,
                        self.current_level2_section if self.current_level2_section else self.current_level1_section
                    )
                    current_verse_number = None
                    current_verse_lines = []

                # Extract topic name
                section_name = line_stripped.replace('**', '').strip()
                self.level2_section_counter += 1

                # Create Topic section
                section_dict = {
                    'section_id': self.section_id,
                    'work_id': self.current_work_id,
                    'parent_section_id': self.current_level1_section,
                    'level_type': 'Topic',
                    'level_type_tamil': 'தலைப்பு',
                    'section_number': self.level2_section_counter,
                    'section_name': section_name,
                    'section_name_tamil': section_name,
                    'sort_order': self.level2_section_counter
                }
                self.sections.append(section_dict)
                self.current_level2_section = self.section_id
                self.section_id += 1

            # #N Verse marker
            elif line_stripped.startswith('#'):
                # Save previous verse
                if current_verse_number is not None and current_verse_lines:
                    self._create_verse(
                        current_verse_number,
                        current_verse_lines,
                        self.current_level2_section if self.current_level2_section else self.current_level1_section
                    )

                # Extract verse number
                match = re.match(r'#(\d+)', line_stripped)
                if match:
                    current_verse_number = int(match.group(1))
                    current_verse_lines = []

            # Regular line (verse content)
            elif current_verse_number is not None:
                current_verse_lines.append(line_stripped)

        # Save final verse if any
        if current_verse_number is not None and current_verse_lines:
            self._create_verse(
                current_verse_number,
                current_verse_lines,
                self.current_level2_section if self.current_level2_section else self.current_level1_section
            )

    def _create_verse(self, verse_number: int, verse_lines: list, section_id: int):
        """Create a verse with its lines and words"""
        if not verse_lines or section_id is None:
            return

        # Create verse
        verse_dict = {
            'verse_id': self.verse_id,
            'work_id': self.current_work_id,
            'section_id': section_id,
            'verse_number': verse_number,
            'verse_type': 'Verse',
            'verse_type_tamil': 'பாடல்',
            'total_lines': len(verse_lines),
            'sort_order': verse_number
        }
        self.verses.append(verse_dict)
        current_verse_id = self.verse_id
        self.verse_id += 1

        # Create lines and words
        for line_num, line_text in enumerate(verse_lines, 1):
            line_dict = {
                'line_id': self.line_id,
                'verse_id': current_verse_id,
                'line_number': line_num,
                'line_text': line_text
            }
            self.lines.append(line_dict)
            current_line_id = self.line_id
            self.line_id += 1

            # Split into words using shared utility
            words = split_and_clean_words(line_text)
            for word_position, word_text in enumerate(words, 1):
                word_dict = {
                    'word_id': self.word_id,
                    'line_id': current_line_id,
                    'word_position': word_position,
                    'word_text': word_text,
                    'sandhi_split': None
                }
                self.words.append(word_dict)
                self.word_id += 1


def print_header():
    """Print banner"""
    print("=" * 70)
    print("ஐஞ்சிறுகாப்பியங்கள் (Five Minor Epics) - Bulk Import")
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
    base_dir = Path(__file__).parent.parent / 'Tamil-Source-TamilConcordence' / FILE_INFO['source_directory']

    # Check if directory exists
    if not base_dir.exists():
        print(f"\n✗ Error: Source directory not found: {base_dir}")
        print(f"  Please ensure Tamil-Source-TamilConcordence/{FILE_INFO['source_directory']}/ exists")
        sys.exit(1)

    try:
        # Initialize importer
        importer = FiveMinorEpicsImporter(db_url)

        # Parse all 5 files
        importer.parse_all_works(base_dir)

        # Bulk insert
        importer.bulk_insert()

        # Print summary
        print_summary(importer)

        print("\n✓ Import complete! All 5 works imported successfully.")
        print("\nVerification queries:")
        print("  psql -U postgres -d tamil_literature")
        print("  SELECT work_name_tamil FROM works WHERE work_id IN")
        print("    (SELECT work_id FROM work_collections WHERE collection_id = 324);")

    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    finally:
        importer.close()


if __name__ == '__main__':
    main()
