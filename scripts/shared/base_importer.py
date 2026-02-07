#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Global Base Importer Class for Tamil Literature Parsers

This base class provides common functionality for all Tamil work import scripts:
- Automatic ID allocation (query MAX once at init)
- Collection creation (idempotent)
- Work creation with collection linking
- Atomic bulk insert using PostgreSQL COPY (1000x faster than INSERT)
- Error handling with rollback

Used by:
- Eighteen Lesser Texts (18 works)
- Can be used by: Sangam, Five Great Epics, Devotional Literature, etc.

Example Usage:
    class MyWorkImporter(BaseWorkImporter):
        def __init__(self, db_connection_string, collection_id=None):
            super().__init__(db_connection_string, collection_id)
            self._ensure_collection_exists(...)
            self.work_id = self._create_work(...)

        def parse_file(self, text_file_path):
            # Parse text file into self.sections, self.verses, self.lines, self.words
            pass

    importer = MyWorkImporter(db_url, collection_id=201)
    importer.parse_file("text.txt")
    importer.bulk_insert()  # Single atomic transaction
    importer.close()
"""

import psycopg2
import csv
import io
import sys


class BaseWorkImporter:
    """Base class for atomic work imports with collection linking

    Provides:
    - Automatic ID allocation (query MAX once at init)
    - Collection creation (idempotent)
    - Work creation with collection linking
    - Atomic bulk insert (single transaction)
    - Error handling with rollback
    """

    def __init__(self, db_connection_string: str, collection_id: int = None):
        """Initialize importer with database connection

        Args:
            db_connection_string: PostgreSQL connection string
            collection_id: Optional collection ID to link work to
        """
        self.conn = psycopg2.connect(db_connection_string)
        self.cursor = self.conn.cursor()
        self.collection_id = collection_id

        # Query MAX IDs ONCE at initialization
        self._initialize_id_counters()

        # Data containers (in-memory lists)
        self.works = []
        self.work_collections = []  # CRITICAL for atomicity
        self.sections = []
        self.verses = []
        self.lines = []
        self.words = []

        print(f"  Starting IDs: work={self.work_id}, section={self.section_id}, "
              f"verse={self.verse_id}, line={self.line_id}, word={self.word_id}")

    def _initialize_id_counters(self):
        """Query MAX IDs for all tables once at initialization

        Critical for delete + reimport cycles:
        - After deletion, MAX IDs remain at highest ever used
        - Next import starts from MAX + 1 (no conflicts)
        """
        self.cursor.execute("SELECT COALESCE(MAX(work_id), 0) FROM works")
        self.work_id = self.cursor.fetchone()[0] + 1

        self.cursor.execute("SELECT COALESCE(MAX(section_id), 0) FROM sections")
        self.section_id = self.cursor.fetchone()[0] + 1

        self.cursor.execute("SELECT COALESCE(MAX(verse_id), 0) FROM verses")
        self.verse_id = self.cursor.fetchone()[0] + 1

        self.cursor.execute("SELECT COALESCE(MAX(line_id), 0) FROM lines")
        self.line_id = self.cursor.fetchone()[0] + 1

        self.cursor.execute("SELECT COALESCE(MAX(word_id), 0) FROM words")
        self.word_id = self.cursor.fetchone()[0] + 1

    def _ensure_collection_exists(self, collection_id, collection_name,
                                   collection_name_tamil, description):
        """Ensure collection exists (idempotent)

        Note: Not committed until bulk_insert() is called
        Part of the same transaction as work creation
        """
        self.cursor.execute(
            "SELECT collection_id FROM collections WHERE collection_id = %s",
            (collection_id,)
        )
        if not self.cursor.fetchone():
            print(f"  Creating collection {collection_id} ({collection_name_tamil})...")
            self.cursor.execute("""
                INSERT INTO collections (
                    collection_id, collection_name, collection_name_tamil,
                    collection_type, description, parent_collection_id
                ) VALUES (%s, %s, %s, %s, %s, %s)
            """, (collection_id, collection_name, collection_name_tamil,
                  'canon', description, 1))  # Type: canon, Parent: Tamil Literature root
        else:
            print(f"  Collection {collection_id} already exists")

    def _create_work(self, work_name, work_name_tamil, metadata):
        """Create work entry and link to collection

        Args:
            work_name: English work name
            work_name_tamil: Tamil work name
            metadata: Dict with work metadata (period, author, description, etc.)

        Returns:
            work_id: Assigned work ID

        Raises:
            ValueError: If work already exists
        """
        # Check for duplicate
        self.cursor.execute(
            "SELECT work_id FROM works WHERE work_name = %s",
            (work_name,)
        )
        if self.cursor.fetchone():
            raise ValueError(f"Work {work_name} already exists. "
                           f"Delete it first using the delete script.")

        work_id = self.work_id
        self.work_id += 1

        # Add to in-memory works list (not committed yet)
        self.works.append({
            'work_id': work_id,
            'work_name': work_name,
            'work_name_tamil': work_name_tamil,
            'period': metadata.get('period'),
            'author': metadata.get('author'),
            'author_tamil': metadata.get('author_tamil'),
            'description': metadata.get('description'),
            'chronology_start_year': metadata.get('chronology_start_year'),
            'chronology_end_year': metadata.get('chronology_end_year'),
            'chronology_confidence': metadata.get('chronology_confidence'),
            'chronology_notes': metadata.get('chronology_notes'),
            'canonical_order': metadata.get('canonical_order')
        })

        # CRITICAL: Link to collection if specified
        if self.collection_id:
            self.work_collections.append({
                'work_id': work_id,
                'collection_id': self.collection_id,
                'position_in_collection': metadata.get('position_in_collection')
            })
            print(f"  Work {work_name_tamil} will be linked to collection {self.collection_id}")

        return work_id

    def bulk_insert(self):
        """Phase 2: Atomic bulk insert with single commit

        Inserts all data in dependency order:
        1. Works
        2. Work collections (links works to collections)
        3. Sections
        4. Verses
        5. Lines
        6. Words

        Single commit at the end = atomic transaction
        """
        print("\nPhase 2: Bulk inserting into database...")

        # Insert in dependency order
        if self.works:
            print(f"  Inserting {len(self.works)} work(s)...")
            self._bulk_copy('works', self.works,
                          ['work_id', 'work_name', 'work_name_tamil', 'period',
                           'author', 'author_tamil', 'description',
                           'chronology_start_year', 'chronology_end_year',
                           'chronology_confidence', 'chronology_notes', 'canonical_order'])

        if self.work_collections:
            print(f"  Linking {len(self.work_collections)} work(s) to collection...")
            self._bulk_copy('work_collections', self.work_collections,
                          ['work_id', 'collection_id', 'position_in_collection'])

        if self.sections:
            print(f"  Inserting {len(self.sections)} sections...")
            self._bulk_copy('sections', self.sections,
                          ['section_id', 'work_id', 'parent_section_id', 'level_type',
                           'level_type_tamil', 'section_number', 'section_name',
                           'section_name_tamil', 'sort_order'])

        if self.verses:
            print(f"  Inserting {len(self.verses)} verses...")
            self._bulk_copy('verses', self.verses,
                          ['verse_id', 'work_id', 'section_id', 'verse_number',
                           'verse_type', 'verse_type_tamil', 'total_lines',
                           'sort_order', 'metadata'])

        if self.lines:
            print(f"  Inserting {len(self.lines)} lines...")
            self._bulk_copy('lines', self.lines,
                          ['line_id', 'verse_id', 'line_number', 'line_text'])

        if self.words:
            print(f"  Inserting {len(self.words)} words...")
            self._bulk_copy('words', self.words,
                          ['word_id', 'line_id', 'word_position', 'word_text', 'sandhi_split'])

        # SINGLE COMMIT - makes entire import atomic
        self.conn.commit()
        print("[OK] Phase 2 complete: All data inserted atomically")

    def _bulk_copy(self, table_name, data, columns):
        """Use COPY for bulk insert (1000x faster than INSERT)

        Special handling for JSON columns (verses.metadata)
        """
        if not data:
            return

        buffer = io.StringIO()

        # Special handling for verses table with metadata column
        if table_name == 'verses' and 'metadata' in columns:
            # Manually format rows to avoid CSV escaping of JSON
            for row in data:
                metadata_value = row.get('metadata', None)
                if metadata_value:
                    # Replace tab characters in JSON to avoid breaking the format
                    metadata_value = metadata_value.replace('\t', ' ')

                # Build row values in column order
                values = []
                for col in columns:
                    if col == 'metadata':
                        values.append(metadata_value if metadata_value else '')
                    else:
                        val = row.get(col)
                        values.append(str(val) if val is not None else '')

                buffer.write('\t'.join(values) + '\n')

            buffer.seek(0)
            self.cursor.copy_from(buffer, table_name, columns=columns, null='')
        else:
            # Use CSV writer for tables without JSON
            writer = csv.writer(buffer, delimiter='\t')
            for row in data:
                writer.writerow([row.get(col) if row.get(col) is not None else '\\N' for col in columns])
            buffer.seek(0)
            self.cursor.copy_from(buffer, table_name, columns=columns, null='\\N')

    def rollback(self):
        """Rollback transaction on error"""
        print("  Rolling back transaction...")
        self.conn.rollback()

    def close(self):
        """Close database connection"""
        self.cursor.close()
        self.conn.close()
