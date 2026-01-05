#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Verify நீதிநூல்கள் (Ethical Literature) import
"""

import psycopg2
import sys
import io

# Set stdout to UTF-8 for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Connect to database
conn = psycopg2.connect('postgresql://postgres:postgres@localhost/tamil_literature')
cursor = conn.cursor()

print("=" * 70)
print("நீதிநூல்கள் (Collection 325) - Verification")
print("=" * 70)

# 1. Verify all 21 works exist
print("\n1. All 21 Works:")
cursor.execute("""
    SELECT work_id, work_name_tamil, author_tamil
    FROM works
    WHERE work_id IN (SELECT work_id FROM work_collections WHERE collection_id = 325)
    ORDER BY canonical_order
""")
works = cursor.fetchall()
for i, (work_id, name_tamil, author_tamil) in enumerate(works, 1):
    print(f"  {i:2}. [{work_id}] {name_tamil} - {author_tamil}")
print(f"\nTotal works: {len(works)}")

# 2. Verify section counts
print("\n2. Section Counts per Work:")
cursor.execute("""
    SELECT w.work_name_tamil, COUNT(s.section_id) as sections
    FROM works w
    LEFT JOIN sections s ON w.work_id = s.work_id
    WHERE w.work_id IN (SELECT work_id FROM work_collections WHERE collection_id = 325)
    GROUP BY w.work_id, w.work_name_tamil
    ORDER BY w.canonical_order
""")
for name_tamil, sections in cursor.fetchall():
    print(f"  {name_tamil}: {sections} sections")

# 3. Verify File 21 (Thirukkural Kumaresa Venpa) has 138 sections
print("\n3. File 21 Section Count:")
cursor.execute("""
    SELECT w.work_name_tamil, COUNT(s.section_id) as sections
    FROM works w
    JOIN sections s ON w.work_id = s.work_id
    WHERE w.work_name = 'Thirukkural Kumaresa Venpa'
    GROUP BY w.work_name_tamil
""")
result = cursor.fetchone()
if result:
    name, count = result
    print(f"  {name}: {count} sections")
    if count == 138:
        print("  ✓ Correct! Expected 138 sections")
    else:
        print(f"  ✗ ERROR: Expected 138, got {count}")

# 4. Verify File 21 verse renumbering (first 5 sections)
print("\n4. File 21 Verse Renumbering (First 5 Sections):")
cursor.execute("""
    SELECT s.section_number, s.section_name_tamil,
           MIN(v.verse_number) as first_verse,
           MAX(v.verse_number) as last_verse,
           COUNT(v.verse_id) as verse_count
    FROM sections s
    JOIN verses v ON s.section_id = v.section_id
    JOIN works w ON s.work_id = w.work_id
    WHERE w.work_name = 'Thirukkural Kumaresa Venpa'
    GROUP BY s.section_id, s.section_number, s.section_name_tamil
    ORDER BY s.section_number
    LIMIT 5
""")
for section_num, section_name, first, last, count in cursor.fetchall():
    status = "✓" if first == 1 else "✗"
    print(f"  {status} Section {section_num} ({section_name}): verses {first}-{last} ({count} verses)")

# 5. Verify total verse/line/word counts
print("\n5. Total Counts:")
cursor.execute("""
    SELECT
        COUNT(DISTINCT w.work_id) as works,
        COUNT(DISTINCT s.section_id) as sections,
        COUNT(DISTINCT v.verse_id) as verses,
        COUNT(DISTINCT l.line_id) as lines,
        COUNT(DISTINCT wd.word_id) as words
    FROM works w
    LEFT JOIN sections s ON w.work_id = s.work_id
    LEFT JOIN verses v ON s.work_id = v.work_id
    LEFT JOIN lines l ON v.verse_id = l.verse_id
    LEFT JOIN words wd ON l.line_id = wd.line_id
    WHERE w.work_id IN (SELECT work_id FROM work_collections WHERE collection_id = 325)
""")
works, sections, verses, lines, words = cursor.fetchone()
print(f"  Works: {works}")
print(f"  Sections: {sections}")
print(f"  Verses: {verses}")
print(f"  Lines: {lines}")
print(f"  Words: {words}")

print("\n" + "=" * 70)
print("✓ Verification complete!")
print("=" * 70)

cursor.close()
conn.close()
