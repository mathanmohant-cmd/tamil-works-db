#!/usr/bin/env python3
"""
Thirukkural Parser - Import all 1,330 Thirukkural kurals into PostgreSQL database

Uses thirukkural_structure.json for Paal/Iyal/Adhikaram mapping
Follows Professor P. Pandiaraja's word segmentation principles
"""

import json
import re
import psycopg2
from pathlib import Path
from typing import Dict, List, Tuple, Optional

class ThirukkuralParser:
    def __init__(self, db_connection_string: str):
        """Initialize parser with database connection"""
        self.conn = psycopg2.connect(db_connection_string)
        self.cursor = self.conn.cursor()

        # Load structure mapping
        structure_file = Path(__file__).parent / "thirukkural_structure.json"
        with open(structure_file, 'r', encoding='utf-8') as f:
            self.structure = json.load(f)

        # Build kural number to hierarchy mapping
        self.kural_to_hierarchy = self._build_kural_mapping()

        # Work ID for Thirukkural
        self.work_id = 3

    def _build_kural_mapping(self) -> Dict[int, Dict]:
        """Build mapping from kural number to Paal/Iyal/Adhikaram"""
        mapping = {}

        for paal in self.structure['structure']['paals']:
            for iyal in paal['iyals']:
                for adhikaram in iyal['adhikarams']:
                    start_kural, end_kural = adhikaram['kurals']
                    for kural_num in range(start_kural, end_kural + 1):
                        mapping[kural_num] = {
                            'paal': paal,
                            'iyal': iyal,
                            'adhikaram': adhikaram
                        }

        return mapping

    def get_or_create_section(self, parent_id: Optional[int], level_type: str,
                              section_number: int, section_name: str,
                              section_name_tamil: str) -> int:
        """Get existing section or create new one, return section_id"""

        # Check if section exists
        self.cursor.execute("""
            SELECT section_id FROM sections
            WHERE work_id = %s
              AND parent_section_id IS NOT DISTINCT FROM %s
              AND level_type = %s
              AND section_number = %s
        """, (self.work_id, parent_id, level_type, section_number))

        result = self.cursor.fetchone()
        if result:
            return result[0]

        # Create new section
        self.cursor.execute("""
            INSERT INTO sections
            (work_id, parent_section_id, level_type, level_type_tamil,
             section_number, section_name, section_name_tamil)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING section_id
        """, (self.work_id, parent_id, level_type, level_type + '_tamil',
              section_number, section_name, section_name_tamil))

        section_id = self.cursor.fetchone()[0]
        return section_id

    def parse_words(self, line_text: str) -> List[Dict]:
        """
        Parse line into words following Professor Pandiaraja's principles
        - Space = word boundary
        - _ = compound word parts (store in sandhi_split)
        - - = particles (keep as single word)
        """
        words = []
        position = 1

        # Split by space
        tokens = line_text.strip().split()

        for token in tokens:
            # Clean punctuation if needed
            token = token.strip('.,;!?')

            if not token:
                continue

            word_data = {
                'word_text': token,
                'word_position': position
            }

            # Handle compound words with underscore
            if '_' in token:
                word_data['sandhi_split'] = token.replace('_', ' + ')

            words.append(word_data)
            position += 1

        return words

    def parse_file(self, text_file_path: str) -> None:
        """Parse Thirukkural text file and import to database"""

        print(f"Parsing {text_file_path}...")

        with open(text_file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        current_adhikaram = None
        current_adhikaram_section_id = None
        current_kural_num = None
        current_kural_lines = []

        verse_count = 0
        line_count = 0
        word_count = 0

        for line in lines:
            line = line.strip()

            if not line:
                continue

            # Check for adhikaram header: # N adhikaram_name
            adhikaram_match = re.match(r'^#\s*(\d+)\s+(.+)$', line)
            if adhikaram_match:
                # Save previous kural if exists
                if current_kural_num and current_kural_lines:
                    self._save_kural(current_kural_num, current_kural_lines,
                                   current_adhikaram_section_id)
                    verse_count += 1
                    line_count += len(current_kural_lines)

                    # Count words
                    for kural_line in current_kural_lines:
                        words = self.parse_words(kural_line)
                        word_count += len(words)

                # Reset for new adhikaram
                current_kural_lines = []
                current_kural_num = None

                adhikaram_num = int(adhikaram_match.group(1))
                adhikaram_name = adhikaram_match.group(2)

                # Get hierarchy from mapping
                # Adhikaram numbers in text are 1-133, use first kural of each adhikaram
                first_kural_of_adhikaram = (adhikaram_num - 1) * 10 + 1

                if first_kural_of_adhikaram in self.kural_to_hierarchy:
                    hierarchy = self.kural_to_hierarchy[first_kural_of_adhikaram]

                    # Create Paal section
                    paal_id = self.get_or_create_section(
                        parent_id=None,
                        level_type='Paal',
                        section_number=hierarchy['paal']['paal_id'],
                        section_name=hierarchy['paal']['paal_name'],
                        section_name_tamil=hierarchy['paal']['paal_name_tamil']
                    )

                    # Create Iyal section
                    iyal_id = self.get_or_create_section(
                        parent_id=paal_id,
                        level_type='Iyal',
                        section_number=hierarchy['iyal']['iyal_id'],
                        section_name=hierarchy['iyal']['iyal_name'],
                        section_name_tamil=hierarchy['iyal']['iyal_name_tamil']
                    )

                    # Create Adhikaram section
                    current_adhikaram_section_id = self.get_or_create_section(
                        parent_id=iyal_id,
                        level_type='Adhikaram',
                        section_number=adhikaram_num,
                        section_name=hierarchy['adhikaram']['name'],
                        section_name_tamil=hierarchy['adhikaram']['tamil']
                    )

                    current_adhikaram = adhikaram_num
                    print(f"  Processing Adhikaram {adhikaram_num}: {hierarchy['adhikaram']['tamil']}")

                continue

            # Check for kural line: N.line_text or just line_text
            kural_line_match = re.match(r'^(\d+)\.(.+)$', line)
            if kural_line_match:
                # Save previous kural if exists
                if current_kural_num and current_kural_lines:
                    self._save_kural(current_kural_num, current_kural_lines,
                                   current_adhikaram_section_id)
                    verse_count += 1
                    line_count += len(current_kural_lines)

                    # Count words
                    for kural_line in current_kural_lines:
                        words = self.parse_words(kural_line)
                        word_count += len(words)

                # Start new kural
                current_kural_num = int(kural_line_match.group(1))
                line_text = kural_line_match.group(2).strip()
                current_kural_lines = [line_text]
            else:
                # Continuation line (second line of kural)
                if current_kural_num:
                    current_kural_lines.append(line)

        # Save last kural
        if current_kural_num and current_kural_lines:
            self._save_kural(current_kural_num, current_kural_lines,
                           current_adhikaram_section_id)
            verse_count += 1
            line_count += len(current_kural_lines)

            # Count words
            for kural_line in current_kural_lines:
                words = self.parse_words(kural_line)
                word_count += len(words)

        # Commit transaction
        self.conn.commit()

        print(f"\n✓ Import complete!")
        print(f"  - Verses (Kurals): {verse_count}")
        print(f"  - Lines: {line_count}")
        print(f"  - Words: {word_count}")

    def _save_kural(self, kural_num: int, lines: List[str], adhikaram_section_id: int) -> None:
        """Save a single kural with its lines and words to database"""

        # Create verse
        self.cursor.execute("""
            INSERT INTO verses (section_id, verse_number)
            VALUES (%s, %s)
            RETURNING verse_id
        """, (adhikaram_section_id, kural_num))

        verse_id = self.cursor.fetchone()[0]

        # Insert lines and words
        for line_num, line_text in enumerate(lines, start=1):
            # Create line
            self.cursor.execute("""
                INSERT INTO lines (verse_id, line_number, line_text)
                VALUES (%s, %s, %s)
                RETURNING line_id
            """, (verse_id, line_num, line_text))

            line_id = self.cursor.fetchone()[0]

            # Parse and insert words
            words = self.parse_words(line_text)
            for word_data in words:
                self.cursor.execute("""
                    INSERT INTO words
                    (line_id, word_position, word_text, sandhi_split)
                    VALUES (%s, %s, %s, %s)
                """, (line_id, word_data['word_position'],
                      word_data['word_text'],
                      word_data.get('sandhi_split')))

    def close(self):
        """Close database connection"""
        self.cursor.close()
        self.conn.close()


def main():
    """Main entry point"""
    import sys
    import os

    # Database connection - check for environment variable or use default
    db_connection = os.getenv('DATABASE_URL', "postgresql://postgres:password@localhost/tamil_literature")

    # Text file path
    text_file = r"C:\Mathan\Tamil\Tamil-Source-TamilConcordence\3_சங்க_இலக்கியம்_பதினெண்கீழ்க்கணக்கு\திருக்குறள்.txt"

    # Allow database URL as command line argument
    if len(sys.argv) > 1:
        db_connection = sys.argv[1]

    print("=" * 60)
    print("Thirukkural Parser - Import all 1,330 Kurals")
    print("=" * 60)
    print(f"Database: {db_connection.split('@')[-1] if '@' in db_connection else db_connection}")
    print(f"Text file: {text_file}")
    print("=" * 60)

    # Parse and import
    parser = ThirukkuralParser(db_connection)

    try:
        parser.parse_file(text_file)
    finally:
        parser.close()

    print("\n✓ Database connection closed")


if __name__ == "__main__":
    main()
