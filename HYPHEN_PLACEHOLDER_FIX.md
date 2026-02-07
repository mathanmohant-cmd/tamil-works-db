# Hyphen Placeholder Fix (2026-02-02)

## Issue

Lost or corrupted words in Tamil literary texts are marked with sequences of hyphens (e.g., `---`, `--------`, `----------------`). These placeholder markers were being tokenized as words in the database, creating meaningless word entries.

**Affected works:**
- புறநானூறு (Purananuru) - Example: Verse 341, Line 6
- பரிபாடல் (Paripaadal) - Multiple verses with mixed content

## Root Cause

In `scripts/sangam_bulk_import.py`, the `_add_poem()` method at line 1083-1084 only checked for single hyphens:

```python
if cleaned_line.strip() == '-':
    continue  # Skip word parsing
```

This missed sequences like:
- `----------------` (16 hyphens)
- `----------` (10 hyphens)
- `-------------` (13 hyphens)

## Solution

Added a regex check at line 1096-1100 to skip **any** token that contains only hyphens:

```python
# Skip tokens that are ONLY hyphens (lost word placeholders)
# Examples: "---", "--------", "----------------"
# These mark lost/corrupted text and should not be tokenized
if re.match(r'^-+$', token):
    continue
```

This pattern matches one or more hyphens (`-+`) from start to end (`^...$`).

## Behavior After Fix

**Line text preservation:**
- Lines with hyphen placeholders are still stored in the `lines` table
- Preserves scholarly context showing where text is lost

**Word tokenization:**
- Tokens that are ONLY hyphens are skipped (not added to `words` table)
- Tamil words on the same line are still tokenized normally
- Legitimate uses of hyphens in compound words are preserved (e.g., `வான்-நிலா`)

## Examples

### Purananuru 341, Line 6
**Source file:**
```
---------------- ------------- --------------
```

**Database:**
- ✓ Line stored: `"---------------- ------------- --------------"`
- ✓ Words created: **0** (none - all are hyphen placeholders)

### Paripaadal with Mixed Content
**Source file:**
```
---------- ------------ மரபினோய் நின் அடி
```

**Database:**
- ✓ Line stored: `"---------- ------------ மரபினோய் நின் அடி"`
- ✓ Words created: **3** (only `மரபினோய்`, `நின்`, `அடி`)
- ✓ Hyphen sequences skipped: `----------`, `------------`

## Files Modified

1. **scripts/sangam_bulk_import.py** (line 1096-1100)
   - Added regex check `if re.match(r'^-+$', token):`
   - Applies to all Sangam works (18 works total)

2. **scripts/test_hyphen_placeholder_fix.py** (new file)
   - Verification tests with 13 test cases
   - Tests real examples from Purananuru and Paripaadal
   - All tests pass ✓

## Testing

Run the test script:
```bash
python scripts/test_hyphen_placeholder_fix.py
```

Expected output:
```
Testing hyphen-only token detection:
============================================================
✓ PASS: '-' -> should_skip=True, matches=True
✓ PASS: '--' -> should_skip=True, matches=True
✓ PASS: '---' -> should_skip=True, matches=True
✓ PASS: '--------' -> should_skip=True, matches=True
✓ PASS: '----------------' -> should_skip=True, matches=True
✓ PASS: 'வான்-நிலா' -> should_skip=False, matches=False
[... 7 more tests ...]
============================================================
Results: 13 passed, 0 failed

✓ All tests passed! Fix is working correctly.
```

## Re-importing Data (Optional)

If you want to clean up the existing database entries with hyphen placeholders:

### Option 1: Delete and Re-import Sangam Literature

```bash
# 1. Delete existing Sangam data
python scripts/delete_sangam.py

# 2. Re-import with fixed parser
python scripts/sangam_bulk_import.py
```

### Option 2: SQL Cleanup (Quick)

Delete word entries that are only hyphens:

```sql
-- Preview affected words
SELECT w.word_id, w.word_text, COUNT(*) as count
FROM words w
WHERE w.word_text ~ '^-+$'
GROUP BY w.word_id, w.word_text
ORDER BY count DESC;

-- Delete hyphen-only words
DELETE FROM words
WHERE word_text ~ '^-+$';

-- Verify deletion
SELECT COUNT(*) FROM words WHERE word_text ~ '^-+$';
-- Should return 0
```

**Note:** The line text in the `lines` table remains unchanged (preserves scholarly context).

## Impact

**Before fix:**
- Hyphen placeholders created meaningless word entries
- Polluted word frequency statistics
- Confused search results

**After fix:**
- Cleaner word database (only actual Tamil words)
- Accurate word frequency counts
- Lines still preserve lost text markers for scholarly reference

## References

- Source file: `Tamil-Source-TamilConcordence/2_Sangam_Literature/8 புறநானூறு.txt`
- Source file: `Tamil-Source-TamilConcordence/2_Sangam_Literature/5 பரிபாடல்.txt`
- Parser: `scripts/sangam_bulk_import.py`
- Related: `scripts/word_cleaning.py` (shared utilities)
