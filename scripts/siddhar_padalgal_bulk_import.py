#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Siddhar Padalgal (சித்தர் பாடல்கள்) Bulk Import
Fast 2-phase import using PostgreSQL COPY

Phase 1: Parse text → Build data structures in memory
Phase 2: Bulk COPY into database (1000x faster than INSERT)

Collection ID: 327 (சித்தர் பாடல்கள் - Siddhar Padalgal)

Works (36 Siddhar mystical poetry texts):
Songs of the Tamil Siddhars - mystic poets and yogis
spanning 7th-19th century CE (some attributions legendary)

Structure:
- ** சித்தர் பாடல்கள் (collection header)
- @N Work identifier
- ** Section markers (ஞானம், யோக நிலை, பூஜாவிதி, etc.)
- #N Verse markers
- *N-N Metadata markers (section-verse reference)
- Verse lines

IMPORTANT: This parser stores metadata in JSONB columns:
- sections.metadata: Section type, category, poetic form
- verses.metadata: Section-verse cross-reference (*N-N markers)
"""

import re
import psycopg2
from pathlib import Path
import csv
import io
import sys
import os
import json
from word_cleaning import split_and_clean_words

# Work metadata for all 36 works
# NOTE: Many Siddhars have legendary/traditional dates that differ from historical estimates
# Periods given are approximate based on linguistic and traditional evidence
WORK_METADATA = {
    1: {
        'work_name': 'Agathiyar Gnanam',
        'work_name_tamil': 'அகத்தியர் ஞானம்',
        'author': 'Agathiyar',
        'author_tamil': 'அகத்தியர்',
        'period': '7th-9th century CE (attributed)',
        'canonical_order': 327001,
        'position_in_collection': 1,
        'file': '1 அகத்தியர் ஞானம்.txt',
        'description': 'Wisdom teachings attributed to the legendary Siddhar Agathiyar'
    },
    2: {
        'work_name': 'Agappey Siddhar Paadal',
        'work_name_tamil': 'அகப்பேய்ச் சித்தர் பாடல்',
        'author': 'Agappey Siddhar',
        'author_tamil': 'அகப்பேய்ச் சித்தர்',
        'period': '10th-14th century CE',
        'canonical_order': 327002,
        'position_in_collection': 2,
        'file': '2 அகப்பேய்ச் சித்தர் பாடல்.txt',
        'description': 'Songs of Siddhar Agappey on spiritual knowledge and yoga'
    },
    3: {
        'work_name': 'Azhugani Siddhar Paadal',
        'work_name_tamil': 'அழுகணிச் சித்தர் பாடல்',
        'author': 'Azhugani Siddhar',
        'author_tamil': 'அழுகணிச் சித்தர்',
        'period': '10th-14th century CE',
        'canonical_order': 327003,
        'position_in_collection': 3,
        'file': '3 அழுகணிச் சித்தர் பாடல்.txt',
        'description': 'Songs of Siddhar Azhugani on mysticism and enlightenment'
    },
    4: {
        'work_name': 'Adhinathar (Vedantha Siddhar) Paadal',
        'work_name_tamil': 'ஆதிநாதர் என்ற வேதாந்தச் சித்தர் பாடல்',
        'author': 'Adhinathar (Vedantha Siddhar)',
        'author_tamil': 'ஆதிநாதர் (வேதாந்தச் சித்தர்)',
        'period': '10th-14th century CE',
        'canonical_order': 327004,
        'position_in_collection': 4,
        'file': '4 ஆதிநாதர் என்ற வேதாந்தச் சித்தர் பாடல்.txt',
        'description': 'Vedantic teachings of Siddhar Adhinathar'
    },
    5: {
        'work_name': 'Idaikkaadu Siddhar Paadal',
        'work_name_tamil': 'இடைக்காட்டுச் சித்தர் பாடல்',
        'author': 'Idaikkaadu Siddhar',
        'author_tamil': 'இடைக்காட்டுச் சித்தர்',
        'period': '10th-14th century CE',
        'canonical_order': 327005,
        'position_in_collection': 5,
        'file': '5 இடைக்காட்டுச் சித்தர் பாடல்.txt',
        'description': 'Songs of Siddhar Idaikkaadu on yogic practices'
    },
    6: {
        'work_name': 'Ramadhevar - Poosaavidhi',
        'work_name_tamil': 'இராமதேவர் – பூசாவிதி',
        'author': 'Ramadhevar',
        'author_tamil': 'இராமதேவர்',
        'period': '10th-14th century CE',
        'canonical_order': 327006,
        'position_in_collection': 6,
        'file': '6. இராமதேவர் – பூசாவிதி.txt',
        'description': 'Worship method by Ramadhevar Siddhar'
    },
    7: {
        'work_name': 'Uroma Rishi Gnanam',
        'work_name_tamil': 'உரோம ரிஷி ஞானம்',
        'author': 'Uroma Rishi',
        'author_tamil': 'உரோம ரிஷி',
        'period': '7th-10th century CE (attributed)',
        'canonical_order': 327007,
        'position_in_collection': 7,
        'file': '7 உரோம ரிஷி ஞானம்.txt',
        'description': 'Wisdom teachings of Rishi Uroma'
    },
    8: {
        'work_name': 'Ekanathar (Brahmanantha Siddhar) Paadal',
        'work_name_tamil': 'ஏகநாதர் என்ற பிரம்மானந்தச் சித்தர் பாடல்',
        'author': 'Ekanathar (Brahmanantha Siddhar)',
        'author_tamil': 'ஏகநாதர் (பிரம்மானந்தச் சித்தர்)',
        'period': '10th-14th century CE',
        'canonical_order': 327008,
        'position_in_collection': 8,
        'file': '8 ஏகநாதர் என்ற பிரம்மானந்தச் சித்தர் பாடல்.txt',
        'description': 'Songs of Brahmanantha Siddhar on divine bliss'
    },
    9: {
        'work_name': 'Kanjamalai Siddhar Paadal',
        'work_name_tamil': 'கஞ்சமலைச் சித்தர் பாடல்',
        'author': 'Kanjamalai Siddhar',
        'author_tamil': 'கஞ்சமலைச் சித்தர்',
        'period': '10th-14th century CE',
        'canonical_order': 327009,
        'position_in_collection': 9,
        'file': '9 கஞ்சமலைச் சித்தர் பாடல்.txt',
        'description': 'Songs of Siddhar Kanjamalai'
    },
    10: {
        'work_name': 'Kaduveli Siddhar Paadal',
        'work_name_tamil': 'கடுவெளிச் சித்தர் பாடல்',
        'author': 'Kaduveli Siddhar',
        'author_tamil': 'கடுவெளிச் சித்தர்',
        'period': '10th-14th century CE',
        'canonical_order': 327010,
        'position_in_collection': 10,
        'file': '10 கடுவெளிச் சித்தர் பாடல்.txt',
        'description': 'Songs of Siddhar Kaduveli'
    },
    11: {
        'work_name': 'Kadaendra Nathar (Vilaiyaadu Siddhar) Paadal',
        'work_name_tamil': 'கடேந்திர நாதர் என்ற விளையாட்டுச் சித்தர் பாடல்',
        'author': 'Kadaendra Nathar (Vilaiyaadu Siddhar)',
        'author_tamil': 'கடேந்திர நாதர் (விளையாட்டுச் சித்தர்)',
        'period': '10th-14th century CE',
        'canonical_order': 327011,
        'position_in_collection': 11,
        'file': '11 கடேந்திர நாதர் என்ற விளையாட்டுச் சித்தர் பாடல்.txt',
        'description': 'Playful songs of Siddhar Kadaendra Nathar'
    },
    12: {
        'work_name': 'Karuvurar - Poojaavidhi',
        'work_name_tamil': 'கருவூரார் – பூஜாவிதி',
        'author': 'Karuvurar',
        'author_tamil': 'கருவூரார்',
        'period': '9th-10th century CE',
        'canonical_order': 327012,
        'position_in_collection': 12,
        'file': '12 கருவூரார் – பூஜாவிதி.txt',
        'description': 'Worship method by the renowned Siddhar Karuvurar'
    },
    13: {
        'work_name': 'Kalluli Siddhar Paadal',
        'work_name_tamil': 'கல்லுளிச் சித்தர் பாடல்',
        'author': 'Kalluli Siddhar',
        'author_tamil': 'கல்லுளிச் சித்தர்',
        'period': '10th-14th century CE',
        'canonical_order': 327013,
        'position_in_collection': 13,
        'file': '13 கல்லுளிச் சித்தர் பாடல்.txt',
        'description': 'Songs of Siddhar Kalluli'
    },
    14: {
        'work_name': 'Kaagapusundar',
        'work_name_tamil': 'காகபுசுண்டர்',
        'author': 'Kaagapusundar',
        'author_tamil': 'காகபுசுண்டர்',
        'period': '10th-14th century CE (attributed)',
        'canonical_order': 327014,
        'position_in_collection': 14,
        'file': '14 காகபுசுண்டர்.txt',
        'description': 'Songs of the legendary Siddhar Kaagapusundar'
    },
    15: {
        'work_name': 'Kaayakka Kappal',
        'work_name_tamil': 'காயக் கப்பல்',
        'author': 'Unknown Siddhar',
        'author_tamil': 'அறியப்படாத சித்தர்',
        'period': '10th-15th century CE',
        'canonical_order': 327015,
        'position_in_collection': 15,
        'file': '15 காயக் கப்பல்.txt',
        'description': 'Ship of the Body - metaphorical teachings on the physical body as a spiritual vessel'
    },
    16: {
        'work_name': 'Kaarai Siddhar',
        'work_name_tamil': 'காரைச் சித்தர்',
        'author': 'Kaarai Siddhar',
        'author_tamil': 'காரைச் சித்தர்',
        'period': '10th-14th century CE',
        'canonical_order': 327016,
        'position_in_collection': 16,
        'file': '16 காரைச் சித்தர்.txt',
        'description': 'Songs of Siddhar Kaarai'
    },
    17: {
        'work_name': 'Kudhambai Siddhar',
        'work_name_tamil': 'குதம்பைச் சித்தர்',
        'author': 'Kudhambai Siddhar',
        'author_tamil': 'குதம்பைச் சித்தர்',
        'period': '10th-14th century CE',
        'canonical_order': 327017,
        'position_in_collection': 17,
        'file': '17 குதம்பைச் சித்தர்.txt',
        'description': 'Songs of Siddhar Kudhambai'
    },
    18: {
        'work_name': 'Kongana Siddhar',
        'work_name_tamil': 'கொங்கண சித்தர்',
        'author': 'Kongana Siddhar',
        'author_tamil': 'கொங்கண சித்தர்',
        'period': '10th-14th century CE',
        'canonical_order': 327018,
        'position_in_collection': 18,
        'file': '18 கொங்கண சித்தர்.txt',
        'description': 'Songs of Siddhar Kongana'
    },
    19: {
        'work_name': 'Kailayakka Kampali Sattai Muni Nayanar',
        'work_name_tamil': 'கைலாயக் கம்பளிச் சட்டை முனி நாயனார்',
        'author': 'Kailayakka Kampali Sattai Muni',
        'author_tamil': 'கைலாயக் கம்பளிச் சட்டை முனி',
        'period': '10th-14th century CE',
        'canonical_order': 327019,
        'position_in_collection': 19,
        'file': '19 கைலாயக் கம்பளிச் சட்டை முனி நாயனார்.txt',
        'description': 'Songs of the Blanket-Robed Muni of Kailash'
    },
    20: {
        'work_name': 'Sangili Siddhar Paadal',
        'work_name_tamil': 'சங்கிலிச் சித்தர் பாடல்',
        'author': 'Sangili Siddhar',
        'author_tamil': 'சங்கிலிச் சித்தர்',
        'period': '10th-14th century CE',
        'canonical_order': 327020,
        'position_in_collection': 20,
        'file': '20 சங்கிலிச் சித்தர் பாடல்.txt',
        'description': 'Songs of Siddhar Sangili'
    },
    21: {
        'work_name': 'Sattai Muni Gnanam',
        'work_name_tamil': 'சட்டை முனி ஞானம்',
        'author': 'Sattai Muni',
        'author_tamil': 'சட்டை முனி',
        'period': '10th-14th century CE',
        'canonical_order': 327021,
        'position_in_collection': 21,
        'file': '21 சட்டை முனி ஞானம்.txt',
        'description': 'Wisdom of Sattai Muni'
    },
    22: {
        'work_name': 'Sathiya Nathar (Gnana Siddhar) Paadal',
        'work_name_tamil': 'சத்திய நாதர் என்ற ஞானச் சித்தர் பாடல்',
        'author': 'Sathiya Nathar (Gnana Siddhar)',
        'author_tamil': 'சத்திய நாதர் (ஞானச் சித்தர்)',
        'period': '10th-14th century CE',
        'canonical_order': 327022,
        'position_in_collection': 22,
        'file': '22 சத்திய நாதர் என்ற ஞானச் சித்தர் பாடல்.txt',
        'description': 'Songs of Gnana Siddhar on truth and wisdom'
    },
    23: {
        'work_name': 'Sadhotha Nathar (Yoga Siddhar) Paadal',
        'work_name_tamil': 'சதோத நாதர் என்ற யோகச் சித்தர் பாடல்',
        'author': 'Sadhotha Nathar (Yoga Siddhar)',
        'author_tamil': 'சதோத நாதர் (யோகச் சித்தர்)',
        'period': '10th-14th century CE',
        'canonical_order': 327023,
        'position_in_collection': 23,
        'file': '23 சதோத நாதர் என்ற யோகச் சித்தர் பாடல்.txt',
        'description': 'Yogic teachings of Siddhar Sadhotha Nathar'
    },
    24: {
        'work_name': 'Sivavaakiyar',
        'work_name_tamil': 'சிவவாக்கியர்',
        'author': 'Sivavaakiyar',
        'author_tamil': 'சிவவாக்கியர்',
        'period': '10th-12th century CE',
        'canonical_order': 327024,
        'position_in_collection': 24,
        'file': '24 சிவவாக்கியர்.txt',
        'description': 'Songs of the renowned Siddhar Sivavaakiyar, known for radical spiritual philosophy'
    },
    25: {
        'work_name': 'Sooriyaanandhar Soothiram',
        'work_name_tamil': 'சூரியானந்தர் சூத்திரம்',
        'author': 'Sooriyaanandhar',
        'author_tamil': 'சூரியானந்தர்',
        'period': '10th-14th century CE',
        'canonical_order': 327025,
        'position_in_collection': 25,
        'file': '25 சூரியானந்தர் சூத்திரம்.txt',
        'description': 'Aphorisms of Sooriyaanandhar Siddhar'
    },
    26: {
        'work_name': 'Thadangan Siddhar Paadalkal',
        'work_name_tamil': 'தடங்கண் சித்தர் பாடல்கள்',
        'author': 'Thadangan Siddhar',
        'author_tamil': 'தடங்கண் சித்தர்',
        'period': '10th-14th century CE',
        'canonical_order': 327026,
        'position_in_collection': 26,
        'file': '26 தடங்கண் சித்தர் பாடல்கள்.txt',
        'description': 'Songs of Siddhar Thadangan'
    },
    27: {
        'work_name': 'Thirikona Siddhar Paadal',
        'work_name_tamil': 'திரிகோணச் சித்தர் பாடல்',
        'author': 'Thirikona Siddhar',
        'author_tamil': 'திரிகோணச் சித்தர்',
        'period': '10th-14th century CE',
        'canonical_order': 327027,
        'position_in_collection': 27,
        'file': '27 திரிகோணச் சித்தர் பாடல்.txt',
        'description': 'Songs of Siddhar Thirikona'
    },
    28: {
        'work_name': 'Thirumoolar Nayanar',
        'work_name_tamil': 'திருமூல நாயனார்',
        'author': 'Thirumoolar',
        'author_tamil': 'திருமூலர்',
        'period': '8th-9th century CE (traditional)',
        'canonical_order': 327028,
        'position_in_collection': 28,
        'file': '28. திருமூல நாயனார்.txt',
        'description': 'Songs attributed to the great Siddhar Thirumoolar (author of Thirumanthiram)'
    },
    29: {
        'work_name': 'Thiruvalluvar Gnanam',
        'work_name_tamil': 'திருவள்ளுவர் ஞானம்',
        'author': 'Attributed to Thiruvalluvar',
        'author_tamil': 'திருவள்ளுவர் (பெயரில்)',
        'period': '10th-15th century CE (attributed)',
        'canonical_order': 327029,
        'position_in_collection': 29,
        'file': '29 திருவள்ளுவர் ஞானம்.txt',
        'description': 'Mystical wisdom attributed to the name of Thiruvalluvar'
    },
    30: {
        'work_name': 'Pattinatthu Siddhar Gnanam',
        'work_name_tamil': 'பட்டினத்துச் சித்தர் ஞானம்',
        'author': 'Pattinatthu Siddhar (Thiruvenkadar)',
        'author_tamil': 'பட்டினத்துச் சித்தர் (திருவெங்கதர்)',
        'period': '11th-12th century CE',
        'canonical_order': 327030,
        'position_in_collection': 30,
        'file': '30 பட்டினத்துச் சித்தர் ஞானம்.txt',
        'description': 'Wisdom of the renowned Siddhar Pattinatthu (also known as Thiruvenkadar)'
    },
    31: {
        'work_name': 'Pathiragiriyaarin Meygnaanap Pulambal',
        'work_name_tamil': 'பத்திரகிரியாரின் மெய்ஞ்ஞானப் புலம்பல்',
        'author': 'Pathiragiriyaar',
        'author_tamil': 'பத்திரகிரியார்',
        'period': '10th-14th century CE',
        'canonical_order': 327031,
        'position_in_collection': 31,
        'file': '31 பத்திரகிரியாரின் மெய்ஞ்ஞானப் புலம்பல்.txt',
        'description': 'Lament on True Knowledge by Siddhar Pathiragiriyaar'
    },
    32: {
        'work_name': 'Paambaatti Siddhar',
        'work_name_tamil': 'பாம்பாட்டிச் சித்தர்',
        'author': 'Paambaatti Siddhar',
        'author_tamil': 'பாம்பாட்டிச் சித்தர்',
        'period': '10th-14th century CE',
        'canonical_order': 327032,
        'position_in_collection': 32,
        'file': '32 பாம்பாட்டிச் சித்தர்.txt',
        'description': 'Songs of the Snake-Charmer Siddhar'
    },
    33: {
        'work_name': 'Punnaakku Siddhar Paadal',
        'work_name_tamil': 'புண்ணாக்குச் சித்தர் பாடல்',
        'author': 'Punnaakku Siddhar',
        'author_tamil': 'புண்ணாக்குச் சித்தர்',
        'period': '10th-14th century CE',
        'canonical_order': 327033,
        'position_in_collection': 33,
        'file': '33 புண்ணாக்குச் சித்தர் பாடல்.txt',
        'description': 'Songs of Siddhar Punnaakku'
    },
    34: {
        'work_name': 'Machaendhira Nathar (Nondi Siddhar) Paadal',
        'work_name_tamil': 'மச்சேந்திர நாதர் என்ற நொண்டிச் சித்தர் பாடல்',
        'author': 'Machaendhira Nathar (Nondi Siddhar)',
        'author_tamil': 'மச்சேந்திர நாதர் (நொண்டிச் சித்தர்)',
        'period': '10th-14th century CE',
        'canonical_order': 327034,
        'position_in_collection': 34,
        'file': '34 மச்சேந்திர நாதர் என்ற நொண்டிச் சித்தர் பாடல்.txt',
        'description': 'Songs of the Limping Siddhar Machaendhira Nathar'
    },
    35: {
        'work_name': 'Vagulinathar (Mauna Siddhar) Paadal',
        'work_name_tamil': 'வகுளிநாதர் என்னும் மௌனச்சித்தர் பாடல்',
        'author': 'Vagulinathar (Mauna Siddhar)',
        'author_tamil': 'வகுளிநாதர் (மௌனச்சித்தர்)',
        'period': '10th-14th century CE',
        'canonical_order': 327035,
        'position_in_collection': 35,
        'file': '35 வகுளிநாதர் என்னும் மௌனச்சித்தர் பாடல்.txt',
        'description': 'Songs of the Silent Siddhar Vagulinathar'
    },
    36: {
        'work_name': 'Valmiki',
        'work_name_tamil': 'வால்மீகர்',
        'author': 'Attributed to Valmiki',
        'author_tamil': 'வால்மீகர் (பெயரில்)',
        'period': '10th-15th century CE (attributed)',
        'canonical_order': 327036,
        'position_in_collection': 36,
        'file': '36 வால்மீகர்.txt',
        'description': 'Tamil Siddha poetry attributed to the legendary Valmiki'
    }
}


class SiddharPadalgalBulkImporter:
    """Import all 36 Siddhar works using 2-phase bulk COPY pattern"""

    def __init__(self, db_connection_string: str):
        """Initialize importer and query MAX IDs from ALL tables"""
        self.conn = psycopg2.connect(db_connection_string)
        self.cursor = self.conn.cursor()
        self.collection_id = 327

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
        self.current_section_id = None
        self.section_counter = 0  # For section numbering

    def _ensure_collection_exists(self):
        """Create collection 327 if missing"""
        # Check if collection exists
        self.cursor.execute("SELECT collection_id FROM collections WHERE collection_id = %s",
                          (self.collection_id,))
        existing = self.cursor.fetchone()

        if not existing:
            print(f"  Creating Siddhar Padalgal collection (ID: {self.collection_id})...")
            self.cursor.execute("""
                INSERT INTO collections (
                    collection_id, collection_name, collection_name_tamil,
                    collection_type, description, parent_collection_id, sort_order
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                self.collection_id,
                'Siddhar Padalgal',
                'சித்தர் பாடல்கள்',
                'tradition',
                'Thirty-six mystical and spiritual poetry works by Tamil Siddhars (7th-19th century CE) - Songs of enlightened yogis and mystics',
                1,  # Parent: தமிழ் இலக்கியம் (designated filter collection)
                6   # After Thirumurai=1, NDPD=2, Devotional=3, சிற்றிலக்கியங்கள்=4, நீதிநூல்கள்=5
            ))
            print(f"  [OK] Collection created (will commit with bulk data)")
        else:
            print(f"  Found existing Siddhar Padalgal collection (ID: {self.collection_id})")

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
            print(f"  [ERROR] Work {metadata['work_name']} already exists (ID: {existing[0]})")
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
            'description': metadata.get('description', ''),
            'canonical_order': metadata['canonical_order']
        })

        # Link work to collection 327
        self.work_collections.append({
            'work_id': work_id,
            'collection_id': self.collection_id,
            'position_in_collection': metadata['position_in_collection']
        })

        print(f"  Created work: {metadata['work_name']} (ID: {work_id}, Canonical: {metadata['canonical_order']})")
        return work_id

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
        elif 'காப்பு' in section_name:
            metadata['category'] = 'invocation'
        elif 'நூல்' in section_name:
            metadata['category'] = 'text_body'
        elif 'நிலை' in section_name:
            metadata['category'] = 'state'
        else:
            metadata['category'] = 'general'

        return metadata

    def _add_section(self, work_id: int, section_name: str,
                     section_metadata: dict) -> int:
        """Add section with metadata to in-memory list and return section_id"""
        section_id = self.section_id
        self.section_id += 1  # Manual increment
        self.section_counter += 1  # Increment section counter

        self.sections.append({
            'section_id': section_id,
            'work_id': work_id,
            'parent_section_id': None,  # No parent - all sections are Level 1
            'level_type': 'Section',
            'level_type_tamil': 'பகுதி',
            'section_number': self.section_counter,
            'section_name': section_name,
            'section_name_tamil': section_name,
            'sort_order': self.section_counter,
            'metadata': json.dumps(section_metadata, ensure_ascii=False)  # Store as JSON
        })

        return section_id

    def _add_verse(self, work_id: int, section_id: int, verse_num: int,
                   verse_lines: list, verse_metadata: dict):
        """Add verse with metadata, lines, and words to in-memory lists"""
        if not verse_lines:
            return

        # Create verse
        verse_id = self.verse_id
        self.verse_id += 1

        # Convert metadata to JSON string
        metadata_json = json.dumps(verse_metadata, ensure_ascii=False) if verse_metadata else None

        self.verses.append({
            'verse_id': verse_id,
            'work_id': work_id,
            'section_id': section_id,
            'verse_number': verse_num,
            'verse_type': 'Siddhar Song',
            'verse_type_tamil': 'சித்தர் பாடல்',
            'total_lines': len(verse_lines),
            'sort_order': verse_num,
            'metadata': metadata_json
        })

        # Create lines and words
        for line_num, line_text in enumerate(verse_lines, start=1):
            line_id = self.line_id
            self.line_id += 1

            # Clean line text
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

    def _create_default_section(self, work_id: int) -> int:
        """Create a default section for works without explicit sections"""
        default_metadata = {
            'section_type': 'Main Text',
            'numbered_section': False,
            'category': 'general'
        }
        return self._add_section(work_id, 'Main Text', default_metadata)

    def parse_file(self, file_path: str, work_num: int):
        """
        Parse one Siddhar work file (Phase 1: Parse into memory)

        Structure:
        - ** சித்தர் பாடல்கள் (collection header - skip)
        - @N Work identifier
        - ** Section marker (with metadata) - OPTIONAL
        - #N Verse marker
        - *N-N Metadata marker (section-verse reference) - OPTIONAL
        - Lines accumulate until blank line or next marker
        """
        print(f"\nParsing File {work_num}: {Path(file_path).name}")

        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        # State tracking
        current_work_id = None
        current_section_id = None
        current_section_metadata = {}
        current_verse_num = None
        current_verse_metadata = {}  # From *N-N marker
        current_verse_lines = []
        self.section_counter = 0  # Reset for each work
        needs_default_section = False  # Flag to create default section when first verse appears

        for line in lines:
            line = line.strip()

            # Empty line - triggers verse save
            if not line:
                if current_verse_num is not None and current_verse_lines:
                    self._add_verse(current_work_id, current_section_id,
                                  current_verse_num, current_verse_lines,
                                  current_verse_metadata)
                    current_verse_num = None
                    current_verse_lines = []
                    current_verse_metadata = {}
                continue

            # @N Work identifier
            if line.startswith('@'):
                # Save previous verse
                if current_verse_num is not None and current_verse_lines:
                    self._add_verse(current_work_id, current_section_id,
                                  current_verse_num, current_verse_lines,
                                  current_verse_metadata)

                # Extract work number from @N pattern (may or may not have dot)
                match = re.match(r'@(\d+)\.?\s*(.*)', line)
                if match:
                    file_work_num = int(match.group(1))
                    if file_work_num != work_num:
                        print(f"  [WARNING] File work number {file_work_num} doesn't match expected {work_num}")

                    # Create work
                    current_work_id = self._create_work(work_num)
                    current_section_id = None
                    current_verse_num = None
                    current_verse_lines = []
                    current_verse_metadata = {}
                    self.section_counter = 0
                    needs_default_section = True  # Will create default section when first verse appears

            # ** Section marker
            elif line.startswith('**'):
                # Skip collection header "** சித்தர் பாடல்கள்"
                if 'சித்தர் பாடல்கள்' in line:
                    continue

                # Save previous verse
                if current_verse_num is not None and current_verse_lines:
                    self._add_verse(current_work_id, current_section_id,
                                  current_verse_num, current_verse_lines,
                                  current_verse_metadata)
                    current_verse_num = None
                    current_verse_lines = []
                    current_verse_metadata = {}

                # Parse section name and extract metadata
                section_name = line.replace('**', '').strip()
                if section_name:  # Only create section if name is not empty
                    current_section_metadata = self._parse_section_metadata(section_name)
                    current_section_id = self._add_section(
                        current_work_id,
                        section_name,
                        current_section_metadata
                    )

            # *N-N Metadata marker (section-verse reference)
            elif line.startswith('*'):
                # Extract section-verse reference
                match = re.match(r'\*(\d+)-(\d+)', line)
                if match:
                    current_verse_metadata = {
                        'section_verse_ref': f"{match.group(1)}-{match.group(2)}",
                        'section_number': int(match.group(1)),
                        'verse_in_section': int(match.group(2))
                    }

            # #N Verse marker
            elif line.startswith('#'):
                # Create default section if needed (for works without explicit sections)
                if needs_default_section and current_section_id is None:
                    current_section_id = self._create_default_section(current_work_id)
                    needs_default_section = False

                # Save previous verse
                if current_verse_num is not None and current_verse_lines:
                    self._add_verse(current_work_id, current_section_id,
                                  current_verse_num, current_verse_lines,
                                  current_verse_metadata)

                # Extract verse number
                match = re.match(r'#(\d+)', line)
                if match:
                    current_verse_num = int(match.group(1))
                    current_verse_lines = []
                    # Keep current_verse_metadata from previous * line (if any)

            # Regular line (verse content)
            elif current_verse_num is not None:
                current_verse_lines.append(line)

        # Save final verse if any
        if current_verse_num is not None and current_verse_lines:
            self._add_verse(current_work_id, current_section_id,
                          current_verse_num, current_verse_lines,
                          current_verse_metadata)

    def bulk_insert(self):
        """Phase 2: Bulk COPY all data into PostgreSQL"""
        print("\n=== Phase 2: Bulk COPY into database ===")

        # Insert works
        if self.works:
            print(f"  Inserting {len(self.works)} works...")
            works_buffer = io.StringIO()
            writer = csv.writer(works_buffer, delimiter='\t')
            for work in self.works:
                writer.writerow([
                    work['work_id'],
                    work['work_name'],
                    work['work_name_tamil'],
                    work.get('period', ''),
                    work.get('author', ''),
                    work.get('author_tamil', ''),
                    work.get('description', ''),
                    work.get('canonical_order', None)
                ])
            works_buffer.seek(0)
            self.cursor.copy_from(
                works_buffer,
                'works',
                columns=['work_id', 'work_name', 'work_name_tamil', 'period',
                        'author', 'author_tamil', 'description', 'canonical_order'],
                null=''
            )

        # Insert sections (with metadata)
        if self.sections:
            print(f"  Inserting {len(self.sections)} sections...")
            sections_buffer = io.StringIO()
            for section in self.sections:
                # Manually format the row to avoid CSV escaping of JSON
                metadata_value = section.get('metadata', None)
                if metadata_value:
                    # Replace tab characters in JSON to avoid breaking the format
                    metadata_value = metadata_value.replace('\t', ' ')
                row = [
                    str(section['section_id']),
                    str(section['work_id']),
                    str(section.get('parent_section_id', '')) if section.get('parent_section_id') else '',
                    section['level_type'],
                    section.get('level_type_tamil', ''),
                    str(section['section_number']),
                    section.get('section_name', ''),
                    section.get('section_name_tamil', ''),
                    str(section['sort_order']),
                    metadata_value if metadata_value else ''
                ]
                sections_buffer.write('\t'.join(row) + '\n')
            sections_buffer.seek(0)
            self.cursor.copy_from(
                sections_buffer,
                'sections',
                columns=['section_id', 'work_id', 'parent_section_id', 'level_type',
                        'level_type_tamil', 'section_number', 'section_name',
                        'section_name_tamil', 'sort_order', 'metadata'],
                null=''
            )

        # Insert verses (with metadata)
        if self.verses:
            print(f"  Inserting {len(self.verses)} verses...")
            verses_buffer = io.StringIO()
            for verse in self.verses:
                # Manually format the row to avoid CSV escaping of JSON
                metadata_value = verse.get('metadata', None)
                if metadata_value:
                    # Replace tab characters in JSON to avoid breaking the format
                    metadata_value = metadata_value.replace('\t', ' ')
                row = [
                    str(verse['verse_id']),
                    str(verse['work_id']),
                    str(verse['section_id']),
                    str(verse['verse_number']),
                    verse.get('verse_type', ''),
                    verse.get('verse_type_tamil', ''),
                    str(verse['total_lines']),
                    str(verse['sort_order']),
                    metadata_value if metadata_value else ''
                ]
                verses_buffer.write('\t'.join(row) + '\n')
            verses_buffer.seek(0)
            self.cursor.copy_from(
                verses_buffer,
                'verses',
                columns=['verse_id', 'work_id', 'section_id', 'verse_number',
                        'verse_type', 'verse_type_tamil', 'total_lines',
                        'sort_order', 'metadata'],
                null=''
            )

        # Insert lines
        if self.lines:
            print(f"  Inserting {len(self.lines)} lines...")
            lines_buffer = io.StringIO()
            writer = csv.writer(lines_buffer, delimiter='\t')
            for line in self.lines:
                writer.writerow([
                    line['line_id'],
                    line['verse_id'],
                    line['line_number'],
                    line['line_text']
                ])
            lines_buffer.seek(0)
            self.cursor.copy_from(
                lines_buffer,
                'lines',
                columns=['line_id', 'verse_id', 'line_number', 'line_text'],
                null=''
            )

        # Insert words
        if self.words:
            print(f"  Inserting {len(self.words)} words...")
            words_buffer = io.StringIO()
            writer = csv.writer(words_buffer, delimiter='\t')
            for word in self.words:
                writer.writerow([
                    word['word_id'],
                    word['line_id'],
                    word['word_position'],
                    word['word_text'],
                    word.get('sandhi_split', '')
                ])
            words_buffer.seek(0)
            self.cursor.copy_from(
                words_buffer,
                'words',
                columns=['word_id', 'line_id', 'word_position', 'word_text', 'sandhi_split'],
                null=''
            )

        # Insert work_collections
        if self.work_collections:
            print(f"  Inserting {len(self.work_collections)} work-collection links...")
            wc_buffer = io.StringIO()
            writer = csv.writer(wc_buffer, delimiter='\t')
            for wc in self.work_collections:
                writer.writerow([
                    wc['work_id'],
                    wc['collection_id'],
                    wc['position_in_collection']
                ])
            wc_buffer.seek(0)
            self.cursor.copy_from(
                wc_buffer,
                'work_collections',
                columns=['work_id', 'collection_id', 'position_in_collection'],
                null=''
            )

        # Commit transaction
        self.conn.commit()
        print(f"  [OK] All data committed successfully!")

    def run(self, source_dir: str):
        """Main execution: Parse all files and bulk insert"""
        try:
            print("=== Siddhar Padalgal (சித்தர் பாடல்கள்) Bulk Import ===")
        except UnicodeEncodeError:
            print("=== Siddhar Padalgal Bulk Import ===")
        print(f"Source directory: {source_dir}\n")

        # Ensure collection exists
        self._ensure_collection_exists()

        # Phase 1: Parse all 36 files into memory
        print("\n=== Phase 1: Parsing all 36 works into memory ===")
        for work_num in range(1, 37):
            if work_num not in WORK_METADATA:
                print(f"[WARNING] Skipping work {work_num} - no metadata found")
                continue

            file_name = WORK_METADATA[work_num]['file']
            file_path = Path(source_dir) / file_name

            if not file_path.exists():
                print(f"[ERROR] File not found: {file_path}")
                continue

            self.parse_file(str(file_path), work_num)

        # Phase 2: Bulk insert all data
        self.bulk_insert()

        # Print statistics
        print("\n=== Import Statistics ===")
        print(f"  Works: {len(self.works)}")
        print(f"  Sections: {len(self.sections)}")
        print(f"  Verses: {len(self.verses)}")
        print(f"  Lines: {len(self.lines)}")
        print(f"  Words: {len(self.words)}")

    def close(self):
        """Close database connection"""
        self.cursor.close()
        self.conn.close()


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
    try:
        importer.run(str(source_path))
        print("\n[SUCCESS] Siddhar Padalgal import completed!")
    except Exception as e:
        print(f"\n[ERROR] Import failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        importer.close()


if __name__ == '__main__':
    main()
