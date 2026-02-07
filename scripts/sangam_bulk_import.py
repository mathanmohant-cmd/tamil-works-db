#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sangam Literature Bulk Import - Fast 2-phase import using PostgreSQL COPY
Phase 1: Parse all text files → Build data structures in memory
Phase 2: Bulk COPY into database (1000x faster than INSERT)

IMPROVEMENTS (2025-12-05):
- Ignore dots/periods used for text alignment (……………………….. or .)
- Ignore line count numbers (multiples of 5: 5, 10, 15, etc.)
- Keep only Tamil characters, hyphens (-), and underscores (_) in words
- Prof. P. Pandiyaraja uses - and _ for specific linguistic segmentation purposes

METADATA EXTRACTION (2026-01-30):
- Extract thinai (திணை) from verse headers: #<num> <thinai>
- Extract author from inline format: #<num> <thinai> - <author>
- Extract author from asterisk lines: * <author>
- Extract pann (பண்) from structured works: ** வண்ணம் : <pann>
- Store all metadata in verses.metadata JSONB column
- Enables rich queries: filter by thinai, author, pann

CRITICAL FIXES (2026-01-31):
- Accept verse #0 for கடவுள் வாழ்த்து (invocation verses)
- Create placeholder verses "-கிடைக்கவில்லை-" for lost/unavailable text
  - Preserves verse numbering (e.g., புறநானூறு #267, #268)
  - Placeholder lines stored but no words created
- Fixed Kalithokai section boundary bug: save poem BEFORE creating new section
  - Prevents last verse of section from being assigned to next section
- Handle "கிடைக்காத பாடல்" markers: create placeholder verses
  - Applies to ஐங்குறுநூறு and other works with missing verses
"""

import re
import psycopg2
from pathlib import Path
from typing import Dict, List
import csv
import io
import os
import json
import sys

class SangamBulkImporter:
    # Map filenames to work information (work_id assigned dynamically)
    # Ordered by standard Sangam literature sequence (1-18)
    SANGAM_WORKS = {
        '1 நற்றிணை.txt': {
            'work_name': 'Natrrinai', 'work_name_tamil': 'நற்றிணை',
            'type': 'thogai', 'description': 'Collection of 400 poems',
            'traditional_order': 2, 'start_year': -100, 'end_year': 100,
            'confidence': 'high', 'notes': 'Considered among the earliest Sangam works'
        },
        '2 குறுந்தொகை.txt': {
            'work_name': 'Kurunthokai', 'work_name_tamil': 'குறுந்தொகை',
            'type': 'thogai', 'description': 'Short poems on love and war',
            'traditional_order': 3, 'start_year': -100, 'end_year': 100,
            'confidence': 'high', 'notes': 'Early Sangam anthology'
        },
        '3 ஐங்குறுநூறு.txt': {
            'work_name': 'Ainkurunuru', 'work_name_tamil': 'ஐங்குறுநூறு',
            'type': 'thogai', 'description': 'Five hundred short poems',
            'traditional_order': 4, 'start_year': -100, 'end_year': 200,
            'confidence': 'high', 'notes': 'Sangam anthology of 500 short love poems'
        },
        '4 பதிற்றுப்பத்து.txt': {
            'work_name': 'Pathitrupathu', 'work_name_tamil': 'பதிற்றுப்பத்து',
            'type': 'thogai', 'description': 'Ten tens of poems',
            'traditional_order': 5, 'start_year': 100, 'end_year': 200,
            'confidence': 'high', 'notes': 'Features Chera kings, slightly later than other anthologies'
        },
        '5 பரிபாடல்.txt': {
            'work_name': 'Paripaadal', 'work_name_tamil': 'பரிபாடல்',
            'type': 'thogai', 'description': 'Songs in Paripadal meter',
            'traditional_order': 6, 'start_year': 100, 'end_year': 200,
            'confidence': 'high', 'notes': 'Religious hymns to Murugan and Thirumal'
        },
        '6 கலித்தொகை.txt': {
            'work_name': 'Kalithokai', 'work_name_tamil': 'கலித்தொகை',
            'type': 'thogai', 'description': 'Collection of Kali meter poems',
            'traditional_order': 7, 'start_year': 100, 'end_year': 250,
            'confidence': 'medium', 'notes': 'Some scholars date to later Sangam period'
        },
        '7 அகநானூறு.txt': {
            'work_name': 'Aganaanuru', 'work_name_tamil': 'அகநானூறு',
            'type': 'thogai', 'description': 'Four hundred poems on love',
            'traditional_order': 8, 'start_year': -100, 'end_year': 200,
            'confidence': 'high', 'notes': '400 love poems from Sangam period'
        },
        '8 புறநானூறு.txt': {
            'work_name': 'Puranaanuru', 'work_name_tamil': 'புறநானூறு',
            'type': 'thogai', 'description': 'Four hundred poems on war and ethics',
            'traditional_order': 9, 'start_year': -100, 'end_year': 200,
            'confidence': 'high', 'notes': 'Historical references help date some poems precisely'
        },
        '9 திருமுருகாற்றுப்படை.txt': {
            'work_name': 'Thirumurugaatruppadai', 'work_name_tamil': 'திருமுருகாற்றுப்படை',
            'type': 'padal', 'description': 'Guide to Lord Murugan',
            'traditional_order': 10, 'start_year': 150, 'end_year': 250,
            'confidence': 'high', 'notes': 'Part of Pathupaattu (Ten Idylls)'
        },
        '10 பொருநராற்றுப்படை.txt': {
            'work_name': 'Porunaraatruppadai', 'work_name_tamil': 'பொருநராற்றுப்படை',
            'type': 'padal', 'description': 'Guide to patron',
            'traditional_order': 11, 'start_year': 150, 'end_year': 250,
            'confidence': 'high', 'notes': 'Part of Pathupaattu (Ten Idylls)'
        },
        '11 சிறுபாணாற்றுப்படை.txt': {
            'work_name': 'Sirupanaatruppadai', 'work_name_tamil': 'சிறுபாணாற்றுப்படை',
            'type': 'padal', 'description': 'Guide to small drum player',
            'traditional_order': 12, 'start_year': 150, 'end_year': 250,
            'confidence': 'high', 'notes': 'Part of Pathupaattu (Ten Idylls)'
        },
        '12 பெரும்பாணாற்றுப்படை.txt': {
            'work_name': 'Perumpanaatruppadai', 'work_name_tamil': 'பெரும்பாணாற்றுப்படை',
            'type': 'padal', 'description': 'Guide to great drum player',
            'traditional_order': 13, 'start_year': 150, 'end_year': 250,
            'confidence': 'high', 'notes': 'Part of Pathupaattu (Ten Idylls)'
        },
        '13 முல்லைப்பாட்டு.txt': {
            'work_name': 'Mullaippaattu', 'work_name_tamil': 'முல்லைப்பாட்டு',
            'type': 'padal', 'description': 'Song of Mullai landscape',
            'traditional_order': 14, 'start_year': 150, 'end_year': 250,
            'confidence': 'high', 'notes': 'Part of Pathupaattu (Ten Idylls)'
        },
        '14 மதுரைக்காஞ்சி.txt': {
            'work_name': 'Madurai kanchi', 'work_name_tamil': 'மதுரைக்காஞ்சி',
            'type': 'padal', 'description': 'Description of Madurai city',
            'traditional_order': 15, 'start_year': 150, 'end_year': 250,
            'confidence': 'high', 'notes': 'Part of Pathupaattu (Ten Idylls)'
        },
        '15 நெடுநல்வாடை.txt': {
            'work_name': 'Nedunalvaadai', 'work_name_tamil': 'நெடுநல்வாடை',
            'type': 'padal', 'description': 'The long north wind',
            'traditional_order': 16, 'start_year': 150, 'end_year': 250,
            'confidence': 'high', 'notes': 'Part of Pathupaattu (Ten Idylls)'
        },
        '16 குறிஞ்சிப்பாட்டு.txt': {
            'work_name': 'Kurinchippaattu', 'work_name_tamil': 'குறிஞ்சிப்பாட்டு',
            'type': 'padal', 'description': 'Song of Kurinji landscape',
            'traditional_order': 17, 'start_year': 150, 'end_year': 250,
            'confidence': 'high', 'notes': 'Part of Pathupaattu (Ten Idylls)'
        },
        '17 பட்டினப்பாலை.txt': {
            'work_name': 'Pattinappaalai', 'work_name_tamil': 'பட்டினப்பாலை',
            'type': 'padal', 'description': 'Description of seaport',
            'traditional_order': 18, 'start_year': 150, 'end_year': 250,
            'confidence': 'high', 'notes': 'Part of Pathupaattu (Ten Idylls)'
        },
        '18 மலைபடுகடாம்.txt': {
            'work_name': 'Malaipadukataam', 'work_name_tamil': 'மலைபடுகடாம்',
            'type': 'padal', 'description': 'Mountain-traversing journey',
            'traditional_order': 19, 'start_year': 150, 'end_year': 250,
            'confidence': 'high', 'notes': 'Part of Pathupaattu (Ten Idylls)'
        }
    }

    def __init__(self, db_connection_string: str):
        """Initialize importer"""
        self.conn = psycopg2.connect(db_connection_string)
        self.cursor = self.conn.cursor()

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

        # Data containers (reset per work)
        self.sections = []
        self.verses = []
        self.lines = []
        self.words = []
        self.works = []

        # Section cache
        self.section_cache = {}

    def _ensure_works_exist(self):
        """Create all Sangam work entries with dynamic work_id assignment"""
        print("  Checking/creating Sangam work entries...")

        # First, check if ANY works already exist
        existing_works = []
        for filename, work_info in self.SANGAM_WORKS.items():
            work_name = work_info['work_name']
            self.cursor.execute("SELECT work_id FROM works WHERE work_name = %s", (work_name,))
            existing = self.cursor.fetchone()
            if existing:
                existing_works.append((work_info['work_name'], work_info['work_name_tamil'], existing[0]))

        # If any works exist, exit with error
        if existing_works:
            print(f"\n✗ Found {len(existing_works)} existing Sangam works in database:")
            for name_en, name_ta, work_id in existing_works:
                print(f"  - {name_ta} ({name_en}) - ID: {work_id}")
            print(f"\nTo re-import, first delete the existing work(s):")
            for name_en, name_ta, work_id in existing_works:
                print(f'  python scripts/delete_work.py "{name_en}"')
            print(f"\nNote: You must delete ALL Sangam works before re-importing.")
            self.cursor.close()
            self.conn.close()
            sys.exit(1)

        # Get next available work_id ONCE before the loop
        self.cursor.execute("SELECT COALESCE(MAX(work_id), 0) FROM works")
        next_work_id = self.cursor.fetchone()[0] + 1

        for filename, work_info in self.SANGAM_WORKS.items():
            # Assign next available work_id and increment
            work_info['work_id'] = next_work_id

            # Calculate canonical order: Sangam works are 200-217
            # Map traditional_order (2-19) to canonical_order (200-217)
            canonical_order = 198 + work_info['traditional_order']  # 198 + 2 = 200, 198 + 19 = 217

            self.works.append({
                'work_id': next_work_id,
                'work_name': work_info['work_name'],
                'work_name_tamil': work_info['work_name_tamil'],
                'period': '300 BCE - 300 CE',
                'author': 'Various',
                'author_tamil': 'பல்வேறு புலவர்கள்',
                'description': work_info['description'],
                'chronology_start_year': work_info['start_year'],
                'chronology_end_year': work_info['end_year'],
                'chronology_confidence': work_info['confidence'],
                'chronology_notes': work_info['notes'],
                'canonical_order': canonical_order
            })

            next_work_id += 1  # Increment for next work

        if self.works:
            self._bulk_copy('works', self.works,
                           ['work_id', 'work_name', 'work_name_tamil', 'period',
                            'author', 'author_tamil', 'description',
                            'chronology_start_year', 'chronology_end_year',
                            'chronology_confidence', 'chronology_notes', 'canonical_order'])
            self.conn.commit()
            print(f"  ✓ Created {len(self.works)} new work entries.")

            # Create collection and link all works to it
            self._create_collection_and_link_works()

    def _create_collection_and_link_works(self):
        """Create பதினெண்மேல்கணக்கு collection and link all 18 Sangam works to it"""
        collection_id = 51
        collection_name = 'Eighteen Major Works'
        collection_name_tamil = 'பதினெண்மேல்கணக்கு'

        # Check if collection exists
        self.cursor.execute("SELECT collection_id FROM collections WHERE collection_id = %s", (collection_id,))
        existing = self.cursor.fetchone()

        if not existing:
            print(f"  Creating collection: {collection_name_tamil}")
            collection_data = [{
                'collection_id': collection_id,
                'collection_name': collection_name,
                'collection_name_tamil': collection_name_tamil,
                'collection_type': 'period',
                'description': 'Sangam Literature - Classical Tamil poetry anthologies from 300 BCE to 300 CE',
                'parent_collection_id': None,
                'sort_order': 51
            }]
            self._bulk_copy('collections', collection_data,
                           ['collection_id', 'collection_name', 'collection_name_tamil',
                            'collection_type', 'description', 'parent_collection_id', 'sort_order'])
            self.conn.commit()
            print(f"  ✓ Created collection {collection_name_tamil}")
        else:
            print(f"  Collection {collection_name_tamil} already exists")

        # Link all works to collection using traditional_order as position
        print(f"  Linking {len(self.works)} Sangam works to collection...")
        work_collections = []

        for filename, work_info in self.SANGAM_WORKS.items():
            # Position in collection is based on traditional_order minus 1
            # (traditional_order goes 2-19, so positions will be 1-18)
            position = work_info['traditional_order'] - 1

            work_collections.append({
                'work_id': work_info['work_id'],
                'collection_id': collection_id,
                'position_in_collection': position,
                'is_primary': True,
                'notes': None
            })

        if work_collections:
            # Use bulk copy for work_collections
            buffer = io.StringIO()
            writer = csv.writer(buffer, delimiter='\t')
            for wc in work_collections:
                writer.writerow([
                    wc['work_id'],
                    wc['collection_id'],
                    wc['position_in_collection'],
                    wc['is_primary'],
                    '\\N' if wc['notes'] is None else wc['notes']
                ])
            buffer.seek(0)
            self.cursor.copy_from(buffer, 'work_collections',
                                 columns=['work_id', 'collection_id', 'position_in_collection', 'is_primary', 'notes'],
                                 null='\\N')
            self.conn.commit()
            print(f"  ✓ Linked {len(work_collections)} works to collection")

    def _reset_data_containers(self):
        """Clear data containers for next work"""
        self.sections = []
        self.verses = []
        self.lines = []
        self.words = []
        self.section_cache = {}

    def _get_or_create_section_id(self, work_id, parent_id=None):
        """
        Get or create root section for work

        This creates a default section for works that start with verse #0 (கடவுள் வாழ்த்து)
        before the first major section marker (நூறு, பத்து, கலி, etc.)

        CRITICAL: Uses sort_order=0 to ensure verse #0 appears BEFORE all other sections
        """
        cache_key = (work_id, parent_id)

        if cache_key in self.section_cache:
            return self.section_cache[cache_key]

        section_id = self.section_id
        self.section_id += 1

        self.sections.append({
            'section_id': section_id,
            'work_id': work_id,
            'parent_section_id': parent_id,
            'level_type': 'Collection',
            'level_type_tamil': 'தொகுப்பு',
            'section_number': 1,
            'section_name': None,  # NULL for flat works to avoid redundant hierarchy
            'section_name_tamil': None,
            'sort_order': 0  # CRITICAL: 0 ensures verse #0 appears FIRST in browse works
        })

        self.section_cache[cache_key] = section_id
        return section_id

    def _create_section(self, work_id, parent_id, level_type, level_type_tamil,
                       section_num, section_name, section_name_tamil, metadata=None):
        """
        Create section with optional metadata (enhanced for hierarchical works)
        Uses rich cache key: (work_id, parent_id, level_type, section_num, section_name)
        Supports sections.metadata JSONB for storing section-level metadata
        """
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
            'section_name_tamil': section_name_tamil,
            'sort_order': section_num,
            'metadata': metadata  # Store section-level metadata (author, thinai, etc.)
        })

        self.section_cache[cache_key] = section_id
        return section_id

    def parse_thogai_file(self, file_path: Path, work_info: Dict):
        """Parse Thogai (poetry collection) format"""
        print(f"  Parsing {work_info['work_name_tamil']} (Thogai)...")

        work_id = work_info['work_id']
        section_id = self._get_or_create_section_id(work_id)

        with open(file_path, 'r', encoding='utf-8') as f:
            lines_text = f.readlines()

        current_poem_num = None
        current_poem_lines = []
        current_thinai = None
        current_author_inline = None
        current_author_fallback = None
        current_pann = None
        current_patron = None
        poem_count = 0

        for line in lines_text:
            line = line.strip()
            if not line:
                continue

            # Check for poem header: #<num> [<thinai>] [ - <author> ]
            # Handles: "#1 thinai - author", "#1 thinai", "#1 - author", "#1"
            # Note: ([^\-]+) is greedy to capture full thinai like "குறிஞ்சி" not just "க"
            poem_match = re.match(r'^#\s*(\d+)(?:\s+([^\-]+))?(?:\s*-\s*(.+))?', line)
            if poem_match:
                if current_poem_num is not None and current_poem_lines:
                    # Determine final author (inline takes priority over fallback)
                    author = current_author_inline if current_author_inline else current_author_fallback
                    # Build metadata with patron
                    metadata = {}
                    if current_thinai:
                        metadata['thinai'] = current_thinai
                    if author:
                        metadata['author'] = author
                    if current_pann:
                        metadata['pann'] = current_pann
                    if current_patron:
                        metadata['patron'] = current_patron
                    self._add_poem(work_id, section_id, current_poem_num, current_poem_lines,
                                 metadata=metadata if metadata else None)
                    poem_count += 1

                current_poem_num = int(poem_match.group(1))
                # Remove tabs from thinai to avoid COPY format issues (thinai may be None)
                current_thinai = poem_match.group(2).strip().replace('\t', ' ') if poem_match.group(2) else None
                # Remove tabs from inline author to avoid COPY format issues
                current_author_inline = poem_match.group(3).strip().replace('\t', ' ') if poem_match.group(3) else None
                current_author_fallback = None  # Reset fallback for new poem
                current_pann = None  # Reset pann for new poem
                current_patron = None  # Reset patron for new poem
                current_poem_lines = []
                continue

            # Capture pann/vannam metadata (structured works like Paditruppathu)
            if line.startswith('** வண்ணம்'):
                if ':' in line:
                    # Remove tabs from metadata to avoid COPY format issues
                    current_pann = line.split(':', 1)[1].strip().replace('\t', ' ')
                continue

            # Capture patron/subject metadata (புறநானூறு pattern)
            # Matches both பாடப்பட்டோன் and பாடப்பட்டோர்
            if line.startswith('** பாடப்பட்டோ'):
                if ':' in line or '-' in line:
                    # Extract value after : or -
                    patron = line.split(':', 1)[-1].split('-', 1)[-1].strip().replace('\t', ' ')
                    current_patron = patron
                continue

            # Skip other metadata lines (like ** பாடினோர், ** துறை, etc.)
            # IMPORTANT: Check for ** BEFORE checking for * (since ** also starts with *)
            if line.startswith('**'):
                continue

            # Capture author from asterisk line (fallback format)
            # Only single * lines are author (not ** metadata)
            if line.startswith('*') and not line.startswith('**'):
                # Remove tabs from author to avoid COPY format issues
                current_author_fallback = line[1:].strip().replace('\t', ' ')
                continue

            # Poem line
            if current_poem_num is not None:
                current_poem_lines.append(line)

        # Save last poem
        if current_poem_num is not None and current_poem_lines:
            author = current_author_inline if current_author_inline else current_author_fallback
            # Build metadata with patron
            metadata = {}
            if current_thinai:
                metadata['thinai'] = current_thinai
            if author:
                metadata['author'] = author
            if current_pann:
                metadata['pann'] = current_pann
            if current_patron:
                metadata['patron'] = current_patron
            self._add_poem(work_id, section_id, current_poem_num, current_poem_lines,
                         metadata=metadata if metadata else None)
            poem_count += 1

        print(f"    Parsed {poem_count} poems")

    def parse_padal_file(self, file_path: Path, work_info: Dict):
        """Parse Padal (continuous poem) format - no verse-level metadata"""
        print(f"  Parsing {work_info['work_name_tamil']} (Padal)...")

        work_id = work_info['work_id']
        section_id = self._get_or_create_section_id(work_id)

        with open(file_path, 'r', encoding='utf-8') as f:
            lines_text = f.readlines()

        poem_lines = []
        for line in lines_text:
            line = line.strip()
            # Skip empty lines and metadata lines (work title, etc.)
            if not line:
                continue
            if line.startswith('**'):  # Skip work title and metadata
                continue
            if line.startswith('*') and not line.startswith('**'):  # Skip author markers
                continue
            poem_lines.append(line)

        if poem_lines:
            # Continuous poems don't have verse-level thinai/author/pann
            self._add_poem(work_id, section_id, 1, poem_lines,
                         thinai=None, author=None, pann=None)
            print(f"    Parsed 1 continuous poem ({len(poem_lines)} lines)")

    def _parse_ainkurunuru_hierarchical(self, file_path: Path, work_info: Dict):
        """
        Parse Ainkurunuru with 3-level hierarchy: நூறு → பத்து → verses
        Structure: 5 நூறு sections × 10 பத்து subsections × 10 poems = 500 total
        Note: Starts with #0 கடவுள் வாழ்த்து BEFORE first நூறு marker
        """
        print(f"  Parsing {work_info['work_name_tamil']} (3-level hierarchy)...")
        work_id = work_info['work_id']

        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        # Create default section for invocation verse (before first நூறு marker)
        current_nooru_id = None
        current_paththu_id = self._get_or_create_section_id(work_id)
        current_poem_num = None
        current_poem_lines = []
        nooru_count = 0
        paththu_count_global = 0
        poem_count = 0

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Level 1: ** <name> நூறு - <thinai>
            nooru_match = re.match(r'^\*\*\s+(.+?)\s+நூறு\s*-\s*(.+)', line)
            if nooru_match:
                # CRITICAL FIX: Save current poem before switching நூறு sections
                if current_poem_num is not None and current_poem_lines:
                    self._add_poem(work_id, current_paththu_id, current_poem_num,
                                 current_poem_lines, thinai=None, author=None, pann=None)
                    poem_count += 1
                    current_poem_num = None
                    current_poem_lines = []

                # NOW create new நூறு section
                nooru_count += 1
                nooru_name = nooru_match.group(1).strip()
                thinai = nooru_match.group(2).strip().replace('\t', ' ')

                current_nooru_id = self._create_section(
                    work_id=work_id,
                    parent_id=None,
                    level_type='நூறு',
                    level_type_tamil='நூறு',
                    section_num=nooru_count,
                    section_name=nooru_name,
                    section_name_tamil=nooru_name,
                    metadata={'thinai': thinai}
                )
                continue

            # Level 2: ** <num> <name with பத்து> [- <author>]
            # Handles: "** 1 வேட்கைப் பத்து - author" AND "** 2 வேழப்பத்து" (no space, no author)
            paththu_match = re.match(r'^\*\*\s+(\d+)\s+(.+)', line)
            if paththu_match and 'பத்து' in line:
                # CRITICAL FIX: Save current poem before switching பத்து sections
                # This prevents last verse of பத்து from being assigned to next பத்து
                if current_poem_num is not None and current_poem_lines:
                    self._add_poem(work_id, current_paththu_id, current_poem_num,
                                 current_poem_lines, thinai=None, author=None, pann=None)
                    poem_count += 1
                    current_poem_num = None
                    current_poem_lines = []

                # NOW create new பத்து section
                paththu_count_global += 1
                paththu_num = int(paththu_match.group(1))
                rest_of_line = paththu_match.group(2).strip()

                # Extract name and author (author optional after -)
                if ' - ' in rest_of_line:
                    paththu_name, author = rest_of_line.split(' - ', 1)
                    author = author.strip().replace('\t', ' ')
                else:
                    paththu_name = rest_of_line
                    author = None

                current_paththu_id = self._create_section(
                    work_id=work_id,
                    parent_id=current_nooru_id,
                    level_type='பத்து',
                    level_type_tamil='பத்து',
                    section_num=paththu_num,
                    section_name=paththu_name.strip(),
                    section_name_tamil=paththu_name.strip(),
                    metadata={'author': author} if author else None
                )
                continue

            # Level 3: #<num> or # <num> verse
            poem_match = re.match(r'^#\s*(\d+)', line)
            if poem_match:
                # Save previous poem
                if current_poem_num is not None and current_poem_lines:
                    self._add_poem(work_id, current_paththu_id, current_poem_num,
                                 current_poem_lines, thinai=None, author=None, pann=None)
                    poem_count += 1

                current_poem_num = int(poem_match.group(1))
                current_poem_lines = []
                continue

            # Skip metadata lines (but handle missing verse markers)
            if line.startswith('**'):
                # Check for missing verse markers (கிடைக்காத பாடல்)
                if 'கிடைக்காத' in line or 'கிடைக்கவில்லை' in line:
                    # Save previous poem first
                    if current_poem_num is not None and current_poem_lines:
                        self._add_poem(work_id, current_paththu_id, current_poem_num,
                                     current_poem_lines, thinai=None, author=None, pann=None)
                        poem_count += 1

                    # Create placeholder verse for missing text
                    if current_paththu_id:
                        placeholder_num = current_poem_num + 1 if current_poem_num else 1
                        # Pass empty list - will trigger placeholder creation in _add_poem()
                        self._add_poem(work_id, current_paththu_id, placeholder_num,
                                     [], thinai=None, author=None, pann=None)
                        poem_count += 1
                        current_poem_num = placeholder_num  # Update for next iteration
                        current_poem_lines = []
                continue

            # Poem content lines
            if current_poem_num is not None:
                current_poem_lines.append(line)

        # Save last poem
        if current_poem_num is not None and current_poem_lines:
            self._add_poem(work_id, current_paththu_id, current_poem_num,
                         current_poem_lines, thinai=None, author=None, pann=None)
            poem_count += 1

        print(f"    Parsed {nooru_count} நூறு, {paththu_count_global} பத்து, {poem_count} poems")

    def _parse_pathitruppathu_metadata(self, file_path: Path, work_info: Dict):
        """
        Parse Pathitruppathu with பத்து sections and comprehensive metadata extraction
        Structure: ** <ordinal> பத்து sections, each with multiple verses
        Note: Starts with #0 கடவுள் வாழ்த்து BEFORE first பத்து marker
        Extracts verse metadata: பெயர், திணை, துறை, வண்ணம், தூக்கு
        Extracts section metadata: பாடினோர், பாடப்பட்டோர்
        """
        print(f"  Parsing {work_info['work_name_tamil']} (with பத்து sections + metadata)...")
        work_id = work_info['work_id']

        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        # Create default section for invocation verse (before first பத்து marker)
        current_section_id = self._get_or_create_section_id(work_id)
        current_poem_num = None
        current_poem_lines = []
        verse_metadata = {}
        section_metadata = {}
        section_count = 0
        poem_count = 0

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # பத்து section marker: ** <ordinal> பத்து
            # Example: ** இரண்டாம் பத்து, ** மூன்றாம் பத்து
            paththu_match = re.match(r'^\*\*\s+(.+?)\s+பத்து\s*$', line)
            if paththu_match:
                # Save previous poem before switching sections
                if current_poem_num is not None and current_poem_lines:
                    self._add_poem(work_id, current_section_id, current_poem_num,
                                 current_poem_lines, metadata=verse_metadata)
                    poem_count += 1
                    current_poem_num = None
                    current_poem_lines = []
                    verse_metadata = {}

                section_count += 1
                section_name = line.replace('**', '').strip()
                section_metadata = {}  # Reset section metadata

                current_section_id = self._create_section(
                    work_id=work_id,
                    parent_id=None,
                    level_type='பத்து',
                    level_type_tamil='பத்து',
                    section_num=section_count,
                    section_name=section_name,
                    section_name_tamil=section_name,
                    metadata=None  # Will update with பாடினோர்/பாடப்பட்டோர்
                )
                continue

            # Poem header: #<num> or # <num> <optional text>
            poem_match = re.match(r'^#\s*(\d+)', line)
            if poem_match:
                # Save previous poem
                if current_poem_num is not None and current_poem_lines:
                    self._add_poem(work_id, current_section_id, current_poem_num,
                                 current_poem_lines, metadata=verse_metadata)
                    poem_count += 1

                current_poem_num = int(poem_match.group(1))
                current_poem_lines = []
                verse_metadata = {}  # Reset metadata for new poem
                continue

            # Extract all ** <field> : <value> or ** <field> - <value> patterns
            metadata_match = re.match(r'^\*\*\s+([^:]+?)\s*[:>-]\s*(.+)', line)
            if metadata_match:
                field = metadata_match.group(1).strip()
                value = metadata_match.group(2).strip().replace('\t', ' ')

                # Map Tamil field names to English keys
                field_map = {
                    'பெயர்': 'name',
                    'திணை': 'thinai',
                    'துறை': 'thurai',
                    'வண்ணம்': 'vannam',
                    'தூக்கு': 'thookku',
                    'பாடினோர்': 'composer',
                    'பாடப்பட்டோர்': 'patron',
                    'பாடப்பட்டோன்': 'patron'
                }

                if field in field_map:
                    # Section-level metadata (பாடினோர், பாடப்பட்டோர்)
                    if field in ['பாடினோர்', 'பாடப்பட்டோர்', 'பாடப்பட்டோன்']:
                        section_metadata[field_map[field]] = value
                    else:
                        # Verse-level metadata
                        verse_metadata[field_map[field]] = value
                continue

            # Skip other ** lines (work title, notes)
            # But handle missing verse markers
            if line.startswith('**'):
                # Check for missing verse markers
                if 'கிடைக்காத' in line or 'கிடைக்கவில்லை' in line:
                    # Save previous poem first
                    if current_poem_num is not None and current_poem_lines:
                        self._add_poem(work_id, current_section_id, current_poem_num,
                                     current_poem_lines, metadata=verse_metadata)
                        poem_count += 1

                    # Create placeholder verse
                    if current_section_id:
                        placeholder_num = current_poem_num + 1 if current_poem_num else 1
                        self._add_poem(work_id, current_section_id, placeholder_num,
                                     [], metadata=None)
                        poem_count += 1
                        current_poem_num = placeholder_num
                        current_poem_lines = []
                        verse_metadata = {}
                continue

            # Poem content
            if current_poem_num is not None:
                current_poem_lines.append(line)

        # Save last poem
        if current_poem_num is not None and current_poem_lines:
            self._add_poem(work_id, current_section_id, current_poem_num,
                         current_poem_lines, metadata=verse_metadata)
            poem_count += 1

        print(f"    Parsed {section_count} பத்து sections, {poem_count} poems with metadata")

    def _parse_paripaadal_subjects(self, file_path: Path, work_info: Dict):
        """
        Parse Paripaadal with deity subjects (NOT thinai)
        Extracts: deity, பாடியவர், இசையமைத்தவர், பண்
        """
        print(f"  Parsing {work_info['work_name_tamil']} (devotional subjects)...")
        work_id = work_info['work_id']
        section_id = self._get_or_create_section_id(work_id)

        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        current_poem_num = None
        current_poem_lines = []
        verse_metadata = {}
        poem_count = 0

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Poem header: #<num> <deity>
            poem_match = re.match(r'^#\s*(\d+)\s+(.+)', line)
            if poem_match:
                # Save previous poem
                if current_poem_num is not None and current_poem_lines:
                    self._add_poem(work_id, section_id, current_poem_num,
                                 current_poem_lines, metadata=verse_metadata)
                    poem_count += 1

                current_poem_num = int(poem_match.group(1))
                deity = poem_match.group(2).strip()
                verse_metadata = {'deity': deity}  # NOT thinai!
                current_poem_lines = []
                continue

            # Extract metadata: பாடியவர், இசையமைத்தவர், பண்
            metadata_match = re.match(r'^\*\*\s+([^:]+?)\s*:[:>]?\s*(.+)', line)
            if metadata_match:
                field = metadata_match.group(1).strip()
                value = metadata_match.group(2).strip().replace('\t', ' ')

                field_map = {
                    'பாடியவர்': 'composer',
                    'இசையமைத்தவர்': 'music_composer',
                    'பண்': 'pann'
                }

                if field in field_map:
                    verse_metadata[field_map[field]] = value
                continue

            # Skip other ** lines (but handle missing verse markers)
            if line.startswith('**'):
                # Check for missing verse markers
                if 'கிடைக்காத' in line or 'கிடைக்கவில்லை' in line:
                    # Save previous poem first
                    if current_poem_num is not None and current_poem_lines:
                        self._add_poem(work_id, section_id, current_poem_num,
                                     current_poem_lines, metadata=verse_metadata)
                        poem_count += 1

                    # Create placeholder verse
                    placeholder_num = current_poem_num + 1 if current_poem_num is not None else 1
                    self._add_poem(work_id, section_id, placeholder_num,
                                 [], metadata=None)
                    poem_count += 1
                    current_poem_num = placeholder_num
                    current_poem_lines = []
                    verse_metadata = {}
                continue

            # Poem content
            if current_poem_num is not None:
                current_poem_lines.append(line)

        # Save last poem
        if current_poem_num is not None and current_poem_lines:
            self._add_poem(work_id, section_id, current_poem_num,
                         current_poem_lines, metadata=verse_metadata)
            poem_count += 1

        print(f"    Parsed {poem_count} poems with deity subjects")

    def _parse_kalithokai_sections(self, file_path: Path, work_info: Dict):
        """
        Parse Kalithokai with @ section markers and per-section authors
        Structure: 5 கலி sections with different authors → ~150 poems total
        Note: Starts with #1 கடவுள் வாழ்த்து BEFORE first @ marker
        """
        print(f"  Parsing {work_info['work_name_tamil']} (section hierarchy)...")
        work_id = work_info['work_id']

        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        # Create default section for invocation verse (before first @ marker)
        current_section_id = self._get_or_create_section_id(work_id)
        current_poem_num = None
        current_poem_lines = []
        current_thinai = None
        section_count = 0
        poem_count = 0

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Section marker: @ <name>கலி - ஆசிரியர்: <author> or ஆசிரியர் :: <author>
            # Note: Section names end with கலி (with preceding consonant cluster varying)
            section_match = re.match(r'^@\s+(.+?)கலி\s*-\s*ஆசிரியர்\s*:+\s*(.+)', line)
            if section_match:
                # CRITICAL FIX: Save current poem before switching sections
                # This prevents last verse of section from being assigned to next section
                if current_poem_num is not None and current_poem_lines:
                    self._add_poem(work_id, current_section_id, current_poem_num,
                                 current_poem_lines, thinai=None, author=None, pann=None)
                    poem_count += 1
                    current_poem_num = None
                    current_poem_lines = []

                # NOW create new section
                section_count += 1
                section_name = section_match.group(1).strip() + 'கலி'  # Group already captured text before கலி
                author = section_match.group(2).strip().replace('\t', ' ')

                # Extract thinai from section name (முதலாவது பாலைக்கலி → பாலை)
                thinai_match = re.search(r'(பாலை|குறிஞ்சி|மருத|முல்லை|நெய்தல்)', section_name)
                current_thinai = thinai_match.group(1) if thinai_match else None

                current_section_id = self._create_section(
                    work_id=work_id,
                    parent_id=None,
                    level_type='கலி',
                    level_type_tamil='கலி',
                    section_num=section_count,
                    section_name=section_name,
                    section_name_tamil=section_name,
                    metadata={'author': author, 'thinai': current_thinai}
                )
                continue

            # Poem header: #<num> or # <num> <optional text>
            poem_match = re.match(r'^#\s*(\d+)', line)
            if poem_match:
                # Save previous poem
                if current_poem_num is not None and current_poem_lines:
                    self._add_poem(work_id, current_section_id, current_poem_num,
                                 current_poem_lines, thinai=None, author=None, pann=None)
                    poem_count += 1

                current_poem_num = int(poem_match.group(1))
                current_poem_lines = []
                continue

            # Skip metadata lines (but handle missing verse markers)
            if line.startswith('**'):
                # Check for missing verse markers
                if 'கிடைக்காத' in line or 'கிடைக்கவில்லை' in line:
                    # Save previous poem first
                    if current_poem_num is not None and current_poem_lines:
                        self._add_poem(work_id, current_section_id, current_poem_num,
                                     current_poem_lines, thinai=None, author=None, pann=None)
                        poem_count += 1

                    # Create placeholder verse
                    if current_section_id:
                        placeholder_num = current_poem_num + 1 if current_poem_num is not None else 1
                        self._add_poem(work_id, current_section_id, placeholder_num,
                                     [], thinai=None, author=None, pann=None)
                        poem_count += 1
                        current_poem_num = placeholder_num
                        current_poem_lines = []
                continue

            # Skip @ markers (already handled above)
            if line.startswith('@'):
                continue

            # Poem content
            if current_poem_num is not None:
                current_poem_lines.append(line)

        # Save last poem
        if current_poem_num is not None and current_poem_lines:
            self._add_poem(work_id, current_section_id, current_poem_num,
                         current_poem_lines, thinai=None, author=None, pann=None)
            poem_count += 1

        print(f"    Parsed {section_count} கலி sections, {poem_count} poems")

    def _clean_word_text(self, word: str) -> str:
        """
        Clean word text according to Prof. P. Pandiyaraja's principles:
        - Keep only Tamil characters, hyphens (-), and underscores (_)
        - Remove dots, punctuation, and line count numbers
        """
        # First, strip trailing numbers (line counts like 5, 10, 15 attached to words)
        word = re.sub(r'\d+$', '', word)

        # Remove all non-Tamil characters except - and _
        # Tamil Unicode range: \u0B80-\u0BFF
        cleaned = re.sub(r'[^\u0B80-\u0BFF\-_]', '', word)
        return cleaned.strip()

    def _is_line_count(self, token: str) -> bool:
        """
        Check if token is a line count number (multiples of 5 or 10)
        Returns True for: 5, 10, 15, 20, 25, etc.
        """
        try:
            num = int(token)
            # Common line counts: multiples of 5
            return num % 5 == 0
        except ValueError:
            return False

    def _add_poem(self, work_id, section_id, poem_num, poem_lines,
                  thinai=None, author=None, pann=None, metadata=None):
        """Add poem to memory with flexible metadata (backwards compatible)"""
        verse_id = self.verse_id
        self.verse_id += 1

        # Build metadata dictionary (backwards compatible + flexible)
        if metadata is None:
            # Backwards compatible: build from individual params
            verse_metadata = {}
            if thinai:
                verse_metadata['thinai'] = thinai
            if author:
                verse_metadata['author'] = author
            if pann:
                verse_metadata['pann'] = pann
        else:
            # New: use provided metadata dict directly
            verse_metadata = metadata

        # We'll count actual lines after cleaning (below)
        # Placeholder for now, will update after processing lines
        verse_placeholder_index = len(self.verses)
        self.verses.append({
            'verse_id': verse_id,
            'work_id': work_id,
            'section_id': section_id,
            'verse_number': poem_num,
            'verse_type': 'poem',
            'verse_type_tamil': 'பாடல்',
            'total_lines': 0,  # Will update after counting non-empty lines
            'sort_order': poem_num,
            'metadata': verse_metadata if verse_metadata else None  # Store dict, not JSON string
        })

        line_num = 0  # Track actual line numbers (skipping empty lines)
        for line_text in poem_lines:
            # Clean line: remove dots/periods, markers, and line numbers
            # Remove alignment dots and ellipsis
            cleaned_line = line_text.replace('.', '').replace('…', '')
            # Replace tabs with spaces (to avoid breaking COPY format)
            cleaned_line = cleaned_line.replace('\t', ' ')
            # Remove structural markers
            cleaned_line = re.sub(r'^[#@$&*]+\s*', '', cleaned_line)
            # Remove ** and *** markers
            cleaned_line = re.sub(r'\*\*\*?', '', cleaned_line)
            # Remove trailing line numbers (with or without preceding space)
            # Matches: "text 5", "text5", "text  10", etc.
            cleaned_line = re.sub(r'\s*\d+$', '', cleaned_line)
            cleaned_line = cleaned_line.strip()

            # Skip empty lines (after cleaning)
            if not cleaned_line:
                continue

            line_num += 1
            line_id = self.line_id
            self.line_id += 1

            self.lines.append({
                'line_id': line_id,
                'verse_id': verse_id,
                'line_number': line_num,
                'line_text': cleaned_line
            })

            # Skip word parsing for lines that are just "-" (lost text markers)
            # This preserves the structure in verses but doesn't create meaningless word entries
            if cleaned_line.strip() == '-':
                continue

            # Parse words
            tokens = cleaned_line.strip().split()
            word_position = 1

            for token in tokens:
                # Skip line count numbers (multiples of 5)
                if self._is_line_count(token):
                    continue

                # Skip tokens that are ONLY hyphens (lost word placeholders)
                # Examples: "---", "--------", "----------------"
                # These mark lost/corrupted text and should not be tokenized
                if re.match(r'^-+$', token):
                    continue

                # Clean word (keep only Tamil, -, and _)
                word_text = self._clean_word_text(token)

                # Skip empty words after cleaning
                if not word_text:
                    continue

                word_id = self.word_id
                self.word_id += 1

                self.words.append({
                    'word_id': word_id,
                    'line_id': line_id,
                    'word_position': word_position,
                    'word_text': word_text,
                    'sandhi_split': None
                })

                word_position += 1

        # Handle verses with no content lines (lost/unavailable text)
        # Create placeholder line to preserve verse numbering
        if line_num == 0:
            line_num = 1
            line_id = self.line_id
            self.line_id += 1

            self.lines.append({
                'line_id': line_id,
                'verse_id': verse_id,
                'line_number': 1,
                'line_text': '-கிடைக்கவில்லை-'
            })
            # Note: No words created for placeholder line

        # Update the total_lines count in the verse (now that we know the actual count)
        self.verses[verse_placeholder_index]['total_lines'] = line_num

    def parse_directory(self, directory_path: Path):
        """Parse and import works one at a time with per-work rollback"""
        print(f"\nParsing Sangam literature files...")

        success_count = 0
        failed_works = []

        for filename, work_info in self.SANGAM_WORKS.items():
            file_path = directory_path / filename
            if not file_path.exists():
                print(f"  Skipping {filename} (not found)")
                continue

            # Check if work already imported
            self.cursor.execute("""
                SELECT COUNT(*) FROM verses WHERE work_id = %s
            """, (work_info['work_id'],))
            existing_count = self.cursor.fetchone()[0]

            if existing_count > 0:
                print(f"  Skipping {work_info['work_name_tamil']} (already imported: {existing_count} verses)")
                continue

            try:
                print(f"\n{'='*70}")
                print(f"Processing: {work_info['work_name_tamil']} (ID: {work_info['work_id']})")
                print(f"{'='*70}")

                # Phase 1: Parse file into memory
                # Delegate to work-specific parsers for complex cases
                if work_info['work_name'] == 'Ainkurunuru':
                    self._parse_ainkurunuru_hierarchical(file_path, work_info)
                elif work_info['work_name'] == 'Pathitrupathu':
                    self._parse_pathitruppathu_metadata(file_path, work_info)
                elif work_info['work_name'] == 'Paripaadal':
                    self._parse_paripaadal_subjects(file_path, work_info)
                elif work_info['work_name'] == 'Kalithokai':
                    self._parse_kalithokai_sections(file_path, work_info)
                elif work_info['type'] == 'thogai':
                    self.parse_thogai_file(file_path, work_info)
                else:
                    self.parse_padal_file(file_path, work_info)

                # Phase 2: Bulk insert for this work
                self._bulk_insert_work(work_info['work_name_tamil'])

                # Commit this work
                self.conn.commit()
                print(f"✓ {work_info['work_name_tamil']} imported successfully")
                success_count += 1

            except Exception as e:
                # Rollback this work
                self.conn.rollback()
                print(f"✗ Failed to import {work_info['work_name_tamil']}: {e}")
                failed_works.append((work_info['work_name_tamil'], str(e)))

            finally:
                # Clear data containers for next work
                self._reset_data_containers()

        # Summary
        print(f"\n{'='*70}")
        print(f"Import Summary:")
        print(f"  ✓ Successfully imported: {success_count} works")
        if failed_works:
            print(f"  ✗ Failed: {len(failed_works)} works")
            for work_name, error in failed_works:
                print(f"    - {work_name}: {error}")
        print(f"{'='*70}")

    def _bulk_insert_work(self, work_name: str):
        """Bulk insert single work using COPY"""
        print(f"  Inserting into database...")

        # Insert sections
        if self.sections:
            print(f"    - {len(self.sections)} sections...")
            self._bulk_copy('sections', self.sections,
                           ['section_id', 'work_id', 'parent_section_id', 'level_type', 'level_type_tamil',
                            'section_number', 'section_name', 'section_name_tamil', 'sort_order', 'metadata'])

        # Insert verses
        if self.verses:
            print(f"    - {len(self.verses)} verses...")
            self._bulk_copy('verses', self.verses,
                           ['verse_id', 'work_id', 'section_id', 'verse_number', 'verse_type',
                            'verse_type_tamil', 'total_lines', 'sort_order', 'metadata'])

        # Insert lines
        if self.lines:
            print(f"    - {len(self.lines)} lines...")
            self._bulk_copy('lines', self.lines,
                           ['line_id', 'verse_id', 'line_number', 'line_text'])

        # Insert words
        if self.words:
            print(f"    - {len(self.words)} words...")
            self._bulk_copy('words', self.words,
                           ['word_id', 'line_id', 'word_position', 'word_text', 'sandhi_split'])

    def _bulk_copy(self, table_name, data, columns):
        """Use COPY for bulk insert with JSON support (no CSV escaping)"""
        if not data:
            return

        buffer = io.StringIO()

        for row in data:
            row_values = []
            for col in columns:
                val = row.get(col)
                if val is None:
                    row_values.append('')  # Use empty string for NULL
                elif isinstance(val, dict):
                    # Serialize dictionaries to JSON string for JSONB columns
                    json_str = json.dumps(val, ensure_ascii=False)
                    # Replace tabs in JSON to avoid breaking tab-delimited format
                    json_str = json_str.replace('\t', ' ')
                    row_values.append(json_str)
                else:
                    row_values.append(str(val))
            # Manually format tab-delimited row (NO csv.writer to avoid escaping)
            buffer.write('\t'.join(row_values) + '\n')

        buffer.seek(0)
        self.cursor.copy_from(buffer, table_name, columns=columns, null='')

    def close(self):
        """Close connection"""
        self.cursor.close()
        self.conn.close()


def main():
    import sys

    # Get database URL
    db_connection = os.getenv('DATABASE_URL', "postgresql://postgres:password@localhost/tamil_literature")
    if len(sys.argv) > 1:
        db_connection = sys.argv[1]

    # Directory path
    script_dir = Path(__file__).parent
    project_dir = script_dir.parent
    sangam_dir = project_dir / "Tamil-Source-TamilConcordence" / "2_Sangam_Literature"

    print("="*70)
    print("Sangam Literature Bulk Import - Fast 2-Phase Import")
    print("="*70)
    print(f"Database: {db_connection[:50]}...")
    print(f"Directory: {sangam_dir}")

    importer = SangamBulkImporter(db_connection)

    try:
        importer._ensure_works_exist()
        importer.parse_directory(sangam_dir)
        print("\n✓ Import complete!")
    finally:
        importer.close()


if __name__ == '__main__':
    main()
