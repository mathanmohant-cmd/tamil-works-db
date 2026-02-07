#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
QA Verification Script for Thirumurai File 11
Compares source file verse counts with database imports
"""

import re
import psycopg2
from pathlib import Path
import csv
from datetime import datetime
from collections import defaultdict

class File11QAVerifier:
    def __init__(self, source_file_path, db_connection_string):
        self.source_file = Path(source_file_path)
        self.db_conn_string = db_connection_string

        # Results storage
        self.source_data = {}  # author_num -> {name, verses[], sections[]}
        self.db_data = {}      # work_id -> {name, verses[], sections[]}
        self.issues = []       # List of issue dictionaries

    def parse_source_file(self):
        """Parse source .txt file and extract structure"""
        with open(self.source_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        current_author_num = None
        current_section_num = None
        verse_count = 0

        for line_num, line in enumerate(lines, 1):
            line = line.strip()

            # Author marker: &N Author Name ^ Work Name
            author_match = re.match(r'^&(\d+)\s+(.+)', line)
            if author_match:
                current_author_num = int(author_match.group(1))
                author_info = author_match.group(2)
                self.source_data[current_author_num] = {
                    'raw_name': author_info,
                    'verses': [],
                    'sections': [],
                    'line_start': line_num
                }
                verse_count = 0
                continue

            # Section marker: @N Section Name OR @Section Name
            section_match = re.match(r'^@(?:(\d+)\s+)?(.+)', line)
            if section_match and current_author_num:
                section_num = section_match.group(1)  # May be None
                section_name = section_match.group(2)
                self.source_data[current_author_num]['sections'].append({
                    'number': section_num,
                    'name': section_name,
                    'line': line_num
                })
                current_section_num = section_num
                continue

            # Verse marker: #N
            verse_match = re.match(r'^#(\d+)$', line)
            if verse_match and current_author_num:
                verse_num = int(verse_match.group(1))
                verse_count += 1
                self.source_data[current_author_num]['verses'].append({
                    'verse_num': verse_num,
                    'line': line_num,
                    'section': current_section_num
                })

        print(f"[SOURCE] Parsed {len(self.source_data)} authors, {sum(len(a['verses']) for a in self.source_data.values())} verses")

    def query_database(self):
        """Query database for File 11 works and verses"""
        conn = psycopg2.connect(self.db_conn_string)
        cursor = conn.cursor()

        # Find all File 11 works (collection ID 32118)
        cursor.execute("""
            SELECT w.work_id, w.work_name, w.work_name_tamil, w.author, w.author_tamil
            FROM works w
            JOIN work_collections wc ON w.work_id = wc.work_id
            WHERE wc.collection_id = 32118
            ORDER BY w.work_id
        """)

        works = cursor.fetchall()
        print(f"[DATABASE] Found {len(works)} works from File 11")

        for work_id, work_name, work_name_tamil, author, author_tamil in works:
            # Count verses for this work
            cursor.execute("""
                SELECT verse_id, verse_number, section_id
                FROM verses
                WHERE work_id = %s
                ORDER BY verse_number
            """, (work_id,))

            verses = cursor.fetchall()

            # Count sections for this work
            cursor.execute("""
                SELECT section_id, section_name, section_name_tamil
                FROM sections
                WHERE work_id = %s
                ORDER BY section_id
            """, (work_id,))

            sections = cursor.fetchall()

            self.db_data[work_id] = {
                'work_name': work_name,
                'work_name_tamil': work_name_tamil,
                'author': author,
                'author_tamil': author_tamil,
                'verses': [{'verse_id': v[0], 'verse_num': v[1], 'section_id': v[2]} for v in verses],
                'sections': [{'section_id': s[0], 'name': s[1], 'name_tamil': s[2]} for s in sections]
            }

        cursor.close()
        conn.close()

    def compare_and_identify_issues(self):
        """Compare source vs database and identify missing data"""
        total_source_verses = sum(len(a['verses']) for a in self.source_data.values())
        total_db_verses = sum(len(w['verses']) for w in self.db_data.values())

        print(f"\n[COMPARISON]")
        print(f"  Source verses: {total_source_verses}")
        print(f"  Database verses: {total_db_verses}")
        print(f"  Missing: {total_source_verses - total_db_verses}")

        # Check each author from source
        for author_num, author_data in sorted(self.source_data.items()):
            expected_count = len(author_data['verses'])

            # Try to find matching work in database (fuzzy match by author name)
            matched_work = None
            for work_id, work_data in self.db_data.items():
                # Simple matching: check if author appears in work name
                if author_data['raw_name'].split('^')[0].strip() in work_data.get('work_name_tamil', ''):
                    matched_work = work_id
                    break

            if matched_work:
                actual_count = len(self.db_data[matched_work]['verses'])
                status = 'OK' if actual_count == expected_count else 'PARTIAL'
            else:
                actual_count = 0
                status = 'MISSING'

            self.issues.append({
                'author_number': author_num,
                'author_name': author_data['raw_name'],
                'work_id_db': matched_work,
                'expected_verses': expected_count,
                'actual_verses': actual_count,
                'missing_verses': expected_count - actual_count,
                'status': status
            })

    def generate_console_report(self):
        """Print summary report to console"""
        print("\n" + "="*70)
        print("QA Verification Report: Thirumurai File 11")
        print("="*70)

        total_source = sum(len(a['verses']) for a in self.source_data.values())
        total_db = sum(len(w['verses']) for w in self.db_data.values())

        print(f"\nSOURCE FILE ANALYSIS:")
        print(f"  - Total verses found: {total_source}")
        print(f"  - Author sections: {len(self.source_data)}")

        print(f"\nDATABASE QUERY:")
        print(f"  - Works found: {len(self.db_data)} (expected: {len(self.source_data)})")
        print(f"  - Total verses imported: {total_db} (expected: {total_source})")
        print(f"  - Missing verses: {total_source - total_db}")

        print(f"\nMISSING DATA BY AUTHOR:")
        for issue in self.issues:
            if issue['status'] != 'OK':
                symbol = '[X]' if issue['status'] == 'MISSING' else '[!]'
                print(f"  {symbol} Author {issue['author_number']}: {issue['expected_verses']} expected, {issue['actual_verses']} found (missing: {issue['missing_verses']})")

        print(f"\nCSV Report: qa_file11_report_{datetime.now().strftime('%Y-%m-%d')}.csv")
        print("="*70)

    def export_csv_report(self, output_path):
        """Export detailed comparison to CSV"""
        with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = [
                'author_number', 'author_name', 'work_id_db', 'work_name_db',
                'expected_verses', 'actual_verses', 'missing_verses', 'status'
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            for issue in self.issues:
                work_name = ''
                if issue['work_id_db']:
                    work_name = self.db_data[issue['work_id_db']]['work_name_tamil']

                writer.writerow({
                    'author_number': issue['author_number'],
                    'author_name': issue['author_name'],
                    'work_id_db': issue['work_id_db'] or '',
                    'work_name_db': work_name,
                    'expected_verses': issue['expected_verses'],
                    'actual_verses': issue['actual_verses'],
                    'missing_verses': issue['missing_verses'],
                    'status': issue['status']
                })

        print(f"[CSV] Exported to {output_path}")

    def run_verification(self):
        """Run complete QA verification workflow"""
        print("Starting QA verification for File 11...")
        self.parse_source_file()
        self.query_database()
        self.compare_and_identify_issues()
        self.generate_console_report()

        csv_path = f"qa_file11_report_{datetime.now().strftime('%Y-%m-%d')}.csv"
        self.export_csv_report(csv_path)

        return len(self.issues)

def main():
    import sys

    # Default connection string
    db_connection = 'postgresql://postgres:postgres@localhost/tamil_literature'
    if len(sys.argv) > 1:
        db_connection = sys.argv[1]

    source_file = Path(__file__).parent.parent / 'Tamil-Source-TamilConcordence' / '6_பக்தி இலக்கியம்' / '11.பதினொன்றாம் திருமுறை.txt'

    verifier = File11QAVerifier(str(source_file), db_connection)
    verifier.run_verification()

if __name__ == '__main__':
    main()
