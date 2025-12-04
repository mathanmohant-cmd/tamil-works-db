# Tamil Literary Works Database - Design Guide

## Overview

This database is designed to store and query five major Tamil literary works with their complete hierarchical structure, allowing word-level analysis and contextual queries.

## Supported Works

1. **Tolkāppiyam** (தொல்காப்பியம்) - Ancient grammar text
2. **Sangam Literature** (சங்க இலக்கியம்) - Classical poetry collections
3. **Thirukkural** (திருக்குறள்) - Ethical couplets
4. **Silapathikaram** (சிலப்பதிகாரம்) - Epic narrative
5. **Kambaramayanam** (கம்பராமாயணம்) - Tamil Ramayana

## Database Schema

### Core Tables

#### 1. `works`
Main table for literary works.

**Columns:**
- `work_id`: Unique identifier
- `work_name`: English name
- `work_name_tamil`: Tamil name
- `period`: Time period of composition
- `author`: Author name
- `author_tamil`: Author name in Tamil

#### 2. `sections`
Hierarchical structure table supporting all organizational levels.

**Key Features:**
- Self-referencing with `parent_section_id` for unlimited hierarchy depth
- `level_type`: Identifies the type of section (paal, kandam, adhikaram, etc.)
- `sort_order`: Maintains proper ordering

**Columns:**
- `section_id`: Unique identifier
- `work_id`: Links to the literary work
- `parent_section_id`: Links to parent section (NULL for top-level)
- `level_type`: Type of section (e.g., 'paal', 'kandam', 'adhikaram')
- `section_number`: Number within its level
- `section_name`: Name of the section
- `sort_order`: Order within same level

#### 3. `verses`
Atomic textual units (kurals, poems, sutras, etc.)

**Columns:**
- `verse_id`: Unique identifier
- `work_id`: Links to work
- `section_id`: Links to most specific section
- `verse_number`: Number of the verse
- `verse_type`: Type (kural, venba, kalippa, etc.)
- `meter`: Poetic meter if applicable
- `total_lines`: Number of lines in verse

#### 4. `lines`
Individual lines within verses.

**Columns:**
- `line_id`: Unique identifier
- `verse_id`: Links to verse
- `line_number`: Position within verse
- `line_text`: Tamil text
- `line_text_transliteration`: Roman transliteration
- `line_text_translation`: English translation

#### 5. `words`
Every individual word with position information.

**Columns:**
- `word_id`: Unique identifier
- `line_id`: Links to line
- `word_position`: Position in line (1, 2, 3, ...)
- `word_text`: Tamil word
- `word_text_transliteration`: Roman transliteration
- `word_root`: Root/base form
- `word_type`: Part of speech (noun, verb, etc.)
- `sandhi_split`: Components if result of sandhi
- `meaning`: Definition/meaning

### Helper Tables

#### `commentaries`
Stores traditional commentaries on verses.

#### `cross_references`
Links related verses across works.

### Views

#### `verse_hierarchy`
Pre-computed hierarchical paths for each verse.

**Columns:**
- `verse_id`
- `verse_number`
- `work_name`
- `hierarchy_path`: Complete path (e.g., "paal:Aram > iyal:Pāyiram > adhikaram:Kadavul Vazhthu")
- `hierarchy_depth`: Number of levels

#### `word_details`
Complete context for every word.

**Columns:**
- All word information
- Line text and number
- Verse information
- Complete hierarchy path

## Hierarchical Structures by Work

### Thirukkural
```
Work: Thirukkural
├── Paal (3)
│   ├── Iyal (13 total)
│   │   ├── Adhikaram (133 total)
│   │   │   ├── Kural (10 per adhikaram, 1330 total)
│   │   │   │   ├── Line 1
│   │   │   │   └── Line 2
```

**Levels:**
1. Paal (பால்) - 3 major sections
2. Iyal (இயல்) - 13 sub-sections
3. Adhikaram (அதிகாரம்) - 133 chapters
4. Kural - 1330 couplets (10 per adhikaram)
5. Line - 2 lines per kural

### Kambaramayanam
```
Work: Kambaramayanam
├── Kandam (6)
│   ├── Padalam (varies)
│   │   ├── Verse (varies by meter)
│   │   │   ├── Line 1
│   │   │   ├── Line 2
│   │   │   ├── Line 3
│   │   │   └── Line 4 (typically)
```

**Levels:**
1. Kandam (காண்டம்) - 6 major cantos
2. Padalam (படலம்) - Chapters/sections
3. Verse - Individual verses (various meters)
4. Line - Typically 4 lines per verse

### Silapathikaram
```
Work: Silapathikaram
├── Kandam (3)
│   ├── Kaathai (30 total)
│   │   ├── Verse/Song
│   │   │   ├── Lines (varies)
```

**Levels:**
1. Kandam (காண்டம்) - 3 major cantos (Puhar, Madurai, Vanji)
2. Kaathai (காதை) - 30 episodes/chapters
3. Verse/Song - Various types
4. Line - Variable number

### Tolkāppiyam
```
Work: Tolkāppiyam
├── Athikaram (3)
│   ├── Iyal (9 total)
│   │   ├── Noorpa (Sutra)
│   │   │   ├── Lines (varies)
```

**Levels:**
1. Athikaram (அதிகாரம்) - 3 main divisions
2. Iyal (இயல்) - 9 sections total
3. Noorpa (நூற்பா) - Sutras/verses
4. Line - Variable lines per sutra

### Sangam Literature
```
Collection
├── Work (e.g., Kuruntokai, Purananuru)
│   ├── Poem (numbered)
│   │   ├── Lines (varies)
```

**Levels:**
1. Collection - Ettuthokai (8) or Pattupattu (10)
2. Work - Individual anthology
3. Poem - Individual poem
4. Line - Variable lines

## Common Query Patterns

### 1. Find All Occurrences of a Specific Word

```sql
-- Find all occurrences of "அறம்"
SELECT
    word_text,
    line_text,
    work_name,
    hierarchy_path,
    line_number,
    word_position
FROM word_details
WHERE word_text = 'அறம்'
ORDER BY work_name, word_id;
```

### 2. Find Words by Root Form

```sql
-- Find all words derived from root "முதல்"
SELECT
    word_text,
    word_root,
    line_text,
    hierarchy_path
FROM word_details
WHERE word_root = 'முதல்'
ORDER BY work_name, line_id;
```

### 3. Get Complete Text of a Specific Section

```sql
-- Get all kurals in "Kadavul Vazhthu" adhikaram (section_id = 6)
SELECT
    v.verse_number as kural_number,
    l.line_number,
    l.line_text,
    l.line_text_translation
FROM verses v
INNER JOIN lines l ON v.verse_id = l.verse_id
WHERE v.section_id = 6
ORDER BY v.verse_number, l.line_number;
```

### 4. Get All Content Under a High-Level Section

```sql
-- Get all content under "Aram Paal" (section_id = 1)
-- This includes all nested sections (Iyal, Adhikaram, Kurals)
WITH RECURSIVE subsections AS (
    SELECT section_id
    FROM sections
    WHERE section_id = 1

    UNION ALL

    SELECT s.section_id
    FROM sections s
    INNER JOIN subsections ss ON s.parent_section_id = ss.section_id
)
SELECT
    v.verse_number,
    l.line_number,
    l.line_text,
    s.level_type,
    s.section_name
FROM verses v
INNER JOIN subsections ss ON v.section_id = ss.section_id
INNER JOIN lines l ON v.verse_id = l.verse_id
INNER JOIN sections s ON v.section_id = s.section_id
ORDER BY v.sort_order, l.line_number;
```

### 5. Find Lines Containing Specific Text

```sql
-- Find all lines containing specific text (Tamil full-text search)
SELECT
    l.line_text,
    v.verse_number,
    vh.work_name,
    vh.hierarchy_path
FROM lines l
INNER JOIN verses v ON l.verse_id = v.verse_id
INNER JOIN verse_hierarchy vh ON v.verse_id = vh.verse_id
WHERE l.line_text LIKE '%அறம்%'
ORDER BY vh.work_name, v.sort_order;
```

### 6. Word Frequency Analysis

```sql
-- Get word frequency across Thirukkural
SELECT
    word_text,
    word_root,
    COUNT(*) as frequency,
    COUNT(DISTINCT verse_id) as verses_appearing_in
FROM word_details
WHERE work_name = 'Thirukkural'
GROUP BY word_text, word_root
ORDER BY frequency DESC
LIMIT 100;
```

### 7. Get Complete Hierarchy Path for a Word

```sql
-- Find where a specific word appears with full context
SELECT
    wd.word_text,
    wd.word_position,
    wd.line_number,
    wd.line_text,
    wd.verse_number,
    wd.hierarchy_path
FROM word_details wd
WHERE wd.word_text = 'கடவுள்';
```

### 8. Compare Word Usage Across Works

```sql
-- Compare usage of a word across different works
SELECT
    work_name,
    COUNT(*) as occurrences,
    COUNT(DISTINCT verse_id) as unique_verses
FROM word_details
WHERE word_root = 'அறம்'
GROUP BY work_name
ORDER BY occurrences DESC;
```

### 9. Get Verse with All Words

```sql
-- Get a complete verse with all words broken down
SELECT
    l.line_number,
    l.line_text,
    w.word_position,
    w.word_text,
    w.word_root,
    w.word_type
FROM verses v
INNER JOIN lines l ON v.verse_id = l.verse_id
INNER JOIN words w ON l.line_id = w.line_id
WHERE v.verse_id = 1
ORDER BY l.line_number, w.word_position;
```

### 10. Search by Meter/Verse Type

```sql
-- Find all verses of a specific meter in Kambaramayanam
SELECT
    vh.hierarchy_path,
    v.verse_number,
    v.meter,
    l.line_text
FROM verses v
INNER JOIN verse_hierarchy vh ON v.verse_id = vh.verse_id
INNER JOIN lines l ON v.verse_id = l.verse_id
WHERE v.work_id = 5  -- Kambaramayanam
  AND v.meter = 'கலித்துறை'
ORDER BY v.sort_order, l.line_number;
```

### 11. Get Section Statistics

```sql
-- Get statistics for each Adhikaram in Thirukkural
SELECT
    s.section_name,
    s.section_name_tamil,
    COUNT(DISTINCT v.verse_id) as total_kurals,
    COUNT(DISTINCT l.line_id) as total_lines,
    COUNT(DISTINCT w.word_id) as total_words
FROM sections s
INNER JOIN verses v ON s.section_id = v.section_id
INNER JOIN lines l ON v.verse_id = l.verse_id
INNER JOIN words w ON l.line_id = w.line_id
WHERE s.level_type = 'adhikaram' AND s.work_id = 3
GROUP BY s.section_id, s.section_name, s.section_name_tamil
ORDER BY s.sort_order;
```

### 12. Find Sandhi-Split Words

```sql
-- Find all words that are results of sandhi
SELECT
    word_text,
    sandhi_split,
    line_text,
    hierarchy_path
FROM word_details
WHERE sandhi_split IS NOT NULL
ORDER BY work_name, word_id;
```

## Advanced Queries

### Context-Based Word Search

```sql
-- Find a word and show surrounding words (context window)
WITH target_words AS (
    SELECT word_id, line_id, word_position
    FROM words
    WHERE word_text = 'அறம்'
)
SELECT
    tw.word_id as target_word_id,
    w.word_text,
    w.word_position,
    CASE
        WHEN w.word_id = tw.word_id THEN '>>> TARGET <<<'
        ELSE ''
    END as marker,
    l.line_text
FROM target_words tw
INNER JOIN words w ON tw.line_id = w.line_id
INNER JOIN lines l ON w.line_id = l.line_id
WHERE w.word_position BETWEEN tw.word_position - 3 AND tw.word_position + 3
ORDER BY tw.word_id, w.word_position;
```

### Co-occurrence Analysis

```sql
-- Find words that commonly appear in the same line as a target word
WITH target_lines AS (
    SELECT DISTINCT line_id
    FROM words
    WHERE word_text = 'அறம்'
)
SELECT
    w.word_text,
    w.word_root,
    COUNT(*) as co_occurrence_count
FROM target_lines tl
INNER JOIN words w ON tl.line_id = w.line_id
WHERE w.word_text != 'அறம்'
GROUP BY w.word_text, w.word_root
ORDER BY co_occurrence_count DESC
LIMIT 50;
```

## Database Setup Instructions

### SQLite

```bash
sqlite3 tamil_literature.db < tamil_literature_schema.sql
```

### PostgreSQL

```bash
psql -d your_database -f tamil_literature_schema.sql
```

### MySQL/MariaDB

```bash
mysql -u username -p database_name < tamil_literature_schema.sql
```

## Data Entry Best Practices

1. **Maintain Consistency**: Use consistent transliteration schemes (e.g., ISO 15919)
2. **Preserve Original Text**: Store exact Tamil text as it appears in authoritative sources
3. **Section Ordering**: Always set `sort_order` correctly to maintain reading sequence
4. **Word Roots**: Standardize word root forms for better analysis
5. **Sandhi Splitting**: Document sandhi splits for compound words
6. **Translations**: Include multiple translation versions if available

## Performance Optimization

### Recommended Indexes

All necessary indexes are included in the schema:
- Foreign key indexes for joins
- Word text and root indexes for searches
- Section parent indexes for hierarchical queries

### Full-Text Search

For better performance on large text searches, consider:

**SQLite:**
```sql
CREATE VIRTUAL TABLE words_fts USING fts5(
    word_text,
    word_root,
    content=words,
    content_rowid=word_id
);
```

**PostgreSQL:**
```sql
CREATE INDEX idx_words_text_fts ON words USING gin(to_tsvector('tamil', word_text));
```

## Future Enhancements

1. **Audio/Pronunciation**: Table for storing audio files of recitations
2. **Manuscripts**: Track different manuscript versions and variations
3. **Grammatical Analysis**: More detailed morphological analysis
4. **Semantic Tags**: Thematic tagging of verses (love, war, ethics, etc.)
5. **Historical Context**: Timeline and historical event associations
6. **Cross-linguistic**: Links to translations in other languages

## License and Attribution

When using this database structure, ensure proper attribution to original texts and respect copyright of modern translations and commentaries.
