# Thiruvasagam Parser Bug Fix

## Problem

**Current State:**
- Work ID 51 (Thiruvasagam): 3,438 verses with 1 line each
- Every line is being stored as a separate verse

**Expected:**
- Verses should have 10-20 lines each
- Verses are separated by blank lines in the source file

## Root Cause

`parse_thiruvasagam()` lines 289-300:

```python
# Regular line - if we have a section, accumulate lines
if current_section_id:
    cleaned = line.replace('…', '').strip()
    # Check if this looks like a verse line (contains Tamil text)
    if cleaned and re.search(r'[\u0B80-\u0BFF]', cleaned):
        # For continuous verses, treat each line as a new verse  ← WRONG!
        if not verse_count or len(current_verse_lines) > 0:
            if current_verse_lines:
                self._add_verse(work_id, current_section_id, verse_count, current_verse_lines)
                current_verse_lines = []
            verse_count += 1
        current_verse_lines.append(cleaned)
```

**Bug:** Creates a verse after EVERY line instead of accumulating lines until a blank line.

## Solution

Replace lines 289-300 with:

```python
# Regular line - if we have a section, accumulate lines
if current_section_id:
    # Skip line numbers (multiples of 5: 5, 10, 15, etc.)
    if re.match(r'^\d+$', line.strip()):
        continue

    cleaned = line.replace('…', '').strip()

    # Check if this is a blank line (verse boundary)
    if not cleaned:
        # Save accumulated verse if any
        if current_verse_lines:
            verse_count += 1
            self._add_verse(work_id, current_section_id, verse_count, current_verse_lines)
            current_verse_lines = []
        continue

    # Regular verse line - accumulate
    if re.search(r'[\u0B80-\u0BFF]', cleaned):
        current_verse_lines.append(cleaned)
```

## Full Corrected Method

```python
def parse_thiruvasagam(self, file_path, file_num):
    """
    Parse Thiruvasagam (File 8.1)
    Structure: @ sections → continuous verses separated by blank lines
    """
    print(f"\nParsing File {file_num}: {Path(file_path).name}")

    with open(file_path, 'r', encoding='utf-8') as f:
        lines_text = f.readlines()

    work_name_tamil = "திருவாசகம் - எட்டாம் திருமுறை"
    work_id = self._create_work(
        work_name=work_name_tamil,
        work_name_tamil=work_name_tamil,
        author="Manikkavasagar",
        author_tamil="மாணிக்கவாசகர்",
        canonical_order=328,
        period='9th century CE'
    )

    if not work_id:
        return

    self.current_work_id = work_id
    current_section_id = None
    current_verse_lines = []
    verse_count = 0

    for line in lines_text[1:]:
        line = line.strip()

        # Skip separators
        if line == 'மேல்' or line.startswith('**'):
            continue

        # Check for @ section marker
        section_match = re.match(r'^@(\d+)\s+(.+)', line)
        if section_match:
            # Save last verse from previous section
            if current_verse_lines:
                verse_count += 1
                self._add_verse(work_id, current_section_id, verse_count, current_verse_lines)
                current_verse_lines = []

            section_num = int(section_match.group(1))
            section_name = section_match.group(2).strip()
            current_section_id = self._get_or_create_section(
                work_id, None, 'Pathigam', 'பதிகம்', section_num, section_name
            )
            verse_count = 0
            continue

        # Skip standalone line numbers (5, 10, 15, etc.)
        if re.match(r'^\d+$', line):
            continue

        # Regular verse content
        if current_section_id:
            # Remove line numbers from end (e.g., "text		5" → "text")
            cleaned = re.sub(r'\s+\d+\s*$', '', line)
            cleaned = cleaned.replace('…', '').strip()

            # Blank line = verse boundary
            if not cleaned:
                if current_verse_lines:
                    verse_count += 1
                    self._add_verse(work_id, current_section_id, verse_count, current_verse_lines)
                    current_verse_lines = []
                continue

            # Accumulate Tamil text lines
            if re.search(r'[\u0B80-\u0BFF]', cleaned):
                current_verse_lines.append(cleaned)

    # Save last verse
    if current_verse_lines:
        verse_count += 1
        self._add_verse(work_id, current_section_id, verse_count, current_verse_lines)

    print(f"  [OK] Parsed {len([v for v in self.verses if v['work_id'] == work_id])} verses")
```

## Expected Result After Fix

- **Before:** 3,438 verses × 1 line = 3,438 lines
- **After:** ~200-350 verses × 10-20 lines = 3,438 lines

Verse structure will match other Devaram works (avg 4-20 lines per verse).

## To Apply Fix

1. Edit `scripts/thirumurai_bulk_import.py`
2. Replace `parse_thiruvasagam()` method (lines 232-305)
3. Delete work_id 51 from database:
   ```sql
   DELETE FROM works WHERE work_id = 51;
   ```
4. Re-run parser:
   ```bash
   python scripts/thirumurai_bulk_import.py
   ```

## Verification Query

```sql
SELECT
    v.work_id,
    w.work_name_tamil,
    MIN(v.total_lines) as min_lines,
    MAX(v.total_lines) as max_lines,
    AVG(v.total_lines) as avg_lines,
    COUNT(*) as verse_count
FROM verses v
JOIN works w ON v.work_id = w.work_id
WHERE v.work_id = 51
GROUP BY v.work_id, w.work_name_tamil;

-- Expected result:
-- min_lines: ~4-10
-- max_lines: ~15-25
-- avg_lines: ~10-15
-- verse_count: ~200-350 (NOT 3438!)
```
