#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Reset Tamil Literature Database
Drops all tables and recreates schema using Python/psycopg2
"""

import os
import sys
import psycopg2
from pathlib import Path

def get_connection_string():
    """Get database connection string"""
    if len(sys.argv) > 1:
        return sys.argv[1]

    db_url = os.getenv("DATABASE_URL")
    if db_url:
        return db_url

    # Default local connection
    return "postgresql://postgres:postgres@localhost/tamil_literature"

def drop_all_tables(conn):
    """Drop all tables, views, and sequences"""
    print("\nDropping all tables, views, and sequences...")

    cursor = conn.cursor()

    # Drop views first
    cursor.execute("""
        DROP VIEW IF EXISTS word_details CASCADE;
        DROP VIEW IF EXISTS verse_hierarchy CASCADE;
    """)

    # Drop tables in reverse dependency order
    cursor.execute("""
        DROP TABLE IF EXISTS cross_references CASCADE;
        DROP TABLE IF EXISTS commentaries CASCADE;
        DROP TABLE IF EXISTS words CASCADE;
        DROP TABLE IF EXISTS lines CASCADE;
        DROP TABLE IF EXISTS verses CASCADE;
        DROP TABLE IF EXISTS sections CASCADE;
        DROP TABLE IF EXISTS work_collections CASCADE;
        DROP TABLE IF EXISTS collections CASCADE;
        DROP TABLE IF EXISTS admin_users CASCADE;
        DROP TABLE IF EXISTS works CASCADE;
    """)

    # Drop sequences
    cursor.execute("""
        DROP SEQUENCE IF EXISTS works_work_id_seq CASCADE;
        DROP SEQUENCE IF EXISTS collections_collection_id_seq CASCADE;
        DROP SEQUENCE IF EXISTS admin_users_user_id_seq CASCADE;
        DROP SEQUENCE IF EXISTS sections_section_id_seq CASCADE;
        DROP SEQUENCE IF EXISTS verses_verse_id_seq CASCADE;
        DROP SEQUENCE IF EXISTS lines_line_id_seq CASCADE;
        DROP SEQUENCE IF EXISTS words_word_id_seq CASCADE;
        DROP SEQUENCE IF EXISTS commentaries_commentary_id_seq CASCADE;
        DROP SEQUENCE IF EXISTS cross_references_reference_id_seq CASCADE;
    """)

    conn.commit()
    cursor.close()
    print("✓ All tables dropped successfully")

def create_schema(conn):
    """Create database schema from complete_setup.sql"""
    print("\nCreating database schema...")

    script_dir = Path(__file__).parent
    schema_file = script_dir.parent / "sql" / "complete_setup.sql"

    if not schema_file.exists():
        print(f"✗ Schema file not found: {schema_file}")
        return False

    with open(schema_file, 'r', encoding='utf-8') as f:
        sql_content = f.read()

    cursor = conn.cursor()
    cursor.execute(sql_content)
    conn.commit()
    cursor.close()

    print("✓ Schema created successfully")
    return True

def verify_schema(conn):
    """Verify the schema was created correctly"""
    print("\nVerifying schema...")

    cursor = conn.cursor()

    # Check for canonical_order field in works table
    cursor.execute("""
        SELECT column_name, data_type
        FROM information_schema.columns
        WHERE table_name = 'works'
        ORDER BY ordinal_position;
    """)

    columns = cursor.fetchall()
    column_names = [col[0] for col in columns]

    print(f"\n✓ Works table has {len(columns)} columns:")
    for col_name, col_type in columns:
        if col_name == 'canonical_order':
            print(f"  ✓ {col_name} ({col_type}) - NEW FIELD")
        else:
            print(f"  - {col_name} ({col_type})")

    if 'canonical_order' not in column_names:
        print("\n✗ WARNING: canonical_order field NOT found in works table!")
        return False

    # Check all tables exist
    cursor.execute("""
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'public'
        AND table_type = 'BASE TABLE'
        ORDER BY table_name;
    """)

    tables = [row[0] for row in cursor.fetchall()]
    expected_tables = [
        'admin_users', 'collections', 'commentaries', 'cross_references',
        'lines', 'sections', 'verses', 'words', 'work_collections', 'works'
    ]

    print(f"\n✓ Database has {len(tables)} tables:")
    for table in tables:
        print(f"  - {table}")

    missing = set(expected_tables) - set(tables)
    if missing:
        print(f"\n✗ WARNING: Missing tables: {missing}")
        return False

    cursor.close()
    return True

def main():
    print("\n" + "="*70)
    print("  RESET TAMIL LITERATURE DATABASE")
    print("="*70)

    connection_string = get_connection_string()
    print(f"\nConnection: {connection_string.split('@')[1] if '@' in connection_string else 'localhost'}")

    try:
        # Connect to database
        print("\nConnecting to database...")
        conn = psycopg2.connect(connection_string)
        print("✓ Connected successfully")

        # Drop all tables
        drop_all_tables(conn)

        # Create schema
        if not create_schema(conn):
            return

        # Verify
        if verify_schema(conn):
            print("\n" + "="*70)
            print("  DATABASE RESET COMPLETE!")
            print("="*70)
            print("\nNext steps:")
            print("1. Import Thirukkural:")
            print("   python scripts/thirukkural_bulk_import.py")
            print("\n2. Import Sangam literature:")
            print("   python scripts/sangam_bulk_import.py")
            print("\n3. Import Silapathikaram:")
            print("   python scripts/silapathikaram_bulk_import.py")
            print("\n4. Import Kambaramayanam:")
            print("   python scripts/kambaramayanam_bulk_import.py")
        else:
            print("\n✗ Schema verification failed!")

        conn.close()

    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
