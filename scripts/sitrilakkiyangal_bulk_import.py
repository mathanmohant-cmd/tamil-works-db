#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Minor Literary Works (சிற்றிலக்கியங்கள்) Bulk Import
Fast 2-phase import using PostgreSQL COPY

Phase 1: Parse text → Build data structures in memory
Phase 2: Bulk COPY into database (1000x faster than INSERT)

Collection ID: 326 (சிற்றிலக்கியங்கள் - Minor Literary Works)

Works (20 minor literary works):
Diverse literary genres spanning 12th-19th century CE including கலம்பகம்,
பரணி, தூது, கோவை, குறவஞ்சி, and other classical Tamil genres.

Structure Patterns:
- simple: Only #N verse markers (5 works)
- dual_at: @N section markers + #N verses (14 works)
- dual_star: *N. section markers + #N verses (1 work: கலிங்கத்துப்பரணி)
"""

import re
import psycopg2
from pathlib import Path
import csv
import io
import sys
import os
import json

# Add path for global shared utilities
sys.path.insert(0, str(Path(__file__).parent))
from shared.base_importer import BaseWorkImporter
from shared.utils import clean_line_text, split_and_clean_words

# Level 1 section names for முக்கூடற்பள்ளு nested_double_star pattern
LEVEL1_SECTION_NAMES = [
    'காப்பு', 'கடவுள் வணக்கம்', 'நூல்', 'மங்கலம்',
    'பயன்', 'முடிவுரை'
]

# Fixed section mapping for முக்கூடற் பள்ளு based on verse ranges
# Format: (start_verse, end_verse, section_name_tamil)
MUKUDAL_PALLU_SECTIONS = [
    (0, 4, 'காப்பு -கடவுள் வணக்கம்'),
    (5, 15, 'பள்ளியர், பள்ளன் வரவு'),
    (16, 39, 'நாட்டு வளம் - நகர் வளம்'),
    (40, 51, 'பல்வகை நிலம் - ஆறு'),
    (52, 80, 'பண்ணைக்காரன் வரவு'),
    (81, 92, 'இடையன் வரவு'),
    (93, 106, 'பள்ளனை அடித்தல்'),
    (107, 118, 'பள்ளனை விடுவித்தல்'),
    (119, 136, 'உழுது விதைத்தல்'),
    (137, 151, 'அறுவடை'),
    (152, 175, 'பள்ளியர் ஏசல் -முடிவு')
]

# Work metadata for all 20 works
WORK_METADATA = {
    1: {
        'work_name': 'Abhirami Andhadhi',
        'work_name_tamil': 'அபிராமி அந்தாதி',
        'author': 'Abhirami Pattar',
        'author_tamil': 'அபிராமி பட்டர்',
        'period': '18th century CE',
        'canonical_order': 326001,
        'position_in_collection': 1,
        'file': 'அபிராமி அந்தாதி.txt',
        'structure_pattern': 'simple',
        'verse_numbering': 'global',
        'extract_metadata': False
    },
    2: {
        'work_name': 'Azhagar Killai Viduthootu',
        'work_name_tamil': 'அழகர் கிள்ளை விடுதூது',
        'author': 'Balapattu Chokkanathar',
        'author_tamil': 'பலபட்டடைச் சொக்கநாதர்',
        'period': '17th-18th century CE',
        'canonical_order': 326002,
        'position_in_collection': 2,
        'file': 'அழகர் கிள்ளை விடுதூது.txt',
        'structure_pattern': 'dual_at',
        'verse_numbering': 'global',
        'extract_metadata': False
    },
    3: {
        'work_name': 'Kachchi Kalambagam',
        'work_name_tamil': 'கச்சிக் கலம்பகம்',
        'author': 'Poonthi Aranganatha Mudaliar',
        'author_tamil': 'பூண்டி அரங்கநாத முதலியார்',
        'period': '17th-18th century CE',
        'canonical_order': 326003,
        'position_in_collection': 3,
        'file': 'கச்சிக் கலம்பகம்.txt',
        'structure_pattern': 'dual_at',
        'verse_numbering': 'section_reset',
        'extract_metadata': True
    },
    4: {
        'work_name': 'Kalingathu Parani',
        'work_name_tamil': 'கலிங்கத்துப்பரணி',
        'author': 'Cheyangkonttar',
        'author_tamil': 'செயங்கொண்டார்',
        'period': '12th century CE',
        'canonical_order': 326004,
        'position_in_collection': 4,
        'file': 'கலிங்கத்துப்பரணி.txt',
        'structure_pattern': 'dual_star',
        'verse_numbering': 'global',
        'extract_metadata': True
    },
    5: {
        'work_name': 'Kasi Kalambagam',
        'work_name_tamil': 'காசிக் கலம்பகம்',
        'author': 'Kumarakuruparar',
        'author_tamil': 'குமரகுருபரர்',
        'period': '17th century CE',
        'canonical_order': 326005,
        'position_in_collection': 5,
        'file': 'காசிக் கலம்பகம்.txt',
        'structure_pattern': 'dual_at',
        'verse_numbering': 'global',
        'extract_metadata': True
    },
    6: {
        'work_name': 'Kavadi Chindu',
        'work_name_tamil': 'காவடிச் சிந்து',
        'author': 'Annamalai Rettiyar',
        'author_tamil': 'அண்ணாமலை ரெட்டியார்',
        'period': '19th century CE',
        'canonical_order': 326006,
        'position_in_collection': 6,
        'file': 'காவடிச் சிந்து.txt',
        'structure_pattern': 'dual_at',
        'verse_numbering': 'section_reset',
        'extract_metadata': False
    },
    7: {
        'work_name': 'Kuselopakyanam',
        'work_name_tamil': 'குசேலோபாக்கியானம்',
        'author': 'Vallur Devaraja Pillai',
        'author_tamil': 'வல்லூர் தேவராச பிள்ளை',
        'period': '18th-19th century CE',
        'canonical_order': 326007,
        'position_in_collection': 7,
        'file': 'குசேலோபாக்கியானம்.txt',
        'structure_pattern': 'dual_at',
        'verse_numbering': 'global',
        'extract_metadata': True
    },
    8: {
        'work_name': 'Kumaresa Sadhagam',
        'work_name_tamil': 'குமரேச சதகம்',
        'author': 'Gurubatha Dasar',
        'author_tamil': 'குருபாத தாசர்',
        'period': '18th-19th century CE',
        'canonical_order': 326008,
        'position_in_collection': 8,
        'file': 'குமரேச சதகம்.txt',
        'structure_pattern': 'simple',
        'verse_numbering': 'section_reset',
        'extract_metadata': True
    },
    9: {
        'work_name': 'Thakayaga Parani',
        'work_name_tamil': 'தக்கயாகப்பரணி',
        'author': 'Ottakkuttar',
        'author_tamil': 'ஒட்டக்கூத்தர்',
        'period': '12th century CE',
        'canonical_order': 326009,
        'position_in_collection': 9,
        'file': 'தக்கயாகப்பரணி.txt',
        'structure_pattern': 'dual_at',
        'verse_numbering': 'global',
        'extract_metadata': False
    },
    10: {
        'work_name': 'Thanjai Vanan Kovai',
        'work_name_tamil': 'தஞ்சைவாணன் கோவை',
        'author': 'Poyyamozhipulavar',
        'author_tamil': 'பொய்யாமொழிப்புலவர்',
        'period': '15th-16th century CE',
        'canonical_order': 326010,
        'position_in_collection': 10,
        'file': 'தஞ்சைவாணன் கோவை.txt',
        'structure_pattern': 'triple_ampersand_at',
        'verse_numbering': 'global',
        'extract_metadata': True
    },
    11: {
        'work_name': 'Thamizh Vidu Thootu',
        'work_name_tamil': 'தமிழ்விடு தூது',
        'author': 'Madurai Chokkanathar',
        'author_tamil': 'மதுரைச் சொக்கநாதர்',
        'period': '17th century CE',
        'canonical_order': 326011,
        'position_in_collection': 11,
        'file': 'தமிழ்விடு தூது.txt',
        'structure_pattern': 'dual_at',
        'verse_numbering': 'global',
        'extract_metadata': False
    },
    12: {
        'work_name': 'Thirukkutrala Kuravanji',
        'work_name_tamil': 'திருக்குற்றாலக் குறவஞ்சி',
        'author': 'Unknown',
        'author_tamil': 'அறியப்படாத ஆசிரியர்',
        'period': '17th-18th century CE',
        'canonical_order': 326012,
        'position_in_collection': 12,
        'file': 'திருக்குற்றாலக் குறவஞ்சி.txt',
        'structure_pattern': 'dual_at',
        'verse_numbering': 'section_reset',
        'extract_metadata': True  # Has extensive ragam/thalam metadata (51+ occurrences)
    },
    13: {
        'work_name': 'Nandhi Kalambagam',
        'work_name_tamil': 'நந்திக் கலம்பகம்',
        'author': 'Unknown',
        'author_tamil': 'அறியப்படாத ஆசிரியர்',
        'period': '17th-18th century CE',
        'canonical_order': 326013,
        'position_in_collection': 13,
        'file': 'நந்திக் கலம்பகம்.txt',
        'structure_pattern': 'dual_at',
        'verse_numbering': 'section_reset',
        'extract_metadata': True
    },
    14: {
        'work_name': 'Nala Venba',
        'work_name_tamil': 'நளவெண்பா',
        'author': 'Pugazhenthi Pulavar',
        'author_tamil': 'புகழேந்திப் புலவர்',
        'period': '16th-17th century CE',
        'canonical_order': 326014,
        'position_in_collection': 14,
        'file': 'நளவெண்பா.txt',
        'structure_pattern': 'kandam_in_verse',
        'verse_numbering': 'global',
        'extract_metadata': False
    },
    15: {
        'work_name': 'Pandi Kovai',
        'work_name_tamil': 'பாண்டிக்கோவை',
        'author': 'Unknown',
        'author_tamil': 'அறியப்படாத ஆசிரியர்',
        'period': '15th-16th century CE',
        'canonical_order': 326015,
        'position_in_collection': 15,
        'file': 'பாண்டிக்கோவை.txt',
        'structure_pattern': 'dual_at',
        'verse_numbering': 'global',
        'extract_metadata': False
    },
    16: {
        'work_name': 'Bethlakema Kuravanji',
        'work_name_tamil': 'பெத்லகேம் குறவஞ்சி',
        'author': 'Vedhanayaga Sasthriyar',
        'author_tamil': 'வேதநாயக சாஸ்திரியார்',
        'period': '19th century CE',
        'canonical_order': 326016,
        'position_in_collection': 16,
        'file': 'பெத்லகேம் குறவஞ்சி.txt',
        'structure_pattern': 'dual_at',
        'verse_numbering': 'global',
        'extract_metadata': False
    },
    17: {
        'work_name': 'Madurai Meenakshiyammai Pillai Thamizh',
        'work_name_tamil': 'மதுரை மீனாட்சியம்மை பிள்ளைத் தமிழ்',
        'author': 'Kumarakuruparar',
        'author_tamil': 'குமரகுருபரர்',
        'period': '17th century CE',
        'canonical_order': 326017,
        'position_in_collection': 17,
        'file': 'மதுரை மீனாட்சியம்மை பிள்ளைத் தமிழ்.txt',
        'structure_pattern': 'dual_at',
        'verse_numbering': 'global',
        'extract_metadata': False
    },
    18: {
        'work_name': 'Madurai Kalambagam',
        'work_name_tamil': 'மதுரைக் கலம்பகம்',
        'author': 'Kumarakuruparar',
        'author_tamil': 'குமரகுருபரர்',
        'period': '17th century CE',
        'canonical_order': 326018,
        'position_in_collection': 18,
        'file': 'மதுரைக் கலம்பகம்.txt',
        'structure_pattern': 'dual_at',
        'verse_numbering': 'section_reset',
        'extract_metadata': True
    },
    19: {
        'work_name': 'Mukkudal Pallu',
        'work_name_tamil': 'முக்கூடற் பள்ளு',
        'author': 'Unknown',
        'author_tamil': 'அறியப்படாத ஆசிரியர்',
        'period': '18th-19th century CE',
        'canonical_order': 326019,
        'position_in_collection': 19,
        'file': 'முக்கூடற் பள்ளு.txt',
        'structure_pattern': 'mukudal_fixed_sections',
        'verse_numbering': 'global',
        'extract_metadata': True
    },
    20: {
        'work_name': 'Muvarula',
        'work_name_tamil': 'மூவருலா',
        'author': 'Kavichakravarthi Ottakkuttar',
        'author_tamil': 'கவிச்சக்கரவர்த்தி ஒட்டக்கூத்தர்',
        'period': '12th century CE',
        'canonical_order': 326020,
        'position_in_collection': 20,
        'file': 'மூவருலா.txt',
        'structure_pattern': 'dual_at',
        'verse_numbering': 'section_reset',
        'extract_metadata': False
    }
}


def is_paa_type(text: str) -> bool:
    """Check if text is a poetic form (paa type)"""
    paa_types = [
        'வெண்பா', 'கலிப்பா', 'சிந்து', 'விருத்தம்', 'தாழிசை',
        'கொச்சகக் கலிப்பா', 'நேரிசை வெண்பா', 'ஆசிரிய விருத்தம்',
        'கலித்தாழிசை', 'தரவு', 'சதகம்', 'அந்தாதி', 'கோவை',
        'கலம்பகம்', 'பரணி', 'தூது', 'குறவஞ்சி', 'பள்ளு', 'உலா'
    ]
    return any(ptype in text for ptype in paa_types)


class SitrilakkiyangalBulkImporter(BaseWorkImporter):
    """Import all 20 minor literary works using 2-phase bulk COPY pattern"""

    # Default collection for this importer
    COLLECTION_ID = 326
    COLLECTION_NAME = 'Sitrilakkiyangal'
    COLLECTION_NAME_TAMIL = 'சிற்றிலக்கியங்கள்'

    def __init__(self, db_connection_string: str):
        """Initialize importer and create collection"""
        super().__init__(db_connection_string, collection_id=self.COLLECTION_ID)

        # Ensure collection exists (idempotent)
        self._ensure_collection_exists(
            collection_id=self.COLLECTION_ID,
            collection_name=self.COLLECTION_NAME,
            collection_name_tamil=self.COLLECTION_NAME_TAMIL,
            description='Minor literary works collection (சிற்றிலக்கியங்கள்) - 20 works spanning 12th-19th century CE'
        )

    def _create_work(self, work_num: int) -> int:
        """Create work entry from WORK_METADATA and return work_id"""
        if work_num not in WORK_METADATA:
            raise ValueError(f"Invalid work number: {work_num}")

        metadata = WORK_METADATA[work_num]

        # Use parent class's _create_work (handles duplicate check, ID allocation, collection linking)
        work_id = super()._create_work(
            work_name=metadata['work_name'],
            work_name_tamil=metadata['work_name_tamil'],
            metadata=metadata
        )

        print(f"  Created work: {metadata['work_name_tamil']} (ID: {work_id}, Canonical: {metadata['canonical_order']})")
        return work_id

    def _add_section(self, work_id: int, section_num: int, section_name: str,
                    parent_section_id: int = None, level_type: str = 'Section') -> int:
        """Add section to in-memory list and return section_id"""
        section_id = self.section_id
        self.section_id += 1  # Manual increment

        self.sections.append({
            'section_id': section_id,
            'work_id': work_id,
            'parent_section_id': parent_section_id,
            'level_type': level_type,
            'level_type_tamil': 'பகுதி' if level_type == 'Section' else level_type,
            'section_number': section_num,
            'section_name': section_name,
            'section_name_tamil': section_name,
            'sort_order': section_num
        })

        return section_id

    def _add_verse(self, work_id: int, section_id: int, verse_num: int, verse_lines: list, metadata: dict = None):
        """Add verse with optional metadata, lines, and words to in-memory lists"""
        if not verse_lines:
            return

        # Create verse
        verse_id = self.verse_id
        self.verse_id += 1

        # Store metadata as dict (will be serialized in _bulk_copy)
        # Only store if metadata is a non-empty dict
        metadata_to_store = metadata if (metadata and isinstance(metadata, dict) and len(metadata) > 0) else None

        self.verses.append({
            'verse_id': verse_id,
            'work_id': work_id,
            'section_id': section_id,
            'verse_number': verse_num,
            'verse_type': 'Verse',
            'verse_type_tamil': 'பாடல்',
            'total_lines': len(verse_lines),
            'sort_order': verse_num,
            'metadata': metadata_to_store
        })

        # Create lines and words
        for line_num, line_text in enumerate(verse_lines, start=1):
            line_id = self.line_id
            self.line_id += 1

            # Clean line text (removes dots, markers, trailing numbers)
            cleaned_line = clean_line_text(line_text)

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
        """Route to appropriate parser based on structure_pattern"""
        pattern = WORK_METADATA[work_num]['structure_pattern']

        print(f"\nParsing File {work_num}: {Path(file_path).name} (Pattern: {pattern})")

        if pattern == 'simple':
            self._parse_simple_pattern(file_path, work_num)
        elif pattern == 'dual_at':
            self._parse_dual_at_pattern(file_path, work_num)
        elif pattern == 'dual_star':
            self._parse_dual_star_pattern(file_path, work_num)
        elif pattern == 'triple_ampersand_at':
            self._parse_triple_ampersand_at_pattern(file_path, work_num)
        elif pattern == 'kandam_in_verse':
            self._parse_kandam_in_verse_pattern(file_path, work_num)
        elif pattern == 'nested_double_star':
            self._parse_nested_double_star_pattern(file_path, work_num)
        elif pattern == 'mukudal_fixed_sections':
            self._parse_mukudal_fixed_sections_pattern(file_path, work_num)
        else:
            raise ValueError(f"Unknown structure pattern: {pattern}")

    def _parse_simple_pattern(self, file_path: str, work_num: int):
        """
        Parse files with simple #N verse numbering (no sections)

        Pattern:
        ** [Work Title]
        #N [Optional Topic]
        [verse lines]
        [blank line]

        Create single default section with NULL name to avoid redundant hierarchy
        """
        # Get configuration
        extract_metadata = WORK_METADATA[work_num]['extract_metadata']

        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        # Create work
        current_work_id = self._create_work(work_num)
        if not current_work_id:
            return

        # Create default section with NULL name (avoids redundant hierarchy in UI)
        default_section = self._add_section(
            current_work_id,
            section_num=1,
            section_name=None,
            level_type='Section'
        )

        # State tracking
        current_verse_num = None
        current_verse_lines = []
        verse_counter = 0  # Simple pattern always uses global numbering
        pending_metadata = {}
        seen_work_title = False

        for line in lines:
            line = line.strip()

            # ** Work title or metadata
            if line.startswith('**'):
                if not seen_work_title:
                    seen_work_title = True
                    continue  # Skip work title

                # If we're in the middle of a verse, save it with current metadata FIRST
                if current_verse_num is not None and current_verse_lines:
                    self._add_verse(current_work_id, default_section,
                                  verse_counter, current_verse_lines, pending_metadata)
                    current_verse_num = None
                    current_verse_lines = []
                    pending_metadata = {}  # Clear for next verse

                # Extract metadata if configured (for NEXT verse)
                if extract_metadata:
                    text = line[2:].strip()

                    # Parse ragam/thalam
                    if 'இராகம்' in text or 'தாளம்' in text:
                        if 'இராகம்' in text:
                            ragam = text.split('இராகம்')[1].split('.')[0].strip(' :')
                            pending_metadata['ragam'] = ragam
                        if 'தாளம்' in text:
                            thalam = text.split('தாளம்')[1].split('.')[0].strip(' :')
                            pending_metadata['thalam'] = thalam

                    # Classify as paa_type or subject
                    elif is_paa_type(text):
                        pending_metadata['paa_type'] = text
                    else:
                        pending_metadata['subject'] = text

                continue  # Don't process ** as verse content

            # Empty line - skip (verses are saved when next ** or # appears)
            if not line:
                continue

            # #N Verse marker
            if line.startswith('#'):
                # Save previous verse (WITHOUT metadata - it was already saved when ** appeared)
                if current_verse_num is not None and current_verse_lines:
                    self._add_verse(current_work_id, default_section,
                                  verse_counter, current_verse_lines, {})  # Empty metadata
                    # DON'T clear pending_metadata - it's for THIS new verse

                # Extract verse number (ignore topic on same line)
                match = re.match(r'#(\d+)', line)
                if match:
                    current_verse_num = int(match.group(1))
                    verse_counter += 1
                    current_verse_lines = []

            # Regular line (verse content)
            elif current_verse_num is not None:
                # Skip continuation markers
                if line == 'மேல்':
                    continue
                current_verse_lines.append(line)

        # Save final verse
        if current_verse_num is not None and current_verse_lines:
            self._add_verse(current_work_id, default_section,
                          verse_counter, current_verse_lines, pending_metadata)

    def _parse_dual_at_pattern(self, file_path: str, work_num: int):
        """
        Parse files with @N section markers

        Pattern:
        ** [Work Title]
        @N [Section Name]
        ** [Optional Verse Metadata]
        #N [Verse]
        [verse lines]
        """
        # Get configuration
        verse_numbering = WORK_METADATA[work_num]['verse_numbering']
        extract_metadata = WORK_METADATA[work_num]['extract_metadata']

        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        # Create work
        current_work_id = self._create_work(work_num)
        if not current_work_id:
            return

        # State tracking
        current_section = None
        current_verse_num = None
        current_verse_lines = []
        verse_counter = 0  # Section-local counter
        global_verse_counter = 0  # Global counter
        pending_metadata = {}  # Accumulate metadata before verse
        seen_work_title = False

        for line in lines:
            line = line.strip()

            # Empty line - skip (verses are saved when next ** or # or section appears)
            if not line:
                continue

            # ** Work title or verse metadata
            if line.startswith('**'):
                if not seen_work_title:
                    seen_work_title = True
                    continue  # Skip work title

                # If we're in the middle of a verse, save it with current metadata FIRST
                if current_verse_num is not None and current_verse_lines:
                    if verse_numbering == 'global':
                        use_verse_num = global_verse_counter
                    else:
                        use_verse_num = verse_counter
                    self._add_verse(current_work_id, current_section,
                                  use_verse_num, current_verse_lines, pending_metadata)
                    current_verse_num = None
                    current_verse_lines = []
                    pending_metadata = {}  # Clear for next verse

                # Extract metadata if configured (for NEXT verse)
                if extract_metadata:
                    text = line[2:].strip()

                    # Parse ragam/thalam
                    if 'இராகம்' in text or 'தாளம்' in text:
                        if 'இராகம்' in text:
                            ragam = text.split('இராகம்')[1].split('.')[0].strip(' :')
                            pending_metadata['ragam'] = ragam
                        if 'தாளம்' in text:
                            thalam = text.split('தாளம்')[1].split('.')[0].strip(' :')
                            pending_metadata['thalam'] = thalam

                    # Classify as paa_type or subject
                    elif is_paa_type(text):
                        pending_metadata['paa_type'] = text
                    else:
                        pending_metadata['subject'] = text

                continue  # Don't process ** as verse content

            # @N Section marker
            if line.startswith('@'):
                # Save previous verse with its metadata
                if current_verse_num is not None and current_verse_lines:
                    if verse_numbering == 'global':
                        use_verse_num = global_verse_counter
                    else:
                        use_verse_num = verse_counter
                    self._add_verse(current_work_id, current_section,
                                  use_verse_num, current_verse_lines, pending_metadata)
                    current_verse_num = None
                    current_verse_lines = []
                    pending_metadata = {}  # Clear for next section

                # Extract section number and name
                match = re.match(r'@(\d+)\.?\s*(.*)', line)
                if match:
                    section_num = int(match.group(1))
                    section_name = match.group(2).strip()
                    if not section_name:
                        section_name = f"Section {section_num}"

                    current_section = self._add_section(
                        current_work_id,
                        section_num,
                        section_name
                    )
                    # Reset only if configured for section_reset
                    if verse_numbering == 'section_reset':
                        verse_counter = 0

            # #N Verse marker
            elif line.startswith('#'):
                # Save previous verse (WITHOUT metadata - it was already saved when ** appeared)
                if current_verse_num is not None and current_verse_lines:
                    if verse_numbering == 'global':
                        use_verse_num = global_verse_counter
                    else:
                        use_verse_num = verse_counter
                    self._add_verse(current_work_id, current_section,
                                  use_verse_num, current_verse_lines, {})  # Empty metadata
                    # DON'T clear pending_metadata - it's for THIS new verse

                # Extract verse number (ignore topic)
                match = re.match(r'#(\d+)', line)
                if match:
                    current_verse_num = int(match.group(1))
                    # Increment both counters
                    verse_counter += 1
                    global_verse_counter += 1
                    current_verse_lines = []

            # Regular line (verse content)
            elif current_verse_num is not None:
                # Skip continuation markers
                if line == 'மேல்':
                    continue
                current_verse_lines.append(line)

        # Save final verse
        if current_verse_num is not None and current_verse_lines:
            if verse_numbering == 'global':
                use_verse_num = global_verse_counter
            else:
                use_verse_num = verse_counter
            self._add_verse(current_work_id, current_section,
                          use_verse_num, current_verse_lines, pending_metadata)

    def _parse_dual_star_pattern(self, file_path: str, work_num: int):
        """
        Parse files with *N. section markers (கலிங்கத்துப்பரணி only)

        Pattern:
        ** [Work Title]
        *N. [Level 1 Section]
        * [subject] (metadata - NOT a subsection marker)
        #N [Verse]

        Build 2-level hierarchy: sections → subsections
        """
        # Get configuration
        verse_numbering = WORK_METADATA[work_num]['verse_numbering']
        extract_metadata = WORK_METADATA[work_num]['extract_metadata']

        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        # Create work
        current_work_id = self._create_work(work_num)
        if not current_work_id:
            return

        # State tracking
        current_level1_section = None
        current_level2_section = None
        current_verse_num = None
        current_verse_lines = []
        verse_counter = 0  # Section-local counter
        global_verse_counter = 0  # Global counter
        pending_metadata = {}  # Accumulate metadata before verse
        level1_counter = 0
        level2_counter = 0

        for line in lines:
            line = line.strip()

            # Empty line - skip (verses are saved when next * or # or section appears)
            if not line:
                continue

            # ** Work title (skip)
            if line.startswith('**'):
                continue

            # *N. Level 1 section marker (numbered)
            if re.match(r'\*\d+\.', line):
                # Save previous verse
                if current_verse_num is not None and current_verse_lines:
                    target_section = current_level2_section if current_level2_section else current_level1_section
                    if verse_numbering == 'global':
                        use_verse_num = global_verse_counter
                    else:
                        use_verse_num = verse_counter
                    self._add_verse(current_work_id, target_section,
                                  use_verse_num, current_verse_lines, pending_metadata)
                    current_verse_num = None
                    current_verse_lines = []
                    pending_metadata = {}

                # Extract section number and name
                match = re.match(r'\*(\d+)\.\s*(.*)', line)
                if match:
                    level1_counter += 1
                    section_name = match.group(2).strip()
                    if not section_name:
                        section_name = f"Section {level1_counter}"

                    current_level1_section = self._add_section(
                        current_work_id,
                        level1_counter,
                        section_name,
                        parent_section_id=None,
                        level_type='Section'
                    )
                    current_level2_section = None  # Reset subsection
                    # Reset only if configured for section_reset
                    if verse_numbering == 'section_reset':
                        verse_counter = 0
                    level2_counter = 0

            # * [subject] - metadata (NOT subsection for கலிங்கத்துப்பரணி)
            elif line.startswith('*') and not re.match(r'\*\d+\.', line):
                # If we're in the middle of a verse, save it with current metadata FIRST
                if current_verse_num is not None and current_verse_lines:
                    target_section = current_level2_section if current_level2_section else current_level1_section
                    if verse_numbering == 'global':
                        use_verse_num = global_verse_counter
                    else:
                        use_verse_num = verse_counter
                    self._add_verse(current_work_id, target_section,
                                  use_verse_num, current_verse_lines, pending_metadata)
                    current_verse_num = None
                    current_verse_lines = []
                    pending_metadata = {}  # Clear for next verse

                # Extract metadata if configured (for NEXT verse)
                if extract_metadata:
                    text = line[1:].strip()
                    # கலிங்கத்துப்பரணி uses single * for subject
                    pending_metadata['subject'] = text
                continue  # Don't create subsection, just store metadata

            # #N Verse marker
            elif line.startswith('#'):
                # Save previous verse (WITHOUT metadata - it was already saved when * appeared)
                if current_verse_num is not None and current_verse_lines:
                    target_section = current_level2_section if current_level2_section else current_level1_section
                    if verse_numbering == 'global':
                        use_verse_num = global_verse_counter
                    else:
                        use_verse_num = verse_counter
                    self._add_verse(current_work_id, target_section,
                                  use_verse_num, current_verse_lines, {})  # Empty metadata
                    # DON'T clear pending_metadata - it's for THIS new verse

                # Extract verse number
                match = re.match(r'#(\d+)', line)
                if match:
                    current_verse_num = int(match.group(1))
                    # Increment both counters
                    verse_counter += 1
                    global_verse_counter += 1
                    current_verse_lines = []

            # Regular line (verse content)
            elif current_verse_num is not None:
                # Skip continuation markers
                if line == 'மேல்':
                    continue
                current_verse_lines.append(line)

        # Save final verse
        if current_verse_num is not None and current_verse_lines:
            target_section = current_level2_section if current_level2_section else current_level1_section
            if verse_numbering == 'global':
                use_verse_num = global_verse_counter
            else:
                use_verse_num = verse_counter
            self._add_verse(current_work_id, target_section,
                          use_verse_num, current_verse_lines, pending_metadata)

    def _parse_triple_ampersand_at_pattern(self, file_path: str, work_num: int):
        """
        Parse 3-level hierarchy: & (major division) → @ (subsection) → # (verse)
        Used by தஞ்சைவாணன் கோவை

        Structure:
        &1 களவியல்          # L1 major division
        @1 கைக்கிளை         # L2 subsection
        ** காட்சி           # Metadata
        #1                  # Verse (global numbering)
        """
        # Get configuration
        extract_metadata = WORK_METADATA[work_num]['extract_metadata']

        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        # Create work
        current_work_id = self._create_work(work_num)
        if not current_work_id:
            return

        # State tracking
        current_l1_section = None
        current_l2_section = None
        l1_counter = 0
        l2_counter = 0
        global_verse_counter = 0
        pending_metadata = {}
        verse_lines = []
        seen_work_title = False

        for line in lines:
            line = line.strip()

            # Skip empty lines
            if not line:
                continue

            # ** Work title or metadata
            if line.startswith('**'):
                if not seen_work_title:
                    seen_work_title = True
                    continue  # Skip work title

                # If we're in the middle of a verse, save it with current metadata FIRST
                if verse_lines and current_l2_section:
                    global_verse_counter += 1
                    self._add_verse(current_work_id, current_l2_section,
                                  global_verse_counter, verse_lines, pending_metadata)
                    verse_lines = []
                    pending_metadata = {}  # Clear for next verse

                # Extract metadata if configured (for NEXT verse)
                if extract_metadata:
                    text = line[2:].strip()

                    # Parse ragam/thalam
                    if 'இராகம்' in text or 'தாளம்' in text:
                        if 'இராகம்' in text:
                            ragam = text.split('இராகம்')[1].split('.')[0].strip(' :')
                            pending_metadata['ragam'] = ragam
                        if 'தாளம்' in text:
                            thalam = text.split('தாளம்')[1].split('.')[0].strip(' :')
                            pending_metadata['thalam'] = thalam

                    # Classify as paa_type or subject
                    elif is_paa_type(text):
                        pending_metadata['paa_type'] = text
                    else:
                        pending_metadata['subject'] = text

                continue

            # L1 major division (& marker)
            if line.startswith('&'):
                match = re.match(r'&(\d+)\s+(.+)', line)
                if match:
                    l1_counter += 1
                    section_name = match.group(2).strip()

                    current_l1_section = self._add_section(
                        current_work_id,
                        l1_counter,
                        section_name,
                        parent_section_id=None,
                        level_type='Division'
                    )
                    l2_counter = 0  # Reset L2 counter

            # L2 subsection (@ marker)
            elif line.startswith('@'):
                match = re.match(r'@(\d+)\s+(.+)', line)
                if match:
                    l2_counter += 1
                    section_name = match.group(2).strip()

                    current_l2_section = self._add_section(
                        current_work_id,
                        l2_counter,
                        section_name,
                        parent_section_id=current_l1_section,
                        level_type='Subsection'
                    )

            # Verse marker
            elif line.startswith('#'):
                # Save previous verse (WITHOUT metadata - it was already saved when ** appeared)
                if verse_lines:
                    global_verse_counter += 1
                    self._add_verse(current_work_id, current_l2_section,
                                  global_verse_counter, verse_lines, {})  # Empty metadata
                    verse_lines = []
                    # DON'T clear pending_metadata - it's for THIS new verse

            # Verse content
            elif line and current_l2_section:
                # Skip continuation markers
                if line == 'மேல்':
                    continue
                verse_lines.append(line)

        # Save last verse
        if verse_lines:
            global_verse_counter += 1
            self._add_verse(current_work_id, current_l2_section,
                          global_verse_counter, verse_lines, pending_metadata)

    def _parse_kandam_in_verse_pattern(self, file_path: str, work_num: int):
        """
        Parse Kandams extracted from #N SectionName format
        Used by நளவெண்பா

        Structure:
        #1 பாயிரம்          # Creates section "பாயிரம்"
        #2                   # Continues in same section
        #8 சுயம்வர காண்டம்  # Creates section "சுயம்வர காண்டம்"
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        # Create work
        current_work_id = self._create_work(work_num)
        if not current_work_id:
            return

        # State tracking
        section_map = {}  # Map section names to section IDs
        current_section = None
        current_section_name = None
        global_verse_counter = 0
        verse_lines = []
        section_counter = 0

        for line in lines:
            line = line.strip()

            # Skip empty lines and ** markers
            if not line or line.startswith('**'):
                continue

            # Verse marker with optional section name
            if line.startswith('#'):
                # Try to extract section name
                match = re.match(r'#(\d+)\s+(.+)', line)
                if match:
                    verse_num_in_file = int(match.group(1))
                    section_name = match.group(2).strip()

                    # Create section if new
                    if section_name not in section_map:
                        section_counter += 1
                        current_section = self._add_section(
                            current_work_id,
                            section_counter,
                            section_name,
                            level_type='Kandam'
                        )
                        section_map[section_name] = current_section
                        current_section_name = section_name
                    else:
                        current_section = section_map[section_name]
                        current_section_name = section_name
                else:
                    # Just #N without section name - continue in current section
                    pass

                # Save previous verse if exists
                if verse_lines and current_section:
                    global_verse_counter += 1
                    self._add_verse(current_work_id, current_section,
                                  global_verse_counter, verse_lines, None)
                    verse_lines = []

            # Verse content
            elif line and not line.startswith('**'):
                # Skip continuation markers
                if line == 'மேல்':
                    continue
                verse_lines.append(line)

        # Save last verse
        if verse_lines and current_section:
            global_verse_counter += 1
            self._add_verse(current_work_id, current_section,
                          global_verse_counter, verse_lines, None)

    def _parse_nested_double_star_pattern(self, file_path: str, work_num: int):
        """
        Parse complex ** pattern that serves dual purpose (sections AND metadata)
        Used by முக்கூடற்பள்ளு

        Detection rules:
        - **NoSpace (காப்பு) → L1 section
        - ** known L1 name → L1 section
        - ** ragam/thalam → metadata
        - ** paa_type → metadata
        - ** other → L2 subsection
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        # Create work
        current_work_id = self._create_work(work_num)
        if not current_work_id:
            return

        # State tracking
        current_l1_section = None
        current_l2_section = None
        l1_counter = 0
        l2_counter = 0
        global_verse_counter = 0
        pending_metadata = {}
        verse_lines = []
        skip_first_title = True  # Skip work title

        for line in lines:
            line_orig = line.rstrip('\n')
            line = line.strip()

            # Skip empty lines
            if not line:
                continue

            # ** marker - context-aware parsing
            if line.startswith('**'):
                # Skip work title (first ** line)
                if skip_first_title:
                    skip_first_title = False
                    continue

                text = line[2:].strip()

                # Ragam/thalam → always metadata
                if 'இராகம்' in text or 'தாளம்' in text:
                    if 'இராகம்' in text:
                        ragam = text.split('இராகம்')[1].split('.')[0].strip(' :')
                        pending_metadata['ragam'] = ragam
                    if 'தாளம்' in text:
                        thalam = text.split('தாளம்')[1].split('.')[0].strip(' :')
                        pending_metadata['thalam'] = thalam

                # Paa type → metadata
                elif is_paa_type(text):
                    pending_metadata['paa_type'] = text

                # Known L1 section name
                elif any(name in text for name in LEVEL1_SECTION_NAMES):
                    l1_counter += 1
                    current_l1_section = self._add_section(
                        current_work_id,
                        l1_counter,
                        text,
                        parent_section_id=None,
                        level_type='Section'
                    )
                    l2_counter = 0
                    current_l2_section = None  # Reset L2 section pointer

                # NoSpace pattern (e.g., **காப்பு)
                elif line_orig.startswith('**') and len(line_orig) > 2 and line_orig[2] != ' ':
                    # L1 section
                    l1_counter += 1
                    current_l1_section = self._add_section(
                        current_work_id,
                        l1_counter,
                        text,
                        parent_section_id=None,
                        level_type='Section'
                    )
                    l2_counter = 0
                    current_l2_section = None  # Reset L2 section pointer

                # Everything else → L2 subsection
                else:
                    l2_counter += 1
                    current_l2_section = self._add_section(
                        current_work_id,
                        l2_counter,
                        text,
                        parent_section_id=current_l1_section,
                        level_type='Subsection'
                    )

            # Verse marker
            elif line.startswith('#'):
                if verse_lines:
                    target_section = current_l2_section if current_l2_section else current_l1_section
                    global_verse_counter += 1
                    self._add_verse(current_work_id, target_section,
                                  global_verse_counter, verse_lines, pending_metadata)
                    verse_lines = []
                    pending_metadata = {}

            # Verse content
            elif line:
                # Skip continuation markers
                if line == 'மேல்':
                    continue
                verse_lines.append(line)

        # Save last verse
        if verse_lines:
            target_section = current_l2_section if current_l2_section else current_l1_section
            global_verse_counter += 1
            self._add_verse(current_work_id, target_section,
                          global_verse_counter, verse_lines, pending_metadata)

    def _parse_mukudal_fixed_sections_pattern(self, file_path: str, work_num: int):
        """
        Parse முக்கூடற் பள்ளு with fixed section mapping based on verse number ranges.
        All ** markers are treated as metadata only (paa type, ragam, thalam).

        Structure:
        - 11 pre-defined sections based on verse ranges
        - ** markers → metadata (paa_type, ragam, thalam)
        - # markers → verses (global numbering 0-175)
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        current_work_id = self._create_work(work_num)

        # Pre-create all sections based on verse ranges
        section_map = {}  # Maps verse number to section_id
        for idx, (start_verse, end_verse, section_name_tamil) in enumerate(MUKUDAL_PALLU_SECTIONS, start=1):
            section_id = self._add_section(
                current_work_id,
                idx,
                section_name_tamil,
                parent_section_id=None,
                level_type='Section'
            )
            # Map all verse numbers in range to this section
            for verse_num in range(start_verse, end_verse + 1):
                section_map[verse_num] = section_id

        global_verse_counter = 0
        pending_metadata = {}
        verse_lines = []
        skip_first_title = True  # Skip work title

        for line in lines:
            line = line.strip()

            # ** marker - always metadata
            if line.startswith('**'):
                # Skip work title (first ** line)
                if skip_first_title:
                    skip_first_title = False
                    continue

                # If we're in the middle of a verse, save it with current metadata FIRST
                if verse_lines:
                    section_id = section_map.get(global_verse_counter)
                    if section_id:
                        self._add_verse(current_work_id, section_id,
                                      global_verse_counter, verse_lines, pending_metadata)
                    global_verse_counter += 1
                    verse_lines = []
                    pending_metadata = {}  # Clear for next verse

                text = line[2:].strip()

                # Ragam/thalam → metadata (for NEXT verse)
                if 'இராகம்' in text or 'தாளம்' in text:
                    if 'இராகம்' in text:
                        ragam = text.split('இராகம்')[1].split('.')[0].strip(' :')
                        pending_metadata['ragam'] = ragam
                    if 'தாளம்' in text:
                        thalam = text.split('தாளம்')[1].split('.')[0].strip(' :')
                        pending_metadata['thalam'] = thalam

                # Paa type → metadata
                elif is_paa_type(text):
                    pending_metadata['paa_type'] = text

                # Other ** text → subject metadata
                else:
                    pending_metadata['subject'] = text

            # Verse marker
            elif line.startswith('#'):
                # Save previous verse (WITHOUT metadata - it was already saved when ** appeared)
                if verse_lines:
                    section_id = section_map.get(global_verse_counter)
                    if section_id:
                        self._add_verse(current_work_id, section_id,
                                      global_verse_counter, verse_lines, {})  # Empty metadata
                    global_verse_counter += 1
                    verse_lines = []
                    # DON'T clear pending_metadata - it's for THIS new verse

            # Verse content
            elif line:
                # Skip continuation markers
                if line == 'மேல்':
                    continue
                verse_lines.append(line)

        # Save last verse
        if verse_lines:
            section_id = section_map.get(global_verse_counter)
            if section_id:
                self._add_verse(current_work_id, section_id,
                              global_verse_counter, verse_lines, pending_metadata)

    def _bulk_copy(self, table_name: str, data: list, columns: list):
        """
        Copy data to table using psycopg2.cursor.copy_from()
        Use '\\N' for NULL values, tab-delimited format
        Manually formats TSV to avoid csv.writer escaping JSON strings
        """
        if not data:
            return

        # Create StringIO buffer
        buffer = io.StringIO()

        for row in data:
            row_values = []
            for col in columns:
                val = row.get(col)
                if val is None:
                    row_values.append('\\N')
                elif isinstance(val, dict):
                    # Serialize dict to JSON for JSONB columns
                    # Don't use csv.writer as it will escape quotes
                    row_values.append(json.dumps(val, ensure_ascii=False))
                else:
                    # Convert to string and escape tabs/newlines/backslashes
                    str_val = str(val)
                    str_val = str_val.replace('\\', '\\\\')  # Escape backslashes
                    str_val = str_val.replace('\t', '\\t')   # Escape tabs
                    str_val = str_val.replace('\n', '\\n')   # Escape newlines
                    str_val = str_val.replace('\r', '\\r')   # Escape carriage returns
                    row_values.append(str_val)

            # Write tab-delimited row
            buffer.write('\t'.join(row_values) + '\n')

        buffer.seek(0)

        # Use COPY command
        self.cursor.copy_from(buffer, table_name, columns=columns, null='\\N')


def print_header():
    """Print banner"""
    print("=" * 70)
    print("சிற்றிலக்கியங்கள் (Minor Literary Works) - Bulk Import")
    print("Collection 326: Twenty Minor Literary Works (12th-19th century CE)")
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
    4. Parse all 20 files
    5. Bulk insert
    6. Print summary
    """
    # Get database URL from command line or environment
    if len(sys.argv) > 1:
        db_url = sys.argv[1]
    else:
        db_url = os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@localhost/tamil_literature')

    # Set stdout to UTF-8 for Windows console (Tamil text support)
    if sys.platform == 'win32':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

    print_header()

    # Base directory for source files
    base_dir = Path(__file__).parent.parent / 'Tamil-Source-TamilConcordence' / '8_சிற்றிலக்கியங்கள்'

    # Check if directory exists
    if not base_dir.exists():
        print(f"\n✗ Error: Source directory not found: {base_dir}")
        print("  Please ensure Tamil-Source-TamilConcordence/8_சிற்றிலக்கியங்கள்/ exists")
        sys.exit(1)

    try:
        # Initialize importer (collection creation is automatic in __init__)
        importer = SitrilakkiyangalBulkImporter(db_url)

        # Parse all 20 files in order
        for work_num in range(1, 21):  # 1-20 inclusive
            file_path = base_dir / WORK_METADATA[work_num]['file']

            if not file_path.exists():
                print(f"  ✗ File not found: {file_path}")
                continue

            importer.parse_file(str(file_path), work_num)

        # Bulk insert
        importer.bulk_insert()

        # Print summary
        print_summary(importer)

        print("\n✓ Import complete! All 20 works imported successfully.")
        print("\nVerification queries:")
        print("  psql -U postgres -d tamil_literature")
        print("  SELECT work_name_tamil FROM works WHERE work_id IN")
        print("    (SELECT work_id FROM work_collections WHERE collection_id = 324);")

    except psycopg2.IntegrityError as e:
        print(f"\n✗ Database integrity error: {e}")
        print("  Possible causes:")
        print("  - Work already exists (run delete script first)")
        print("  - Duplicate IDs (check ID allocation logic)")
        importer.rollback()
        sys.exit(1)

    except FileNotFoundError as e:
        print(f"\n✗ File error: {e}")
        print("  Check Tamil-Source-TamilConcordence/8_சிற்றிலக்கியங்கள்/ directory")
        sys.exit(1)

    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        importer.rollback()
        sys.exit(1)

    finally:
        importer.close()


if __name__ == '__main__':
    main()
