# Parser ID Allocation Patterns - Deep Dive Guide

## Table of Contents
1. [Why This Matters](#why-this-matters)
2. [Understanding the Schema Design](#understanding-the-schema-design)
3. [The Five Critical Patterns](#the-five-critical-patterns)
4. [Common Pitfalls and Solutions](#common-pitfalls-and-solutions)
5. [Code Examples](#code-examples)

---

## Why This Matters

### The Problem We're Solving

You have a database with 5 major literary works. Each work contains:
- Thousands of verses
- Tens of thousands of lines
- Hundreds of thousands of words

Each of these items needs a **unique ID** across ALL works. For example:
- Thirukkural has 1,330 verses → uses verse_id 1-1330
- Tolkappiyam has ~1,600 verses → must use verse_id 1331-2930 (NOT 1-1600!)
- Sangam has ~2,300 verses → must use verse_id 2931-5230 (NOT 1-2300!)

**If parsers don't coordinate IDs, they'll try to reuse the same IDs and crash.**

### Real-World Scenario

```
Scenario: You run parsers in this order:
1. Tolkappiyam imports → creates section_id 1-50
2. Thirukkural imports → tries to create section_id 1-145 ← CRASH! IDs 1-50 already exist!

Error: "duplicate key value violates unique constraint sections_pkey"
```

---

## Understanding the Schema Design

### Key Insight: No Auto-Increment Sequences

Look at the schema (sql/schema.sql):

```sql
CREATE TABLE works (
    work_id INTEGER PRIMARY KEY,  -- ← Just INTEGER, not SERIAL!
    work_name VARCHAR(200) NOT NULL,
    ...
);

CREATE TABLE sections (
    section_id INTEGER PRIMARY KEY,  -- ← Just INTEGER, not SERIAL!
    work_id INTEGER NOT NULL,
    ...
);
```

**What this means:**
- `INTEGER PRIMARY KEY` = PostgreSQL will NOT auto-generate IDs
- `SERIAL PRIMARY KEY` (not used) = PostgreSQL would auto-generate IDs
- **We chose INTEGER** because we use bulk COPY, which requires explicit IDs

### Why Bulk COPY Requires Explicit IDs

The 2-phase import pattern uses PostgreSQL's COPY command:

```python
# Phase 1: Build data in memory
self.sections = [
    {'section_id': 1, 'work_id': 1, 'section_name': 'Paal 1', ...},
    {'section_id': 2, 'work_id': 1, 'section_name': 'Paal 2', ...},
    # ... 1000s more rows ...
]

# Phase 2: Bulk insert with COPY
buffer = io.StringIO()
writer = csv.writer(buffer, delimiter='\t')
for row in self.sections:
    writer.writerow([row['section_id'], row['work_id'], ...])
buffer.seek(0)
cursor.copy_from(buffer, 'sections', columns=['section_id', 'work_id', ...])
```

**COPY requires you to provide section_id values explicitly** - it doesn't use sequences.

This is 1000x faster than:
```python
# Slow way: row-by-row INSERT (uses auto-increment)
for section in sections:
    cursor.execute("INSERT INTO sections (work_id, section_name, ...) VALUES (%s, %s, ...)")
```

---

## The Five Critical Patterns

### Pattern 1: Query MAX IDs at Initialization

**Rule:** ALWAYS query the database for current MAX IDs before starting to parse.

**Bad Code (hardcoded to 1):**
```python
class ThirukkuralBulkImporter:
    def __init__(self, db_connection_string: str):
        self.conn = psycopg2.connect(db_connection_string)
        self.cursor = self.conn.cursor()

        # ❌ WRONG: Hardcoded to 1
        self.section_id = 1
        self.verse_id = 1
        self.line_id = 1
        self.word_id = 1
```

**Why it fails:**
- First parser to run: Works fine (database is empty, so starting at 1 is correct)
- Second parser to run: CRASHES (IDs 1, 2, 3... already exist from first parser!)

**Good Code (queries MAX):**
```python
class ThirukkuralBulkImporter:
    def __init__(self, db_connection_string: str):
        self.conn = psycopg2.connect(db_connection_string)
        self.cursor = self.conn.cursor()

        # ✅ CORRECT: Query database for current MAX
        self.cursor.execute("SELECT COALESCE(MAX(section_id), 0) FROM sections")
        self.section_id = self.cursor.fetchone()[0] + 1

        self.cursor.execute("SELECT COALESCE(MAX(verse_id), 0) FROM verses")
        self.verse_id = self.cursor.fetchone()[0] + 1

        self.cursor.execute("SELECT COALESCE(MAX(line_id), 0) FROM lines")
        self.line_id = self.cursor.fetchone()[0] + 1

        self.cursor.execute("SELECT COALESCE(MAX(word_id), 0) FROM words")
        self.word_id = self.cursor.fetchone()[0] + 1

        print(f"Starting IDs: section={self.section_id}, verse={self.verse_id}")
```

**Why it works:**
- Empty database: `MAX(section_id)` returns NULL → `COALESCE(NULL, 0)` = 0 → start at 1
- After Tolkappiyam: `MAX(section_id)` = 50 → start at 51
- After Thirukkural: `MAX(section_id)` = 195 → start at 196

**COALESCE explained:**
```sql
SELECT COALESCE(MAX(section_id), 0) FROM sections;

-- If table is empty: MAX returns NULL → COALESCE returns 0
-- If table has data: MAX returns highest ID → COALESCE returns that ID
```

---

### Pattern 2: NEVER Hardcode IDs to 1

**Rule:** Parsers must work when run in ANY order.

**Test Scenarios:**
```bash
# Scenario A: Parser runs first
python thirukkural_bulk_import.py  # Should work (starts at ID 1)

# Scenario B: Parser runs after others
python tolkappiyam_bulk_import.py   # Creates IDs 1-50
python thirukkural_bulk_import.py   # Should work (starts at ID 51, NOT 1!)

# Scenario C: Parser runs multiple times
python thirukkural_bulk_import.py   # First run: IDs 1-145
# ... delete Thirukkural data only ...
python thirukkural_bulk_import.py   # Second run: Should still work!
```

**Implementation:**
Every parser's `__init__()` should look like this:
```python
def __init__(self, db_connection_string: str):
    self.conn = psycopg2.connect(db_connection_string)
    self.cursor = self.conn.cursor()

    # Query ALL table IDs
    self.cursor.execute("SELECT COALESCE(MAX(section_id), 0) FROM sections")
    self.section_id = self.cursor.fetchone()[0] + 1

    # ... repeat for ALL tables: verses, lines, words ...
```

---

### Pattern 3: Multiple Works in One Script - Query Once, Increment Manually

**Rule:** When a single parser creates multiple works, query MAX work_id ONCE, then increment manually.

**Context:** Sangam parser imports 18 separate works (Kuruntokai, Natrinai, etc.)

**Bad Code (queries inside loop):**
```python
def _ensure_works_exist(self):
    for filename, work_info in self.SANGAM_WORKS.items():  # 18 works
        work_name = work_info['work_name']

        # Check if exists
        self.cursor.execute("SELECT work_id FROM works WHERE work_name = %s", (work_name,))
        existing = self.cursor.fetchone()

        if not existing:
            # ❌ WRONG: Query MAX inside loop
            self.cursor.execute("SELECT COALESCE(MAX(work_id), 0) + 1 FROM works")
            new_work_id = self.cursor.fetchone()[0]

            work_info['work_id'] = new_work_id
            self.works.append({'work_id': new_work_id, ...})
```

**Why it fails:**
```
Before loop: MAX(work_id) = 2 (Tolkappiyam and Thirukkural exist)

Iteration 1 (Kuruntokai):
  - Query: "SELECT MAX(work_id) + 1" → returns 3
  - Assigns work_id = 3 ✓
  - Appends to self.works (not yet in database!)

Iteration 2 (Natrinai):
  - Query: "SELECT MAX(work_id) + 1" → returns 3 (still!)
  - Assigns work_id = 3 ❌ DUPLICATE!

Iteration 3-18: All get work_id = 3 ❌

Later: Bulk COPY tries to insert 18 works all with work_id=3 → CRASH!
```

**Good Code (query once, increment manually):**
```python
def _ensure_works_exist(self):
    # ✅ CORRECT: Query MAX ONCE before loop
    self.cursor.execute("SELECT COALESCE(MAX(work_id), 0) FROM works")
    next_work_id = self.cursor.fetchone()[0] + 1

    for filename, work_info in self.SANGAM_WORKS.items():  # 18 works
        work_name = work_info['work_name']

        # Check if exists
        self.cursor.execute("SELECT work_id FROM works WHERE work_name = %s", (work_name,))
        existing = self.cursor.fetchone()

        if existing:
            work_info['work_id'] = existing[0]
        else:
            # ✅ Use and increment manually
            work_info['work_id'] = next_work_id
            self.works.append({'work_id': next_work_id, ...})
            next_work_id += 1  # ← KEY: Increment for next work
```

**Why it works:**
```
Before loop: MAX(work_id) = 2, next_work_id = 3

Iteration 1 (Kuruntokai):   work_id = 3,  next_work_id becomes 4
Iteration 2 (Natrinai):     work_id = 4,  next_work_id becomes 5
Iteration 3 (Ainkurunuru):  work_id = 5,  next_work_id becomes 6
...
Iteration 18:               work_id = 20, next_work_id becomes 21

Result: 18 unique work_ids (3-20) ✓
```

---

### Pattern 4: Schema Has No Auto-Sequences

**Rule:** Understand that the schema requires manual ID management.

**Comparison:**

| Feature | With SERIAL | With INTEGER (Our Schema) |
|---------|-------------|---------------------------|
| Definition | `work_id SERIAL PRIMARY KEY` | `work_id INTEGER PRIMARY KEY` |
| Auto-generates IDs? | Yes | No |
| Requires explicit ID in INSERT? | No | Yes |
| Requires explicit ID in COPY? | No | Yes |
| Who manages IDs? | PostgreSQL | Parser scripts |
| Performance with COPY | Slower (sequence locks) | Faster (no sequence) |

**Why we use INTEGER:**
1. **Bulk COPY performance**: Avoids sequence lock contention
2. **Explicit control**: Parser knows exactly what IDs it's using
3. **Pre-allocation**: Can allocate ID ranges before parsing (Phase 1)

**Implications:**
- Parsers MUST calculate IDs manually
- Parsers MUST coordinate IDs across runs
- Parsers MUST query MAX to avoid collisions

---

### Pattern 5: Drop Sequences When Resetting

**Rule:** The setup script must clean up sequences when dropping tables.

**Context:** Even though we use INTEGER (not SERIAL), old sequences might exist from:
- Previous schema versions that used SERIAL
- Manual sequence creation
- PostgreSQL auto-creating sequences in some edge cases

**Bad Code:**
```python
def drop_tables(connection_string):
    conn = psycopg2.connect(connection_string)
    cursor = conn.cursor()

    # ❌ Only drops tables, not sequences
    cursor.execute("""
        DROP TABLE IF EXISTS words CASCADE;
        DROP TABLE IF EXISTS lines CASCADE;
        DROP TABLE IF EXISTS verses CASCADE;
        DROP TABLE IF EXISTS sections CASCADE;
        DROP TABLE IF EXISTS works CASCADE;
    """)

    conn.commit()
```

**Good Code:**
```python
def drop_tables(connection_string):
    conn = psycopg2.connect(connection_string)
    cursor = conn.cursor()

    # Drop tables
    cursor.execute("""
        DROP TABLE IF EXISTS words CASCADE;
        DROP TABLE IF EXISTS lines CASCADE;
        DROP TABLE IF EXISTS verses CASCADE;
        DROP TABLE IF EXISTS sections CASCADE;
        DROP TABLE IF EXISTS works CASCADE;
    """)

    # ✅ Also drop sequences (if they exist)
    cursor.execute("""
        DROP SEQUENCE IF EXISTS works_work_id_seq CASCADE;
        DROP SEQUENCE IF EXISTS sections_section_id_seq CASCADE;
        DROP SEQUENCE IF EXISTS verses_verse_id_seq CASCADE;
        DROP SEQUENCE IF EXISTS lines_line_id_seq CASCADE;
        DROP SEQUENCE IF EXISTS words_word_id_seq CASCADE;
    """)

    conn.commit()
```

**Why it matters:**
- Ensures a truly clean slate when resetting the database
- Prevents ghost sequences from interfering with new data
- Makes the reset operation idempotent (can run multiple times safely)

---

## Common Pitfalls and Solutions

### Pitfall 1: "It works on empty database, so it's fine"

**Mistake:** Testing parser only on empty database.

```bash
# ❌ Incomplete testing
python setup_railway_db.py        # Empty database
python thirukkural_bulk_import.py  # Works! ✓
# Developer thinks: "Great, it works!"
```

**Problem:** Parser breaks when run after other works exist.

**Solution:** Always test parsers in multiple scenarios:

```bash
# ✅ Complete testing
# Test 1: Empty database
python setup_railway_db.py
python thirukkural_bulk_import.py  # Should work

# Test 2: After another work
python setup_railway_db.py
python tolkappiyam_bulk_import.py  # Run different work first
python thirukkural_bulk_import.py  # Should still work

# Test 3: Different orders
python setup_railway_db.py
python thirukkural_bulk_import.py
python tolkappiyam_bulk_import.py
python sangam_bulk_import.py       # Should all work
```

---

### Pitfall 2: Querying MAX in wrong place

**Mistake:** Querying MAX IDs in a method that might not be called, or called too late.

```python
class BadImporter:
    def __init__(self, db_connection_string):
        self.conn = psycopg2.connect(db_connection_string)
        self.cursor = self.conn.cursor()

        # ❌ Hardcoded here
        self.section_id = 1
        self.verse_id = 1

    def _ensure_work_exists(self):
        # ... later, queries MAX and updates IDs ...
        # ❌ But parsing might happen before this is called!
        self.cursor.execute("SELECT COALESCE(MAX(section_id), 0) FROM sections")
        self.section_id = self.cursor.fetchone()[0] + 1
```

**Problem:** If `parse_file()` is called before `_ensure_work_exists()`, it uses hardcoded ID=1.

**Solution:** Query MAX IDs in `__init__()` or ensure setup method is always called first:

```python
class GoodImporter:
    def __init__(self, db_connection_string):
        self.conn = psycopg2.connect(db_connection_string)
        self.cursor = self.conn.cursor()

        # ✅ Query MAX immediately in __init__
        self.cursor.execute("SELECT COALESCE(MAX(section_id), 0) FROM sections")
        self.section_id = self.cursor.fetchone()[0] + 1
```

Or:

```python
class AlsoGoodImporter:
    def __init__(self, db_connection_string):
        self.conn = psycopg2.connect(db_connection_string)
        self.cursor = self.conn.cursor()

        # IDs will be set in _ensure_work_exists
        self.section_id = None  # ← Explicitly None, not 1

    def _ensure_work_exists(self):
        # ✅ Query MAX here
        self.cursor.execute("SELECT COALESCE(MAX(section_id), 0) FROM sections")
        self.section_id = self.cursor.fetchone()[0] + 1

    def import_work(self):
        # ✅ ALWAYS call setup first
        self._ensure_work_exists()  # ← Guarantees IDs are set
        self.parse_files()
```

---

### Pitfall 3: Forgetting to query ALL tables

**Mistake:** Querying MAX for some tables but not others.

```python
# ❌ Incomplete
self.cursor.execute("SELECT COALESCE(MAX(section_id), 0) FROM sections")
self.section_id = self.cursor.fetchone()[0] + 1

self.cursor.execute("SELECT COALESCE(MAX(verse_id), 0) FROM verses")
self.verse_id = self.cursor.fetchone()[0] + 1

# Forgot lines and words!
self.line_id = 1      # ❌ Hardcoded
self.word_id = 1      # ❌ Hardcoded
```

**Problem:** Parser works for sections and verses, but crashes on lines/words.

**Solution:** Query MAX for EVERY table you insert into:

```python
# ✅ Complete
self.cursor.execute("SELECT COALESCE(MAX(section_id), 0) FROM sections")
self.section_id = self.cursor.fetchone()[0] + 1

self.cursor.execute("SELECT COALESCE(MAX(verse_id), 0) FROM verses")
self.verse_id = self.cursor.fetchone()[0] + 1

self.cursor.execute("SELECT COALESCE(MAX(line_id), 0) FROM lines")
self.line_id = self.cursor.fetchone()[0] + 1

self.cursor.execute("SELECT COALESCE(MAX(word_id), 0) FROM words")
self.word_id = self.cursor.fetchone()[0] + 1
```

---

## Code Examples

### Example 1: Simple Single-Work Parser (Thirukkural)

```python
class ThirukkuralBulkImporter:
    def __init__(self, db_connection_string: str):
        self.conn = psycopg2.connect(db_connection_string)
        self.cursor = self.conn.cursor()

        # ✅ Query MAX IDs for all tables
        self.cursor.execute("SELECT COALESCE(MAX(section_id), 0) FROM sections")
        self.section_id = self.cursor.fetchone()[0] + 1

        self.cursor.execute("SELECT COALESCE(MAX(verse_id), 0) FROM verses")
        self.verse_id = self.cursor.fetchone()[0] + 1

        self.cursor.execute("SELECT COALESCE(MAX(line_id), 0) FROM lines")
        self.line_id = self.cursor.fetchone()[0] + 1

        self.cursor.execute("SELECT COALESCE(MAX(word_id), 0) FROM words")
        self.word_id = self.cursor.fetchone()[0] + 1

        print(f"Starting IDs: section={self.section_id}, verse={self.verse_id}, "
              f"line={self.line_id}, word={self.word_id}")

        # Data containers
        self.sections = []
        self.verses = []
        self.lines = []
        self.words = []
        self.work_id = None

    def _ensure_work_exists(self):
        """Create Thirukkural work if it doesn't exist"""
        # Check if work exists
        self.cursor.execute("SELECT work_id FROM works WHERE work_name = 'Thirukkural'")
        existing = self.cursor.fetchone()

        if existing:
            self.work_id = existing[0]
        else:
            # Get next work_id
            self.cursor.execute("SELECT COALESCE(MAX(work_id), 0) + 1 FROM works")
            self.work_id = self.cursor.fetchone()[0]

            # Insert work
            self.cursor.execute("""
                INSERT INTO works (work_id, work_name, work_name_tamil, ...)
                VALUES (%s, 'Thirukkural', 'திருக்குறள்', ...)
            """, (self.work_id,))
            self.conn.commit()

    def parse_kurals(self):
        """Phase 1: Parse kurals into memory"""
        for kural_num in range(1, 1331):
            # Create verse
            verse_id = self.verse_id
            self.verse_id += 1  # ✅ Increment counter

            self.verses.append({
                'verse_id': verse_id,
                'work_id': self.work_id,
                'verse_number': kural_num,
                ...
            })

            # Create 2 lines per kural
            for line_num in [1, 2]:
                line_id = self.line_id
                self.line_id += 1  # ✅ Increment counter

                self.lines.append({
                    'line_id': line_id,
                    'verse_id': verse_id,
                    'line_number': line_num,
                    ...
                })

                # Parse words in line
                for word_text in line_words:
                    word_id = self.word_id
                    self.word_id += 1  # ✅ Increment counter

                    self.words.append({
                        'word_id': word_id,
                        'line_id': line_id,
                        'word_text': word_text,
                        ...
                    })

    def bulk_insert(self):
        """Phase 2: Bulk COPY into database"""
        # Insert all data using COPY
        self._bulk_copy('sections', self.sections, [...])
        self._bulk_copy('verses', self.verses, [...])
        self._bulk_copy('lines', self.lines, [...])
        self._bulk_copy('words', self.words, [...])
        self.conn.commit()
```

---

### Example 2: Multi-Work Parser (Sangam - 18 works)

```python
class SangamBulkImporter:
    SANGAM_WORKS = {
        'குறுந்தொகை.txt': {'work_name': 'Kuruntokai', ...},
        'நற்றிணை.txt': {'work_name': 'Natrinai', ...},
        # ... 16 more works ...
    }

    def __init__(self, db_connection_string: str):
        self.conn = psycopg2.connect(db_connection_string)
        self.cursor = self.conn.cursor()

        # ✅ Query MAX IDs for sections, verses, lines, words
        self.cursor.execute("SELECT COALESCE(MAX(section_id), 0) FROM sections")
        self.section_id = self.cursor.fetchone()[0] + 1

        self.cursor.execute("SELECT COALESCE(MAX(verse_id), 0) FROM verses")
        self.verse_id = self.cursor.fetchone()[0] + 1

        self.cursor.execute("SELECT COALESCE(MAX(line_id), 0) FROM lines")
        self.line_id = self.cursor.fetchone()[0] + 1

        self.cursor.execute("SELECT COALESCE(MAX(word_id), 0) FROM words")
        self.word_id = self.cursor.fetchone()[0] + 1

        # Data containers
        self.works = []
        self.sections = []
        self.verses = []
        self.lines = []
        self.words = []

    def _ensure_works_exist(self):
        """Create all 18 Sangam work entries"""
        # ✅ Query MAX work_id ONCE before loop
        self.cursor.execute("SELECT COALESCE(MAX(work_id), 0) FROM works")
        next_work_id = self.cursor.fetchone()[0] + 1

        for filename, work_info in self.SANGAM_WORKS.items():
            # Check if work already exists
            self.cursor.execute("SELECT work_id FROM works WHERE work_name = %s",
                              (work_info['work_name'],))
            existing = self.cursor.fetchone()

            if existing:
                work_info['work_id'] = existing[0]
            else:
                # ✅ Assign next_work_id and increment
                work_info['work_id'] = next_work_id

                self.works.append({
                    'work_id': next_work_id,
                    'work_name': work_info['work_name'],
                    ...
                })

                next_work_id += 1  # ✅ Increment for next work

        # Bulk insert new works
        if self.works:
            self._bulk_copy('works', self.works, [...])
            self.conn.commit()

    def parse_all_works(self):
        """Parse all 18 Sangam works"""
        for filename, work_info in self.SANGAM_WORKS.items():
            work_id = work_info['work_id']

            # Parse this work's poems
            for poem in parse_file(filename):
                # ✅ Use shared counters that keep incrementing
                verse_id = self.verse_id
                self.verse_id += 1

                self.verses.append({
                    'verse_id': verse_id,
                    'work_id': work_id,  # ← Each work has its own work_id
                    ...
                })

                # ... continue with lines and words ...
```

---

## Summary Checklist

When creating a new parser, ensure:

- [ ] Query `MAX(section_id)` in `__init__()` or before parsing
- [ ] Query `MAX(verse_id)` in `__init__()` or before parsing
- [ ] Query `MAX(line_id)` in `__init__()` or before parsing
- [ ] Query `MAX(word_id)` in `__init__()` or before parsing
- [ ] NEVER hardcode any ID to start at 1
- [ ] For work_id: If single work, query MAX; if multiple works, query once and increment manually
- [ ] Test parser on empty database
- [ ] Test parser after other works have been imported
- [ ] Test parser in different execution orders
- [ ] Verify no duplicate key errors occur

**Remember:** The goal is for parsers to work in ANY order, ANY number of times!
