#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Setup Tamil Literary Works Database on Railway PostgreSQL
Connect directly to Railway and populate the database with schema and data
"""

import os
import sys
import io
from pathlib import Path

# Fix encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def check_psycopg2():
    """Check if psycopg2 is installed"""
    try:
        import psycopg2
        return True
    except ImportError:
        return False

def get_connection_string():
    """Get Railway PostgreSQL connection string from environment or user input"""
    print("\n" + "="*70)
    print("RAILWAY POSTGRESQL CONNECTION")
    print("="*70)

    # Check for environment variable
    connection_string = os.getenv("DATABASE_URL")

    if connection_string:
        print(f"\n✓ Found DATABASE_URL in environment")
        return connection_string

    print("\nPlease set DATABASE_URL environment variable with your Railway connection string")
    print("\nExample:")
    print('  export DATABASE_URL="postgresql://postgres:password@...railway.app:7432/railway"')
    print("\nOr pass as command line argument:")
    print('  python setup_railway_db.py "postgresql://postgres:password@...railway.app:7432/railway"')
    return None

def test_connection(connection_string):
    """Test the database connection"""
    import psycopg2

    print("\nTesting connection to Railway PostgreSQL...")
    try:
        conn = psycopg2.connect(connection_string)
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        print(f"✓ Connected successfully!")
        print(f"  PostgreSQL version: {version.split(',')[0]}")
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print(f"✗ Connection failed: {e}")
        return False

def run_sql_file(connection_string, sql_file_path, description):
    """Run a SQL file on the database"""
    import psycopg2

    print(f"\n{description}...")

    if not os.path.exists(sql_file_path):
        print(f"✗ File not found: {sql_file_path}")
        return False

    try:
        with open(sql_file_path, 'r', encoding='utf-8') as f:
            sql_content = f.read()

        conn = psycopg2.connect(connection_string)
        cursor = conn.cursor()
        cursor.execute(sql_content)
        conn.commit()
        cursor.close()
        conn.close()

        print(f"✓ {description} completed successfully!")
        return True

    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def check_existing_schema(connection_string):
    """Check if our tables already exist"""
    import psycopg2

    try:
        conn = psycopg2.connect(connection_string)
        cursor = conn.cursor()

        # Check if works table exists
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables
                WHERE table_schema = 'public'
                AND table_name = 'works'
            );
        """)
        table_exists = cursor.fetchone()[0]

        if not table_exists:
            cursor.close()
            conn.close()
            return None

        # Get counts
        cursor.execute("SELECT COUNT(*) FROM works;")
        work_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM verses;")
        verse_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM words;")
        word_count = cursor.fetchone()[0]

        cursor.close()
        conn.close()

        return {
            'works': work_count,
            'verses': verse_count,
            'words': word_count
        }

    except Exception:
        return None

def drop_tables(connection_string):
    """Drop our project tables and views"""
    import psycopg2

    print("\nDropping existing tables and views...")
    try:
        conn = psycopg2.connect(connection_string)
        cursor = conn.cursor()

        # Drop views first (they depend on tables)
        cursor.execute("""
            DROP VIEW IF EXISTS word_details CASCADE;
            DROP VIEW IF EXISTS verse_hierarchy CASCADE;
        """)

        # Drop tables in reverse order of dependencies
        cursor.execute("""
            DROP TABLE IF EXISTS cross_references CASCADE;
            DROP TABLE IF EXISTS commentaries CASCADE;
            DROP TABLE IF EXISTS words CASCADE;
            DROP TABLE IF EXISTS lines CASCADE;
            DROP TABLE IF EXISTS verses CASCADE;
            DROP TABLE IF EXISTS sections CASCADE;
            DROP TABLE IF EXISTS works CASCADE;
        """)

        # Reset sequences - CRITICAL for avoiding duplicate key errors
        # The sequences are auto-created when tables are recreated,
        # but we need to ensure they start from 1
        print("  Resetting ID sequences...")
        cursor.execute("""
            -- Reset sequences if they exist (will be recreated with tables)
            DROP SEQUENCE IF EXISTS works_work_id_seq CASCADE;
            DROP SEQUENCE IF EXISTS sections_section_id_seq CASCADE;
            DROP SEQUENCE IF EXISTS verses_verse_id_seq CASCADE;
            DROP SEQUENCE IF EXISTS lines_line_id_seq CASCADE;
            DROP SEQUENCE IF EXISTS words_word_id_seq CASCADE;
            DROP SEQUENCE IF EXISTS commentaries_commentary_id_seq CASCADE;
            DROP SEQUENCE IF EXISTS cross_references_reference_id_seq CASCADE;
        """)

        conn.commit()
        cursor.close()
        conn.close()
        print("✓ Tables, views, and sequences dropped successfully")
        return True
    except Exception as e:
        print(f"✗ Error dropping tables: {e}")
        return False

def verify_setup(connection_string):
    """Verify the database setup"""
    import psycopg2

    print("\nVerifying database setup...")

    try:
        conn = psycopg2.connect(connection_string)
        cursor = conn.cursor()

        # Check tables
        cursor.execute("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
            AND table_type = 'BASE TABLE'
            ORDER BY table_name;
        """)
        tables = cursor.fetchall()

        print("\n✓ Tables created:")
        for table in tables:
            print(f"  - {table[0]}")

        # Check views
        cursor.execute("""
            SELECT table_name
            FROM information_schema.views
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """)
        views = cursor.fetchall()

        if views:
            print("\n✓ Views created:")
            for view in views:
                print(f"  - {view[0]}")

        # Check works
        cursor.execute("SELECT COUNT(*) FROM works;")
        work_count = cursor.fetchone()[0]

        if work_count > 0:
            cursor.execute("SELECT work_name, author FROM works ORDER BY work_id;")
            works = cursor.fetchall()
            print(f"\n✓ Literary works ({work_count}):")
            for work_name, author in works:
                print(f"  - {work_name} by {author}")

        # Check data
        cursor.execute("SELECT COUNT(*) FROM verses;")
        verse_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM words;")
        word_count = cursor.fetchone()[0]

        print(f"\n✓ Database statistics:")
        print(f"  - Verses: {verse_count}")
        print(f"  - Words: {word_count}")

        cursor.close()
        conn.close()
        return True

    except Exception as e:
        print(f"✗ Verification failed: {e}")
        return False

def main():
    """Main setup function"""
    print("\n" + "="*70)
    print("  RAILWAY DATABASE SETUP - TAMIL LITERARY WORKS")
    print("="*70)

    # Check psycopg2
    if not check_psycopg2():
        print("\n✗ psycopg2 not installed")
        print("Install it: pip install psycopg2-binary")
        return

    # Get connection string
    if len(sys.argv) > 1:
        connection_string = sys.argv[1]
    else:
        connection_string = get_connection_string()

    if not connection_string:
        return

    # Test connection
    if not test_connection(connection_string):
        print("\nPlease check your connection string and try again.")
        return

    # Check if schema already exists
    existing = check_existing_schema(connection_string)
    if existing:
        print("\n" + "="*70)
        print("⚠ EXISTING SCHEMA DETECTED")
        print("="*70)
        print(f"\nFound existing Tamil literature database with:")
        print(f"  - Works: {existing['works']}")
        print(f"  - Verses: {existing['verses']}")
        print(f"  - Words: {existing['words']}")

        response = input("\nDrop existing tables and rebuild? (yes/no): ").strip().lower()
        if response not in ['yes', 'y']:
            print("Setup cancelled.")
            return

        if not drop_tables(connection_string):
            print("\n✗ Failed to drop existing tables")
            return

    # Get SQL file path
    script_dir = Path(__file__).parent
    project_dir = script_dir.parent
    schema_file = project_dir / "sql" / "complete_setup.sql"

    if not schema_file.exists():
        print(f"\n✗ Schema file not found: {schema_file}")
        return

    print("\n" + "="*70)
    print("SETUP PLAN")
    print("="*70)
    print(f"1. Create database schema")
    print(f"2. Verify setup")
    print(f"\nNote: After schema setup, use parser scripts to import data:")
    print(f"  - python scripts/thirukkural_parser.py")
    print(f"  - python scripts/sangam_parser.py")

    response = input("\nProceed with schema setup? (yes/no): ").strip().lower()
    if response not in ['yes', 'y']:
        print("Setup cancelled.")
        return

    # Run schema file
    if not run_sql_file(connection_string, str(schema_file), "Creating database schema"):
        return

    # Verify setup
    if verify_setup(connection_string):
        print("\n" + "="*70)
        print("  DATABASE SCHEMA SETUP COMPLETE!")
        print("="*70)
        print("\nNext steps:")
        print("1. Import Thirukkural:")
        print(f'   python scripts/thirukkural_parser.py "{connection_string}"')
        print("\n2. Import Sangam literature:")
        print(f'   python scripts/sangam_parser.py "{connection_string}"')
        print("\n3. Start your FastAPI backend:")
        print("   cd webapp/backend && python main.py")
    else:
        print("\nSetup verification failed. Please check the errors above.")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nSetup cancelled by user.")
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
