#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Siddhar Padalgal (சித்தர் பாடல்கள்) Bulk Import
Fast 2-phase import using PostgreSQL COPY with BaseWorkImporter pattern

Phase 1: Parse text → Build data structures in memory
Phase 2: Bulk COPY into database (1000x faster than INSERT)

Collection ID: 327 (சித்தர் பாடல்கள் - Siddhar Padalgal)

Works imported: 36 Siddhar mystical poetry texts spanning 7th-19th century CE

Structure:
- ** சித்தர் பாடல்கள் (collection header)
- @N Work identifier
- ** Section markers (create sections, e.g., "** ஞானம் - 1")
- ** Verse tags (metadata for next verse, e.g., "** உயர் ஞானம்")
- #N Verse markers (maintains running number across sections within work)
- *N-N Metadata markers (section-verse reference)
- Verse lines

IMPORTANT: This parser stores metadata in JSONB columns:
- sections.metadata: Section type, category, poetic form
- verses.metadata: Verse tags, section-verse cross-references
"""

import re
import psycopg2
from pathlib import Path
import csv
import io
import sys
import os
import json

# Add paths for shared utilities
sys.path.insert(0, str(Path(__file__).parent))
from shared.base_importer import BaseWorkImporter
from shared.utils import clean_line_text, split_and_clean_words

# Import centralized metadata
from metadata.siddhar_padalgal_metadata import (
    WORK_METADATA,
    VERSE_TAG_PATTERNS,
    SECTION_NAME_REPLACEMENTS,
    COLLECTION_ID,
    COLLECTION_NAME,
    COLLECTION_NAME_TAMIL,
    COLLECTION_DESCRIPTION
)


class SiddharPadalgalBulkImporter:
    """
    Master importer for all 36 Siddhar works

    Unlike the Eighteen Lesser Texts modular approach (one script per work),
    this importer handles all 36 works in one run because the source files
    are already organized as one text file per work.

    Each work gets its own BaseWorkImporter instance for atomic transactions.
    """

    def __init__(self, db_connection_string: str):
        """Initialize master importer"""
        self.db_connection_string = db_connection_string
        self.collection_id = COLLECTION_ID  # From centralized metadata

        # Connect to database for collection creation
        self.conn = psycopg2.connect(db_connection_string)
        self.cursor = self.conn.cursor()

        # Ensure collection exists
        self._ensure_collection_exists()

        # Close initial connection (each work will open its own)
        self.cursor.close()
        self.conn.close()

    def _ensure_collection_exists(self):
        """Create collection if missing (uses centralized metadata)"""
        self.cursor.execute("SELECT collection_id FROM collections WHERE collection_id = %s",
                          (self.collection_id,))
        existing = self.cursor.fetchone()

        if not existing:
            print(f"  Creating {COLLECTION_NAME_TAMIL} collection (ID: {self.collection_id})...")
            self.cursor.execute("""
                INSERT INTO collections (
                    collection_id, collection_name, collection_name_tamil,
                    collection_type, description, parent_collection_id, sort_order
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                self.collection_id,
                COLLECTION_NAME,
                COLLECTION_NAME_TAMIL,
                'tradition',
                COLLECTION_DESCRIPTION,
                1,  # Parent: தமிழ் இலக்கியம் (designated filter collection)
                6   # After Thirumurai=1, NDPD=2, Devotional=3, சிற்றிலக்கியங்கள்=4, நீதிநூல்கள்=5
            ))
            self.conn.commit()
            print(f"  [OK] Collection created")
        else:
            print(f"  Found existing {COLLECTION_NAME_TAMIL} collection (ID: {self.collection_id})")

    def import_work(self, work_num: int, file_path: str):
        """
        Import one Siddhar work using atomic transaction

        Each work gets its own BaseWorkImporter instance and transaction.
        This allows individual works to succeed/fail independently.
        """
        if work_num not in WORK_METADATA:
            print(f"[ERROR] Invalid work number: {work_num}")
            return False

        metadata = WORK_METADATA[work_num]
        print(f"\n{'='*70}")
        print(f"[{work_num}/36] Importing: {metadata['work_name_tamil']}")
        print(f"{'='*70}")

        # Create work-specific importer
        importer = SiddharWorkImporter(
            self.db_connection_string,
            self.collection_id,
            work_num,
            metadata
        )

        try:
            # Parse file (Phase 1)
            importer.parse_file(file_path)

            # Bulk insert (Phase 2)
            importer.bulk_insert()

            print(f"[OK] {metadata['work_name_tamil']} imported successfully!")
            return True

        except ValueError as e:
            print(f"[ERROR] {e}")
            print(f"  To re-import, first delete: python delete_siddhar_work.py {work_num}")
            importer.rollback()
            return False

        except Exception as e:
            print(f"[ERROR] Unexpected error: {e}")
            import traceback
            traceback.print_exc()
            importer.rollback()
            return False

        finally:
            importer.close()

    def run(self, source_dir: str):
        """Main execution: Import all 36 works"""
        print("\n" + "="*70)
        try:
            print("  SIDDHAR PADALGAL BULK IMPORT (சித்தர் பாடல்கள்)")
        except UnicodeEncodeError:
            print("  SIDDHAR PADALGAL BULK IMPORT")
        print("="*70)
        print(f"Source directory: {source_dir}")
        print(f"Collection ID: {self.collection_id}")
        print(f"Total works: 36\n")

        success_count = 0
        failed_works = []

        # Import each work
        for work_num in range(1, 37):
            metadata = WORK_METADATA[work_num]
            file_path = Path(source_dir) / metadata['file']

            if not file_path.exists():
                print(f"[ERROR] File not found: {file_path}")
                failed_works.append(metadata['work_name_tamil'])
                continue

            if self.import_work(work_num, str(file_path)):
                success_count += 1
            else:
                failed_works.append(metadata['work_name_tamil'])

        # Summary
        print("\n" + "="*70)
        print("  IMPORT SUMMARY")
        print("="*70)
        print(f"  ✓ Successfully imported: {success_count}/36 works")

        if failed_works:
            print(f"  ✗ Failed: {len(failed_works)} work(s)")
            for work in failed_works:
                print(f"    - {work}")
            return False
        else:
            print(f"\n✓ All 36 Siddhar Padalgal works imported successfully!")
            return True


class SiddharWorkImporter(BaseWorkImporter):
    """
    Atomic importer for one Siddhar work

    Extends BaseWorkImporter to handle Siddhar-specific parsing:
    - Verse tags vs. section markers
    - Running verse numbers across sections
    - Section name normalization
    - JSONB metadata storage
    """

    def __init__(self, db_connection_string: str, collection_id: int,
                 work_num: int, metadata: dict):
        """Initialize work importer"""
        super().__init__(db_connection_string, collection_id)

        # Create work entry
        self.work_id = self._create_work(
            work_name=metadata['work_name'],
            work_name_tamil=metadata['work_name_tamil'],
            metadata=metadata
        )

        # Track parsing state
        self.current_section_id = None
        self.section_counter = 0  # For section numbering
        self.global_verse_number = 0  # Running counter across sections within this work
        self.pending_verse_tag = None  # ** marker that's a verse tag, not section

    def _is_verse_tag(self, section_name: str) -> bool:
        """
        Determine if a ** marker is a verse tag (metadata) or a section marker

        Verse tags are ** markers that apply to the NEXT verse, not create a section.
        Examples: "** உயர் ஞானம்", "** விநாயகர் துதி"
        """
        # Check against known verse tag patterns
        for pattern in VERSE_TAG_PATTERNS:
            if pattern in section_name:
                return True

        # Additional heuristics:
        # - Very short names (1-2 words) are often tags
        # - Contains "துதி", "காப்பு", "வாழ்த்து" = invocation/tag
        if any(keyword in section_name for keyword in ['துதி', 'காப்பு', 'வாழ்த்து']):
            return True

        return False

    def _normalize_section_name(self, section_name: str) -> str:
        """Normalize section names using replacement rules"""
        # Apply direct replacements
        for old_name, new_name in SECTION_NAME_REPLACEMENTS.items():
            if old_name in section_name:
                return new_name

        return section_name

    def _parse_section_metadata(self, section_name: str) -> dict:
        """Extract structured metadata from section name"""
        metadata = {}

        # Check for numbered sections (e.g., "ஞானம் - 1")
        match = re.match(r'(.+?)\s*-\s*(\d+)', section_name)
        if match:
            metadata['section_type'] = match.group(1).strip()
            metadata['numbered_section'] = True
            metadata['section_sequence'] = int(match.group(2))
        else:
            metadata['section_type'] = section_name
            metadata['numbered_section'] = False

        # Classify section category based on keywords
        if 'ஞானம்' in section_name:
            metadata['category'] = 'knowledge'
        elif 'யோக' in section_name:
            metadata['category'] = 'yoga'
        elif 'பூஜா' in section_name or 'பூசா' in section_name:
            metadata['category'] = 'worship'
        elif 'தாழிசை' in section_name or 'விருத்தம்' in section_name or 'களிப்பு' in section_name:
            metadata['category'] = 'poetic_form'
            metadata['poetic_form'] = section_name
        elif 'நூல்' in section_name:
            metadata['category'] = 'text_body'
        elif 'நிலை' in section_name:
            metadata['category'] = 'state'
        else:
            metadata['category'] = 'general'

        return metadata

    def _add_section(self, section_name: str) -> int:
        """Add section to in-memory list and return section_id"""
        # Normalize section name
        section_name = self._normalize_section_name(section_name)

        # Extract metadata
        section_metadata = self._parse_section_metadata(section_name)

        section_id = self.section_id
        self.section_id += 1
        self.section_counter += 1

        self.sections.append({
            'section_id': section_id,
            'work_id': self.work_id,
            'parent_section_id': None,  # No parent - all sections are Level 1
            'level_type': 'Section',
            'level_type_tamil': 'பகுதி',
            'section_number': self.section_counter,
            'section_name': section_name,
            'section_name_tamil': section_name,
            'sort_order': self.section_counter,
            'metadata': json.dumps(section_metadata, ensure_ascii=False)
        })

        return section_id

    def _add_verse(self, verse_num: int, verse_lines: list,
                   section_verse_ref: dict = None, verse_tag: str = None):
        """Add verse with metadata to in-memory lists"""
        if not verse_lines:
            return

        verse_id = self.verse_id
        self.verse_id += 1

        # Build verse metadata
        verse_metadata = {}

        # Add section-verse reference if present (*N-N marker)
        if section_verse_ref:
            verse_metadata.update(section_verse_ref)

        # Add verse tag if present (** marker that's a tag, not section)
        if verse_tag:
            verse_metadata['verse_tag'] = verse_tag

        # Convert to JSON
        metadata_json = json.dumps(verse_metadata, ensure_ascii=False) if verse_metadata else None

        self.verses.append({
            'verse_id': verse_id,
            'work_id': self.work_id,
            'section_id': self.current_section_id,
            'verse_number': verse_num,
            'verse_type': 'paadal',
            'verse_type_tamil': 'பாடல்',
            'total_lines': len(verse_lines),
            'sort_order': verse_num,
            'metadata': metadata_json
        })

        # Create lines and words
        for line_num, line_text in enumerate(verse_lines, start=1):
            line_id = self.line_id
            self.line_id += 1

            # Clean line text using shared utilities
            cleaned_line = clean_line_text(line_text)

            self.lines.append({
                'line_id': line_id,
                'verse_id': verse_id,
                'line_number': line_num,
                'line_text': cleaned_line
            })

            # Split into words using shared utilities
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

    def _create_default_section(self) -> int:
        """Create default section for works without explicit sections"""
        return self._add_section('பாடல் தொகுப்பு')

    def parse_file(self, file_path: str):
        """
        Phase 1: Parse Siddhar work file into memory

        Parsing logic:
        1. @N identifies the work (should match work_num)
        2. ** can be either:
           - Section marker (if followed by multiple verses)
           - Verse tag (if it's a known tag pattern)
        3. #N verse markers - verse numbers are GLOBAL within work
        4. *N-N metadata markers for section-verse references
        5. Lines accumulate until blank line or next marker

        CRITICAL: Verse numbering continues across sections (not reset)
        """
        print("\nPhase 1: Parsing file...")

        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        # State tracking
        current_verse_num = None
        current_verse_lines = []
        current_section_verse_ref = {}
        needs_default_section = True

        for line in lines:
            line = line.strip()

            # Empty line - triggers verse save
            if not line:
                if current_verse_num is not None and current_verse_lines:
                    self._add_verse(
                        current_verse_num,
                        current_verse_lines,
                        current_section_verse_ref,
                        self.pending_verse_tag
                    )
                    current_verse_num = None
                    current_verse_lines = []
                    current_section_verse_ref = {}
                    self.pending_verse_tag = None
                continue

            # @N Work identifier - skip (already handled in constructor)
            if line.startswith('@'):
                # Reset state for new work
                self.current_section_id = None
                needs_default_section = True
                continue

            # ** Marker - could be section or verse tag
            if line.startswith('**'):
                # Skip collection header
                if 'சித்தர் பாடல்கள்' in line:
                    continue

                # Save previous verse if any
                if current_verse_num is not None and current_verse_lines:
                    self._add_verse(
                        current_verse_num,
                        current_verse_lines,
                        current_section_verse_ref,
                        self.pending_verse_tag
                    )
                    current_verse_num = None
                    current_verse_lines = []
                    current_section_verse_ref = {}
                    self.pending_verse_tag = None

                # Extract name
                section_name = line.replace('**', '').strip()

                # Skip empty markers or end markers (*** becomes *, **** becomes **, etc.)
                # Skip if empty or contains only asterisks
                if not section_name or section_name.replace('*', '').strip() == '':
                    continue

                # Determine if it's a verse tag or section marker
                if self._is_verse_tag(section_name):
                    # It's a verse tag - store for next verse
                    self.pending_verse_tag = section_name
                else:
                    # It's a section marker - create new section
                    self.current_section_id = self._add_section(section_name)
                    needs_default_section = False

            # *N-N Metadata marker (section-verse reference)
            elif line.startswith('*'):
                match = re.match(r'\*(\d+)-(\d+)', line)
                if match:
                    current_section_verse_ref = {
                        'section_verse_ref': f"{match.group(1)}-{match.group(2)}",
                        'section_number': int(match.group(1)),
                        'verse_in_section': int(match.group(2))
                    }

            # #N Verse marker
            elif line.startswith('#'):
                # Create default section if needed
                if needs_default_section and self.current_section_id is None:
                    self.current_section_id = self._create_default_section()
                    needs_default_section = False

                # Save previous verse
                if current_verse_num is not None and current_verse_lines:
                    self._add_verse(
                        current_verse_num,
                        current_verse_lines,
                        current_section_verse_ref,
                        self.pending_verse_tag
                    )
                    self.pending_verse_tag = None  # Clear after use

                # Extract verse number (GLOBAL within work)
                match = re.match(r'#(\d+)', line)
                if match:
                    current_verse_num = int(match.group(1))
                    self.global_verse_number = current_verse_num  # Track highest
                    current_verse_lines = []
                    # Keep current_section_verse_ref from previous * line (if any)

            # Regular line (verse content)
            elif current_verse_num is not None:
                current_verse_lines.append(line)

        # Save final verse if any
        if current_verse_num is not None and current_verse_lines:
            self._add_verse(
                current_verse_num,
                current_verse_lines,
                current_section_verse_ref,
                self.pending_verse_tag
            )

        print(f"[OK] Phase 1 complete")
        print(f"  - Sections: {len(self.sections)}")
        print(f"  - Verses: {len(self.verses)} (global numbering 1-{self.global_verse_number})")
        print(f"  - Lines: {len(self.lines)}")
        print(f"  - Words: {len(self.words)}")


def main():
    """Main entry point"""
    # Set UTF-8 encoding for stdout on Windows
    if sys.platform == 'win32':
        import codecs
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, errors='replace')
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, errors='replace')

    # Get database URL from environment or command line
    db_url = os.environ.get('DATABASE_URL')
    if len(sys.argv) > 1:
        db_url = sys.argv[1]

    if not db_url:
        db_url = "postgresql://postgres:postgres@localhost/tamil_literature"
        print(f"Using default database URL: {db_url}")

    # Get source directory
    source_dir = "Tamil-Source-TamilConcordence/11_சித்தர்_பாடல்கள்"
    if len(sys.argv) > 2:
        source_dir = sys.argv[2]

    # Resolve absolute path
    source_path = Path(source_dir)
    if not source_path.is_absolute():
        # Try relative to script directory
        script_dir = Path(__file__).parent.parent
        source_path = script_dir / source_dir

    if not source_path.exists():
        print(f"[ERROR] Source directory not found: {source_path}")
        sys.exit(1)

    # Run import
    importer = SiddharPadalgalBulkImporter(db_url)
    if importer.run(str(source_path)):
        print("\n[SUCCESS] Siddhar Padalgal import completed!")
        sys.exit(0)
    else:
        print("\n[FAILED] Siddhar Padalgal import incomplete (see errors above)")
        sys.exit(1)


if __name__ == '__main__':
    main()
