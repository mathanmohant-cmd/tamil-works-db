#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Populate phoneme column for all words in the database
Processes ~1.5M words in batches with progress reporting

Usage:
    python populate_phoneme_column.py [database_url] [--yes]

    database_url: Optional database connection string
    --yes: Skip confirmation prompt (for automated runs)

    If database_url is not provided, uses DATABASE_URL environment variable
    or defaults to: postgresql://postgres:postgres@localhost/tamil_literature
"""
import os
import sys
import psycopg2
import time
from tamil_phoneme_converter import convert_to_phoneme


def get_connection_string():
    """Get database connection string from args, env, or default"""
    # Check for database URL in args (not --yes flag)
    for arg in sys.argv[1:]:
        if not arg.startswith('--'):
            return arg

    db_url = os.getenv("DATABASE_URL")
    if db_url:
        return db_url

    return "postgresql://postgres:postgres@localhost/tamil_literature"


def should_skip_confirmation():
    """Check if --yes flag is present"""
    return '--yes' in sys.argv or '-y' in sys.argv


def populate_phonemes(batch_size=10000):
    """
    Populate phoneme column for all words

    Args:
        batch_size: Number of records to process per batch (default: 10,000)

    The script processes words in batches, committing after each batch for
    transaction safety. Progress is reported every batch.
    """
    print("=" * 70)
    print("Populate Phoneme Column for All Words")
    print("=" * 70)

    conn = None
    cursor = None

    try:
        # Connect to database
        connection_string = get_connection_string()
        print(f"\nConnecting to database...")
        conn = psycopg2.connect(connection_string)
        conn.autocommit = False  # Use explicit transactions
        cursor = conn.cursor()

        # Get total count of words without phoneme (excluding special markers)
        print("Analyzing database...")
        cursor.execute("""
            SELECT COUNT(*) FROM words
            WHERE phoneme IS NULL
            AND position('_' in word_text) = 0
            AND position('-' in word_text) = 0
        """)
        total_words = cursor.fetchone()[0]

        # Count words that will be skipped (compound/particle markers)
        cursor.execute("""
            SELECT COUNT(*) FROM words
            WHERE (position('_' in word_text) > 0 OR position('-' in word_text) > 0)
        """)
        skipped_words = cursor.fetchone()[0]

        # Get total count of all words
        cursor.execute("SELECT COUNT(*) FROM words")
        all_words = cursor.fetchone()[0]

        print(f"\nDatabase Statistics:")
        print(f"  Total words in database: {all_words:,}")
        print(f"  Words to process: {total_words:,}")
        print(f"  Words to skip (with _ or -): {skipped_words:,}")
        print(f"  Words already processed: {all_words - total_words - skipped_words:,}")
        print(f"\nProcessing Configuration:")
        print(f"  Batch size: {batch_size:,} words per transaction")
        print(f"  Estimated batches: {(total_words + batch_size - 1) // batch_size:,}")

        if total_words == 0:
            print("\n✓ All words already have phoneme data. Nothing to do.")
            return

        # Confirm before proceeding (unless --yes flag)
        if not should_skip_confirmation():
            print()
            response = input("Proceed with update? (yes/no): ").strip().lower()
            if response not in ['yes', 'y']:
                print("Cancelled by user.")
                return
        else:
            print("\nAuto-confirmed with --yes flag. Starting processing...")


        print("\nProcessing words...")
        print("-" * 70)
        start_time = time.time()
        processed = 0
        batch_num = 0

        while True:
            # Fetch batch of words without phoneme (excluding special markers)
            cursor.execute("""
                SELECT word_id, word_text
                FROM words
                WHERE phoneme IS NULL
                AND position('_' in word_text) = 0
                AND position('-' in word_text) = 0
                LIMIT %s
            """, [batch_size])

            batch = cursor.fetchall()
            if not batch:
                break  # No more records

            batch_num += 1

            # Process batch
            for word_id, word_text in batch:
                phoneme = convert_to_phoneme(word_text)

                # Skip if None (shouldn't happen with our filter, but defensive)
                if phoneme is None:
                    continue

                cursor.execute("""
                    UPDATE words
                    SET phoneme = %s
                    WHERE word_id = %s
                """, [phoneme, word_id])

            conn.commit()  # Commit after each batch
            processed += len(batch)

            # Progress reporting
            pct = (processed / total_words) * 100
            elapsed = time.time() - start_time
            rate = processed / elapsed if elapsed > 0 else 0
            eta = (total_words - processed) / rate if rate > 0 else 0

            print(f"Batch {batch_num:,}: {processed:,}/{total_words:,} ({pct:.1f}%) | "
                  f"Rate: {rate:.0f} words/sec | ETA: {eta/60:.1f} min")

        # Final statistics
        elapsed = time.time() - start_time
        print("-" * 70)
        print(f"\n✓ Processing completed successfully!")
        print(f"\nExecution Statistics:")
        print(f"  Total time: {elapsed:.1f} seconds ({elapsed/60:.1f} minutes)")
        print(f"  Words processed: {processed:,}")
        print(f"  Average rate: {processed/elapsed:.0f} words/sec")
        print(f"  Batches processed: {batch_num:,}")

        # Verify results
        print(f"\nVerifying results...")
        cursor.execute("SELECT COUNT(*) FROM words WHERE phoneme IS NOT NULL")
        count_with_phoneme = cursor.fetchone()[0]

        cursor.execute("""
            SELECT COUNT(*) FROM words
            WHERE phoneme IS NULL
            AND (position('_' in word_text) > 0 OR position('-' in word_text) > 0)
        """)
        count_skipped = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM words")
        total_count = cursor.fetchone()[0]

        count_processable = total_count - count_skipped

        print(f"\nFinal Database State:")
        print(f"  Total words: {total_count:,}")
        print(f"  Words with phoneme: {count_with_phoneme:,}")
        print(f"  Words skipped (with _ or -): {count_skipped:,}")
        print(f"  Words without phoneme: {total_count - count_with_phoneme - count_skipped:,}")
        print(f"  Coverage: {(count_with_phoneme/count_processable)*100:.2f}% of processable words")

        if count_with_phoneme == count_processable:
            print(f"\n✓ All processable words now have phoneme data!")
            print(f"  ({count_skipped:,} words with special markers were intentionally skipped)")
        else:
            print(f"\n⚠ Warning: {count_processable - count_with_phoneme:,} processable words still without phoneme")

    except KeyboardInterrupt:
        print("\n\n⚠ Process interrupted by user (Ctrl+C)")
        print("Rolling back current batch...")
        if conn:
            conn.rollback()
        print("Some words may have been processed in previous batches.")
        sys.exit(1)

    except psycopg2.Error as e:
        print(f"\n✗ Database error: {e}")
        if conn:
            print("Rolling back transaction...")
            conn.rollback()
        raise

    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        if conn:
            print("Rolling back transaction...")
            conn.rollback()
        raise

    finally:
        # Clean up database connections
        if cursor:
            cursor.close()
        if conn:
            conn.close()


if __name__ == '__main__':
    try:
        populate_phonemes()
    except Exception as e:
        print(f"\nScript failed: {e}")
        sys.exit(1)
