#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Thiruvisaippa & Thiruppallandu Bulk Import - Fast 2-phase import using PostgreSQL COPY
Phase 1: Parse text → Build data structures in memory
Phase 2: Bulk COPY into database (1000x faster than INSERT)

File 9 - Thirumurai 9 (ஒன்பதாம் திருமுறை), Collection ID: 3220

10 Works:
1-9: Thiruvisaippa (திருவிசைப்பா) - 9 authors
10: Thiruppallandu (திருப்பல்லாண்டு) - Sendhanaár

Structure per work:
- பதிகம் (Pathigam) sections
  - Section metadata: பண் (Pan)
  - பாடல் (Verses)

Markers:
&N [Author] ^ [Work Name]  → New work
@N [Section Name]          → New section (பதிகம்)
** பண் :[Pan Name]         → Section metadata
#N                         → Verse number
"""

import re
import psycopg2
from pathlib import Path
import io
import sys
import os
from word_cleaning import split_and_clean_words

class ThiruvisaippaBulkImporter:
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

        # Track current parsing state
        self.current_work_id = None
        self.current_work_num = 0

    def ensure_collection_exists(self):
        """Ensure the 9th Thirumurai collection and sub-collection exist"""
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

        # Check if 9th Thirumurai collection exists (3219)
        self.cursor.execute("SELECT collection_id FROM collections WHERE collection_id = 3219")
        if not self.cursor.fetchone():
            print("  Creating 9th Thirumurai collection (3219)...")
            self.cursor.execute("""
                INSERT INTO collections (collection_id, collection_name, collection_name_tamil,
                                       collection_type, parent_collection_id, description, sort_order)
                VALUES (3219, 'Ninth Thirumurai', 'ஒன்பதாம் திருமுறை', 'devotional', 321,
                        '9th Thirumurai - Thiruvisaippa and Thiruppallandu by 10 saints', 3219)
            """)
            self.conn.commit()
            print("  [OK] 9th Thirumurai collection created")
        else:
            print("  [OK] 9th Thirumurai collection already exists")

        # Check if Thiruvisaippa sub-collection exists (32191)
        self.cursor.execute("SELECT collection_id FROM collections WHERE collection_id = 32191")
        if not self.cursor.fetchone():
            print("  Creating Thiruvisaippa sub-collection (32191)...")
            self.cursor.execute("""
                INSERT INTO collections (collection_id, collection_name, collection_name_tamil,
                                       collection_type, parent_collection_id, description, sort_order)
                VALUES (32191, 'Thiruvisaippa', 'திருவிசைப்பா', 'devotional', 3219,
                        'Thiruvisaippa - Works 1-9 of 9th Thirumurai', 32191)
            """)
            self.conn.commit()
            print("  [OK] Thiruvisaippa sub-collection created")
        else:
            print("  [OK] Thiruvisaippa sub-collection already exists")

        # Query and store collection IDs as instance variables
        self.cursor.execute("SELECT collection_id FROM collections WHERE collection_id = 3219")
        self.ninth_thirumurai_collection_id = self.cursor.fetchone()[0]

        self.cursor.execute("SELECT collection_id FROM collections WHERE collection_id = 32191")
        self.thiruvisaippa_subcollection_id = self.cursor.fetchone()[0]

    def parse_file_9(self, file_path):
        """
        Parse File 9 with 10 separate works

        Structure:
        &N [Author] ^ [Work Name]  → Each creates a separate work
        @N [Section Name]          → Pathigam section
        ** பண் :[Pan Name]         → Section metadata
        #N                         → Verse number
        """
        print(f"\n=== PHASE 1: Parsing {Path(file_path).name} ===")

        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        current_work_id = None
        current_section_id = None
        current_pan_metadata = None
        current_verse_lines = []
        verse_count = 0

        for line in lines[1:]:  # Skip first line
            line = line.strip()

            if not line or line == 'மேல்':
                continue

            # Check for work marker: &N [Author] ^ [Work Name]
            work_match = re.match(r'^&(\d+)\s+(.+?)\s+\^\s+(.+)', line)
            if work_match:
                # Save previous verse if any
                if current_verse_lines and current_section_id and current_work_id:
                    self._add_verse(current_work_id, current_section_id, verse_count,
                                  current_verse_lines, current_pan_metadata)
                    current_verse_lines = []

                work_num = int(work_match.group(1))
                author_name = work_match.group(2).strip()
                work_name = work_match.group(3).strip()

                current_work_id = self._create_work(work_num, author_name, work_name)
                current_section_id = None
                current_pan_metadata = None
                verse_count = 0
                continue

            # Check for section marker: @N [Section Name]
            section_match = re.match(r'^@(\d+)\s+(.+)', line)
            if section_match and current_work_id:
                # Save previous verse if any
                if current_verse_lines and current_section_id:
                    self._add_verse(current_work_id, current_section_id, verse_count,
                                  current_verse_lines, current_pan_metadata)
                    current_verse_lines = []

                section_num = int(section_match.group(1))
                section_name = section_match.group(2).strip()

                current_section_id = self._create_section(
                    current_work_id, section_num, section_name
                )
                current_pan_metadata = None
                verse_count = 0
                continue

            # Check for பண் metadata: ** பண் :[Pan Name]
            pan_match = re.match(r'^\*\*\s*பண்\s*[:：]\s*(.+)', line)
            if pan_match and current_section_id:
                pan_name = pan_match.group(1).strip()
                current_pan_metadata = pan_name
                # Update section metadata
                self._update_section_metadata(current_section_id, pan_name)
                continue

            # Skip other ** lines
            if line.startswith('**'):
                continue

            # Check for verse marker: #N
            verse_match = re.match(r'^#(\d+)', line)
            if verse_match and current_work_id and current_section_id:
                # Save previous verse if any
                if current_verse_lines:
                    self._add_verse(current_work_id, current_section_id, verse_count,
                                  current_verse_lines, current_pan_metadata)
                    current_verse_lines = []

                verse_count = int(verse_match.group(1))
                continue

            # Regular verse line
            if verse_count > 0 and current_section_id and current_work_id:
                cleaned = line.replace('…', '').strip()
                if cleaned:
                    current_verse_lines.append(cleaned)

        # Save last verse
        if current_verse_lines and current_section_id and current_work_id:
            self._add_verse(current_work_id, current_section_id, verse_count,
                          current_verse_lines, current_pan_metadata)

        print(f"  [OK] Parsed {len(self.works)} works, {len(self.sections)} sections, {len(self.verses)} verses")

    def _create_work(self, work_num, author_name, work_name):
        """Create a work entry and return work_id"""
        work_id = self.work_id
        self.work_id += 1
        self.current_work_num += 1

        # Works 1-9: Thiruvisaippa sub-collection
        # Work 10: Thiruppallandu → main 9th Thirumurai collection
        if work_num <= 9:
            collection_id = self.thiruvisaippa_subcollection_id
            collection_name = 'Thiruvisaippa'
            collection_name_tamil = 'திருவிசைப்பா'
        else:
            collection_id = self.ninth_thirumurai_collection_id
            collection_name = 'Ninth Thirumurai'
            collection_name_tamil = 'ஒன்பதாம் திருமுறை'

        work_metadata = {
            'tradition': 'Shaivite',
            'collection_id': collection_id,
            'collection_name': collection_name,
            'collection_name_tamil': collection_name_tamil,
            'thirumurai_number': 9,
            'file_work_number': work_num,
            'saint': author_name
        }

        self.works.append({
            'work_id': work_id,
            'work_name': work_name,
            'work_name_tamil': work_name,
            'author': author_name,
            'author_tamil': author_name,
            'period': '6th-12th century CE',
            'canonical_order': 330 + work_num,  # 331-340
            'primary_collection_id': collection_id,
            'metadata': work_metadata
        })

        print(f"  Created work {self.current_work_num}: {work_name} (Author: {author_name}, Collection: {collection_name_tamil})")
        return work_id

    def _create_section(self, work_id, section_num, section_name):
        """Create a section (பதிகம்) and return section_id"""
        section_id = self.section_id
        self.section_id += 1

        self.sections.append({
            'section_id': section_id,
            'work_id': work_id,
            'parent_section_id': None,
            'level_type': 'Pathigam',
            'level_type_tamil': 'பதிகம்',
            'section_number': section_num,
            'section_name': section_name,
            'section_name_tamil': section_name,
            'sort_order': section_num,
            'metadata': {}
        })

        return section_id

    def _update_section_metadata(self, section_id, pan_name):
        """Update section metadata with பண் (Pan) information"""
        for section in self.sections:
            if section['section_id'] == section_id:
                section['metadata']['pan'] = pan_name
                break

    def _add_verse(self, work_id, section_id, verse_num, verse_lines, pan_metadata=None):
        """Add verse with lines and words to memory"""
        if not verse_lines:
            return

        verse_id = self.verse_id
        self.verse_id += 1

        # Build verse metadata
        metadata = {}
        if pan_metadata:
            metadata['pan'] = pan_metadata

        self.verses.append({
            'verse_id': verse_id,
            'work_id': work_id,
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
        """Link works to collections:
        - Works 1-9: Both Thiruvisaippa (primary) and 9th Thirumurai (secondary)
        - Work 10: Only 9th Thirumurai (primary)
        """
        if not self.works:
            return

        print(f"  Linking {len(self.works)} works to collections...")

        # Get next available positions for both collections
        self.cursor.execute("""
            SELECT COALESCE(MAX(position_in_collection), 0) + 1
            FROM work_collections
            WHERE collection_id = %s
        """, (self.thiruvisaippa_subcollection_id,))
        thiruvisaippa_position = self.cursor.fetchone()[0]

        self.cursor.execute("""
            SELECT COALESCE(MAX(position_in_collection), 0) + 1
            FROM work_collections
            WHERE collection_id = %s
        """, (self.ninth_thirumurai_collection_id,))
        ninth_thirumurai_position = self.cursor.fetchone()[0]

        buffer = io.StringIO()
        for work in self.works:
            work_num = work['metadata']['file_work_number']

            if work_num <= 9:
                # Works 1-9: Link to Thiruvisaippa sub-collection (primary)
                fields = [
                    str(work['work_id']),
                    str(self.thiruvisaippa_subcollection_id),
                    str(thiruvisaippa_position),
                    't',  # is_primary = true
                    ''
                ]
                buffer.write('\t'.join(fields) + '\n')
                thiruvisaippa_position += 1

                # Also link to 9th Thirumurai (secondary)
                fields = [
                    str(work['work_id']),
                    str(self.ninth_thirumurai_collection_id),
                    str(ninth_thirumurai_position),
                    'f',  # is_primary = false
                    ''
                ]
                buffer.write('\t'.join(fields) + '\n')
                ninth_thirumurai_position += 1
            else:
                # Work 10: Link only to 9th Thirumurai (primary)
                fields = [
                    str(work['work_id']),
                    str(self.ninth_thirumurai_collection_id),
                    str(ninth_thirumurai_position),
                    't',  # is_primary = true
                    ''
                ]
                buffer.write('\t'.join(fields) + '\n')
                ninth_thirumurai_position += 1

        buffer.seek(0)
        self.cursor.copy_from(
            buffer, 'work_collections',
            columns=['work_id', 'collection_id', 'position_in_collection', 'is_primary', 'notes'],
            null=''
        )
        print(f"  [OK] Linked works: 9 to Thiruvisaippa + 9th Thirumurai, 1 to 9th Thirumurai only")

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
    file_path = project_dir / "Tamil-Source-TamilConcordence" / "6_பக்தி இலக்கியம்" / "9.ஒன்பதாம் திருமுறை.txt"

    print("="*70)
    print("  THIRUVISAIPPA & THIRUPPALLANDU BULK IMPORT (FILE 9)")
    print("="*70)
    print(f"Database: {db_connection[:50]}...")
    print(f"File: {file_path.name}")

    if not file_path.exists():
        print(f"\n[ERROR] File not found: {file_path}")
        sys.exit(1)

    importer = ThiruvisaippaBulkImporter(db_connection)

    try:
        # Ensure collection exists
        importer.ensure_collection_exists()

        # Parse file
        importer.parse_file_9(file_path)

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
