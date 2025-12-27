#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Thirumurai Bulk Import - Fast 2-phase import using PostgreSQL COPY
Phase 1: Parse text → Build data structures in memory
Phase 2: Bulk COPY into database (1000x faster than INSERT)

Thirumurai Collection (திருமுறை) - 12 files, Collection ID: 321

Structure:
- Files 1-7: Devaram (தேவாரம்) - 7 works by 3 authors
- File 8.1: Thiruvasagam (திருவாசகம்) - 1 work
- File 8.2: Thirukkovayar (திருக்கோவையார்) - 1 work
- File 9: Thiruvisaippa child collection (ID: 3211)
  - Each author creates a work: "Author பதிகங்கள்" (~10 works)
  - @ sections become sections within each author's work
- File 10: Thirumanthiram (திருமந்திரம்) - 1 work
- File 11: Each author creates a separate work (~11 works)
  - Author names with "பாசுரங்கள்" suffix are cleaned
  - @ sections become sections within each author's work
- File 12: Periya Puranam (பெரியபுராணம்) - 1 work
"""

import re
import psycopg2
from pathlib import Path
import csv
import io
import sys
import os
from word_cleaning import split_and_clean_words

class ThirumuraiBulkImporter:
    def __init__(self, db_connection_string: str):
        """Initialize importer"""
        self.conn = psycopg2.connect(db_connection_string)
        self.cursor = self.conn.cursor()

        # Data containers
        self.works = []
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

        self.cursor.execute("SELECT COALESCE(MAX(work_id), 0) FROM works")
        self.work_id = self.cursor.fetchone()[0] + 1

        print(f"  Starting IDs: work={self.work_id}, section={self.section_id}, verse={self.verse_id}, line={self.line_id}, word={self.word_id}")

        # Track current parsing state
        self.current_work_id = None
        self.section_cache = {}

    def _ensure_collection_exists(self):
        """Ensure Thirumurai collection exists"""
        # Check if collection exists
        self.cursor.execute("SELECT collection_id FROM collections WHERE collection_id = %s", (self.collection_id,))
        existing = self.cursor.fetchone()

        if not existing:
            print(f"  Creating Thirumurai collection (ID: {self.collection_id})...")
            self.cursor.execute("""
                INSERT INTO collections (
                    collection_id, collection_name, collection_name_tamil,
                    collection_type, description, sort_order
                )
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                self.collection_id, 'Thirumurai', 'திருமுறை',
                'tradition',
                'Twelve books of Shaivite devotional hymns by various Nayanmars',
                1  # Before Naalayira Divya Prabandham
            ))
            print(f"  [OK] Collection created (will commit with bulk data)")
        else:
            print(f"  Found existing Thirumurai collection (ID: {self.collection_id})")

    def _create_child_collection(self, collection_id, collection_name, collection_name_tamil, parent_id, sort_order, description=None):
        """Create or get a child collection"""
        # Check if collection exists
        self.cursor.execute("SELECT collection_id FROM collections WHERE collection_id = %s", (collection_id,))
        existing = self.cursor.fetchone()

        if not existing:
            print(f"  Creating child collection: {collection_name_tamil} (ID: {collection_id})...")
            self.cursor.execute("""
                INSERT INTO collections (
                    collection_id, collection_name, collection_name_tamil,
                    collection_type, description, parent_collection_id, sort_order
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                collection_id, collection_name, collection_name_tamil,
                'tradition', description, parent_id, sort_order
            ))
            print(f"  [OK] Child collection created (will commit with bulk data)")
        else:
            print(f"  Found existing child collection: {collection_name_tamil} (ID: {collection_id})")

        return collection_id

    def _create_work(self, work_name, work_name_tamil, author, author_tamil, canonical_order, period='6th-12th century CE'):
        """Create a work entry and return work_id"""
        # Check if work already exists
        self.cursor.execute("SELECT work_id FROM works WHERE work_name = %s AND work_name_tamil = %s",
                          (work_name, work_name_tamil))
        existing = self.cursor.fetchone()

        if existing:
            print(f"  [ERROR] Work {work_name_tamil} already exists (ID: {existing[0]})")
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
            'period': period,
            'canonical_order': canonical_order
        })

        print(f"  Created work: {work_name_tamil} (ID: {work_id}, Canonical: {canonical_order})")
        return work_id

    def parse_devaram_file(self, file_path, file_num):
        """
        Parse Devaram files (Files 1-7)
        Structure: Numbered temple sections → # verses
        """
        print(f"\nParsing File {file_num}: {Path(file_path).name}")

        with open(file_path, 'r', encoding='utf-8') as f:
            lines_text = f.readlines()

        # Parse first line to get author and work name
        first_line = lines_text[0].strip()
        match = re.match(r'(.+?)\s*-\s*(.+?)\s+\d+\.', first_line)
        if match:
            author_tamil = match.group(1).strip()
            work_base = match.group(2).strip()
        else:
            author_tamil = "Unknown"
            work_base = "தேவாரம்"

        # Map file number to Thirumurai name
        thirumurai_names = {
            1: "முதலாம் திருமுறை", 2: "இரண்டாம் திருமுறை", 3: "மூன்றாம் திருமுறை",
            4: "நான்காம் திருமுறை", 5: "ஐந்தாம் திருமுறை", 6: "ஆறாம் திருமுறை",
            7: "ஏழாம் திருமுறை"
        }

        work_name_tamil = f"{work_base} - {thirumurai_names[file_num]}"
        author_english = author_tamil  # Can add transliteration if needed

        # Create work (canonical_order = 320 + file_num)
        work_id = self._create_work(
            work_name=work_name_tamil,
            work_name_tamil=work_name_tamil,
            author=author_english,
            author_tamil=author_tamil,
            canonical_order=320 + file_num
        )

        if not work_id:
            return

        self.current_work_id = work_id
        current_section_id = None
        current_verse_lines = []
        verse_count = 0

        for line in lines_text[1:]:  # Skip first line
            line = line.strip()
            if not line or line == 'மேல்' or line.startswith('**'):
                continue

            # Check for numbered section (temple)
            section_match = re.match(r'^(\d+)\.\s*(.+)', line)
            if section_match:
                section_num = int(section_match.group(1))
                section_name = section_match.group(2).strip()

                # Remove பண் part if present
                section_name = re.sub(r':\s*பண்\s*-\s*.+$', '', section_name).strip()

                current_section_id = self._get_or_create_section(
                    work_id, None, 'Temple', 'தலம்', section_num, section_name
                )
                continue

            # Check for verse marker
            verse_match = re.match(r'^#(\d+)', line)
            if verse_match:
                if current_verse_lines:
                    self._add_verse(work_id, current_section_id, verse_count, current_verse_lines)
                    current_verse_lines = []

                verse_count += 1
                continue

            # Regular verse line
            if verse_count > 0:
                cleaned = line.replace('…', '').strip()
                if cleaned:
                    current_verse_lines.append(cleaned)

        # Save last verse
        if current_verse_lines:
            self._add_verse(work_id, current_section_id, verse_count, current_verse_lines)

        print(f"  [OK] Parsed {len([v for v in self.verses if v['work_id'] == work_id])} verses")

    def parse_thiruvasagam(self, file_path, file_num):
        """
        Parse Thiruvasagam (File 8.1)
        Structure: @ sections → continuous verses (some #, some not)
        """
        print(f"\nParsing File {file_num}: {Path(file_path).name}")

        with open(file_path, 'r', encoding='utf-8') as f:
            lines_text = f.readlines()

        work_name_tamil = "திருவாசகம் - எட்டாம் திருமுறை"
        work_id = self._create_work(
            work_name=work_name_tamil,
            work_name_tamil=work_name_tamil,
            author="Manikkavasagar",
            author_tamil="மாணிக்கவாசகர்",
            canonical_order=328,
            period='9th century CE'
        )

        if not work_id:
            return

        self.current_work_id = work_id
        current_section_id = None
        current_verse_lines = []
        verse_count = 0

        for line in lines_text[1:]:
            line = line.strip()
            if not line or line == 'மேல்' or line.startswith('**'):
                continue

            # Check for @ section marker
            section_match = re.match(r'^@(\d+)\s+(.+)', line)
            if section_match:
                # Save accumulated lines from previous section as ONE verse
                if current_verse_lines:
                    # If no # markers were used, this is verse 1 of the section
                    if verse_count == 0:
                        verse_count = 1
                    self._add_verse(work_id, current_section_id, verse_count, current_verse_lines)
                    current_verse_lines = []

                section_num = int(section_match.group(1))
                section_name = section_match.group(2).strip()
                current_section_id = self._get_or_create_section(
                    work_id, None, 'Pathigam', 'பதிகம்', section_num, section_name
                )
                verse_count = 0
                continue

            # Check for # verse marker (some sections have them)
            verse_match = re.match(r'^#(\d+)', line)
            if verse_match:
                if current_verse_lines:
                    self._add_verse(work_id, current_section_id, verse_count, current_verse_lines)
                    current_verse_lines = []
                verse_count += 1
                continue

            # Regular line - accumulate for current section
            if current_section_id:
                # Remove line numbers and clean
                cleaned = re.sub(r'\s+\d+\s*$', '', line)
                cleaned = cleaned.replace('…', '').strip()

                # Skip standalone line numbers
                if re.match(r'^\d+$', cleaned):
                    continue

                # Accumulate Tamil text lines
                if cleaned and re.search(r'[\u0B80-\u0BFF]', cleaned):
                    current_verse_lines.append(cleaned)

        # Save last verse
        if current_verse_lines:
            if verse_count == 0:
                verse_count = 1
            self._add_verse(work_id, current_section_id, verse_count, current_verse_lines)

        print(f"  [OK] Parsed {len([v for v in self.verses if v['work_id'] == work_id])} verses")

    def parse_thirukkovayar(self, file_path, file_num):
        """
        Parse Thirukkovayar (File 8.2)
        Structure: * main → *N sub → *N.M subsub → # verses
        """
        print(f"\nParsing File {file_num}: {Path(file_path).name}")

        with open(file_path, 'r', encoding='utf-8') as f:
            lines_text = f.readlines()

        work_name_tamil = "திருக்கோவையார் - எட்டாம் திருமுறை"
        work_id = self._create_work(
            work_name=work_name_tamil,
            work_name_tamil=work_name_tamil,
            author="Manikkavasagar",
            author_tamil="மாணிக்கவாசகர்",
            canonical_order=329,
            period='9th century CE'
        )

        if not work_id:
            return

        self.current_work_id = work_id
        main_section_id = None
        sub_section_id = None
        subsub_section_id = None
        current_verse_lines = []
        verse_count = 0

        for line in lines_text[1:]:
            line = line.strip()
            if not line or line == 'மேல்' or line.startswith('**'):
                continue

            # Check for main section: * [name] - [tamil]
            main_match = re.match(r'^\*\s+([^-*]+)\s*-\s*(.+)', line)
            if main_match and not line.startswith('**'):
                section_name = main_match.group(2).strip()
                main_section_id = self._get_or_create_section(
                    work_id, None, 'Adhikaram', 'அதிகாரம்', 1, section_name
                )
                sub_section_id = None
                subsub_section_id = None
                continue

            # Check for subsection: *N [name]
            sub_match = re.match(r'^\*(\d+)\s+(.+)', line)
            if sub_match and '.' not in sub_match.group(1):
                section_num = int(sub_match.group(1))
                section_name = sub_match.group(2).strip()
                sub_section_id = self._get_or_create_section(
                    work_id, main_section_id, 'Subsection', 'துறை', section_num, section_name
                )
                subsub_section_id = None
                continue

            # Check for sub-subsection: *N.M [name]
            subsub_match = re.match(r'^\*(\d+)\.(\d+)\s+(.+)', line)
            if subsub_match:
                section_num = int(subsub_match.group(2))
                section_name = subsub_match.group(3).strip()
                subsub_section_id = self._get_or_create_section(
                    work_id, sub_section_id, 'Subtopic', 'இயல்', section_num, section_name
                )
                continue

            # Check for verse marker
            verse_match = re.match(r'^#(\d+)', line)
            if verse_match:
                if current_verse_lines:
                    active_section = subsub_section_id or sub_section_id or main_section_id
                    self._add_verse(work_id, active_section, verse_count, current_verse_lines)
                    current_verse_lines = []
                verse_count += 1
                continue

            # Regular verse line
            if verse_count > 0:
                cleaned = line.replace('…', '').strip()
                if cleaned:
                    current_verse_lines.append(cleaned)

        if current_verse_lines:
            active_section = subsub_section_id or sub_section_id or main_section_id
            self._add_verse(work_id, active_section, verse_count, current_verse_lines)

        print(f"  [OK] Parsed {len([v for v in self.verses if v['work_id'] == work_id])} verses")

    def parse_file_9(self, file_path, file_num):
        """
        Parse File 9: Thiruvisaippa and Thiruppallandu
        - Each author gets a separate work: "Author பதிகங்கள்"
        - @ sections become sections within each author's work
        """
        print(f"\nParsing File {file_num}: {Path(file_path).name}")

        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Split at ** திருப்பல்லாண்டு marker
        parts = re.split(r'\*\*\s*திருப்பல்லாண்டு', content, maxsplit=1)

        # Parse Thiruvisaippa (first part) - authors 1-9, canonical orders 330-338
        self._parse_file_9_authors(parts[0], 330, max_author=9)

        # Parse Thiruppallandu (second part) - author 10, canonical order 339
        if len(parts) > 1:
            self._parse_file_9_authors(parts[1], 339, author_offset=10)

    def _parse_file_9_authors(self, content, base_canonical_order, max_author=None, author_offset=0):
        """
        Parse File 9 with each author as a separate work: "Author பதிகங்கள்"
        @ sections become sections within each work
        """
        lines = content.split('\n')
        current_work_id = None
        current_section_id = None
        current_verse_lines = []
        verse_count = 0
        author_count = 0

        for line in lines:
            line = line.strip()
            if not line or line.startswith('**') or line.startswith('****') or line == '*':
                continue

            # Check for & author marker - creates a new work
            author_match = re.match(r'^&(\d+)\s+(.+)', line)
            if author_match:
                author_num = int(author_match.group(1))

                # Skip if outside range
                if max_author and author_num > max_author:
                    break
                if author_offset and author_num < author_offset:
                    continue

                # Save previous verse if any
                if current_verse_lines and current_section_id and current_work_id:
                    self._add_verse(current_work_id, current_section_id, verse_count, current_verse_lines)
                    current_verse_lines = []

                # Extract author name
                author_name_tamil = author_match.group(2).strip()

                # Create work: "Author பதிகங்கள்"
                work_name_tamil = f"{author_name_tamil} பதிகங்கள்"
                author_count += 1

                current_work_id = self._create_work(
                    work_name=work_name_tamil,
                    work_name_tamil=work_name_tamil,
                    author=author_name_tamil,
                    author_tamil=author_name_tamil,
                    canonical_order=base_canonical_order + author_count - 1,
                    period='6th-12th century CE'
                )

                current_section_id = None
                verse_count = 0
                continue

            # Check for @ section marker
            section_match = re.match(r'^@(\d+)\s+(.+)', line)
            if section_match and current_work_id:
                if current_verse_lines and current_section_id:
                    self._add_verse(current_work_id, current_section_id, verse_count, current_verse_lines)
                    current_verse_lines = []

                section_num = int(section_match.group(1))
                section_name = section_match.group(2).strip()
                current_section_id = self._get_or_create_section(
                    current_work_id, None, 'Pathigam', 'பதிகம்', section_num, section_name
                )
                verse_count = 0
                continue

            # Check for verse marker
            verse_match = re.match(r'^#(\d+)', line)
            if verse_match and current_work_id:
                if current_verse_lines and current_section_id:
                    self._add_verse(current_work_id, current_section_id, verse_count, current_verse_lines)
                    current_verse_lines = []
                verse_count += 1
                continue

            # Regular verse line
            if verse_count > 0 and current_section_id and current_work_id:
                cleaned = line.replace('…', '').strip()
                if cleaned and not re.match(r'^\d+$', cleaned):
                    current_verse_lines.append(cleaned)

        # Save last verse
        if current_verse_lines and current_section_id and current_work_id:
            self._add_verse(current_work_id, current_section_id, verse_count, current_verse_lines)

        print(f"  [OK] Parsed {author_count} author works from File 9 section")

    def _parse_multi_author_work(self, work_id, content, max_author=None, author_offset=0):
        """
        Parse work with & author markers and @ section markers
        Creates hierarchy: Author section → Work sections → Verses
        """
        lines = content.split('\n')
        current_author_section = None
        current_work_section = None
        current_verse_lines = []
        verse_count = 0

        for line in lines:
            line = line.strip()
            if not line or line == 'மேல்' or line.startswith('**') or line.startswith('****'):
                continue

            # Check for & author marker
            author_match = re.match(r'^&(\d+)\s+(.+)', line)
            if author_match:
                author_num = int(author_match.group(1))
                if max_author and author_num > max_author:
                    break
                if author_offset and author_num < author_offset:
                    continue

                if current_verse_lines and current_work_section:
                    self._add_verse(work_id, current_work_section, verse_count, current_verse_lines)
                    current_verse_lines = []

                author_name = author_match.group(2).strip()
                current_author_section = self._get_or_create_section(
                    work_id, None, 'Author', 'ஆசிரியர்', author_num, author_name
                )
                current_work_section = None
                verse_count = 0
                continue

            # Check for @ work section marker
            section_match = re.match(r'^@(\d+)\s+(.+)', line)
            if section_match:
                if current_verse_lines and current_work_section:
                    self._add_verse(work_id, current_work_section, verse_count, current_verse_lines)
                    current_verse_lines = []

                section_num = int(section_match.group(1))
                section_name = section_match.group(2).strip()
                current_work_section = self._get_or_create_section(
                    work_id, current_author_section, 'Work', 'படைப்பு', section_num, section_name
                )
                verse_count = 0
                continue

            # Check for verse marker
            verse_match = re.match(r'^#(\d+)', line)
            if verse_match:
                if current_verse_lines and current_work_section:
                    self._add_verse(work_id, current_work_section, verse_count, current_verse_lines)
                    current_verse_lines = []
                verse_count += 1
                continue

            # Regular verse line
            if verse_count > 0 and current_work_section:
                cleaned = line.replace('…', '').strip()
                if cleaned and not re.match(r'^\d+$', cleaned):
                    current_verse_lines.append(cleaned)

        if current_verse_lines and current_work_section:
            self._add_verse(work_id, current_work_section, verse_count, current_verse_lines)

        print(f"  [OK] Parsed {len([v for v in self.verses if v['work_id'] == work_id])} verses")

    def parse_thirumanthiram(self, file_path, file_num):
        """
        Parse Thirumanthiram (File 10)
        Structure: @ Thanthiram sections → # verses
        """
        print(f"\nParsing File {file_num}: {Path(file_path).name}")

        with open(file_path, 'r', encoding='utf-8') as f:
            lines_text = f.readlines()

        work_name_tamil = "திருமந்திரம் - பத்தாம் திருமுறை"
        work_id = self._create_work(
            work_name=work_name_tamil,
            work_name_tamil=work_name_tamil,
            author="Thirumular",
            author_tamil="திருமூலர்",
            canonical_order=340,
            period='6th-10th century CE'
        )

        if not work_id:
            return

        self.current_work_id = work_id
        current_section_id = None
        current_verse_lines = []
        verse_count = 0

        for line in lines_text[1:]:
            line = line.strip()
            if not line or line == 'மேல்' or line.startswith('**'):
                continue

            # Check for @ section (Thanthiram)
            section_match = re.match(r'^@(\d+)\s+(.+)', line)
            if section_match:
                if current_verse_lines:
                    self._add_verse(work_id, current_section_id, verse_count, current_verse_lines)
                    current_verse_lines = []

                section_num = int(section_match.group(1))
                section_name = section_match.group(2).strip()
                current_section_id = self._get_or_create_section(
                    work_id, None, 'Thanthiram', 'தந்திரம்', section_num, section_name
                )
                verse_count = 0
                continue

            # Check for verse marker
            verse_match = re.match(r'^#(\d+)', line)
            if verse_match:
                if current_verse_lines:
                    self._add_verse(work_id, current_section_id, verse_count, current_verse_lines)
                    current_verse_lines = []
                verse_count += 1
                continue

            # Regular verse line
            if verse_count > 0:
                cleaned = line.replace('…', '').strip()
                if cleaned and not re.match(r'^\d+$', cleaned):
                    current_verse_lines.append(cleaned)

        if current_verse_lines:
            self._add_verse(work_id, current_section_id, verse_count, current_verse_lines)

        print(f"  [OK] Parsed {len([v for v in self.verses if v['work_id'] == work_id])} verses")

    def parse_file_11(self, file_path, file_num):
        """
        Parse File 11: Saiva Prabandha Malai
        Each & author creates a separate work (not a combined work)
        Structure: & author → @ sections → # verses
        """
        print(f"\nParsing File {file_num}: {Path(file_path).name}")

        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Parse each author as a separate work
        self._parse_file_11_multi_works(content, file_num)

    def _parse_file_11_multi_works(self, content, file_num):
        """
        Parse File 11 with each author as a separate work
        """
        lines = content.split('\n')
        current_work_id = None
        current_section_id = None
        current_verse_lines = []
        verse_count = 0
        author_count = 0
        base_canonical_order = 341  # Starting order for File 11 works (after File 10 at 340)

        for line in lines:
            line = line.strip()
            if not line or line.startswith('**') or line.startswith('****') or line == '*':
                continue

            # Check for & author marker - creates a new work
            author_match = re.match(r'^&(\d+)\s+(.+)', line)
            if author_match:
                # Save previous verse if any
                if current_verse_lines and current_section_id and current_work_id:
                    self._add_verse(current_work_id, current_section_id, verse_count, current_verse_lines)
                    current_verse_lines = []

                # Extract author name and remove "பாசுரங்கள்" if present
                author_name_tamil = author_match.group(2).strip()
                author_name_clean = re.sub(r'\s*பாசுரங்கள்\s*$', '', author_name_tamil)

                # Create a new work for this author
                work_name_tamil = f"{author_name_clean} - பதினொன்றாம் திருமுறை"
                author_count += 1

                current_work_id = self._create_work(
                    work_name=work_name_tamil,
                    work_name_tamil=work_name_tamil,
                    author=author_name_clean,
                    author_tamil=author_name_clean,
                    canonical_order=base_canonical_order + author_count - 1,
                    period='6th-12th century CE'
                )

                current_section_id = None
                verse_count = 0
                continue

            # Check for @ section marker
            section_match = re.match(r'^@(\d+)\s+(.+)', line)
            if section_match and current_work_id:
                if current_verse_lines and current_section_id:
                    self._add_verse(current_work_id, current_section_id, verse_count, current_verse_lines)
                    current_verse_lines = []

                section_num = int(section_match.group(1))
                section_name = section_match.group(2).strip()
                current_section_id = self._get_or_create_section(
                    current_work_id, None, 'Section', 'பகுதி', section_num, section_name
                )
                verse_count = 0
                continue

            # Check for verse marker
            verse_match = re.match(r'^#(\d+)', line)
            if verse_match and current_work_id:
                if current_verse_lines and current_section_id:
                    self._add_verse(current_work_id, current_section_id, verse_count, current_verse_lines)
                    current_verse_lines = []
                verse_count += 1
                continue

            # Regular verse line
            if verse_count > 0 and current_section_id and current_work_id:
                cleaned = line.replace('…', '').strip()
                if cleaned and not re.match(r'^\d+$', cleaned):
                    current_verse_lines.append(cleaned)

        # Save last verse
        if current_verse_lines and current_section_id and current_work_id:
            self._add_verse(current_work_id, current_section_id, verse_count, current_verse_lines)

        print(f"  [OK] Parsed {author_count} works from File 11")

    def parse_periya_puranam(self, file_path, file_num):
        """
        Parse Periya Puranam (File 12)
        Structure: & or numbered Sarrukkam → @ Puranam → # verses
        """
        print(f"\nParsing File {file_num}: {Path(file_path).name}")

        with open(file_path, 'r', encoding='utf-8') as f:
            lines_text = f.readlines()

        work_name_tamil = "பெரியபுராணம் - பன்னிரண்டாம் திருமுறை"
        work_id = self._create_work(
            work_name=work_name_tamil,
            work_name_tamil=work_name_tamil,
            author="Sekkizhar",
            author_tamil="சேக்கிழார்",
            canonical_order=352,
            period='12th century CE'
        )

        if not work_id:
            return

        self.current_work_id = work_id
        current_sarrukkam_id = None
        current_puranam_id = None
        current_verse_lines = []
        verse_count = 0

        for line in lines_text[1:]:
            line = line.strip()
            if not line or line == 'மேல்' or line.startswith('**') or line.startswith('****') or line == '*':
                continue

            # Check for Sarrukkam: & or numbered format
            sarrukkam_match = re.match(r'^&(\d+)\s+(.+)', line)
            if not sarrukkam_match:
                sarrukkam_match = re.match(r'^(\d+)\.\s*(.+?)\s*சருக்கம்', line)

            if sarrukkam_match:
                if current_verse_lines and current_puranam_id:
                    self._add_verse(work_id, current_puranam_id, verse_count, current_verse_lines)
                    current_verse_lines = []

                section_num = int(sarrukkam_match.group(1))
                section_name = sarrukkam_match.group(2).strip()
                if not section_name.endswith('சருக்கம்'):
                    section_name += ' சருக்கம்'

                current_sarrukkam_id = self._get_or_create_section(
                    work_id, None, 'Sarrukkam', 'சருக்கம்', section_num, section_name
                )
                current_puranam_id = None
                verse_count = 0
                continue

            # Check for @ Puranam (subsection)
            puranam_match = re.match(r'^@(\d+)\s+(.+)', line)
            if puranam_match:
                if current_verse_lines and current_puranam_id:
                    self._add_verse(work_id, current_puranam_id, verse_count, current_verse_lines)
                    current_verse_lines = []

                section_num = int(puranam_match.group(1))
                section_name = puranam_match.group(2).strip()
                current_puranam_id = self._get_or_create_section(
                    work_id, current_sarrukkam_id, 'Puranam', 'புராணம்', section_num, section_name
                )
                verse_count = 0
                continue

            # Check for verse marker
            verse_match = re.match(r'^#(\d+)', line)
            if verse_match:
                if current_verse_lines and current_puranam_id:
                    self._add_verse(work_id, current_puranam_id, verse_count, current_verse_lines)
                    current_verse_lines = []
                verse_count += 1
                continue

            # Regular verse line
            if verse_count > 0 and current_puranam_id:
                cleaned = line.replace('…', '').strip()
                if cleaned and not re.match(r'^\d+$', cleaned):
                    current_verse_lines.append(cleaned)

        if current_verse_lines and current_puranam_id:
            self._add_verse(work_id, current_puranam_id, verse_count, current_verse_lines)

        print(f"  [OK] Parsed {len([v for v in self.verses if v['work_id'] == work_id])} verses")

    def _get_or_create_section(self, work_id, parent_id, level_type, level_type_tamil, section_num, section_name):
        """Get or create section and return section_id"""
        cache_key = (work_id, parent_id, level_type, section_num, section_name)

        if cache_key in self.section_cache:
            return self.section_cache[cache_key]

        section_id = self.section_id
        self.section_id += 1

        self.sections.append({
            'section_id': section_id,
            'work_id': work_id,
            'parent_section_id': parent_id,
            'level_type': level_type,
            'level_type_tamil': level_type_tamil,
            'section_number': section_num,
            'section_name': section_name,
            'section_name_tamil': section_name,
            'sort_order': section_num
        })

        self.section_cache[cache_key] = section_id
        return section_id

    def _add_verse(self, work_id, section_id, verse_num, verse_lines):
        """Add verse with lines and words to memory"""
        if not verse_lines:
            return

        verse_id = self.verse_id
        self.verse_id += 1

        self.verses.append({
            'verse_id': verse_id,
            'work_id': work_id,
            'section_id': section_id,
            'verse_number': verse_num,
            'verse_type': 'verse',
            'verse_type_tamil': 'பாடல்',
            'total_lines': len(verse_lines),
            'sort_order': verse_num
        })

        for line_num, line_text in enumerate(verse_lines, start=1):
            line_id = self.line_id
            self.line_id += 1

            # Clean line text: remove trailing numbers, normalize whitespace, remove tabs
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
        if self.verses:
            print(f"  Inserting {len(self.verses)} verses...")
            self._bulk_copy('verses', self.verses,
                           ['verse_id', 'work_id', 'section_id', 'verse_number', 'verse_type',
                            'verse_type_tamil', 'total_lines', 'sort_order'])

        # Insert lines
        if self.lines:
            print(f"  Inserting {len(self.lines)} lines...")
            self._bulk_copy('lines', self.lines,
                           ['line_id', 'verse_id', 'line_number', 'line_text'])

        # Insert words
        if self.words:
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

    # Define all Thirumurai files
    files = [
        (1, base_dir / "1.முதலாம் திருமுறை.txt", "devaram"),
        (2, base_dir / "2.இரண்டாம் திருமுறை.txt", "devaram"),
        (3, base_dir / "3.மூன்றாம் திருமுறை.txt", "devaram"),
        (4, base_dir / "4.நான்காம்_திருமுறை.txt", "devaram"),
        (5, base_dir / "5.ஐந்தாம் திருமுறை.txt", "devaram"),
        (6, base_dir / "6.ஆறாம் திருமுறை.txt", "devaram"),
        (7, base_dir / "7.ஏழாம் திருமுறை.txt", "devaram"),
        (8.1, base_dir / "8.1எட்டாம் திருமுறை.txt", "thiruvasagam"),
        (8.2, base_dir / "8.2 எட்டாம் திருமுறை.txt", "thirukkovayar"),
        (9, base_dir / "9.ஒன்பதாம் திருமுறை.txt", "file_9"),
        (10, base_dir / "10.பத்தாம் திருமுறை.txt", "thirumanthiram"),
        (11, base_dir / "11.பதினொன்றாம் திருமுறை.txt", "file_11"),
        (12, base_dir / "12.பன்னிரண்டாம் திருமுறை.txt", "periya_puranam"),
    ]

    print("="*70)
    print("Thirumurai Bulk Import - Fast 2-Phase Import")
    print("="*70)
    print(f"Database: {db_connection[:50]}...")
    print(f"Files: 13 (Files 1-12, with 8 split into 8.1 and 8.2)")

    importer = ThirumuraiBulkImporter(db_connection)

    try:
        # Parse all files
        for file_num, file_path, file_type in files:
            if not file_path.exists():
                print(f"  [ERROR] File not found: {file_path}")
                continue

            if file_type == "devaram":
                importer.parse_devaram_file(str(file_path), int(file_num))
            elif file_type == "thiruvasagam":
                importer.parse_thiruvasagam(str(file_path), int(file_num))
            elif file_type == "thirukkovayar":
                importer.parse_thirukkovayar(str(file_path), int(file_num))
            elif file_type == "file_9":
                importer.parse_file_9(str(file_path), int(file_num))
            elif file_type == "thirumanthiram":
                importer.parse_thirumanthiram(str(file_path), int(file_num))
            elif file_type == "file_11":
                importer.parse_file_11(str(file_path), int(file_num))
            elif file_type == "periya_puranam":
                importer.parse_periya_puranam(str(file_path), int(file_num))

        # Bulk insert
        importer.bulk_insert()

        print("\n" + "="*70)
        print("[OK] Import complete!")
        print(f"  - Works created: {len(importer.works)}")
        print(f"  - Sections imported: {len(importer.sections)}")
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
