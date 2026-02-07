#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Run migration 005: Add verse_tag column
"""

import os
import psycopg2

db_connection = os.getenv('DATABASE_URL', "postgresql://postgres:postgres@localhost/tamil_literature")

print("Running migration 005: Add verse_tag column...")
print(f"Database: {db_connection.split('@')[-1] if '@' in db_connection else db_connection}")

try:
    conn = psycopg2.connect(db_connection)
    cursor = conn.cursor()

    # Add verse_tag column
    print("  Adding verse_tag column...")
    cursor.execute("ALTER TABLE verses ADD COLUMN IF NOT EXISTS verse_tag VARCHAR(100);")

    # Create index
    print("  Creating index...")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_verses_verse_tag ON verses(verse_tag);")

    # Add comment
    print("  Adding column comment...")
    cursor.execute("""
        COMMENT ON COLUMN verses.verse_tag IS
          'Special verse classification: "migai_padal" for additional verses, NULL for regular verses';
    """)

    conn.commit()

    # Verify
    cursor.execute("""
        SELECT column_name, data_type, character_maximum_length
        FROM information_schema.columns
        WHERE table_name = 'verses' AND column_name = 'verse_tag';
    """)
    result = cursor.fetchone()

    if result:
        print(f"  ✓ Column added successfully: {result}")
    else:
        print("  ✗ Column not found after migration!")

    cursor.close()
    conn.close()

    print("✓ Migration completed successfully!")

except Exception as e:
    print(f"✗ Migration failed: {e}")
    import traceback
    traceback.print_exc()
    if 'conn' in locals():
        conn.rollback()
        conn.close()
