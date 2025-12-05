#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Kambaramayanam Parser for Tamil Literature Database

This script parses Kambaramayanam text files and imports them into the database.

Structure:
- Work: Kambaramayanam (கம்பராமாயணம்)
- Level 1 (Kandam): 6 chapters marked with &
  - &1 பாலகாண்டம் (Bala Kandam)
  - &2 அயோத்தியா காண்டம் (Ayodhya Kandam)
  - &3 ஆரணிய காண்டம் (Aranya Kandam)
  - &4 கிட்கிந்தா காண்டம் (Kishkindha Kandam)
  - &5 சுந்தர காண்டம் (Sundara Kandam)
  - &61, &62, &63, &64 யுத்த காண்டம் (Yuddha Kandam - 4 parts)
- Level 2 (Padalam): Subsections marked with @
- Verses: Numbered with # (each verse is typically a 4-line stanza)
- Lines: Individual lines within verses
- Notes: Lines starting with ** or *** are ignored
"""

import os
import re
import sys
import psycopg2
from pathlib import Path

# Kandam files (ordered)
KANDAM_FILES = [
    ('1-கம்பராமாயணம்-பாலகாண்டம்.txt', 'பாலகாண்டம்', 'Bala Kandam', 1),
    ('2-கம்பராமாயணம்-அயோத்தியா காண்டம்.txt', 'அயோத்தியா காண்டம்', 'Ayodhya Kandam', 2),
    ('3-கம்பராமாயணம்-ஆரணிய காண்டம்.txt', 'ஆரணிய காண்டம்', 'Aranya Kandam', 3),
    ('4-கம்பராமாயணம்-கிட்கிந்தா காண்டம்.txt', 'கிட்கிந்தா காண்டம்', 'Kishkindha Kandam', 4),
    ('5-கம்பராமாயணம்-சுந்தர காண்டம்.txt', 'சுந்தர காண்டம்', 'Sundara Kandam', 5),
    ('6-கம்பராமாயணம்-யுத்த காண்டம்-1.txt', 'யுத்த காண்டம்-1', 'Yuddha Kandam-1', 61),
    ('6-கம்பராமாயணம்-யுத்த காண்டம்-2.txt', 'யுத்த காண்டம்-2', 'Yuddha Kandam-2', 62),
    ('6-கம்பராமாயணம்-யுத்த காண்டம்-3.txt', 'யுத்த காண்டம்-3', 'Yuddha Kandam-3', 63),
    ('6-கம்பராமாயணம்-யுத்த காண்டம்-4.txt', 'யுத்த காண்டம்-4', 'Yuddha Kandam-4', 64),
]


def clean_line(line):
    """
    Clean a line by:
    - Removing line numbers (multiples of 5) at the end
    - Removing anything after **
    - Stripping whitespace
    """
    # Remove anything after ** (including **)
    if '**' in line:
        return ''  # Ignore entire line with **

    # Remove trailing numbers (multiples of 5)
    line = re.sub(r'\s+\d+$', '', line)

    return line.strip()


def parse_kandam_file(file_path):
    """
    Parse a single Kandam file and extract structure.

    Returns:
    {
        'kandam_name_tamil': str,
        'kandam_name_english': str,
        'kandam_number': int,
        'padalams': [
            {
                'number': int,
                'name': str,
                'verses': [
                    {
                        'verse_number': int,
                        'lines': [str, str, ...]
                    },
                    ...
                ]
            },
            ...
        ]
    }
    """
    print(f"Parsing file: {file_path}")

    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    kandam_info = {
        'padalams': []
    }

    current_padalam = None
    current_verse_number = None
    current_verse_lines = []

    for line in lines:
        line = line.rstrip('\n')

        # Skip lines starting with ** or ***
        if line.strip().startswith('**'):
            continue

        # Skip empty lines
        if not line.strip():
            # Save current verse if we have lines
            if current_verse_lines and current_padalam is not None and current_verse_number is not None:
                current_padalam['verses'].append({
                    'verse_number': current_verse_number,
                    'lines': current_verse_lines.copy()
                })
                current_verse_lines = []
                current_verse_number = None
            continue

        # Check for Kandam marker (&)
        if line.startswith('&'):
            # Extract kandam info (format: &1 பாலகாண்டம் or &61 யுத்த காண்டம்-1)
            match = re.match(r'^&(\d+)\s+(.+)$', line)
            if match:
                kandam_num = int(match.group(1))
                kandam_text = match.group(2).strip()
                kandam_info['kandam_name_tamil'] = kandam_text
                kandam_info['kandam_number'] = kandam_num
            continue

        # Check for Padalam marker (@)
        if line.startswith('@'):
            # Save previous padalam's last verse
            if current_verse_lines and current_padalam is not None and current_verse_number is not None:
                current_padalam['verses'].append({
                    'verse_number': current_verse_number,
                    'lines': current_verse_lines.copy()
                })
                current_verse_lines = []
                current_verse_number = None

            # Parse padalam header (format: @0 கடவுள் வாழ்த்து or @1 ஆற்றுப்படலம்)
            match = re.match(r'^@(\d+)\s+(.+)$', line)
            if match:
                padalam_number = int(match.group(1))
                padalam_name = match.group(2).strip()

                current_padalam = {
                    'number': padalam_number,
                    'name': padalam_name,
                    'verses': []
                }
                kandam_info['padalams'].append(current_padalam)
            continue

        # Check for verse number marker (#)
        if line.startswith('#'):
            # Save previous verse if exists
            if current_verse_lines and current_padalam is not None and current_verse_number is not None:
                current_padalam['verses'].append({
                    'verse_number': current_verse_number,
                    'lines': current_verse_lines.copy()
                })
                current_verse_lines = []

            # Parse verse number (format: #1, #2, etc.)
            match = re.match(r'^#(\d+)$', line)
            if match:
                current_verse_number = int(match.group(1))
            continue

        # Regular content line
        cleaned = clean_line(line)
        if cleaned and current_padalam is not None and current_verse_number is not None:
            current_verse_lines.append(cleaned)

    # Save last verse
    if current_verse_lines and current_padalam is not None and current_verse_number is not None:
        current_padalam['verses'].append({
            'verse_number': current_verse_number,
            'lines': current_verse_lines.copy()
        })

    return kandam_info


def simple_word_split(line):
    """
    Simple word segmentation for Tamil text.
    Splits on whitespace and basic punctuation.
    """
    # Replace common punctuation with spaces
    line = re.sub(r'[,;!?()।]', ' ', line)

    # Split on whitespace and filter empty strings
    words = [w.strip() for w in line.split() if w.strip()]

    return words


def insert_kambaramayanam(conn, source_dir):
    """Insert Kambaramayanam into the database."""
    cur = conn.cursor()

    try:
        # 1. Insert or get work
        work_name_tamil = 'கம்பராமாயணம்'
        work_name_english = 'Kambaramayanam'

        # Get next available work_id
        cur.execute("SELECT COALESCE(MAX(work_id), 0) + 1 FROM works")
        work_id = cur.fetchone()[0]

        # Check if work already exists by name
        cur.execute("SELECT work_id FROM works WHERE work_name = %s", (work_name_english,))
        existing = cur.fetchone()

        if existing:
            work_id = existing[0]
            print(f"Work {work_name_tamil} already exists (ID: {work_id})")
        else:
            print(f"Creating work entry for {work_name_tamil}...")
            cur.execute("""
                INSERT INTO works (work_id, work_name, work_name_tamil, description, period, author)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                work_id,
                work_name_english,
                work_name_tamil,
                'Tamil version of the Ramayana epic',
                '12th century CE',
                'Kambar'
            ))
            conn.commit()

        print(f"Work ID: {work_id}")

        # Get next available section_id
        cur.execute("SELECT COALESCE(MAX(section_id), 0) + 1 FROM sections")
        next_section_id = cur.fetchone()[0]

        # Track Yuddha Kandam parent section (for parts 61-64)
        yuddha_kandam_parent_id = None

        # 2. Process each Kandam file
        for filename, kandam_tamil, kandam_english, kandam_num in KANDAM_FILES:
            file_path = source_dir / filename

            if not os.path.exists(file_path):
                print(f"Warning: File not found: {file_path}")
                continue

            print(f"\n{'='*60}")
            print(f"Processing Kandam {kandam_num}: {kandam_tamil}")
            print(f"{'='*60}")

            # Parse the file
            kandam_data = parse_kandam_file(file_path)

            # Handle Yuddha Kandam parts (61-64)
            if kandam_num in [61, 62, 63, 64]:
                # For first Yuddha Kandam file, create parent section
                if kandam_num == 61:
                    cur.execute("""
                        INSERT INTO sections (section_id, work_id, parent_section_id, level_type, level_type_tamil,
                                             section_number, section_name, section_name_tamil, sort_order)
                        VALUES (%s, %s, NULL, %s, %s, %s, %s, %s, %s)
                    """, (next_section_id, work_id, 'kandam', 'காண்டம்', 6,
                          'Yuddha Kandam', 'யுத்த காண்டம்', 6))
                    yuddha_kandam_parent_id = next_section_id
                    next_section_id += 1
                    print(f"Yuddha Kandam Parent Section ID: {yuddha_kandam_parent_id}")

                # Insert as sub-section under Yuddha Kandam
                cur.execute("""
                    INSERT INTO sections (section_id, work_id, parent_section_id, level_type, level_type_tamil,
                                         section_number, section_name, section_name_tamil, sort_order)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (next_section_id, work_id, yuddha_kandam_parent_id, 'kandam_part', 'காண்டம் பகுதி',
                      kandam_num, kandam_english, kandam_tamil, kandam_num))
                kandam_section_id = next_section_id
                next_section_id += 1
            else:
                # Regular Kandam (1-5)
                cur.execute("""
                    INSERT INTO sections (section_id, work_id, parent_section_id, level_type, level_type_tamil,
                                         section_number, section_name, section_name_tamil, sort_order)
                    VALUES (%s, %s, NULL, %s, %s, %s, %s, %s, %s)
                """, (next_section_id, work_id, 'kandam', 'காண்டம்', kandam_num,
                      kandam_english, kandam_tamil, kandam_num))
                kandam_section_id = next_section_id
                next_section_id += 1

            print(f"Kandam Section ID: {kandam_section_id}")

            # 3. Process each Padalam (subsection)
            for padalam_data in kandam_data['padalams']:
                padalam_name = padalam_data['name']
                padalam_number = padalam_data['number']

                # Insert Padalam section
                cur.execute("""
                    INSERT INTO sections (section_id, work_id, parent_section_id, level_type, level_type_tamil,
                                         section_number, section_name, section_name_tamil, sort_order)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (next_section_id, work_id, kandam_section_id, 'padalam', 'படலம்',
                      padalam_number, padalam_name, padalam_name, padalam_number))
                padalam_section_id = next_section_id
                next_section_id += 1

                verse_count = len(padalam_data['verses'])
                print(f"  Padalam #{padalam_number}: {padalam_name} ({verse_count} verses)")

                # 4. Process verses
                for verse_data in padalam_data['verses']:
                    verse_num = verse_data['verse_number']
                    verse_lines = verse_data['lines']

                    if not verse_lines:
                        continue

                    # Insert verse
                    cur.execute("""
                        INSERT INTO verses (section_id, verse_number, verse_text, sort_order)
                        VALUES (%s, %s, %s, %s)
                        RETURNING verse_id
                    """, (padalam_section_id, verse_num, '\n'.join(verse_lines), verse_num))
                    verse_id = cur.fetchone()[0]

                    # 5. Process lines
                    for line_num, line_text in enumerate(verse_lines, 1):
                        # Insert line
                        cur.execute("""
                            INSERT INTO lines (verse_id, line_number, line_text, sort_order)
                            VALUES (%s, %s, %s, %s)
                            RETURNING line_id
                        """, (verse_id, line_num, line_text, line_num))
                        line_id = cur.fetchone()[0]

                        # 6. Process words
                        words = simple_word_split(line_text)
                        for word_pos, word_text in enumerate(words, 1):
                            if word_text:
                                cur.execute("""
                                    INSERT INTO words (line_id, word_number, word_text, sort_order)
                                    VALUES (%s, %s, %s, %s)
                                """, (line_id, word_pos, word_text, word_pos))

                # Commit after each Padalam
                conn.commit()
                print(f"    ✓ Committed {verse_count} verses")

        print(f"\n{'='*60}")
        print("Kambaramayanam import completed successfully!")
        print(f"{'='*60}")

    except Exception as e:
        conn.rollback()
        print(f"Error during import: {e}")
        raise
    finally:
        cur.close()


def main():
    """Main execution function."""
    # Fix Windows console encoding for Tamil characters
    if sys.platform == 'win32':
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

    # Database connection - check for environment variable or use default
    db_connection = os.getenv('DATABASE_URL',
                             "postgresql://postgres:postgres@localhost/tamil_literature")

    # Source directory path
    script_dir = Path(__file__).parent
    project_dir = script_dir.parent
    source_dir = project_dir / "Tamil-Source-TamilConcordence" / "5 _கம்பராமாயணம்"

    # Allow database URL as command line argument
    if len(sys.argv) > 1:
        db_connection = sys.argv[1]

    print("=" * 60)
    print("Kambaramayanam Parser")
    print("=" * 60)
    print(f"Database: {db_connection.split('@')[-1] if '@' in db_connection else db_connection}")
    print(f"Source: {source_dir}")
    print("=" * 60)

    # Connect to database
    print(f"Connecting to database...")
    conn = psycopg2.connect(db_connection)

    try:
        insert_kambaramayanam(conn, source_dir)
    finally:
        conn.close()
        print("\n✓ Database connection closed")


if __name__ == '__main__':
    main()
