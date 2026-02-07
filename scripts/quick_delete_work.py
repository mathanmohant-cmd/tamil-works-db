#!/usr/bin/env python3
import psycopg2
import sys

work_id = int(sys.argv[1]) if len(sys.argv) > 1 else 22

conn = psycopg2.connect("postgresql://postgres:postgres@localhost/tamil_literature")
cursor = conn.cursor()

print(f"Deleting work ID {work_id}...")
cursor.execute("DELETE FROM words WHERE line_id IN (SELECT l.line_id FROM lines l JOIN verses v ON l.verse_id = v.verse_id WHERE v.work_id = %s)", (work_id,))
print(f"  Deleted {cursor.rowcount} words")

cursor.execute("DELETE FROM lines WHERE verse_id IN (SELECT verse_id FROM verses WHERE work_id = %s)", (work_id,))
print(f"  Deleted {cursor.rowcount} lines")

cursor.execute("DELETE FROM verses WHERE work_id = %s", (work_id,))
print(f"  Deleted {cursor.rowcount} verses")

cursor.execute("DELETE FROM sections WHERE work_id = %s", (work_id,))
print(f"  Deleted {cursor.rowcount} sections")

cursor.execute("DELETE FROM work_collections WHERE work_id = %s", (work_id,))
print(f"  Deleted {cursor.rowcount} work_collections")

cursor.execute("DELETE FROM works WHERE work_id = %s", (work_id,))
print(f"  Deleted {cursor.rowcount} works")

conn.commit()
print("Done!")
conn.close()
