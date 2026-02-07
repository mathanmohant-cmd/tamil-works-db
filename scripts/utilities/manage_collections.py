#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Collection Management Utility
Manage work-collection relationships and ordering
"""

import os
import sys
import psycopg2
from psycopg2.extras import RealDictCursor
from typing import Optional

class CollectionManager:
    def __init__(self, db_connection_string: str):
        """Initialize collection manager"""
        self.conn = psycopg2.connect(db_connection_string)
        self.cursor = self.conn.cursor(cursor_factory=RealDictCursor)

    def list_collections(self, collection_type: Optional[str] = None):
        """List all collections"""
        if collection_type:
            self.cursor.execute("""
                SELECT
                    c.collection_id,
                    c.collection_name,
                    c.collection_name_tamil,
                    c.collection_type,
                    pc.collection_name as parent_name,
                    COUNT(wc.work_id) as work_count
                FROM collections c
                LEFT JOIN collections pc ON c.parent_collection_id = pc.collection_id
                LEFT JOIN work_collections wc ON c.collection_id = wc.collection_id
                WHERE c.collection_type = %s
                GROUP BY c.collection_id, c.collection_name, c.collection_name_tamil, c.collection_type, pc.collection_name
                ORDER BY c.sort_order, c.collection_name
            """, (collection_type,))
        else:
            self.cursor.execute("""
                SELECT
                    c.collection_id,
                    c.collection_name,
                    c.collection_name_tamil,
                    c.collection_type,
                    pc.collection_name as parent_name,
                    COUNT(wc.work_id) as work_count
                FROM collections c
                LEFT JOIN collections pc ON c.parent_collection_id = pc.collection_id
                LEFT JOIN work_collections wc ON c.collection_id = wc.collection_id
                GROUP BY c.collection_id, c.collection_name, c.collection_name_tamil, c.collection_type, pc.collection_name
                ORDER BY c.collection_type, c.sort_order, c.collection_name
            """)

        results = self.cursor.fetchall()

        print("\n" + "="*80)
        print("COLLECTIONS")
        print("="*80)
        print(f"{'ID':<5} {'Name':<30} {'Type':<12} {'Parent':<20} {'Works':<6}")
        print("-"*80)

        for row in results:
            parent = row['parent_name'] or '-'
            print(f"{row['collection_id']:<5} {row['collection_name']:<30} {row['collection_type']:<12} {parent:<20} {row['work_count']:<6}")

    def list_works(self, unassigned_only: bool = False):
        """List all works"""
        if unassigned_only:
            self.cursor.execute("""
                SELECT
                    w.work_id,
                    w.work_name,
                    w.work_name_tamil,
                    w.period
                FROM works w
                LEFT JOIN work_collections wc ON w.work_id = wc.work_id
                WHERE wc.work_id IS NULL
                ORDER BY w.work_name
            """)
        else:
            self.cursor.execute("""
                SELECT
                    w.work_id,
                    w.work_name,
                    w.work_name_tamil,
                    w.period,
                    COUNT(wc.collection_id) as collection_count
                FROM works w
                LEFT JOIN work_collections wc ON w.work_id = wc.work_id
                GROUP BY w.work_id, w.work_name, w.work_name_tamil, w.period
                ORDER BY w.work_name
            """)

        results = self.cursor.fetchall()

        print("\n" + "="*80)
        print("WORKS" + (" (Unassigned Only)" if unassigned_only else ""))
        print("="*80)
        print(f"{'ID':<5} {'Name':<30} {'Period':<25} {'Collections':<12}")
        print("-"*80)

        for row in results:
            period = row['period'] or '-'
            coll_count = row.get('collection_count', 0) if not unassigned_only else 0
            print(f"{row['work_id']:<5} {row['work_name']:<30} {period:<25} {coll_count:<12}")

    def list_work_collections(self, work_id: int):
        """List all collections a work belongs to"""
        self.cursor.execute("""
            SELECT
                c.collection_id,
                c.collection_name,
                c.collection_name_tamil,
                c.collection_type,
                wc.position_in_collection,
                wc.is_primary
            FROM work_collections wc
            JOIN collections c ON wc.collection_id = c.collection_id
            WHERE wc.work_id = %s
            ORDER BY wc.is_primary DESC, c.collection_name
        """, (work_id,))

        results = self.cursor.fetchall()

        # Get work name
        self.cursor.execute("SELECT work_name, work_name_tamil FROM works WHERE work_id = %s", (work_id,))
        work = self.cursor.fetchone()

        print("\n" + "="*80)
        print(f"COLLECTIONS FOR: {work['work_name']} ({work['work_name_tamil']})")
        print("="*80)
        print(f"{'Collection ID':<15} {'Name':<35} {'Position':<10} {'Primary':<8}")
        print("-"*80)

        if not results:
            print("  (No collections assigned)")
        else:
            for row in results:
                pos = str(row['position_in_collection']) if row['position_in_collection'] else '-'
                primary = '✓' if row['is_primary'] else ''
                print(f"{row['collection_id']:<15} {row['collection_name']:<35} {pos:<10} {primary:<8}")

    def list_collection_works(self, collection_id: int):
        """List all works in a collection"""
        self.cursor.execute("""
            SELECT
                w.work_id,
                w.work_name,
                w.work_name_tamil,
                wc.position_in_collection,
                wc.is_primary
            FROM work_collections wc
            JOIN works w ON wc.work_id = w.work_id
            WHERE wc.collection_id = %s
            ORDER BY wc.position_in_collection NULLS LAST, w.work_name
        """, (collection_id,))

        results = self.cursor.fetchall()

        # Get collection name
        self.cursor.execute("SELECT collection_name, collection_name_tamil FROM collections WHERE collection_id = %s", (collection_id,))
        coll = self.cursor.fetchone()

        print("\n" + "="*80)
        print(f"WORKS IN: {coll['collection_name']} ({coll['collection_name_tamil']})")
        print("="*80)
        print(f"{'Position':<10} {'Work ID':<10} {'Name':<40} {'Primary':<8}")
        print("-"*80)

        if not results:
            print("  (No works assigned)")
        else:
            for row in results:
                pos = str(row['position_in_collection']) if row['position_in_collection'] else '-'
                primary = '✓' if row['is_primary'] else ''
                print(f"{pos:<10} {row['work_id']:<10} {row['work_name']:<40} {primary:<8}")

    def assign_work_to_collection(self, work_id: int, collection_id: int, position: Optional[int] = None, is_primary: bool = False):
        """Assign a work to a collection"""
        try:
            self.cursor.execute("""
                INSERT INTO work_collections (work_id, collection_id, position_in_collection, is_primary)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (work_id, collection_id)
                DO UPDATE SET
                    position_in_collection = EXCLUDED.position_in_collection,
                    is_primary = EXCLUDED.is_primary
            """, (work_id, collection_id, position, is_primary))

            # If this is primary, unset other primary flags for this work
            if is_primary:
                self.cursor.execute("""
                    UPDATE work_collections
                    SET is_primary = FALSE
                    WHERE work_id = %s AND collection_id != %s
                """, (work_id, collection_id))

            self.conn.commit()
            print(f"✓ Assigned work {work_id} to collection {collection_id}" +
                  (f" at position {position}" if position else "") +
                  (" (PRIMARY)" if is_primary else ""))
        except Exception as e:
            self.conn.rollback()
            print(f"✗ Error: {e}")

    def remove_work_from_collection(self, work_id: int, collection_id: int):
        """Remove a work from a collection"""
        try:
            self.cursor.execute("""
                DELETE FROM work_collections
                WHERE work_id = %s AND collection_id = %s
            """, (work_id, collection_id))

            self.conn.commit()
            print(f"✓ Removed work {work_id} from collection {collection_id}")
        except Exception as e:
            self.conn.rollback()
            print(f"✗ Error: {e}")

    def set_primary_collection(self, work_id: int, collection_id: int):
        """Set primary collection for a work"""
        try:
            # Unset all primary flags for this work
            self.cursor.execute("""
                UPDATE work_collections
                SET is_primary = FALSE
                WHERE work_id = %s
            """, (work_id,))

            # Set the new primary
            self.cursor.execute("""
                UPDATE work_collections
                SET is_primary = TRUE
                WHERE work_id = %s AND collection_id = %s
            """, (work_id, collection_id))

            # Also update works.primary_collection_id
            self.cursor.execute("""
                UPDATE works
                SET primary_collection_id = %s
                WHERE work_id = %s
            """, (collection_id, work_id))

            self.conn.commit()
            print(f"✓ Set collection {collection_id} as primary for work {work_id}")
        except Exception as e:
            self.conn.rollback()
            print(f"✗ Error: {e}")

    def reorder_collection(self, collection_id: int):
        """Interactive reordering of works in a collection"""
        self.cursor.execute("""
            SELECT w.work_id, w.work_name, wc.position_in_collection
            FROM work_collections wc
            JOIN works w ON wc.work_id = w.work_id
            WHERE wc.collection_id = %s
            ORDER BY wc.position_in_collection NULLS LAST, w.work_name
        """, (collection_id,))

        works = self.cursor.fetchall()

        if not works:
            print("No works in this collection")
            return

        print("\nCurrent order:")
        for i, work in enumerate(works, 1):
            pos = work['position_in_collection'] if work['position_in_collection'] else '?'
            print(f"{i}. [{pos}] {work['work_name']}")

        print("\nEnter new positions (comma-separated), or press Enter to keep current:")
        new_order = input("> ").strip()

        if not new_order:
            print("Cancelled")
            return

        try:
            positions = [int(x.strip()) for x in new_order.split(',')]
            if len(positions) != len(works):
                print(f"Error: Expected {len(works)} positions, got {len(positions)}")
                return

            for work, new_pos in zip(works, positions):
                self.cursor.execute("""
                    UPDATE work_collections
                    SET position_in_collection = %s
                    WHERE work_id = %s AND collection_id = %s
                """, (new_pos, work['work_id'], collection_id))

            self.conn.commit()
            print("✓ Reordered successfully")
            self.list_collection_works(collection_id)
        except Exception as e:
            self.conn.rollback()
            print(f"✗ Error: {e}")

    def close(self):
        """Close database connection"""
        self.cursor.close()
        self.conn.close()


def print_help():
    """Print usage help"""
    print("""
Collection Management Utility

Usage: python manage_collections.py <command> [options]

Commands:
  list-collections [type]           List all collections (optionally filter by type)
  list-works [--unassigned]         List all works
  list-work-collections <work_id>   List collections for a work
  list-collection-works <coll_id>   List works in a collection

  assign <work_id> <coll_id> [pos] [--primary]   Assign work to collection
  remove <work_id> <coll_id>                     Remove work from collection
  set-primary <work_id> <coll_id>                Set primary collection for work
  reorder <coll_id>                              Interactively reorder works in collection

Examples:
  python manage_collections.py list-collections period
  python manage_collections.py list-works --unassigned
  python manage_collections.py assign 20 100 20 --primary
  python manage_collections.py list-collection-works 100
  python manage_collections.py reorder 100

Environment:
  DATABASE_URL  Database connection string (default: localhost)
""")


def main():
    if len(sys.argv) < 2 or sys.argv[1] in ['-h', '--help', 'help']:
        print_help()
        return

    # Get database URL
    db_url = os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@localhost/tamil_literature')

    manager = CollectionManager(db_url)

    try:
        command = sys.argv[1]

        if command == 'list-collections':
            coll_type = sys.argv[2] if len(sys.argv) > 2 else None
            manager.list_collections(coll_type)

        elif command == 'list-works':
            unassigned = '--unassigned' in sys.argv
            manager.list_works(unassigned)

        elif command == 'list-work-collections':
            work_id = int(sys.argv[2])
            manager.list_work_collections(work_id)

        elif command == 'list-collection-works':
            coll_id = int(sys.argv[2])
            manager.list_collection_works(coll_id)

        elif command == 'assign':
            work_id = int(sys.argv[2])
            coll_id = int(sys.argv[3])
            position = int(sys.argv[4]) if len(sys.argv) > 4 and sys.argv[4] != '--primary' else None
            is_primary = '--primary' in sys.argv
            manager.assign_work_to_collection(work_id, coll_id, position, is_primary)

        elif command == 'remove':
            work_id = int(sys.argv[2])
            coll_id = int(sys.argv[3])
            manager.remove_work_from_collection(work_id, coll_id)

        elif command == 'set-primary':
            work_id = int(sys.argv[2])
            coll_id = int(sys.argv[3])
            manager.set_primary_collection(work_id, coll_id)

        elif command == 'reorder':
            coll_id = int(sys.argv[2])
            manager.reorder_collection(coll_id)

        else:
            print(f"Unknown command: {command}")
            print_help()

    finally:
        manager.close()


if __name__ == '__main__':
    main()
