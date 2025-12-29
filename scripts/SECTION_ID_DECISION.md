# Section ID Architecture Decision

## Problem Statement

When importing devotional literature works, the question arose: **Should we allow NULL section_id for verses without explicit hierarchical structure, or should we always create a default section?**

## Analysis

### Backend Dependencies on section_id

The backend has **critical dependencies** on section_id that make NULL values non-viable:

#### 1. verse_hierarchy View (sql/complete_setup.sql:287)
```sql
FROM verses v
INNER JOIN works w ON v.work_id = w.work_id
INNER JOIN section_path sp ON v.section_id = sp.section_id;  -- INNER JOIN!
```
**Problem:** Uses INNER JOIN → verses with NULL section_id are excluded from view

#### 2. word_details View (sql/complete_setup.sql:324)
```sql
FROM words w
INNER JOIN lines l ON w.line_id = l.line_id
INNER JOIN verses v ON l.verse_id = v.verse_id
INNER JOIN verse_hierarchy vh ON v.verse_id = vh.verse_id;  -- Depends on verse_hierarchy!
```
**Problem:** Since verse_hierarchy excludes NULL sections, word_details also excludes them

#### 3. Backend Search (webapp/backend/database.py:103-106)
```python
query = """
    SELECT ... FROM word_details wd
    LEFT JOIN works w ON wd.work_name = w.work_name
    LEFT JOIN verses v ON wd.verse_id = v.verse_id
    LEFT JOIN sections s ON v.section_id = s.section_id
    WHERE 1=1
"""
```
**Problem:** While backend uses LEFT JOIN (which could handle NULL), word_details view already excluded those verses

### Consequences of NULL section_id

If section_id is nullable:
- ❌ **Verses invisible in word_details view** → Cannot search for those verses
- ❌ **Verses invisible in verse_hierarchy view** → Cannot display verse context
- ❌ **Backend get_verse_context() fails** → API errors when viewing verses
- ❌ **Frontend search broken** → No search results for verses without sections

## Decision: ALWAYS Create Default Sections

Following the **Sangam parser pattern**, all parsers create a default section for works without explicit hierarchy.

### Implementation Pattern

```python
def _get_or_create_section_id(self, work_id):
    """
    Get or create a default root section for a work (for works without explicit hierarchy)
    Follows Sangam parser pattern to ensure all verses have a section_id
    """
    section_id = self.section_id
    self.section_id += 1

    self.sections.append({
        'section_id': section_id,
        'work_id': work_id,
        'parent_section_id': None,
        'level_type': 'Chapter',
        'level_type_tamil': 'பகுதி',
        'section_number': 1,
        'section_name': None,  # NULL name to avoid redundant display
        'section_name_tamil': None,
        'sort_order': 1,
        'metadata': {}
    })

    return section_id
```

### Usage in Parsers

At the start of parsing each work:
```python
# Create default section (fallback if no explicit sections found)
default_section = self._get_or_create_section_id(self.current_work_id)
current_section_id = default_section  # Update when explicit section found
```

### Benefits

✅ **All verses have section_id** → Views work correctly
✅ **Search functionality intact** → word_details includes all verses
✅ **Verse context displays properly** → verse_hierarchy includes all verses
✅ **Section name is NULL** → Frontend doesn't show redundant "Collection:" text
✅ **Clean hierarchy** → Work → [Default Section] → Verses
✅ **Backward compatible** → Works with existing Sangam, Thirukkural parsers

## Applied To

- ✅ `sangam_bulk_import.py` (original implementation)
- ✅ `devaram_bulk_import.py` (updated 2025-12-28)
- ✅ `thiruvasagam_bulk_import.py` (updated 2025-12-28)
- 🔜 All future devotional literature parsers

## Database Schema

section_id remains NOT NULL:
```sql
ALTER TABLE verses ALTER COLUMN section_id SET NOT NULL;
```

## Alternative Considered (Rejected)

Making section_id nullable and converting views to LEFT JOIN would require:
- Rewriting verse_hierarchy view (complex recursive CTE changes)
- Rewriting word_details view
- Testing all backend query logic
- Handling NULL hierarchy_path in frontend display
- Much higher risk of breaking existing functionality

The default section approach is **simpler, safer, and already proven** in production parsers.
