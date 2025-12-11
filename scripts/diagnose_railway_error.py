#!/usr/bin/env python3
"""
Diagnostic script to identify the cause of the Railway 500 error.

Usage:
    python diagnose_railway_error.py [database_url]
"""

import sys
import os
import psycopg2
from psycopg2.extras import RealDictCursor


def get_database_url():
    """Get database URL from command line, environment, or use default."""
    if len(sys.argv) > 1:
        return sys.argv[1]
    elif 'DATABASE_URL' in os.environ:
        return os.environ['DATABASE_URL']
    else:
        return 'postgresql://postgres:postgres@localhost/tamil_literature'


def diagnose(db_url):
    """Run diagnostic checks."""

    print(f"Connecting to database...")
    conn = psycopg2.connect(db_url)
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    try:
        print("\n" + "="*70)
        print("DIAGNOSTIC CHECKS FOR RAILWAY 500 ERROR")
        print("="*70)

        # Check 1: Verify tables exist
        print("\n[1] Checking if all tables exist...")
        cursor.execute("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
            AND table_type = 'BASE TABLE'
            ORDER BY table_name;
        """)
        tables = [row['table_name'] for row in cursor.fetchall()]
        print(f"    Found {len(tables)} tables: {', '.join(tables)}")

        required_tables = ['works', 'sections', 'verses', 'lines', 'words']
        missing = [t for t in required_tables if t not in tables]
        if missing:
            print(f"    ✗ MISSING TABLES: {', '.join(missing)}")
            return
        else:
            print(f"    ✓ All required tables exist")

        # Check 2: Verify views exist
        print("\n[2] Checking if views exist...")
        cursor.execute("""
            SELECT table_name
            FROM information_schema.views
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """)
        views = [row['table_name'] for row in cursor.fetchall()]
        print(f"    Found {len(views)} views: {', '.join(views)}")

        required_views = ['verse_hierarchy', 'word_details']
        missing = [v for v in required_views if v not in views]
        if missing:
            print(f"    ✗ MISSING VIEWS: {', '.join(missing)}")
            print("    → Run: psql $DATABASE_URL -f migrations/refresh_views.sql")
            return
        else:
            print(f"    ✓ All required views exist")

        # Check 3: Verify verse_type_tamil column exists
        print("\n[3] Checking verse_type_tamil column in verses table...")
        cursor.execute("""
            SELECT column_name, data_type
            FROM information_schema.columns
            WHERE table_name = 'verses'
            AND column_name IN ('verse_type', 'verse_type_tamil')
            ORDER BY column_name;
        """)
        cols = cursor.fetchall()
        print(f"    Found columns: {', '.join([c['column_name'] for c in cols])}")
        if len(cols) < 2:
            print(f"    ✗ Missing verse_type or verse_type_tamil column")
            return
        else:
            print(f"    ✓ Both columns exist")

        # Check 4: Check verse_type_tamil values
        print("\n[4] Checking verse_type_tamil values...")
        cursor.execute("""
            SELECT
                w.work_id,
                w.work_name,
                COUNT(*) as verse_count,
                COUNT(CASE WHEN verse_type_tamil IS NULL THEN 1 END) as null_count,
                COUNT(CASE WHEN verse_type_tamil IS NOT NULL THEN 1 END) as non_null_count
            FROM verses v
            JOIN works w ON v.work_id = w.work_id
            GROUP BY w.work_id, w.work_name
            ORDER BY w.work_id;
        """)
        for row in cursor.fetchall():
            status = "✓" if row['null_count'] == 0 else "⚠"
            print(f"    {status} {row['work_name']}: {row['verse_count']} verses "
                  f"({row['non_null_count']} with verse_type_tamil, {row['null_count']} NULL)")

        # Check 5: Test word_details view
        print("\n[5] Testing word_details view...")
        try:
            cursor.execute("""
                SELECT verse_type, verse_type_tamil
                FROM word_details
                WHERE word_text = 'சொல்'
                LIMIT 1;
            """)
            result = cursor.fetchone()
            if result:
                print(f"    ✓ word_details view accessible")
                print(f"      Sample: verse_type={result['verse_type']}, "
                      f"verse_type_tamil={result['verse_type_tamil']}")
            else:
                print(f"    ⚠ No results found for test word 'சொல்'")
        except Exception as e:
            print(f"    ✗ Error querying word_details: {e}")

        # Check 6: Simulate the exact search query that's failing
        print("\n[6] Simulating the failing search query...")
        search_term = 'சொல்'
        print(f"    Searching for: {search_term}")

        try:
            # This is the unique_words query from database.py
            cursor.execute("""
                WITH word_stats AS (
                    SELECT
                        word_text,
                        COUNT(*) as count,
                        COUNT(DISTINCT verse_id) as verse_count
                    FROM word_details
                    WHERE word_text = %s
                    GROUP BY word_text
                ),
                work_breakdown_stats AS (
                    SELECT
                        word_text,
                        work_name,
                        work_name_tamil,
                        COUNT(*) as work_count
                    FROM word_details
                    WHERE word_text = %s
                    GROUP BY word_text, work_name, work_name_tamil
                )
                SELECT
                    ws.word_text,
                    ws.count,
                    ws.verse_count,
                    json_agg(json_build_object(
                        'work_name', wbs.work_name,
                        'work_name_tamil', wbs.work_name_tamil,
                        'count', wbs.work_count
                    )) as work_breakdown
                FROM word_stats ws
                JOIN work_breakdown_stats wbs ON ws.word_text = wbs.word_text
                GROUP BY ws.word_text, ws.count, ws.verse_count
                ORDER BY ws.word_text
            """, [search_term, search_term])

            results = cursor.fetchall()
            print(f"    ✓ Query executed successfully")
            print(f"    Found {len(results)} unique words")
            if results:
                for row in results:
                    print(f"      - {row['word_text']}: {row['count']} occurrences, "
                          f"{row['verse_count']} verses")
        except Exception as e:
            print(f"    ✗ ERROR: {e}")
            print(f"    This is likely the cause of the 500 error!")
            import traceback
            traceback.print_exc()

        # Check 7: Test with limit=0 scenario
        print("\n[7] Testing limit=0 scenario...")
        try:
            cursor.execute("""
                SELECT
                    wd.word_id,
                    wd.word_text,
                    wd.verse_type,
                    wd.verse_type_tamil
                FROM word_details wd
                WHERE wd.word_text = %s
                LIMIT 0 OFFSET 0
            """, [search_term])

            results = cursor.fetchall()
            print(f"    ✓ Limit 0 query executed successfully")
            print(f"    Returned {len(results)} results (should be 0)")
        except Exception as e:
            print(f"    ✗ ERROR: {e}")

        print("\n" + "="*70)
        print("DIAGNOSTIC COMPLETE")
        print("="*70)

    except Exception as e:
        print(f"\n✗ Diagnostic failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        cursor.close()
        conn.close()


if __name__ == '__main__':
    db_url = get_database_url()
    print(f"Database: {db_url.split('@')[-1] if '@' in db_url else db_url}")
    diagnose(db_url)
