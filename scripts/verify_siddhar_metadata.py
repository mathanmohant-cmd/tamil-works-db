#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Verify Siddhar Padalgal metadata storage
"""

import psycopg2
import json
import sys

def main():
    db_url = "postgresql://postgres:postgres@localhost/tamil_literature"

    conn = psycopg2.connect(db_url)
    cursor = conn.cursor()

    # Set UTF-8 encoding for stdout on Windows
    if sys.platform == 'win32':
        import codecs
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, errors='replace')

    print("=== Verifying Siddhar Padalgal Metadata ===\n")

    # 1. Check sections metadata
    print("1. Section Metadata (first 10 sections):")
    print("-" * 80)
    cursor.execute("""
        SELECT w.work_name, s.section_name_tamil, s.metadata::text
        FROM works w
        JOIN sections s ON w.work_id = s.work_id
        WHERE w.work_id BETWEEN 261 AND 296
        LIMIT 10
    """)

    for row in cursor.fetchall():
        work_name, section_name, metadata_str = row
        print(f"Work: {work_name}")
        print(f"  Section: {section_name}")
        if metadata_str:
            metadata = json.loads(metadata_str)
            print(f"  Metadata: {json.dumps(metadata, ensure_ascii=False, indent=2)}")
        else:
            print(f"  Metadata: None")
        print()

    # 2. Check verses metadata (verses with *N-N markers)
    print("\n2. Verse Metadata (verses with section-verse references):")
    print("-" * 80)
    cursor.execute("""
        SELECT w.work_name, v.verse_number, v.metadata::text
        FROM works w
        JOIN verses v ON w.work_id = v.work_id
        WHERE w.work_id BETWEEN 261 AND 296
          AND v.metadata IS NOT NULL
        LIMIT 10
    """)

    for row in cursor.fetchall():
        work_name, verse_number, metadata_str = row
        print(f"Work: {work_name}, Verse: {verse_number}")
        if metadata_str:
            metadata = json.loads(metadata_str)
            print(f"  Metadata: {json.dumps(metadata, ensure_ascii=False, indent=2)}")
        else:
            print(f"  Metadata: None")
        print()

    # 3. Count verses with and without metadata
    print("\n3. Metadata Coverage Statistics:")
    print("-" * 80)
    cursor.execute("""
        SELECT
            COUNT(*) as total_verses,
            COUNT(v.metadata) as verses_with_metadata,
            COUNT(*) - COUNT(v.metadata) as verses_without_metadata
        FROM verses v
        JOIN works w ON v.work_id = w.work_id
        WHERE w.work_id BETWEEN 261 AND 296
    """)

    row = cursor.fetchone()
    print(f"Total verses: {row[0]}")
    print(f"Verses with metadata: {row[1]}")
    print(f"Verses without metadata: {row[2]}")

    # 4. Check collection
    print("\n4. Collection Verification:")
    print("-" * 80)
    cursor.execute("""
        SELECT collection_id, collection_name, collection_name_tamil,
               collection_type, description
        FROM collections
        WHERE collection_id = 327
    """)

    row = cursor.fetchone()
    if row:
        print(f"Collection ID: {row[0]}")
        print(f"Name: {row[1]} / {row[2]}")
        print(f"Type: {row[3]}")
        print(f"Description: {row[4]}")
    else:
        print("Collection 327 not found!")

    # 5. Check work count
    print("\n5. Works Count:")
    print("-" * 80)
    cursor.execute("""
        SELECT COUNT(*) FROM works WHERE work_id BETWEEN 261 AND 296
    """)
    print(f"Total Siddhar works imported: {cursor.fetchone()[0]}")

    cursor.close()
    conn.close()

    print("\n[SUCCESS] Verification complete!")

if __name__ == '__main__':
    main()
