#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Naalayira Divya Prabandham Bulk Import - Using BaseWorkImporter Pattern
Phase 1: Parse text → Build data structures in memory
Phase 2: Bulk COPY into database (1000x faster than INSERT)

Naalayira Divya Prabandham Collection (நாலாயிரத் திவ்விய பிரபந்தம்) - 25 works across 4 files
4 Ayiram subcollections under Devotional Literature (323)

Structure:
- File 13: முதல் ஆயிரம் (First Ayiram) - 10 works
- File 14: இரண்டாம் ஆயிரம் (Second Ayiram) - 3 works
- File 15: மூன்றாம் ஆயிரம் (Third Ayiram) - 11 works
- File 16: நான்காம் ஆயிரம் (Fourth Ayiram) - 1 work (Thiruvaaymozhi)
"""

import re
import sys
import os
from pathlib import Path

# Add shared directory to path for imports
script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir))
sys.path.insert(0, str(script_dir / 'shared'))
sys.path.insert(0, str(script_dir / 'metadata'))

from shared.base_importer import BaseWorkImporter
from shared.utils import split_and_clean_words
from naalayira_divya_prabandham_metadata import (
    COLLECTION_ID,
    COLLECTION_NAME,
    COLLECTION_NAME_TAMIL,
    SUBCOLLECTIONS,
    WORK_METADATA
)


class NaalayiraDivyaPrabandhamImporter(BaseWorkImporter):
    """Import all 25 Naalayira Divya Prabandham works using BaseWorkImporter pattern"""

    def __init__(self, db_connection_string):
        # Initialize with Devotional Literature as parent collection
        super().__init__(db_connection_string, collection_id=None)

        # Ensure Devotional Literature collection exists (parent)
        self._ensure_devotional_literature_exists()

        # Create main NDP collection
        self._ensure_ndp_collection_exists()

        # Create 4 Ayiram subcollections
        self._create_ayiram_subcollections()

    def _ensure_devotional_literature_exists(self):
        """Ensure Devotional Literature collection (323) exists"""
        self.cursor.execute(
            "SELECT collection_id FROM collections WHERE collection_id = 323"
        )
        if not self.cursor.fetchone():
            print("  Creating Devotional Literature collection (323)...")
            self.cursor.execute("""
                INSERT INTO collections (
                    collection_id, collection_name, collection_name_tamil,
                    collection_type, description, parent_collection_id, sort_order
                ) VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                323, 'Devotional Literature', 'பக்தி இலக்கியம்',
                'period', 'Devotional hymns and religious poetry from 6th-19th century CE',
                1, 4
            ))
        else:
            print("  Devotional Literature collection (323) already exists")

    def _ensure_ndp_collection_exists(self):
        """Ensure NDP main collection (322) exists"""
        self.cursor.execute(
            "SELECT collection_id FROM collections WHERE collection_id = %s",
            (COLLECTION_ID,)
        )
        if not self.cursor.fetchone():
            print(f"  Creating Naalayira Divya Prabandham collection ({COLLECTION_ID})...")
            self.cursor.execute("""
                INSERT INTO collections (
                    collection_id, collection_name, collection_name_tamil,
                    collection_type, description, parent_collection_id, sort_order
                ) VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                COLLECTION_ID, COLLECTION_NAME, COLLECTION_NAME_TAMIL,
                'tradition', 'Four thousand sacred hymns of Vaishnavite devotion by 12 Azhvaars',
                323, 2
            ))
        else:
            print(f"  Naalayira Divya Prabandham collection ({COLLECTION_ID}) already exists")

    def _create_ayiram_subcollections(self):
        """Create 4 Ayiram subcollections under NDP (322)"""
        for num, subinfo in SUBCOLLECTIONS.items():
            self.cursor.execute(
                "SELECT collection_id FROM collections WHERE collection_id = %s",
                (subinfo['id'],)
            )
            if not self.cursor.fetchone():
                print(f"  Creating {subinfo['name']} ({subinfo['id']})...")
                self.cursor.execute("""
                    INSERT INTO collections (
                        collection_id, collection_name, collection_name_tamil,
                        collection_type, description, parent_collection_id, sort_order
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (
                    subinfo['id'], subinfo['name_en'], subinfo['name'],
                    'subcollection', f'{subinfo["name_en"]} of Naalayira Divya Prabandham',
                    COLLECTION_ID, num
                ))
            else:
                print(f"  {subinfo['name']} ({subinfo['id']}) already exists")

    def parse_and_import_all_works(self, source_dir: Path):
        """Parse all 25 works from 4 Ayiram files"""
        print("\n=== PHASE 1: Parsing all NDP Ayiram files ===")

        # Group works by source file
        works_by_file = {}
        for work_key, work_meta in WORK_METADATA.items():
            file_name = work_meta['file']
            if file_name not in works_by_file:
                works_by_file[file_name] = []
            works_by_file[file_name].append((work_key, work_meta))

        # Parse each file (all use same @ Author ^ Work format)
        for file_name, works_list in sorted(works_by_file.items()):
            file_path = source_dir / file_name
            if not file_path.exists():
                print(f"  [WARNING] File not found: {file_path}")
                continue

            print(f"\n  Parsing {file_name} ({len(works_list)} work(s))...")
            self._parse_ayiram_file(file_path, works_list)

    def _parse_ayiram_file(self, file_path: Path, works_list: list):
        """
        Parse a single Ayiram file containing multiple works.
        
        All NDP files use the same format:
        - @ marks author/work: @Author ^ Work Title
        - # marks verse number
        - Blank lines separate verses
        """
        # Build work lookup by author+title
        work_lookup = {}
        for work_key, work_meta in works_list:
            author = work_meta['author_tamil']
            work_name = work_meta['work_name_tamil']
            lookup_key = f"{author}|{work_name}"
            work_lookup[lookup_key] = (work_key, work_meta)

        with open(file_path, 'r', encoding='utf-8') as f:
            content_lines = f.readlines()

        # State variables
        current_work_id = None
        current_work_meta = None
        current_section_id = None
        verse_count = 0
        current_verse_lines = []

        for line in content_lines:
            line = line.strip()

            # Skip empty lines when not accumulating verse
            if not line and not current_verse_lines:
                continue

            # Check for @ author/work marker
            author_match = re.match(r'^@(.+?)\s*\^\s*(.+)', line)
            if author_match:
                # Save previous verse if exists
                if current_verse_lines and current_section_id and current_work_id and verse_count > 0:
                    self._save_verse(current_work_id, current_section_id, verse_count,
                                   current_verse_lines)
                    current_verse_lines = []

                # Print completion stats for previous work
                if current_work_meta:
                    total_verses = len([v for v in self.verses if v['work_id'] == current_work_id])
                    print(f"    ✓ {current_work_meta['work_name_tamil']}: {total_verses} verses")

                # Start new work
                author, work_name = author_match.groups()
                author = author.strip()
                work_name = work_name.strip()
                lookup_key = f"{author}|{work_name}"

                if lookup_key not in work_lookup:
                    print(f"[WARNING] Unknown work: {author} - {work_name}")
                    current_work_id = None
                    current_work_meta = None
                    current_section_id = None
                    verse_count = 0
                    continue

                work_key, work_meta = work_lookup[lookup_key]

                # Create work
                current_work_id = self._create_work(
                    work_name=work_meta['work_name'],
                    work_name_tamil=work_meta['work_name_tamil'],
                    metadata=work_meta
                )

                # Link to subcollection
                self.work_collections.append({
                    'work_id': current_work_id,
                    'collection_id': work_meta['subcollection_id'],
                    'position_in_collection': work_meta['position_in_collection']
                })

                current_work_meta = work_meta

                # Create default section for this work
                current_section_id = self.section_id
                self.section_id += 1

                self.sections.append({
                    'section_id': current_section_id,
                    'work_id': current_work_id,
                    'parent_section_id': None,
                    'level_type': 'Default',
                    'level_type_tamil': 'இயல்புநிலை',
                    'section_number': 1,
                    'section_name': work_meta['work_name'],
                    'section_name_tamil': work_meta['work_name_tamil'],
                    'sort_order': 1
                })

                verse_count = 0
                current_verse_lines = []
                continue

            # Check for # verse marker
            verse_match = re.match(r'^#(\d+)', line)
            if verse_match and current_work_id:
                # Save previous verse if exists (CRITICAL: BEFORE incrementing)
                if current_verse_lines and current_section_id:
                    self._save_verse(current_work_id, current_section_id, verse_count,
                                   current_verse_lines)
                    current_verse_lines = []

                verse_count += 1  # Increment AFTER saving
                continue

            # Accumulate verse lines (only if we've started a verse with #)
            if current_work_id and verse_count > 0 and line:
                current_verse_lines.append(line)

        # Save last verse of last work
        if current_verse_lines and current_section_id and current_work_id and verse_count > 0:
            self._save_verse(current_work_id, current_section_id, verse_count,
                           current_verse_lines)

        # Print completion stats for last work
        if current_work_meta:
            total_verses = len([v for v in self.verses if v['work_id'] == current_work_id])
            print(f"    ✓ {current_work_meta['work_name_tamil']}: {total_verses} verses")

    def _save_verse(self, work_id, section_id, verse_number, verse_lines):
        """Save a verse and its lines/words"""
        if not verse_lines:
            return

        verse_id = self.verse_id
        self.verse_id += 1

        self.verses.append({
            'verse_id': verse_id,
            'work_id': work_id,
            'section_id': section_id,
            'verse_number': verse_number,
            'verse_type': 'Paasuram',
            'verse_type_tamil': 'பாசுரம்',
            'total_lines': len(verse_lines),
            'sort_order': verse_number
        })

        # Process each line
        for line_num, line_text in enumerate(verse_lines, start=1):
            line_id = self.line_id
            self.line_id += 1

            # Clean line text
            cleaned_line = self._clean_line_text(line_text)

            self.lines.append({
                'line_id': line_id,
                'verse_id': verse_id,
                'line_number': line_num,
                'line_text': cleaned_line
            })

            # Tokenize and create words
            words = split_and_clean_words(cleaned_line)
            for word_pos, word_text in enumerate(words, start=1):
                word_id = self.word_id
                self.word_id += 1

                self.words.append({
                    'word_id': word_id,
                    'line_id': line_id,
                    'word_position': word_pos,
                    'word_text': word_text,
                    'sandhi_split': None
                })

    def _clean_line_text(self, line_text: str) -> str:
        """Clean line text by removing markers and line numbers"""
        # Remove ** and *** markers
        line_text = re.sub(r'\*+', '', line_text)
        # Remove line numbers at end
        line_text = re.sub(r'\s+\d+$', '', line_text)
        # Remove alignment dots
        line_text = re.sub(r'\.\. +', '', line_text)
        return line_text.strip()


def main():
    """Main import function"""
    import os

    # Get database URL from environment or command line
    db_url = os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@localhost/tamil_literature')
    if len(sys.argv) > 1:
        db_url = sys.argv[1]

    print("=" * 70)
    print("THIRUMURAI BULK IMPORT - 60 WORKS")
    print("=" * 70)
    print(f"Database: {db_url}")

    # Locate source directory
    project_dir = Path(__file__).parent.parent
    source_dir = project_dir / "Tamil-Source-TamilConcordence" / "6_பக்தி இலக்கியம்"

    if not source_dir.exists():
        print(f"\n[ERROR] Source directory not found: {source_dir}")
        return 1

    print(f"Source: {source_dir}")

    try:
        importer = NaalayiraDivyaPrabandhamImporter(db_url)
        importer.parse_and_import_all_works(source_dir)
        importer.bulk_insert()

        print("\n" + "=" * 70)
        print("[SUCCESS] All 25 Naalayira Divya Prabandham works imported successfully!")
        print("=" * 70)

        importer.close()
        return 0

    except Exception as e:
        print(f"\n[ERROR] Import failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
