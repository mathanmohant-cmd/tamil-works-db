#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Thirukovayar Bulk Import - Fast 2-phase import using PostgreSQL COPY
Phase 1: Parse text → Build data structures in memory
Phase 2: Bulk COPY into database (1000x faster than INSERT)

Thirukovayar (திருக்கோவையார்) - File 8.2, Collection ID: 3218
Author: Manikkavasagar (மாணிக்கவாசகர்)

Structure (2 levels):
- இயல் (Main division): களவியல், கற்பியல்
  - அதிகாரம் (Chapters 1-25)
    - பாடல் (Verses)
      - Metadata: துறை (from *N.M markers)

Markers:
* [name] - [description]  → Main division (களவியல், கற்பியல்)
*N [name]                 → Chapter (அதிகாரம்)
*N.M [name]               → Verse metadata (துறை)
#N                        → Verse number
மேல்                       → Separator
"""

import re
import psycopg2
from pathlib import Path
import io
import sys
import os
from word_cleaning import split_and_clean_words

class ThirukovayarBulkImporter:
    def __init__(self, db_connection_string: str):
        """Initialize importer with database connection"""
        self.conn = psycopg2.connect(db_connection_string)
        self.cursor = self.conn.cursor()

        # Data containers for bulk insert
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

        print(f"Starting IDs: work={self.work_id}, section={self.section_id}, verse={self.verse_id}, line={self.line_id}, word={self.word_id}")

        # Track current work
        self.current_work_id = None

    def ensure_collection_exists(self):
        """Ensure the 8th Thirumurai collection exists and return its ID"""
        # Check if main Thirumurai collection exists (321)
        self.cursor.execute("SELECT collection_id FROM collections WHERE collection_id = 321")
        if not self.cursor.fetchone():
            print("  Creating main Thirumurai collection (321)...")
            self.cursor.execute("""
                INSERT INTO collections (collection_id, collection_name, collection_name_tamil,
                                       collection_type, description, sort_order)
                VALUES (321, 'Thirumurai', 'திருமுறை', 'devotional',
                        'Thirumurai - 12 books of Shaivite devotional literature', 321)
            """)
            self.conn.commit()

        # Check if 8th Thirumurai collection exists (3218)
        self.cursor.execute("SELECT collection_id FROM collections WHERE collection_id = 3218")
        result = self.cursor.fetchone()

        if not result:
            print("  Creating 8th Thirumurai collection (3218)...")
            self.cursor.execute("""
                INSERT INTO collections (collection_id, collection_name, collection_name_tamil,
                                       collection_type, parent_collection_id, description, sort_order)
                VALUES (3218, 'Eighth Thirumurai', 'எட்டாம் திருமுறை', 'devotional', 321,
                        '8th Thirumurai - Thiruvasagam and Thirukovayar by Manikkavasagar', 3218)
            """)
            self.conn.commit()
            print("  [OK] 8th Thirumurai collection created")
        else:
            print("  [OK] 8th Thirumurai collection already exists")

        # Query and return the collection_id
        self.cursor.execute("SELECT collection_id FROM collections WHERE collection_id = 3218")
        self.eighth_thirumurai_collection_id = self.cursor.fetchone()[0]
        return self.eighth_thirumurai_collection_id

    def _get_or_create_section_id(self, work_id, parent_section_id=None, level_type='Chapter',
                                   level_type_tamil='பகுதி', section_number=1, section_name=None):
        """
        Get or create a section and return section_id
        Follows Sangam/Devaram parser pattern to ensure all verses have a section_id
        """
        section_id = self.section_id
        self.section_id += 1

        self.sections.append({
            'section_id': section_id,
            'work_id': work_id,
            'parent_section_id': parent_section_id,
            'level_type': level_type,
            'level_type_tamil': level_type_tamil,
            'section_number': section_number,
            'section_name': section_name,
            'section_name_tamil': section_name,
            'sort_order': section_number,
            'metadata': {}
        })

        return section_id

    def parse_thirukovayar(self, file_path):
        """
        Parse Thirukovayar file

        Structure:
        * Main division (இயல்): களவியல், கற்பியல்
          *N Chapter (அதிகாரம்)
            *N.M துறை (verse metadata)
            #N Verse
        """
        print(f"\n=== PHASE 1: Parsing {Path(file_path).name} ===")

        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        # Create work (use collection_id from ensure_collection_exists)
        work_metadata = {
            'tradition': 'Shaivite',
            'collection_id': self.eighth_thirumurai_collection_id,
            'collection_name': 'Eighth Thirumurai',
            'collection_name_tamil': 'எட்டாம் திருமுறை',
            'thirumurai_number': 8,
            'file_part': '8.2',
            'saint': 'மாணிக்கவாசகர்',
            'saint_transliteration': 'Manikkavasagar'
        }

        self.current_work_id = self.work_id
        self.work_id += 1

        self.works.append({
            'work_id': self.current_work_id,
            'work_name': 'Thirukovayar',
            'work_name_tamil': 'திருக்கோவையார்',
            'author': 'Manikkavasagar',
            'author_tamil': 'மாணிக்கவாசகர்',
            'period': '9th century CE',
            'canonical_order': 329,
            'primary_collection_id': self.eighth_thirumurai_collection_id,
            'metadata': work_metadata
        })

        print(f"  Created work: திருக்கோவையார் (ID: {self.current_work_id})")

        # Parse structure
        current_iyal_section = None  # Main division (களவியல், கற்பியல்)
        current_adhikaram_section = None  # Chapter
        current_thurai = None  # Verse metadata (from *N.M)
        current_verse_lines = []
        verse_count = 0

        for line in lines[1:]:  # Skip first line (author ^ work)
            line = line.strip()

            if not line or line == 'மேல்' or line.startswith('**'):
                continue

            # Check for main division: * [name] - [description]
            main_match = re.match(r'^\*\s+([^-*\d]+)\s*-\s*(.+)', line)
            if main_match and not line.startswith('**'):
                # Save previous verse if any
                if current_verse_lines and current_adhikaram_section:
                    self._add_verse(current_adhikaram_section, verse_count, current_verse_lines, current_thurai)
                    current_verse_lines = []

                iyal_name = main_match.group(1).strip()
                iyal_number = 1 if 'களவியல்' in iyal_name else 2

                current_iyal_section = self._get_or_create_section_id(
                    self.current_work_id,
                    parent_section_id=None,
                    level_type='Iyal',
                    level_type_tamil='இயல்',
                    section_number=iyal_number,
                    section_name=iyal_name
                )
                print(f"  Found இயல்: {iyal_name}")
                current_adhikaram_section = None
                current_thurai = None
                verse_count = 0
                continue

            # Check for chapter: *N [name] (without dot)
            chapter_match = re.match(r'^\*(\d+)\s+(.+)', line)
            if chapter_match and '.' not in chapter_match.group(1):
                # Save previous verse if any
                if current_verse_lines and current_adhikaram_section:
                    self._add_verse(current_adhikaram_section, verse_count, current_verse_lines, current_thurai)
                    current_verse_lines = []

                adhikaram_num = int(chapter_match.group(1))
                adhikaram_name = chapter_match.group(2).strip()

                current_adhikaram_section = self._get_or_create_section_id(
                    self.current_work_id,
                    parent_section_id=current_iyal_section,
                    level_type='Adhikaram',
                    level_type_tamil='அதிகாரம்',
                    section_number=adhikaram_num,
                    section_name=adhikaram_name
                )
                current_thurai = None
                verse_count = 0
                continue

            # Check for துறை metadata: *N.M [name]
            thurai_match = re.match(r'^\*(\d+)\.(\d+)\.?\s*(.+)', line)
            if thurai_match:
                # Save previous verse if any
                if current_verse_lines and current_adhikaram_section:
                    self._add_verse(current_adhikaram_section, verse_count, current_verse_lines, current_thurai)
                    current_verse_lines = []

                thurai_name = thurai_match.group(3).strip()
                current_thurai = thurai_name
                verse_count = 0
                continue

            # Check for verse marker: #N
            verse_match = re.match(r'^#(\d+)', line)
            if verse_match:
                # Save previous verse if any
                if current_verse_lines and current_adhikaram_section:
                    self._add_verse(current_adhikaram_section, verse_count, current_verse_lines, current_thurai)
                    current_verse_lines = []

                verse_count = int(verse_match.group(1))
                continue

            # Regular verse line
            if verse_count > 0 and current_adhikaram_section:
                cleaned = line.replace('…', '').strip()
                if cleaned:
                    current_verse_lines.append(cleaned)

        # Save last verse
        if current_verse_lines and current_adhikaram_section:
            self._add_verse(current_adhikaram_section, verse_count, current_verse_lines, current_thurai)

        print(f"  [OK] Parsed {len(self.sections)} sections, {len(self.verses)} verses")

    def _add_verse(self, section_id, verse_num, verse_lines, thurai_metadata=None):
        """Add verse with lines and words to memory"""
        if not verse_lines:
            return

        verse_id = self.verse_id
        self.verse_id += 1

        # Build verse metadata
        metadata = {}
        if thurai_metadata:
            metadata['thuRai'] = thurai_metadata

        self.verses.append({
            'verse_id': verse_id,
            'work_id': self.current_work_id,
            'section_id': section_id,
            'verse_number': verse_num,
            'verse_type': 'verse',
            'verse_type_tamil': 'பாடல்',
            'total_lines': len(verse_lines),
            'sort_order': verse_num,
            'metadata': metadata
        })

        # Add lines and words
        for line_num, line_text in enumerate(verse_lines, start=1):
            line_id = self.line_id
            self.line_id += 1

            # Clean line text: remove tabs, newlines, normalize whitespace
            cleaned_line = line_text.replace('\t', ' ').replace('\n', ' ').replace('\r', '')
            cleaned_line = re.sub(r'\s+', ' ', cleaned_line).strip()

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

    def bulk_insert_works(self):
        """Bulk insert works using PostgreSQL COPY"""
        if not self.works:
            return

        print(f"  Bulk inserting {len(self.works)} work(s)...")

        buffer = io.StringIO()
        for work in self.works:
            # Convert metadata dict to JSON string
            import json
            metadata_json = json.dumps(work['metadata'], ensure_ascii=False)

            fields = [
                str(work['work_id']),
                work['work_name'],
                work['work_name_tamil'],
                work['period'],
                work['author'],
                work['author_tamil'],
                str(work['canonical_order']),
                str(work['primary_collection_id']),
                metadata_json
            ]
            buffer.write('\t'.join(fields) + '\n')

        buffer.seek(0)
        self.cursor.copy_from(
            buffer, 'works',
            columns=['work_id', 'work_name', 'work_name_tamil', 'period', 'author',
                    'author_tamil', 'canonical_order', 'primary_collection_id', 'metadata'],
            null=''
        )
        print(f"  [OK] Bulk inserted {len(self.works)} work(s)")

    def bulk_insert_work_collections(self):
        """Link work to 8th Thirumurai collection"""
        if not self.works:
            return

        print(f"  Linking work to 8th Thirumurai collection...")

        # Get next available position in this collection
        self.cursor.execute("""
            SELECT COALESCE(MAX(position_in_collection), 0) + 1
            FROM work_collections
            WHERE collection_id = %s
        """, (self.eighth_thirumurai_collection_id,))
        next_position = self.cursor.fetchone()[0]

        buffer = io.StringIO()
        for work in self.works:
            fields = [
                str(work['work_id']),
                str(self.eighth_thirumurai_collection_id),  # Use dynamic collection_id
                str(next_position),     # position_in_collection (dynamic)
                't',     # is_primary (true)
                ''       # notes (NULL)
            ]
            buffer.write('\t'.join(fields) + '\n')
            next_position += 1

        buffer.seek(0)
        self.cursor.copy_from(
            buffer, 'work_collections',
            columns=['work_id', 'collection_id', 'position_in_collection', 'is_primary', 'notes'],
            null=''
        )
        print(f"  [OK] Linked work to collection")

    def bulk_insert_sections(self):
        """Bulk insert sections using PostgreSQL COPY"""
        if not self.sections:
            return

        print(f"  Bulk inserting {len(self.sections)} sections...")

        buffer = io.StringIO()
        for section in self.sections:
            import json
            metadata_json = json.dumps(section['metadata'], ensure_ascii=False) if section['metadata'] else ''

            fields = [
                str(section['section_id']),
                str(section['work_id']),
                str(section['parent_section_id']) if section['parent_section_id'] else '',
                section['level_type'],
                section['level_type_tamil'],
                str(section['section_number']),
                section['section_name'] if section['section_name'] else '',
                section['section_name_tamil'] if section['section_name_tamil'] else '',
                str(section['sort_order']),
                metadata_json
            ]
            buffer.write('\t'.join(fields) + '\n')

        buffer.seek(0)
        self.cursor.copy_from(
            buffer, 'sections',
            columns=['section_id', 'work_id', 'parent_section_id', 'level_type', 'level_type_tamil',
                    'section_number', 'section_name', 'section_name_tamil', 'sort_order', 'metadata'],
            null=''
        )
        print(f"  [OK] Bulk inserted {len(self.sections)} sections")

    def bulk_insert_verses(self):
        """Bulk insert verses using PostgreSQL COPY"""
        if not self.verses:
            return

        print(f"  Bulk inserting {len(self.verses)} verses...")

        buffer = io.StringIO()
        for verse in self.verses:
            import json
            metadata_json = json.dumps(verse['metadata'], ensure_ascii=False) if verse['metadata'] else ''

            fields = [
                str(verse['verse_id']),
                str(verse['work_id']),
                str(verse['section_id']),
                str(verse['verse_number']),
                verse['verse_type'],
                verse['verse_type_tamil'],
                str(verse['total_lines']),
                str(verse['sort_order']),
                metadata_json
            ]
            buffer.write('\t'.join(fields) + '\n')

        buffer.seek(0)
        self.cursor.copy_from(
            buffer, 'verses',
            columns=['verse_id', 'work_id', 'section_id', 'verse_number', 'verse_type',
                    'verse_type_tamil', 'total_lines', 'sort_order', 'metadata'],
            null=''
        )
        print(f"  [OK] Bulk inserted {len(self.verses)} verses")

    def bulk_insert_lines(self):
        """Bulk insert lines using PostgreSQL COPY"""
        if not self.lines:
            return

        print(f"  Bulk inserting {len(self.lines)} lines...")

        buffer = io.StringIO()
        for line in self.lines:
            # Clean line_text to remove tabs and newlines
            line_text = str(line['line_text']).replace('\t', ' ').replace('\n', ' ').replace('\r', '')

            fields = [
                str(line['line_id']),
                str(line['verse_id']),
                str(line['line_number']),
                line_text
            ]
            buffer.write('\t'.join(fields) + '\n')

        buffer.seek(0)
        self.cursor.copy_from(
            buffer, 'lines',
            columns=['line_id', 'verse_id', 'line_number', 'line_text'],
            null=''
        )
        print(f"  [OK] Bulk inserted {len(self.lines)} lines")

    def bulk_insert_words(self):
        """Bulk insert words using PostgreSQL COPY"""
        if not self.words:
            return

        print(f"  Bulk inserting {len(self.words)} words...")

        buffer = io.StringIO()
        for word in self.words:
            fields = [
                str(word['word_id']),
                str(word['line_id']),
                str(word['word_position']),
                word['word_text'],
                word['sandhi_split'] if word['sandhi_split'] else ''
            ]
            buffer.write('\t'.join(fields) + '\n')

        buffer.seek(0)
        self.cursor.copy_from(
            buffer, 'words',
            columns=['word_id', 'line_id', 'word_position', 'word_text', 'sandhi_split'],
            null=''
        )
        print(f"  [OK] Bulk inserted {len(self.words)} words")

    def import_data(self):
        """Execute bulk imports in correct order"""
        print("\n=== PHASE 2: Bulk inserting into database ===")

        try:
            self.bulk_insert_works()
            self.bulk_insert_work_collections()
            self.bulk_insert_sections()
            self.bulk_insert_verses()
            self.bulk_insert_lines()
            self.bulk_insert_words()

            self.conn.commit()
            print("[OK] Phase 2 complete: All data committed")

        except Exception as e:
            print(f"\n[ERROR] Bulk insert failed: {e}")
            self.conn.rollback()
            raise

    def close(self):
        """Close database connection"""
        self.cursor.close()
        self.conn.close()


def main():
    # Get database connection string
    db_connection = os.getenv('DATABASE_URL', "postgresql://postgres:postgres@localhost/tamil_literature")
    if len(sys.argv) > 1:
        db_connection = sys.argv[1]

    # File path
    script_dir = Path(__file__).parent
    project_dir = script_dir.parent
    file_path = project_dir / "Tamil-Source-TamilConcordence" / "6_பக்தி இலக்கியம்" / "8.2 எட்டாம் திருமுறை.txt"

    print("="*70)
    print("  THIRUKOVAYAR BULK IMPORT")
    print("="*70)
    print(f"Database: {db_connection[:50]}...")
    print(f"File: {file_path.name}")

    if not file_path.exists():
        print(f"\n[ERROR] File not found: {file_path}")
        sys.exit(1)

    importer = ThirukovayarBulkImporter(db_connection)

    try:
        # Ensure collection exists
        importer.ensure_collection_exists()

        # Parse file
        importer.parse_thirukovayar(file_path)

        # Import to database
        importer.import_data()

        print("\n" + "="*70)
        print("[OK] Import complete!")
        print(f"  Works: {len(importer.works)}")
        print(f"  Sections: {len(importer.sections)}")
        print(f"  Verses: {len(importer.verses)}")
        print(f"  Lines: {len(importer.lines)}")
        print(f"  Words: {len(importer.words)}")
        print("="*70)

    except Exception as e:
        print(f"\n[ERROR] Import failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        importer.close()


if __name__ == '__main__':
    main()
