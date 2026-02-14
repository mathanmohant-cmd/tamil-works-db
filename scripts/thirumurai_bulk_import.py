#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Thirumurai Bulk Import - Using BaseWorkImporter Pattern
Phase 1: Parse text → Build data structures in memory
Phase 2: Bulk COPY into database (1000x faster than INSERT)

Thirumurai Collection (திருமுறை) - 60 works across 13 files
12 Thirumurai subcollections under Devotional Literature (323)

Structure:
- Files 1-7: Devaram (தேவாரம்) - 7 works by 3 Nayanmars
- File 8.1: Thiruvasagam - 1 work
- File 8.2: Thirukkovayar - 1 work
- File 9: Thiruvisaippa + Thiruppallandu - 10 works
- File 10: Thirumanthiram - 1 work
- File 11: Saiva Prabandha Malai - 39 works
- File 12: Periya Puranam - 1 work
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
from thirumurai_metadata import (
    COLLECTION_ID,
    COLLECTION_NAME,
    COLLECTION_NAME_TAMIL,
    SUBCOLLECTIONS,
    WORK_METADATA
)


class ThirumuraiImporter(BaseWorkImporter):
    """Import all 60 Thirumurai works using BaseWorkImporter pattern"""

    def __init__(self, db_connection_string):
        # Initialize with Devotional Literature as parent collection
        super().__init__(db_connection_string, collection_id=None)

        # Ensure Devotional Literature collection exists (parent)
        self._ensure_devotional_literature_exists()

        # Create main Thirumurai collection
        self._ensure_thirumurai_collection_exists()

        # Create 12 Thirumurai subcollections
        self._create_thirumurai_subcollections()

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

    def _ensure_thirumurai_collection_exists(self):
        """Ensure Thirumurai main collection (321) exists"""
        self.cursor.execute(
            "SELECT collection_id FROM collections WHERE collection_id = %s",
            (COLLECTION_ID,)
        )
        if not self.cursor.fetchone():
            print(f"  Creating Thirumurai collection ({COLLECTION_ID})...")
            self.cursor.execute("""
                INSERT INTO collections (
                    collection_id, collection_name, collection_name_tamil,
                    collection_type, description, parent_collection_id, sort_order
                ) VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                COLLECTION_ID, COLLECTION_NAME, COLLECTION_NAME_TAMIL,
                'tradition', 'Twelve books of Shaivite devotional hymns',
                323, 1
            ))
        else:
            print(f"  Thirumurai collection ({COLLECTION_ID}) already exists")

    def _create_thirumurai_subcollections(self):
        """Create 12 Thirumurai subcollections under Thirumurai (321)"""
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
                    'subcollection', f'Thirumurai {num}',
                    COLLECTION_ID, num
                ))
            else:
                print(f"  {subinfo['name']} ({subinfo['id']}) already exists")

    def parse_and_import_all_works(self, source_dir: Path):
        """Parse all 60 works from 13 source files"""
        print("\n=== PHASE 1: Parsing all Thirumurai files ===")

        # Group works by source file
        works_by_file = {}
        for work_key, work_meta in WORK_METADATA.items():
            file_name = work_meta['file']
            if file_name not in works_by_file:
                works_by_file[file_name] = []
            works_by_file[file_name].append((work_key, work_meta))

        # Parse each file
        for file_name, works_list in sorted(works_by_file.items()):
            file_path = source_dir / file_name
            if not file_path.exists():
                print(f"  [WARNING] File not found: {file_path}")
                continue

            print(f"\n  Parsing {file_name} ({len(works_list)} work(s))...")

            # Different parsing logic based on file type
            if file_name.startswith('1.') or file_name.startswith('2.') or \
               file_name.startswith('3.') or file_name.startswith('4.') or \
               file_name.startswith('5.') or file_name.startswith('6.') or \
               file_name.startswith('7.'):
                # Devaram files (1 work per file)
                self._parse_devaram_file(file_path, works_list[0])
            elif file_name.startswith('8.1'):
                # Thiruvasagam
                self._parse_file8_single_work(file_path, works_list[0])
            elif file_name.startswith('8.2'):
                # Thirukkovayar
                self._parse_file8_single_work(file_path, works_list[0])
            elif file_name.startswith('9.'):
                # File 9: 10 works with & markers for authors
                self._parse_file9_multi_work(file_path, works_list)
            elif file_name.startswith('10.'):
                # Thirumanthiram
                self._parse_file10_single_work(file_path, works_list[0])
            elif file_name.startswith('11.'):
                # File 11: 39 works with & markers for authors
                self._parse_file11_multi_work(file_path, works_list)
            elif file_name.startswith('12.'):
                # Periya Puranam
                self._parse_file12_single_work(file_path, works_list[0])

    def _parse_devaram_file(self, file_path: Path, work_tuple):
        """Parse Devaram files (Files 1-7) - numbered sections → # verses"""
        work_key, work_meta = work_tuple

        # Create work
        work_id = self._create_work(
            work_name=work_meta['work_name'],
            work_name_tamil=work_meta['work_name_tamil'],
            metadata=work_meta
        )

        # Link to subcollection
        self.work_collections.append({
            'work_id': work_id,
            'collection_id': work_meta['subcollection_id'],
            'position_in_collection': work_meta['position_in_collection']
        })

        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        current_section_id = None
        current_verse_lines = []
        verse_count = 0

        for line in lines[1:]:  # Skip header line
            line = line.strip()
            if not line or line == 'மேல்' or line.startswith('**'):
                continue

            # Check for numbered section (temple/location)
            section_match = re.match(r'^(\d+)\.\s*(.+)', line)
            if section_match:
                section_num = int(section_match.group(1))
                section_name = section_match.group(2).strip()

                # Create section
                current_section_id = self.section_id
                self.section_id += 1
                self.sections.append({
                    'section_id': current_section_id,
                    'work_id': work_id,
                    'parent_section_id': None,
                    'level_type': 'Location',
                    'level_type_tamil': 'இடம்',
                    'section_number': section_num,
                    'section_name': section_name,
                    'section_name_tamil': section_name,
                    'sort_order': section_num
                })
                continue

            # Check for verse marker
            verse_match = re.match(r'^#(\d+)', line)
            if verse_match:
                # Save previous verse if exists
                if current_verse_lines and current_section_id:
                    self._save_verse(work_id, current_section_id, verse_count,
                                   current_verse_lines, 'Verse', 'பாடல்')

                verse_count += 1
                current_verse_lines = []
                continue

            # Accumulate verse lines
            if current_section_id and line:
                current_verse_lines.append(line)

        # Save last verse
        if current_verse_lines and current_section_id:
            self._save_verse(work_id, current_section_id, verse_count,
                           current_verse_lines, 'Verse', 'பாடல்')

        print(f"    ✓ {work_meta['work_name_tamil']}: {verse_count} verses")

    def _parse_file8_single_work(self, file_path: Path, work_tuple):
        """Parse File 8 works (Thiruvasagam, Thirukkovayar) - @ sections → # verses"""
        work_key, work_meta = work_tuple

        # Create work
        work_id = self._create_work(
            work_name=work_meta['work_name'],
            work_name_tamil=work_meta['work_name_tamil'],
            metadata=work_meta
        )

        # Link to subcollection
        self.work_collections.append({
            'work_id': work_id,
            'collection_id': work_meta['subcollection_id'],
            'position_in_collection': work_meta['position_in_collection']
        })

        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        current_section_id = None
        current_verse_lines = []
        verse_count = 0
        section_count = 0

        for line in lines:
            line = line.strip()
            if not line or line.startswith('**'):
                continue

            # Check for @ section marker
            section_match = re.match(r'^@(\d+)\s*(.+)', line)
            if section_match:
                section_num = int(section_match.group(1))
                section_name = section_match.group(2).strip()

                section_count += 1
                current_section_id = self.section_id
                self.section_id += 1
                self.sections.append({
                    'section_id': current_section_id,
                    'work_id': work_id,
                    'parent_section_id': None,
                    'level_type': 'Section',
                    'level_type_tamil': 'பகுதி',
                    'section_number': section_num,
                    'section_name': section_name,
                    'section_name_tamil': section_name,
                    'sort_order': section_num
                })
                continue

            # Check for verse marker
            verse_match = re.match(r'^#(\d+)', line)
            if verse_match:
                # Save previous verse if exists
                if current_verse_lines and current_section_id:
                    self._save_verse(work_id, current_section_id, verse_count,
                                   current_verse_lines, 'Verse', 'பாடல்')

                verse_count += 1
                current_verse_lines = []
                continue

            # Accumulate verse lines
            if current_section_id and line:
                current_verse_lines.append(line)

        # Save last verse
        if current_verse_lines and current_section_id:
            self._save_verse(work_id, current_section_id, verse_count,
                           current_verse_lines, 'Verse', 'பாடல்')

        print(f"    ✓ {work_meta['work_name_tamil']}: {section_count} sections, {verse_count} verses")

    def _parse_file9_multi_work(self, file_path: Path, works_list):
        """Parse File 9 - Multiple works with & author markers"""
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        # Build work lookup by author marker number
        work_by_author_num = {}
        for work_key, work_meta in works_list:
            if work_key.startswith('file9_') or work_key.startswith('file11_'):
                author_num = int(work_key.split('_')[1])
                work_by_author_num[author_num] = (work_key, work_meta)

        current_work_id = None
        current_section_id = None
        current_verse_lines = []
        verse_count = 0
        section_count = 0
        current_work_meta = None

        for line in lines:
            line = line.strip()
            if not line or line.startswith('**'):
                continue

            # Check for & author marker (new work)
            author_match = re.match(r'^&(\d+)\s+(.+?)\s*\^\s*(.+)', line)
            if author_match:
                # Save last verse of previous work before starting new work
                if current_verse_lines and current_section_id and current_work_id and verse_count > 0:
                    self._save_verse(current_work_id, current_section_id, verse_count,
                                   current_verse_lines, 'Verse', 'பதிகம்')
                    current_verse_lines = []

                    # Print completion stats for previous work
                    if current_work_meta:
                        total_verses = len([v for v in self.verses if v['work_id'] == current_work_id])
                        print(f"    ✓ {current_work_meta['work_name_tamil']}: {total_verses} verses")

                author_num = int(author_match.group(1))

                if author_num in work_by_author_num:
                    work_key, work_meta = work_by_author_num[author_num]

                    # Create new work
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
                    current_section_id = None
                    verse_count = 0
                    section_count = 0
                continue

            # Check for @ section marker
            section_match = re.match(r'^@(\d+)\s*(.+)', line)
            if section_match and current_work_id:
                # Save previous verse before changing sections
                if current_verse_lines and current_section_id and verse_count > 0:
                    self._save_verse(current_work_id, current_section_id, verse_count,
                                   current_verse_lines, 'Verse', 'பதிகம்')
                    current_verse_lines = []

                section_num = int(section_match.group(1))
                section_name = section_match.group(2).strip()

                section_count += 1
                current_section_id = self.section_id
                self.section_id += 1
                self.sections.append({
                    'section_id': current_section_id,
                    'work_id': current_work_id,
                    'parent_section_id': None,
                    'level_type': 'Section',
                    'level_type_tamil': 'பகுதி',
                    'section_number': section_num,
                    'section_name': section_name,
                    'section_name_tamil': section_name,
                    'sort_order': section_num
                })
                verse_count = 0  # Reset verse count for new section
                continue

            # Check for verse marker
            verse_match = re.match(r'^#(\d+)', line)
            if verse_match and current_work_id:
                # Create default section if none exists (before saving verse)
                if not current_section_id:
                    current_section_id = self.section_id
                    self.section_id += 1
                    self.sections.append({
                        'section_id': current_section_id,
                        'work_id': current_work_id,
                        'parent_section_id': None,
                        'level_type': 'Section',
                        'level_type_tamil': 'பகுதி',
                        'section_number': 1,
                        'section_name': 'Main',
                        'section_name_tamil': 'முதன்மை',
                        'sort_order': 1
                    })

                # Save previous verse if exists
                if current_verse_lines and current_section_id:
                    self._save_verse(current_work_id, current_section_id, verse_count,
                                   current_verse_lines, 'Verse', 'பதிகம்')
                    current_verse_lines = []

                verse_count += 1
                continue

            # Accumulate verse lines (only if we've started a verse with #)
            if current_work_id and verse_count > 0 and line:
                current_verse_lines.append(line)

        # Save last verse of last work
        if current_verse_lines and current_section_id and current_work_id and verse_count > 0:
            self._save_verse(current_work_id, current_section_id, verse_count,
                           current_verse_lines, 'Verse', 'பதிகம்')

        # Print final work stats
        if current_work_meta and current_work_id:
            total_verses = len([v for v in self.verses if v['work_id'] == current_work_id])
            print(f"    ✓ {current_work_meta['work_name_tamil']}: {total_verses} verses")

    def _parse_file10_single_work(self, file_path: Path, work_tuple):
        """Parse File 10 (Thirumanthiram) - @ sections → # verses"""
        self._parse_file8_single_work(file_path, work_tuple)

    def _parse_file11_multi_work(self, file_path: Path, works_list):
        """Parse File 11 - Multiple works with & author markers (39 works)"""
        # Same pattern as File 9
        self._parse_file9_multi_work(file_path, works_list)

    def _parse_file12_single_work(self, file_path: Path, work_tuple):
        """Parse File 12 (Periya Puranam) - @ sections → # verses"""
        self._parse_file8_single_work(file_path, work_tuple)

    def _save_verse(self, work_id, section_id, verse_num, verse_lines,
                    verse_type, verse_type_tamil):
        """Save a complete verse with lines and words"""
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
            'verse_type': verse_type,
            'verse_type_tamil': verse_type_tamil,
            'total_lines': len(verse_lines),
            'sort_order': verse_num,
            'metadata': None
        })

        # Create lines and words
        for line_num, line_text in enumerate(verse_lines, 1):
            line_id = self.line_id
            self.line_id += 1
            self.lines.append({
                'line_id': line_id,
                'verse_id': verse_id,
                'line_number': line_num,
                'line_text': line_text
            })

            # Split line into words
            words = split_and_clean_words(line_text)
            for word_pos, word_text in enumerate(words, 1):
                self.words.append({
                    'word_id': self.word_id,
                    'line_id': line_id,
                    'word_position': word_pos,
                    'word_text': word_text,
                    'sandhi_split': None
                })
                self.word_id += 1


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
        importer = ThirumuraiImporter(db_url)
        importer.parse_and_import_all_works(source_dir)
        importer.bulk_insert()

        print("\n" + "=" * 70)
        print("[SUCCESS] All 60 Thirumurai works imported successfully!")
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
