#!/usr/bin/env python3
"""
Sangam Literature Parser - Import all 18 Sangam works into PostgreSQL database

Handles two formats:
1. Thogai (தொகை) - Poetry collections with poem numbers
   Format: # N theme/title, poem lines, * author

2. Padal (பாட்டு) - Continuous poems with just line numbers
   Format: Continuous lines (no poem divisions)

Follows Professor P. Pandiaraja's word segmentation principles
"""

import re
import psycopg2
from pathlib import Path
from typing import Dict, List, Optional
import sys
import os

class SangamParser:
    # Map filenames to work information
    SANGAM_WORKS = {
        'குறுந்தொகை.txt': {
            'work_id': 4,
            'work_name': 'Kuruntokai',
            'work_name_tamil': 'குறுந்தொகை',
            'type': 'thogai',  # Poetry collection
            'description': 'Short poems on love and war'
        },
        'நற்றிணை.txt': {
            'work_id': 5,
            'work_name': 'Natrinai',
            'work_name_tamil': 'நற்றிணை',
            'type': 'thogai',
            'description': 'Collection of 400 poems'
        },
        'ஐங்குறுநூறு.txt': {
            'work_id': 6,
            'work_name': 'Ainkurunuru',
            'work_name_tamil': 'ஐங்குறுநூறு',
            'type': 'thogai',
            'description': 'Five hundred short poems'
        },
        'அகநானூறு.txt': {
            'work_id': 7,
            'work_name': 'Akananuru',
            'work_name_tamil': 'அகநானூறு',
            'type': 'thogai',
            'description': 'Four hundred poems on love'
        },
        'புறநானூறு.txt': {
            'work_id': 8,
            'work_name': 'Purananuru',
            'work_name_tamil': 'புறநானூறு',
            'type': 'thogai',
            'description': 'Four hundred poems on war and ethics'
        },
        'கலித்தொகை.txt': {
            'work_id': 9,
            'work_name': 'Kalittokai',
            'work_name_tamil': 'கலித்தொகை',
            'type': 'thogai',
            'description': 'Collection of Kali meter poems'
        },
        'பதிற்றுப்பத்து.txt': {
            'work_id': 10,
            'work_name': 'Patirruppattu',
            'work_name_tamil': 'பதிற்றுப்பத்து',
            'type': 'thogai',
            'description': 'Ten tens of poems'
        },
        'பரிபாடல்.txt': {
            'work_id': 11,
            'work_name': 'Paripadal',
            'work_name_tamil': 'பரிபாடல்',
            'type': 'thogai',
            'description': 'Songs in Paripadal meter'
        },
        'திருமுருகாற்றுப்படை.txt': {
            'work_id': 12,
            'work_name': 'Tirumurukāṟṟuppaṭai',
            'work_name_tamil': 'திருமுருகாற்றுப்படை',
            'type': 'padal',
            'description': 'Guide to Lord Murugan'
        },
        'பொருநராற்றுப்படை.txt': {
            'work_id': 13,
            'work_name': 'Porunarāṟṟuppaṭai',
            'work_name_tamil': 'பொருநராற்றுப்படை',
            'type': 'padal',
            'description': 'Guide to patron'
        },
        'சிறுபாணாற்றுப்படை.txt': {
            'work_id': 14,
            'work_name': 'Sirupāṇāṟṟuppaṭai',
            'work_name_tamil': 'சிறுபாணாற்றுப்படை',
            'type': 'padal',
            'description': 'Guide to small drum player'
        },
        'பெரும்பாணாற்றுப்படை.txt': {
            'work_id': 15,
            'work_name': 'Perumpāṇāṟṟuppaṭai',
            'work_name_tamil': 'பெரும்பாணாற்றுப்படை',
            'type': 'padal',
            'description': 'Guide to great drum player'
        },
        'முல்லைப்பாட்டு.txt': {
            'work_id': 16,
            'work_name': 'Mullaippāṭṭu',
            'work_name_tamil': 'முல்லைப்பாட்டு',
            'type': 'padal',
            'description': 'Song of Mullai landscape'
        },
        'மதுரைக்காஞ்சி.txt': {
            'work_id': 17,
            'work_name': 'Maturaikkāñci',
            'work_name_tamil': 'மதுரைக்காஞ்சி',
            'type': 'padal',
            'description': 'Description of Madurai city'
        },
        'நெடுநல்வாடை.txt': {
            'work_id': 18,
            'work_name': 'Neṭunalvāṭai',
            'work_name_tamil': 'நெடுநல்வாடை',
            'type': 'padal',
            'description': 'The long north wind'
        },
        'பட்டினப்பாலை.txt': {
            'work_id': 19,
            'work_name': 'Paṭṭiṉappālai',
            'work_name_tamil': 'பட்டினப்பாலை',
            'type': 'padal',
            'description': 'Description of seaport'
        },
        'மலைபடுகடாம்.txt': {
            'work_id': 20,
            'work_name': 'Malaippaṭukaṭām',
            'work_name_tamil': 'மலைபடுகடாம்',
            'type': 'padal',
            'description': 'Mountain-traversing journey'
        },
        'குறிஞ்சிப்பாட்டு.txt': {
            'work_id': 21,
            'work_name': 'Kuṟiñcippāṭṭu',
            'work_name_tamil': 'குறிஞ்சிப்பாட்டு',
            'type': 'padal',
            'description': 'Song of Kurinji landscape'
        }
    }

    def __init__(self, db_connection_string: str):
        """Initialize parser with database connection"""
        self.conn = psycopg2.connect(db_connection_string)
        self.cursor = self.conn.cursor()

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
            # Clean punctuation if needed (but keep internal punctuation)
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

    def get_or_create_work(self, work_info: Dict) -> int:
        """Get work_id or create work if it doesn't exist"""

        # Check if work exists
        self.cursor.execute("""
            SELECT work_id FROM works
            WHERE work_id = %s
        """, (work_info['work_id'],))

        result = self.cursor.fetchone()
        if result:
            return result[0]

        # Create work
        self.cursor.execute("""
            INSERT INTO works
            (work_id, work_name, work_name_tamil, period, description)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING work_id
        """, (work_info['work_id'],
              work_info['work_name'],
              work_info['work_name_tamil'],
              'Sangam Period (300 BCE - 300 CE)',
              work_info['description']))

        return self.cursor.fetchone()[0]

    def parse_thogai_file(self, file_path: str, work_info: Dict) -> Dict:
        """
        Parse Thogai (collection) format files
        Format:
        # N theme/title
        poem lines
        * author
        """
        print(f"\nParsing {work_info['work_name_tamil']} (Thogai - Poetry Collection)...")

        work_id = self.get_or_create_work(work_info)

        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        current_poem_num = None
        current_poem_theme = None
        current_poem_lines = []

        verse_count = 0
        line_count = 0
        word_count = 0

        for line in lines:
            line = line.strip()

            if not line:
                continue

            # Check for poem header: # N theme
            poem_match = re.match(r'^#\s*(\d+)\s*(.*)$', line)
            if poem_match:
                # Save previous poem if exists
                if current_poem_num is not None and current_poem_lines:
                    self._save_poem(work_id, current_poem_num,
                                  current_poem_theme, current_poem_lines)
                    verse_count += 1
                    line_count += len(current_poem_lines)
                    word_count += sum(len(self.parse_words(l)) for l in current_poem_lines)

                # Start new poem
                current_poem_num = int(poem_match.group(1))
                current_poem_theme = poem_match.group(2).strip()
                current_poem_lines = []

                if current_poem_num % 50 == 0:
                    print(f"  Processing poem {current_poem_num}...")

                continue

            # Check for author line: * author_name
            if line.startswith('*'):
                # Skip author line (metadata for later)
                continue

            # Regular poem line
            if current_poem_num is not None:
                # Remove line numbers if present (e.g., "line text……5")
                line = re.sub(r'…+\d+$', '', line).strip()
                if line:
                    current_poem_lines.append(line)

        # Save last poem
        if current_poem_num is not None and current_poem_lines:
            self._save_poem(work_id, current_poem_num,
                          current_poem_theme, current_poem_lines)
            verse_count += 1
            line_count += len(current_poem_lines)
            word_count += sum(len(self.parse_words(l)) for l in current_poem_lines)

        self.conn.commit()

        return {
            'verses': verse_count,
            'lines': line_count,
            'words': word_count
        }

    def parse_padal_file(self, file_path: str, work_info: Dict) -> Dict:
        """
        Parse Padal (continuous poem) format files
        Format: Continuous lines (treat entire work as one poem)
        """
        print(f"\nParsing {work_info['work_name_tamil']} (Padal - Continuous Poem)...")

        work_id = self.get_or_create_work(work_info)

        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        poem_lines = []

        for line in lines:
            line = line.strip()

            if not line:
                continue

            # Skip header/title lines starting with #
            if line.startswith('#'):
                continue

            # Remove line numbers if present
            line = re.sub(r'…+\d+$', '', line).strip()

            if line:
                poem_lines.append(line)

        # Save entire work as one poem
        if poem_lines:
            self._save_poem(work_id, 1, work_info['work_name_tamil'], poem_lines)

        self.conn.commit()

        word_count = sum(len(self.parse_words(l)) for l in poem_lines)

        return {
            'verses': 1,
            'lines': len(poem_lines),
            'words': word_count
        }

    def _save_poem(self, work_id: int, poem_num: int, theme: str,
                   lines: List[str]) -> None:
        """Save a single poem with its lines and words to database"""

        # Get or create root section for this work first
        self.cursor.execute("""
            SELECT section_id FROM sections
            WHERE work_id = %s AND parent_section_id IS NULL
            LIMIT 1
        """, (work_id,))

        result = self.cursor.fetchone()
        if result:
            section_id = result[0]
        else:
            # Create root section
            # Get next section_id
            self.cursor.execute("SELECT COALESCE(MAX(section_id), 0) + 1 FROM sections")
            section_id = self.cursor.fetchone()[0]

            self.cursor.execute("""
                INSERT INTO sections
                (section_id, work_id, parent_section_id, level_type, section_number, section_name, sort_order)
                VALUES (%s, %s, NULL, 'Poems', 1, 'Main Collection', 1)
            """, (section_id, work_id))

        # Create verse (poem) with explicit verse_id
        self.cursor.execute("SELECT COALESCE(MAX(verse_id), 0) + 1 FROM verses")
        verse_id = self.cursor.fetchone()[0]

        self.cursor.execute("""
            INSERT INTO verses (verse_id, work_id, section_id, verse_number, total_lines, sort_order)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (verse_id, work_id, section_id, poem_num, len(lines), poem_num))

        # Insert lines and words
        for line_num, line_text in enumerate(lines, start=1):
            # Create line with explicit line_id
            self.cursor.execute("SELECT COALESCE(MAX(line_id), 0) + 1 FROM lines")
            line_id = self.cursor.fetchone()[0]

            self.cursor.execute("""
                INSERT INTO lines (line_id, verse_id, line_number, line_text)
                VALUES (%s, %s, %s, %s)
            """, (line_id, verse_id, line_num, line_text))

            # Parse and insert words
            words = self.parse_words(line_text)
            for word_data in words:
                # Get next word_id
                self.cursor.execute("SELECT COALESCE(MAX(word_id), 0) + 1 FROM words")
                word_id = self.cursor.fetchone()[0]

                self.cursor.execute("""
                    INSERT INTO words
                    (word_id, line_id, word_position, word_text, sandhi_split)
                    VALUES (%s, %s, %s, %s, %s)
                """, (word_id, line_id, word_data['word_position'],
                      word_data['word_text'],
                      word_data.get('sandhi_split')))

    def parse_directory(self, directory_path: str) -> None:
        """Parse all Sangam works in directory"""

        dir_path = Path(directory_path)

        print("=" * 70)
        print("Sangam Literature Parser - Import all 18 works")
        print("=" * 70)

        total_stats = {'verses': 0, 'lines': 0, 'words': 0}
        works_processed = 0

        for filename, work_info in self.SANGAM_WORKS.items():
            file_path = dir_path / filename

            if not file_path.exists():
                print(f"\n⚠ File not found: {filename}")
                continue

            try:
                if work_info['type'] == 'thogai':
                    stats = self.parse_thogai_file(str(file_path), work_info)
                else:  # padal
                    stats = self.parse_padal_file(str(file_path), work_info)

                print(f"  ✓ {work_info['work_name_tamil']}: "
                      f"{stats['verses']} poems, "
                      f"{stats['lines']} lines, "
                      f"{stats['words']} words")

                total_stats['verses'] += stats['verses']
                total_stats['lines'] += stats['lines']
                total_stats['words'] += stats['words']
                works_processed += 1

            except Exception as e:
                print(f"  ✗ Error processing {filename}: {e}")
                import traceback
                traceback.print_exc()

        print("\n" + "=" * 70)
        print(f"✓ Import Complete!")
        print(f"  Works processed: {works_processed}/18")
        print(f"  Total poems: {total_stats['verses']}")
        print(f"  Total lines: {total_stats['lines']}")
        print(f"  Total words: {total_stats['words']}")
        print("=" * 70)

    def close(self):
        """Close database connection"""
        self.cursor.close()
        self.conn.close()


def main():
    """Main entry point"""

    # Fix Windows console encoding for Tamil characters
    if sys.platform == 'win32':
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

    # Database connection - check for environment variable or use default
    db_connection = os.getenv('DATABASE_URL',
                             "postgresql://postgres:postgres@localhost/tamil_literature_db")

    # Directory path
    script_dir = Path(__file__).parent
    project_dir = script_dir.parent
    sangam_dir = project_dir / "Tamil-Source-TamilConcordence" / "2_Sangam_Litrature"

    # Allow database URL as command line argument
    if len(sys.argv) > 1:
        db_connection = sys.argv[1]

    # Parse and import
    parser = SangamParser(db_connection)

    try:
        parser.parse_directory(sangam_dir)
    finally:
        parser.close()

    print("\n✓ Database connection closed")


if __name__ == "__main__":
    main()
