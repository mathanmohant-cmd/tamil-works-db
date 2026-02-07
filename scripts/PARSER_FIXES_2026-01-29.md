# Parser Fixes for Special Characters and Numbers
**Date:** 2026-01-29

## Issues Found

Database contained words and lines with special characters and numbers that should have been cleaned during parsing:

### Words Table Issues
1. **திருவருட்பா - Balakrishnapillai Edition**: 961 words with numbers, 4,744 with dots, 13 with special chars
2. **திருவருட்பா - Uran Adigal Edition**: 811 words with numbers, 4,550 with dots, 14 with special chars
3. **திருவாசகம்**: 660 words with numbers/special characters

**Examples of problematic words:**
- Line numbers: `5`, `10`, `15`, `100`, `1000`
- Section markers: `@1.குடும்ப`, `@15.மங்களம்`, `&8.`
- Verse markers: `#1`, `#10`, `#100`
- Dots in words: `அச்சோ.`, `அடியே.`

### Lines Table Issues
Works with asterisks (*) in line_text:
- **ஆத்திசூடி வெண்பா**: 43 lines (glossary/annotation markers)
- **திருக்கோவையார்**: 26 lines (chapter annotation markers)
- **கம்பராமாயணம்**: 4 lines (editorial notes)
- 27 other works: 1 line each

**Examples of problematic lines:**
- `* ஆத்திசூடி விநாயகர்` (glossary entry)
- `* இரண்டாம் அதிகாரம்` (chapter annotation)
- `*பால காண்டம் - தனியன்` (editorial note)

## Root Causes

### Problem 1: Inadequate Word Cleaning
Three parsers used basic `segment_line()` that only split on whitespace without removing special characters:
- `thiruvarutpa_uran_bulk_import.py`
- `thiruvarutpa_balakrishnapillai_bulk_import.py`
- `thiruvasagam_bulk_import.py`

### Problem 2: Annotation Lines Not Filtered
Three parsers accepted annotation/glossary lines starting with `*` as verse content:
- `neethinoolkal_bulk_import.py` (ஆத்திசூடி வெண்பா and others)
- `thirukovayar_bulk_import.py`
- `kambaramayanam_bulk_import.py`

## Fixes Applied

### Fix 1: Use word_cleaning Module for Word Segmentation

**Files Modified:**
1. `thiruvarutpa_uran_bulk_import.py`
2. `thiruvarutpa_balakrishnapillai_bulk_import.py`
3. `thiruvasagam_bulk_import.py`

**Changes:**
- Added import: `from word_cleaning import split_and_clean_words`
- Replaced: `words = self.segment_line(line_text)`
- With: `words = split_and_clean_words(line_text)`

**Effect:**
Now properly removes:
- Line count numbers (5, 10, 15, etc.)
- Section/verse markers (@, #, &)
- Dots and special characters from words
- Keeps only Tamil characters, hyphens (-), and underscores (_)

### Fix 2: Skip Annotation Lines Starting with Asterisk

**Files Modified:**
1. `neethinoolkal_bulk_import.py` (lines 549-552)
2. `thirukovayar_bulk_import.py` (lines 255-259)
3. `kambaramayanam_bulk_import.py` (lines 152-156)

**Changes:**
Added check before appending lines to verses:
```python
# Skip annotation/glossary lines (start with *)
if line.startswith('*'):
    continue
```

**Effect:**
Excludes annotation/glossary/editorial lines from verse content, keeping line_text clean.

## Verification

Run this script to check for remaining issues:
```bash
cd scripts
python check_problematic_words.py
```

The script checks:
1. Words with numbers
2. Words with dots
3. Words with special characters (*, @, #, $, &)
4. Lines with numbers
5. Summary by work

## Next Steps

To clean the database:

1. **Delete problematic works:**
   ```bash
   # Delete Thiruvarutpa editions
   python scripts/delete_thiruvarutpa.py

   # Delete Thiruvasagam
   python scripts/delete_thiruvasagam.py

   # Delete ethical literature (includes ஆத்திசூடி வெண்பா)
   python scripts/delete_neethinoolkal.py

   # Delete Thirukovayar
   python scripts/delete_thirukovayar.py

   # Delete Kambaramayanam
   python scripts/delete_kambaramayanam.py
   ```

2. **Re-import with fixed parsers:**
   ```bash
   # Re-import Thiruvarutpa editions
   python scripts/thiruvarutpa_uran_bulk_import.py
   python scripts/thiruvarutpa_balakrishnapillai_bulk_import.py

   # Re-import Thiruvasagam
   python scripts/thiruvasagam_bulk_import.py

   # Re-import ethical literature (21 works including ஆத்திசூடி வெண்பா)
   python scripts/neethinoolkal_bulk_import.py

   # Re-import Thirukovayar
   python scripts/thirukovayar_bulk_import.py

   # Re-import Kambaramayanam
   python scripts/kambaramayanam_bulk_import.py
   ```

3. **Verify clean data:**
   ```bash
   python scripts/check_problematic_words.py
   ```

## Summary

- **Total parsers fixed:** 6
- **Issue types:** 2 (word cleaning, line filtering)
- **Works affected:** ~40+ works across 6 parsers
- **Lines with problems:** 600+ words, 70+ lines

All fixes ensure that:
- Words contain **only Tamil characters, hyphens, and underscores**
- Lines contain **no annotation/editorial markers**
- Line numbers and structural markers are **completely removed**
