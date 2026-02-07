#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Verify Kambaramayanam migai padal import
"""

import os
import psycopg2

# Fix Windows console encoding
import sys
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

db_connection = os.getenv('DATABASE_URL', "postgresql://postgres:postgres@localhost/tamil_literature")

print("="*70)
print("  KAMBARAMAYANAM MIGAI PADAL VERIFICATION")
print("="*70)

try:
    conn = psycopg2.connect(db_connection)
    cursor = conn.cursor()

    # Get work_id
    cursor.execute("SELECT work_id FROM works WHERE work_name = 'Kambaramayanam'")
    work_id = cursor.fetchone()[0]
    print(f"\nWork ID: {work_id}")

    # Test 1: Count migai verses
    print("\n1. Count of migai padal verses:")
    cursor.execute("""
        SELECT COUNT(*) as migai_count
        FROM verses
        WHERE work_id = %s AND verse_tag = 'migai_padal'
    """, (work_id,))
    migai_count = cursor.fetchone()[0]
    print(f"   Total migai verses: {migai_count:,}")

    # Test 2: Count regular verses
    cursor.execute("""
        SELECT COUNT(*) as regular_count
        FROM verses
        WHERE work_id = %s AND verse_tag IS NULL
    """, (work_id,))
    regular_count = cursor.fetchone()[0]
    print(f"   Total regular verses: {regular_count:,}")
    print(f"   Grand total: {migai_count + regular_count:,}")

    # Test 3: Sample migai verses
    print("\n2. Sample migai padal verses (first 10):")
    cursor.execute("""
        SELECT s.section_name_tamil, v.verse_number, LEFT(l.line_text, 60)
        FROM verses v
        JOIN sections s ON v.section_id = s.section_id
        JOIN lines l ON v.verse_id = l.verse_id
        WHERE v.work_id = %s
          AND v.verse_tag = 'migai_padal'
          AND l.line_number = 1
        ORDER BY s.section_id, v.verse_number
        LIMIT 10
    """, (work_id,))
    for row in cursor.fetchall():
        print(f"   {row[0][:30]:30} | Verse {row[1]:3} | {row[2]}")

    # Test 4: Verify Yuddha Kandam sort order
    print("\n3. Yuddha Kandam padalam sort order (first 15):")
    cursor.execute("""
        SELECT section_number, LEFT(section_name_tamil, 40) as name, sort_order
        FROM sections
        WHERE work_id = %s
          AND parent_section_id = (
            SELECT section_id FROM sections
            WHERE work_id = %s
              AND level_type = 'kandam' AND section_number = 6
          )
        ORDER BY sort_order
        LIMIT 15
    """, (work_id, work_id))
    for row in cursor.fetchall():
        print(f"   #{row[0]:2} | {row[1]:40} | sort_order={row[2]}")

    # Test 5: Count migai verses per Kandam
    print("\n4. Migai verses per Kandam:")
    cursor.execute("""
        SELECT
          k.section_name_tamil as kandam,
          COUNT(DISTINCT s.section_id) as padalams_with_migai,
          COUNT(*) as total_migai_verses
        FROM verses v
        JOIN sections s ON v.section_id = s.section_id
        JOIN sections k ON s.parent_section_id = k.section_id
        WHERE v.verse_tag = 'migai_padal'
          AND v.work_id = %s
        GROUP BY k.section_id, k.section_name_tamil
        ORDER BY k.section_number
    """, (work_id,))
    for row in cursor.fetchall():
        print(f"   {row[0]:30} | {row[1]:2} padalams | {row[2]:4} verses")

    # Test 6: Total verse count
    print("\n5. Total verse count check:")
    cursor.execute("SELECT COUNT(*) FROM verses WHERE work_id = %s", (work_id,))
    total_verses = cursor.fetchone()[0]
    print(f"   Total verses in database: {total_verses:,}")
    print(f"   Expected (from import log): 11,579")
    if total_verses == 11579:
        print("   ✓ Verse count matches!")
    else:
        print(f"   ✗ Mismatch! Difference: {total_verses - 11579}")

    cursor.close()
    conn.close()

    print("\n" + "="*70)
    print("✓ Verification complete!")
    print("="*70)

except Exception as e:
    print(f"\n✗ Error: {e}")
    import traceback
    traceback.print_exc()
    if 'conn' in locals():
        conn.close()
