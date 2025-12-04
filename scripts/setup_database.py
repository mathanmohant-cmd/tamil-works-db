#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Setup Tamil Literary Works Database on Neon
This script connects to your Neon database and creates the schema with sample data
"""

import os
import sys
import io

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

def install_psycopg2():
    """Install psycopg2-binary"""
    print("Installing psycopg2-binary (PostgreSQL adapter for Python)...")
    import subprocess
    result = subprocess.run([sys.executable, "-m", "pip", "install", "psycopg2-binary"],
                          capture_output=True, text=True)
    if result.returncode == 0:
        print("✓ psycopg2-binary installed successfully!")
        return True
    else:
        print("✗ Failed to install psycopg2-binary:")
        print(result.stderr)
        return False

def get_connection_string():
    """Get Neon connection string from user"""
    print("\n" + "="*70)
    print("NEON DATABASE CONNECTION SETUP")
    print("="*70)
    print("\nPlease provide your Neon database connection string.")
    print("\nYou can find this in your Neon dashboard:")
    print("1. Go to https://console.neon.tech")
    print("2. Select your project")
    print("3. Click 'Connection Details'")
    print("4. Copy the connection string\n")
    print("It should look like:")
    print("postgresql://user:password@ep-xxxxx.region.aws.neon.tech/dbname?sslmode=require\n")

    connection_string = input("Enter your Neon connection string: ").strip()

    if not connection_string.startswith("postgresql://"):
        print("\n✗ Invalid connection string. It should start with 'postgresql://'")
        return None

    if "sslmode=require" not in connection_string:
        print("\nWarning: Adding sslmode=require to connection string...")
        if "?" in connection_string:
            connection_string += "&sslmode=require"
        else:
            connection_string += "?sslmode=require"

    return connection_string

def test_connection(connection_string):
    """Test the database connection"""
    import psycopg2

    print("\nTesting connection to Neon database...")
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

        # Execute the SQL
        cursor.execute(sql_content)
        conn.commit()

        print(f"✓ {description} completed successfully!")

        cursor.close()
        conn.close()
        return True

    except Exception as e:
        print(f"✗ Error: {e}")
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

        print("\n✓ Views created:")
        for view in views:
            print(f"  - {view[0]}")

        # Check works
        cursor.execute("SELECT work_name, author FROM works ORDER BY work_id;")
        works = cursor.fetchall()

        print("\n✓ Literary works loaded:")
        for work_name, author in works:
            print(f"  - {work_name} by {author}")

        # Check sample data
        cursor.execute("SELECT COUNT(*) FROM words;")
        word_count = cursor.fetchone()[0]
        print(f"\n✓ Sample data: {word_count} words loaded")

        cursor.close()
        conn.close()
        return True

    except Exception as e:
        print(f"✗ Verification failed: {e}")
        return False

def save_connection_string(connection_string):
    """Save connection string to .env file"""
    env_file = os.path.join(os.path.dirname(__file__), '..', '.env')

    try:
        with open(env_file, 'w', encoding='utf-8') as f:
            f.write(f"# Neon Database Connection\n")
            f.write(f"NEON_DB_URL={connection_string}\n")
        print(f"\n✓ Connection string saved to: {env_file}")
        print("  You can use this in your applications by loading the .env file")
        return True
    except Exception as e:
        print(f"✗ Could not save connection string: {e}")
        return False

def main():
    """Main setup function"""
    print("\n" + "="*70)
    print("  TAMIL LITERARY WORKS DATABASE - SETUP SCRIPT")
    print("="*70)

    # Check/install psycopg2
    if not check_psycopg2():
        print("\npsycopg2 not found. Installing...")
        if not install_psycopg2():
            print("\nPlease install manually: pip install psycopg2-binary")
            return
        # Import after installation
        import importlib
        importlib.import_module('psycopg2')

    # Get connection string
    connection_string = get_connection_string()
    if not connection_string:
        return

    # Test connection
    if not test_connection(connection_string):
        print("\nPlease check your connection string and try again.")
        return

    # Get SQL file paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(script_dir)
    schema_file = os.path.join(project_dir, 'sql', 'schema.sql')
    sample_data_file = os.path.join(project_dir, 'sql', 'sample_word_data.sql')

    print("\n" + "="*70)
    print("SETUP PLAN")
    print("="*70)
    print(f"1. Create database schema from: {schema_file}")
    print(f"2. Load sample data from: {sample_data_file}")
    print(f"3. Verify setup")

    response = input("\nProceed with setup? (yes/no): ").strip().lower()
    if response not in ['yes', 'y']:
        print("Setup cancelled.")
        return

    # Run schema file
    if not run_sql_file(connection_string, schema_file, "Creating database schema"):
        return

    # Run sample data file
    if not run_sql_file(connection_string, sample_data_file, "Loading sample word data"):
        print("\nNote: Schema was created, but sample data failed to load.")
        print("You can try loading sample data manually later.")

    # Verify setup
    if verify_setup(connection_string):
        print("\n" + "="*70)
        print("  DATABASE SETUP COMPLETE!")
        print("="*70)

        # Save connection string
        save_response = input("\nSave connection string to .env file? (yes/no): ").strip().lower()
        if save_response in ['yes', 'y']:
            save_connection_string(connection_string)

        print("\nNext steps:")
        print("1. Check out the sample queries in sql/queries.sql")
        print("2. View word usage examples in docs/word_usage_examples.md")
        print("3. Start populating with complete Tamil literary texts")
        print("\nTo connect using psql:")
        print(f'  psql "{connection_string}"')

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
