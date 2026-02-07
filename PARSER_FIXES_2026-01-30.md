# Parser Marker Cleanup - 2026-01-30

## Issue Summary

Special characters (`&`, `@`, `#`) that are supposed to mark sections and verses in source files were appearing in the imported database content (lines and words). These markers should have been parsed out and used only for structural parsing, not included in the actual verse text.

## Root Causes

1. **Regex too strict**: Subsection/Thirumurai marker regexes required `\s+` (one or more spaces) after the number, but some source files had no space after the dot (e.g., `@22.பணித்திறஞ்` instead of `@22. பணித்திறஞ்`)

2. **No content filtering**: Parsers were not filtering out lines that looked like markers but somehow slipped through the regex matching

3. **Embedded markers not cleaned**: Some source files had footnote references like `களிறு#1` or `#ஃ31` embedded in the content

## Affected Works

| Work | Lines with markers | Issue |
|------|-------------------|-------|
| திருவருட்பா - பாலகிருஷ்ணபிள்ளை பதிப்பு | 26 | Missing space after @ in section markers |
| திருவருட்பா - ஊரன் அடிகள் பதிப்பு | (same) | Missing space after @ in section markers |
| திருவாசகம் | 660 | Standalone `#1`, `#2`, etc. footnote markers |
| ஐந்திணை எழுபது | 1 | Embedded `#1` in word `களிறு#1` |
| தேம்பாவணி | 1 | Embedded `#ஃ31` marker |

## Parsers Fixed

1. **thiruvarutpa_balakrishnapillai_bulk_import.py**
2. **thiruvarutpa_uran_bulk_import.py**
3. **thiruvasagam_bulk_import.py**
4. **ainthinai_ezhubathu_bulk_import.py**
5. **thembavani_bulk_import.py**

## Fixes Applied

### 1. Regex Pattern Fixes

Changed section marker regexes to allow optional space after number:

```python
# BEFORE
thirumurai_match = re.match(r'^&(\d+)\s+(.+)', line)      # Required space
subsection_match = re.match(r'^@(\d+)\.?\s+(.+)', line)   # Required space

# AFTER
thirumurai_match = re.match(r'^&(\d+)\.?\s*(.+)', line)   # Optional space
subsection_match = re.match(r'^@(\d+)\.?\s*(.+)', line)   # Optional space
```

### 2. Content Filtering

Added filtering to skip lines that start with marker patterns:

```python
# In verse content collection section
if in_verse and current_subsection:
    # Skip lines that look like markers (formatting artifacts)
    if re.match(r'^[@#&]\d+', line):
        continue  # Don't add to verse content
```

### 3. Embedded Marker Cleaning

Added regex to clean embedded marker references from content:

```python
# Remove embedded marker references (e.g., "களிறு#1" -> "களிறு")
cleaned_line = re.sub(r'[#@&]\d+', '', line).strip()
```

For Thembavani specifically, also removed standalone `#` characters:
```python
cleaned_line = re.sub(r'#', '', cleaned_line).strip()
```

## Reimport Process

All affected works were deleted and reimported with the fixed parsers:

1. **Thiruvarutpa** (2 works): 11,867 verses reimported
2. **Thiruvasagam**: 51 verses, 3,438 lines reimported
3. **Ainthinai Ezhubathu**: 68 verses, 272 lines reimported
4. **Thembavani**: 3,614 verses, 14,461 lines reimported

## Verification

Final database check confirms **zero** occurrences of `@`, `#`, or `&` characters in:
- Lines table: 0 problematic lines
- Words table: 0 problematic words

✅ **SUCCESS**: Database is completely clean!

## Scripts Created

1. `scripts/check_special_chars.py` - Check for special characters in database
2. `scripts/analyze_problematic_lines.py` - Detailed analysis of issues
3. `scripts/identify_works_with_markers.py` - Identify which works have marker issues
4. `scripts/reimport_thiruvarutpa.py` - Reimport both Thiruvarutpa editions
5. `scripts/reimport_thiruvasagam.py` - Reimport Thiruvasagam
6. `scripts/reimport_final_two_works.py` - Reimport Ainthinai Ezhubathu and Thembavani

## Best Practices for Future Parsers

1. **Always use `\s*` not `\s+`** for optional whitespace in marker regexes
2. **Filter content lines** - skip lines that start with `[@#&]\d+` pattern
3. **Clean embedded markers** - use `re.sub(r'[#@&]\d+', '', line)` on all content
4. **Test with edge cases** - check for markers without spaces, embedded markers, etc.
5. **Verify after import** - run special character check to ensure clean data

## Related Files

- `PARSER_FIXES_2026-01-29.md` - Previous parser fixes for different issues
- `scripts/WORD_SEGMENTATION_PRINCIPLES.md` - Word segmentation guidelines
