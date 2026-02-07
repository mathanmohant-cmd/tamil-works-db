"""
Force reset Railway database - ensures complete clean slate
"""
import sys
import os
import psycopg2
from pathlib import Path

def force_reset(connection_string):
    """Forcefully drop and recreate the database schema"""
    print("\n" + "="*70)
    print("  FORCE RESET RAILWAY DATABASE")
    print("="*70)

    try:
        print("\nConnecting to database...")
        conn = psycopg2.connect(connection_string)
        conn.autocommit = True
        cursor = conn.cursor()

        print("\nStep 1: Dropping public schema (CASCADE removes everything)...")
        cursor.execute("DROP SCHEMA IF EXISTS public CASCADE;")
        print("✓ Public schema dropped")

        print("\nStep 2: Recreating public schema...")
        cursor.execute("CREATE SCHEMA public;")
        print("✓ Public schema created")

        print("\nStep 3: Granting permissions...")
        cursor.execute("GRANT ALL ON SCHEMA public TO postgres;")
        cursor.execute("GRANT ALL ON SCHEMA public TO public;")
        print("✓ Permissions granted")

        print("\nStep 4: Verifying clean slate...")
        cursor.execute("""
            SELECT COUNT(*)
            FROM information_schema.tables
            WHERE table_schema = 'public'
        """)
        table_count = cursor.fetchone()[0]

        if table_count == 0:
            print(f"✓ Database is clean (0 tables)")
        else:
            print(f"⚠ Warning: Found {table_count} tables after drop")
            return False

        cursor.close()
        conn.close()

        print("\n" + "="*70)
        print("  DATABASE RESET COMPLETE")
        print("="*70)
        print("\nNext: Run setup_railway_db.py to create schema")
        return True

    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    if len(sys.argv) > 1:
        connection_string = sys.argv[1]
    else:
        connection_string = os.getenv('DATABASE_URL')

    if not connection_string:
        print("Usage: python force_reset_railway.py <DATABASE_URL>")
        print("Or set DATABASE_URL environment variable")
        sys.exit(1)

    print(f"\nConnection: {connection_string[:30]}...")
    response = input("\n⚠ This will DELETE ALL DATA. Continue? (yes/no): ").strip().lower()

    if response not in ['yes', 'y']:
        print("Cancelled.")
        sys.exit(0)

    if force_reset(connection_string):
        print("\n✓ Database is ready for setup_railway_db.py")
    else:
        print("\n✗ Reset failed")
        sys.exit(1)
