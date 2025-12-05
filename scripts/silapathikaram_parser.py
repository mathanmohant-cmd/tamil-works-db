#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Silapathikaram Parser for Tamil Literature Database

This script parses Silapathikaram text files and imports them into the database.

Structure:
- Work: Silapathikaram (சிலப்பதிகாரம்)
- Level 1 (Kandam): 3 chapters
  - புகார்க் காண்டம் (Pukar Kandam)
  - மதுரைக் காண்டம் (Madurai Kandam)
  - வஞ்சிக் காண்டம் (Vanci Kandam)
- Level 2 (Kaathai/Paayiram/Vazhuthu): Subsections marked with #
- Verses: Groups of lines (until blank line or next section marker)
- Lines: Individual lines with numbers (multiples of 5) removed
"""

import os
import re
import psycopg2
from psycopg2.extras import execute_batch
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://localhost/tamil_literature')

# File paths
SOURCE_DIR = r'Tamil-Source-TamilConcordence\4_ஐம்பெருங்காப்பியங்கள்\சிலப்பதிகாரம்'

# Kandam files (ordered)
KANDAM_FILES = [
    ('சிலப்பதிகாரம் – புகார்க் காண்டம்.txt', 'புகார்க் காண்டம்', 'Pukar Kandam', 1),
    ('சிலப்பதிகாரம் – மதுரைக் காண்டம்.txt', 'மதுரைக் காண்டம்', 'Madurai Kandam', 2),
    ('சிலப்பதிகாரம் – வஞ்சிக் காண்டம்.txt', 'வஞ்சிக் காண்டம்', 'Vanci Kandam', 3),
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
        line = line.split('**')[0]

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
        'sections': [
            {
                'number': int,
                'name': str,
                'verses': [
                    {
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
        'sections': []
    }

    current_section = None
    current_verse_lines = []

    for line in lines:
        line = line.rstrip('\n')

        # Skip empty lines (they mark verse boundaries)
        if not line.strip():
            # Save current verse if we have lines
            if current_verse_lines and current_section is not None:
                current_section['verses'].append({
                    'lines': current_verse_lines.copy()
                })
                current_verse_lines = []
            continue

        # Check for Kandam marker ($)
        if line.startswith('$'):
            # Extract kandam info (format: $புகார்க் காண்டம் or $2 மதுரைக் காண்டம்)
            kandam_text = line[1:].strip()
            # Remove leading number if present
            kandam_text = re.sub(r'^\d+\s+', '', kandam_text)
            kandam_info['kandam_name_tamil'] = kandam_text
            continue

        # Check for section marker (#)
        if line.startswith('#'):
            # Save previous section's last verse
            if current_verse_lines and current_section is not None:
                current_section['verses'].append({
                    'lines': current_verse_lines.copy()
                })
                current_verse_lines = []

            # Parse section header (format: #0 பதிகம் or #11 காடுகாண் காதை)
            match = re.match(r'^#(\d+)\s+(.+)$', line)
            if match:
                section_number = int(match.group(1))
                section_name = match.group(2).strip()

                current_section = {
                    'number': section_number,
                    'name': section_name,
                    'verses': []
                }
                kandam_info['sections'].append(current_section)
            continue

        # Regular content line
        cleaned = clean_line(line)
        if cleaned and current_section is not None:
            current_verse_lines.append(cleaned)

    # Save last verse
    if current_verse_lines and current_section is not None:
        current_section['verses'].append({
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


def insert_silapathikaram(conn):
    """Insert Silapathikaram into the database."""
    cur = conn.cursor()

    try:
        # 1. Insert or get work
        work_name_tamil = 'சிலப்பதிகாரம்'
        work_name_english = 'Silapathikaram'

        cur.execute("""
            INSERT INTO works (work_name, work_name_tamil, description, period, author)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (work_name) DO UPDATE SET work_name = EXCLUDED.work_name
            RETURNING work_id
        """, (
            work_name_english,
            work_name_tamil,
            'One of the Five Great Epics of Tamil Literature',
            '5th-6th century CE',
            'Ilango Adigal'
        ))
        work_id = cur.fetchone()[0]
        print(f"Work ID: {work_id}")

        # 2. Process each Kandam file
        for filename, kandam_tamil, kandam_english, kandam_num in KANDAM_FILES:
            file_path = os.path.join(SOURCE_DIR, filename)

            if not os.path.exists(file_path):
                print(f"Warning: File not found: {file_path}")
                continue

            print(f"\n{'='*60}")
            print(f"Processing Kandam {kandam_num}: {kandam_tamil}")
            print(f"{'='*60}")

            # Parse the file
            kandam_data = parse_kandam_file(file_path)

            # Insert Kandam section
            cur.execute("""
                INSERT INTO sections (work_id, section_name, section_name_tamil,
                                     section_number, parent_section_id, sort_order)
                VALUES (%s, %s, %s, %s, NULL, %s)
                RETURNING section_id
            """, (work_id, kandam_english, kandam_tamil, kandam_num, kandam_num))
            kandam_section_id = cur.fetchone()[0]
            print(f"Kandam Section ID: {kandam_section_id}")

            # 3. Process each Kaathai (subsection)
            for section_data in kandam_data['sections']:
                section_name = section_data['name']
                section_number = section_data['number']

                # Insert Kaathai section
                cur.execute("""
                    INSERT INTO sections (work_id, section_name, section_name_tamil,
                                         section_number, parent_section_id, sort_order)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    RETURNING section_id
                """, (work_id, section_name, section_name, section_number,
                      kandam_section_id, section_number))
                kaathai_section_id = cur.fetchone()[0]

                verse_count = len(section_data['verses'])
                print(f"  Kaathai #{section_number}: {section_name} ({verse_count} verses)")

                # 4. Process verses
                for verse_idx, verse_data in enumerate(section_data['verses'], 1):
                    verse_lines = verse_data['lines']

                    if not verse_lines:
                        continue

                    # Insert verse
                    cur.execute("""
                        INSERT INTO verses (section_id, verse_number, verse_text, sort_order)
                        VALUES (%s, %s, %s, %s)
                        RETURNING verse_id
                    """, (kaathai_section_id, verse_idx, '\n'.join(verse_lines), verse_idx))
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

                # Commit after each Kaathai
                conn.commit()
                print(f"    ✓ Committed {verse_count} verses")

        print(f"\n{'='*60}")
        print("Silapathikaram import completed successfully!")
        print(f"{'='*60}")

    except Exception as e:
        conn.rollback()
        print(f"Error during import: {e}")
        raise
    finally:
        cur.close()


def main():
    """Main execution function."""
    print("Silapathikaram Parser")
    print("="*60)

    # Connect to database
    print(f"Connecting to database...")
    conn = psycopg2.connect(DATABASE_URL)

    try:
        insert_silapathikaram(conn)
    finally:
        conn.close()
        print("Database connection closed.")


if __name__ == '__main__':
    main()
