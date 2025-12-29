# Metadata Integration Guide for Import Scripts

This guide shows how to add JSONB metadata to the bulk import scripts, specifically for devotional literature.

## Step 1: Run the Migration

First, apply the metadata columns migration:

```bash
psql tamil_literature -f sql/migrations/add_metadata_columns.sql
```

## Step 2: Update Import Script Data Structures

### Add metadata field to data containers

```python
class ThirumuraiBulkImporter:
    def __init__(self, db_connection_string: str):
        # Existing code...
        self.works = []
        self.sections = []
        self.verses = []
        self.lines = []
        self.words = []
```

### Metadata field is already in dictionaries, just populate it

When creating work/section/verse dictionaries, add metadata:

```python
# Example: Creating a work with metadata
work_dict = {
    'work_id': self.work_id,
    'work_name': work_name,
    'work_name_tamil': work_name_tamil,
    'work_type': 'devotional',
    'work_type_tamil': 'பக்தி இலக்கியம்',
    'author': author,
    'language': 'Tamil',
    'metadata': {
        'tradition': 'Shaivite',
        'collection_id': 321,
        'collection_name': 'Thirumurai',
        'time_period': '6th-9th century CE',
        'saint': saint_name,
        'musical_tradition': True,
        'thematic_focus': ['devotion', 'philosophy', 'theology']
    }
}
self.works.append(work_dict)
```

## Step 3: Metadata Examples by Level

### Work-Level Metadata (Devotional Literature)

```python
work_metadata = {
    # Religious tradition
    'tradition': 'Shaivite' | 'Vaishnavite' | 'Christian' | 'Islamic' | 'Murugan worship',

    # Collection information
    'collection_id': 321,  # Thirumurai
    'collection_name': 'Thirumurai',
    'position_in_collection': 1,

    # Historical context
    'time_period': '6th-9th century CE',
    'century': 7,
    'author_period': 'Nayanmars',

    # Author/Saint information
    'saint': 'திருஞானசம்பந்தர்',
    'saint_transliteration': 'Thirugnanasambandar',
    'author_count': 1,  # or multiple for anthologies

    # Musical/Performance
    'musical_tradition': True,
    'panns_used': ['குறிஞ்சி', 'முல்லை'],  # Musical modes
    'performance_context': 'temple worship',

    # Thematic
    'deity_focus': 'Shiva' | 'Vishnu' | 'Murugan' | 'Christ' | 'Prophet',
    'thematic_focus': ['devotion', 'philosophy', 'theology', 'ethics'],

    # Manuscript/Edition
    'critical_edition': 'Swaminatha Iyer, 1900',
    'manuscript_count': 5,
    'variant_readings': True,

    # Statistics
    'verse_count': 384,
    'has_music': True,
    'has_commentary': True
}
```

### Section-Level Metadata (Devotional Literature)

```python
section_metadata = {
    # Musical context
    'pann': 'குறிஞ்சி',  # Musical mode
    'pann_transliteration': 'Kurinji',
    'talam': 'ஆதி',  # Rhythmic cycle

    # Thematic
    'theme': 'divine grace',
    'theme_tamil': 'திருவருள்',
    'sub_theme': 'surrender',

    # Structural
    'section_type': 'pathigam',  # Group of 10-11 verses
    'pathigam_number': 1,
    'verses_in_section': 10,

    # Contextual
    'deity_addressed': 'Shiva at Mylapore',
    'temple': 'காபாலீச்சுவரம்',
    'location': 'Mylapore, Chennai',

    # Literary
    'meter_type': 'venba',
    'poetic_form': 'stuti'  # praise poem
}
```

### Verse-Level Metadata (Devotional Literature)

```python
verse_metadata = {
    # Authorship
    'saint': 'திருஞானசம்பந்தர்',
    'composition_period': '7th century CE',

    # Musical
    'raga': 'பைரவி',
    'talam': 'ஆதி',
    'pann': 'குறிஞ்சி',

    # Literary
    'meter': 'venba',
    'line_count': 4,
    'syllable_pattern': '4-4-3-4',

    # Theological/Thematic
    'deity': 'Shiva',
    'deity_epithet': 'காபாலீச்சுவரர்',
    'temple': 'காபாலீச்சுவரம் temple, Mylapore',
    'themes': ['divine grace', 'devotion', 'refuge'],

    # Literary devices
    'literary_devices': ['metaphor', 'alliteration', 'imagery'],
    'refrain': 'குரைகழல்',  # Repeated phrase

    # Theological concepts
    'theological_concepts': ['grace', 'karma', 'liberation'],
    'philosophical_school': 'Shaiva Siddhanta',

    # Commentary
    'has_commentary': True,
    'commentators': ['சேக்கிழார்', 'உமாபதி சிவாசாரியார்'],
    'commentary_count': 2,

    # Usage
    'liturgical_use': True,
    'worship_context': 'evening worship',
    'festival_association': 'Arudra Darisanam',

    # Textual
    'variant_readings': False,
    'manuscript_notes': 'Clear reading in all MSS'
}
```

### Word-Level Metadata (Theological Terms)

```python
word_metadata = {
    # Etymology
    'etymology': 'Proto-Dravidian *aram',
    'root': 'அறு',

    # Semantic
    'semantic_field': 'theology',
    'theological_term': True,
    'deity_name': True,  # For divine names
    'epithet': True,  # For divine epithets

    # Theological significance
    'theological_concept': 'divine grace',
    'tradition_specific': 'Shaivite',
    'technical_term': True,

    # Usage patterns
    'frequency_in_work': 23,
    'frequency_rank': 15,
    'collocations': ['திருவருள்', 'அருட்பெருஞ்சோதி'],

    # Cross-references
    'related_concepts': ['கருணை', 'அருள்'],
    'sanskrit_equivalent': 'anugraha',

    # Commentary notes
    'commentator_glosses': {
        'உமாபதி': 'இறைவன் தரும் அருள்',
        'சேக்கிழார்': 'திருவருளின் வெளிப்பாடு'
    }
}
```

## Step 4: Update Bulk COPY Operations

### Modify COPY statements to include metadata

**For works table:**

```python
def bulk_insert_works(self):
    """Bulk insert works with metadata"""
    if not self.works:
        return

    buffer = io.StringIO()
    writer = csv.writer(buffer, delimiter='\t', quoting=csv.QUOTE_MINIMAL, escapechar='\\')

    for work in self.works:
        import json
        metadata_json = json.dumps(work.get('metadata', {})) if work.get('metadata') else None

        writer.writerow([
            work['work_id'],
            work['work_name'],
            work['work_name_tamil'],
            work.get('work_type'),
            work.get('work_type_tamil'),
            work.get('author'),
            work.get('time_period'),
            work.get('language', 'Tamil'),
            work.get('transliteration_scheme'),
            work.get('description'),
            metadata_json  # Add metadata as last column
        ])

    buffer.seek(0)

    # Include metadata column in COPY
    self.cursor.copy_from(
        buffer,
        'works',
        columns=('work_id', 'work_name', 'work_name_tamil', 'work_type',
                'work_type_tamil', 'author', 'time_period', 'language',
                'transliteration_scheme', 'description', 'metadata'),
        null=''
    )
    print(f"  Inserted {len(self.works)} works with metadata")
```

**For sections table:**

```python
def bulk_insert_sections(self):
    """Bulk insert sections with metadata"""
    if not self.sections:
        return

    buffer = io.StringIO()
    writer = csv.writer(buffer, delimiter='\t', quoting=csv.QUOTE_MINIMAL, escapechar='\\')

    for section in self.sections:
        import json
        metadata_json = json.dumps(section.get('metadata', {})) if section.get('metadata') else None

        writer.writerow([
            section['section_id'],
            section['work_id'],
            section.get('parent_section_id', ''),
            section.get('level_type'),
            section.get('level_type_tamil'),
            section.get('section_number', ''),
            section.get('section_name', ''),
            section.get('section_name_tamil', ''),
            section['sort_order'],
            metadata_json  # Add metadata
        ])

    buffer.seek(0)

    self.cursor.copy_from(
        buffer,
        'sections',
        columns=('section_id', 'work_id', 'parent_section_id', 'level_type',
                'level_type_tamil', 'section_number', 'section_name',
                'section_name_tamil', 'sort_order', 'metadata'),
        null=''
    )
    print(f"  Inserted {len(self.sections)} sections with metadata")
```

**For verses table:**

```python
def bulk_insert_verses(self):
    """Bulk insert verses with metadata"""
    if not self.verses:
        return

    buffer = io.StringIO()
    writer = csv.writer(buffer, delimiter='\t', quoting=csv.QUOTE_MINIMAL, escapechar='\\')

    for verse in self.verses:
        import json
        metadata_json = json.dumps(verse.get('metadata', {})) if verse.get('metadata') else None

        writer.writerow([
            verse['verse_id'],
            verse['work_id'],
            verse.get('section_id', ''),
            verse['verse_number'],
            verse.get('verse_type'),
            verse.get('verse_type_tamil'),
            verse['total_lines'],
            verse['sort_order'],
            metadata_json  # Add metadata
        ])

    buffer.seek(0)

    self.cursor.copy_from(
        buffer,
        'verses',
        columns=('verse_id', 'work_id', 'section_id', 'verse_number',
                'verse_type', 'verse_type_tamil', 'total_lines', 'sort_order',
                'metadata'),
        null=''
    )
    print(f"  Inserted {len(self.verses)} verses with metadata")
```

## Step 5: Specific Metadata for Thirumurai

```python
# File 1-7: Devaram works
devaram_saints = {
    1: {
        'saint': 'திருஞானசம்பந்தர்',
        'transliteration': 'Thirugnanasambandar',
        'period': '7th century CE',
        'pathigam_count': 384
    },
    2: {
        'saint': 'திருநாவுக்கரசர்',
        'transliteration': 'Thirunavukkarasar (Appar)',
        'period': '7th century CE',
        'pathigam_count': 311
    },
    3: {
        'saint': 'சுந்தரர்',
        'transliteration': 'Sundarar',
        'period': '8th century CE',
        'pathigam_count': 100
    }
}

# When parsing Devaram works
work_metadata = {
    'tradition': 'Shaivite',
    'collection_id': 321,
    'collection_name': 'Thirumurai',
    'sub_collection': 'Devaram',
    'file_number': file_number,
    'saint': saint_info['saint'],
    'saint_transliteration': saint_info['transliteration'],
    'time_period': saint_info['period'],
    'pathigam_count': saint_info['pathigam_count'],
    'musical_tradition': True,
    'performance_context': 'temple worship',
    'deity_focus': 'Shiva',
    'liturgical_use': True
}
```

## Step 6: Metadata for Naalayira Divya Prabandham

```python
# Vaishnavite collection
work_metadata = {
    'tradition': 'Vaishnavite',
    'collection_id': 322,
    'collection_name': 'Naalayira Divya Prabandham',
    'saint': alvar_name,  # One of 12 Alvars
    'time_period': '6th-9th century CE',
    'deity_focus': 'Vishnu',
    'divya_desam_count': 108,  # Sacred Vishnu temples
    'musical_tradition': True,
    'performance_context': 'temple worship',
    'liturgical_use': True,
    'thematic_focus': ['devotion', 'bhakti', 'surrender']
}

# Verse-level metadata
verse_metadata = {
    'alvar': alvar_name,
    'deity': 'Vishnu',
    'divya_desam': temple_name,
    'location': location,
    'deity_form': 'Ranganatha' | 'Parthasarathy' | etc.,
    'themes': ['surrender', 'longing', 'divine beauty']
}
```

## Step 7: Testing Metadata Queries

After importing with metadata:

```sql
-- Find all Shaivite works
SELECT work_name_tamil, metadata->>'saint'
FROM works
WHERE metadata->>'tradition' = 'Shaivite';

-- Find verses about specific deity
SELECT verse_id, metadata->>'deity', metadata->>'temple'
FROM verses
WHERE metadata->>'deity' = 'Shiva'
  AND metadata->>'temple' LIKE '%Mylapore%';

-- Find works by time period
SELECT work_name_tamil, metadata->>'time_period'
FROM works
WHERE metadata->>'time_period' LIKE '%7th century%';

-- Find verses with specific ragas
SELECT COUNT(*)
FROM verses
WHERE metadata->>'raga' = 'பைரவி';

-- Get all musical modes used in a work
SELECT DISTINCT metadata->>'pann'
FROM sections
WHERE work_id = 100;
```

## Summary Checklist

- [ ] Run migration: `psql tamil_literature -f sql/migrations/add_metadata_columns.sql`
- [ ] Import `json` module in import script
- [ ] Add metadata dictionaries when creating works/sections/verses
- [ ] Update `bulk_insert_*` methods to include metadata column
- [ ] Use `json.dumps()` to serialize metadata before COPY
- [ ] Test metadata queries after import
- [ ] Document metadata schema for each work type

## Performance Note

JSONB metadata adds minimal overhead to bulk COPY operations:
- ~5-10% slower than without metadata
- Still 1000x faster than row-by-row INSERT
- GIN indexes make queries on metadata very fast
