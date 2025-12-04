# Word Usage Examples - Same Words Across Verses and Works

## Overview

This document demonstrates how the database tracks the same word appearing in:
1. **Different verses within the same work**
2. **Different works entirely**

## Sample Data Summary

The sample data (`sql/sample_word_data.sql`) includes:

- **Thirukkural**: 4 kurals (1, 2, 11, 31)
- **Kambaramayanam**: 1 verse (Bala Kandam, Nagar Padalam)
- **Silapathikaram**: 1 verse (Puhaar Kandam, Mangala Vazhthu)

## Key Words Tracked Across Multiple Contexts

### 1. முதல் (mudhal) - "first/primary"

| Work | Location | Word Form | Context | Word ID |
|------|----------|-----------|---------|---------|
| Thirukkural | Kural 1, Line 1 | முதல | "அகர முதல எழுத்தெல்லாம்" (A is first of all letters) | 2 |
| Kambaramayanam | Bala Kandam > Nagar Padalam, Verse 1 | முதல் | "முதல் நகர் அது" (That is the first city) | 42 |
| Silapathikaram | Puhaar Kandam > Mangala Vazhthu, Verse 1 | முதல் | "இலகு முதல் பொருள்" (The primary wealth) | 51 |

**Analysis**: The root word "முதல்" appears in 3 different works, showing its fundamental importance in Tamil literature when describing primacy or firstness.

---

### 2. உலகு/உலகம் (ulagu/ulagam) - "world"

| Work | Location | Word Form | Context | Word ID |
|------|----------|-----------|---------|---------|
| Thirukkural | Kural 1, Line 2 | உலகு | "பகவன் முதற்றே உலகு" (God is first of the world) | 7 |
| Thirukkural | Kural 11, Line 1 | உலகம் | "வான் நின்று உலகம் வழங்கி" (Rain sustains the world) | 18 |
| Kambaramayanam | Bala Kandam > Nagar Padalam, Verse 1 | உலகம் | "உலகம் போற்றும் அயோத்தி" (Ayodhya which the world praises) | 39 |
| Silapathikaram | Puhaar Kandam > Mangala Vazhthu, Verse 1 | உலகம் | "உலகம் உவப்ப வாழ்வோம்" (We shall live so the world rejoices) | 46 |

**Analysis**: "உலகு" appears **4 times** - twice in Thirukkural (in different kurals), once in Kambaramayanam, and once in Silapathikaram. Shows how each work references the world in different contexts.

---

### 3. அறம் (aram) - "virtue/righteousness"

| Work | Location | Word Form | Sandhi Split | Context | Word ID |
|------|----------|-----------|--------------|---------|---------|
| Thirukkural | Kural 31, Line 1 | அறத்தான் | அறம் + தான் | "அறத்தான் வருவதே இன்பம்" (Happiness comes from virtue) | 25 |
| Kambaramayanam | Bala Kandam > Nagar Padalam, Verse 1 | அறம் | - | "அறம் புரிந்த மன்னர்" (Kings who performed virtue) | 32 |
| Silapathikaram | Puhaar Kandam > Mangala Vazhthu, Verse 1 | அறத்தொடு | அறம் + ஒடு | "உலகம் உவப்ப வாழ்வோம் அறத்தொடு" (Let us live with virtue) | 49 |

**Analysis**: "அறம்" appears in **3 different works** in **3 different forms** due to sandhi (phonetic combination):
- அறத்தான் (from virtue)
- அறம் (virtue, base form)
- அறத்தொடு (with virtue)

This demonstrates the power of tracking `word_root` separately from `word_text`.

---

### 4. இன்பு/இன்பம் (inbu/inbam) - "happiness/pleasure"

| Work | Location | Word Form | Context | Word ID |
|------|----------|-----------|---------|---------|
| Thirukkural | Kural 31, Line 1 | இன்பம் | "அறத்தான் வருவதே இன்பம்" (That which comes from virtue is happiness) | 27 |
| Silapathikaram | Puhaar Kandam > Mangala Vazhthu, Verse 1 | இன்பம் | "முதல் பொருள் இன்பம் தரும்" (Primary wealth gives happiness) | 53 |

**Analysis**: "இன்பம்" appears in 2 works, both emphasizing happiness as a result of righteous living.

---

### 5. வாழ் (vaazh) - "to live"

| Work | Location | Word Form | Context | Word ID |
|------|----------|-----------|---------|---------|
| Kambaramayanam | Bala Kandam > Nagar Padalam, Verse 1 | வாழும் | "மன்னர் வாழும்" (Kings live) | 35 |
| Silapathikaram | Puhaar Kandam > Mangala Vazhthu, Verse 1 | வாழ்வோம் | "உலகம் உவப்ப வாழ்வோம்" (We shall live) | 48 |
| Silapathikaram | Puhaar Kandam > Mangala Vazhthu, Verse 1 | வாழும் | "அன்பொடு வாழும் தம்பதிகள்" (Couples living with love) | 56 |

**Analysis**: The verb "வாழ்" (to live) appears in different conjugations across works.

---

## Query Results Examples

### Query 1: Find All Occurrences of "முதல்" Across Works

```sql
SELECT
    w.work_name,
    vh.hierarchy_path,
    v.verse_number,
    l.line_text,
    wd.word_text,
    wd.meaning
FROM word_details wd
JOIN works w ON wd.work_name = w.work_name
JOIN verses v ON wd.verse_id = v.verse_id
JOIN verse_hierarchy vh ON v.verse_id = vh.verse_id
JOIN lines l ON wd.line_id = l.line_id
WHERE wd.word_root = 'முதல்';
```

**Expected Results:**

| work_name | hierarchy_path | verse_number | line_text | word_text | meaning |
|-----------|----------------|--------------|-----------|-----------|---------|
| Thirukkural | paal:Aram > iyal:Pāyiram > adhikaram:Kadavul Vazhthu | 1 | அகர முதல எழுத்தெல்லாம் ஆதி | முதல | first |
| Kambaramayanam | kandam:Bala Kandam > padalam:Nagar Padalam | 1 | முதல் நகர் அது தானே | முதல் | first/primary |
| Silapathikaram | kandam:Puhaar Kandam > kathai:Mangala Vazhthu | 1 | இலகு முதல் பொருள் இன்பம் தரும் | முதல் | first/primary |

---

### Query 2: Find All Occurrences of "உலகு" (World)

```sql
SELECT
    wd.work_name,
    wd.hierarchy_path,
    wd.word_text,
    wd.line_text
FROM word_details wd
WHERE wd.word_root = 'உலகு'
ORDER BY wd.work_name, wd.verse_id;
```

**Expected Results:**

| work_name | hierarchy_path | word_text | line_text |
|-----------|----------------|-----------|-----------|
| Thirukkural | paal:Aram > iyal:Pāyiram > adhikaram:Kadavul Vazhthu | உலகு | பகவன் முதற்றே உலகு |
| Thirukkural | paal:Aram > iyal:Pāyiram > adhikaram:Vaan Sirappu | உலகம் | வான் நின்று உலகம் வழங்கி வருதலால் |
| Kambaramayanam | kandam:Bala Kandam > padalam:Nagar Padalam | உலகம் | உலகம் போற்றும் அயோத்தி |
| Silapathikaram | kandam:Puhaar Kandam > kathai:Mangala Vazhthu | உலகம் | உலகம் உவப்ப வாழ்வோம் அறத்தொடு |

---

### Query 3: Words Appearing in Multiple Works

```sql
SELECT
    wd.word_root,
    COUNT(DISTINCT wd.work_name) as num_works,
    COUNT(*) as total_occurrences,
    GROUP_CONCAT(DISTINCT wd.work_name) as appears_in_works
FROM word_details wd
WHERE wd.word_root IS NOT NULL
GROUP BY wd.word_root
HAVING COUNT(DISTINCT wd.work_name) > 1
ORDER BY num_works DESC, total_occurrences DESC;
```

**Expected Results:**

| word_root | num_works | total_occurrences | appears_in_works |
|-----------|-----------|-------------------|------------------|
| உலகு | 3 | 4 | Thirukkural, Kambaramayanam, Silapathikaram |
| முதல் | 3 | 3 | Thirukkural, Kambaramayanam, Silapathikaram |
| அறம் | 3 | 3 | Thirukkural, Kambaramayanam, Silapathikaram |
| இன்பு | 2 | 2 | Thirukkural, Silapathikaram |
| வாழ் | 2 | 3 | Kambaramayanam, Silapathikaram |

---

### Query 4: Same Word in Different Verses Within Thirukkural

```sql
SELECT
    wd.word_root,
    wd.word_text,
    COUNT(DISTINCT wd.verse_id) as num_verses,
    GROUP_CONCAT(DISTINCT wd.hierarchy_path SEPARATOR ' | ') as locations
FROM word_details wd
WHERE wd.work_name = 'Thirukkural'
  AND wd.word_root IS NOT NULL
GROUP BY wd.word_root, wd.word_text
HAVING COUNT(DISTINCT wd.verse_id) > 1;
```

**Expected Results:**

| word_root | word_text | num_verses | locations |
|-----------|-----------|------------|-----------|
| உலகு | உலகம் | 2 | paal:Aram > iyal:Pāyiram > adhikaram:Kadavul Vazhthu \| paal:Aram > iyal:Pāyiram > adhikaram:Vaan Sirappu |

---

## Use Cases Demonstrated

### 1. **Literary Analysis**
Track how key concepts like "virtue" (அறம்), "world" (உலகு), and "happiness" (இன்பம்) are used across different Tamil literary works.

### 2. **Linguistic Study**
Observe how the same root word appears in different forms due to Tamil grammar and sandhi rules:
- அறம் (base form)
- அறத்தான் (ablative case)
- அறத்தொடு (sociative case)

### 3. **Comparative Literature**
Compare how different authors use the same concepts:
- Thiruvalluvar focuses on virtue leading to happiness
- Kambar describes virtuous kings
- Ilango Adigal emphasizes living virtuously with love

### 4. **Concordance Building**
Create a complete concordance showing every occurrence of important words across the entire Tamil literary canon.

### 5. **Word Frequency Analysis**
Determine which words are most common across works or within specific works.

---

## Database Design Benefits

### 1. Word Root Tracking
By storing `word_root` separately from `word_text`, we can:
- Find all forms of a word (உலகு, உலகம், உலகத்து, etc.)
- Track morphological variations
- Build comprehensive word families

### 2. Hierarchical Context
Every word includes its complete hierarchical path:
- Work → Section → Verse → Line → Word
- Enables precise citation and reference

### 3. Cross-Work Analysis
The same schema works for all literary works, enabling:
- Cross-work queries
- Comparative analysis
- Unified search across corpus

### 4. Sandhi Split Tracking
The `sandhi_split` field preserves compound word structure:
- எழுத்தெல்லாம் = எழுத்து + எல்லாம் (letters + all)
- அறத்தொடு = அறம் + ஒடு (virtue + with)

---

## Loading Sample Data

To load this sample data into your database:

```bash
# After loading the main schema
psql $NEON_DB_URL -f sql/schema.sql

# Load the sample word data
psql $NEON_DB_URL -f sql/sample_word_data.sql
```

Or if testing locally:

```bash
psql -U postgres -d tamil_literature < sql/schema.sql
psql -U postgres -d tamil_literature < sql/sample_word_data.sql
```

---

## Next Steps

1. **Populate with complete texts** - Add all 1,330 kurals of Thirukkural
2. **Add more works** - Include Sangam literature, Tolkappiyam
3. **Build word frequency tables** - Create materialized views for common queries
4. **Add translations** - Include English and other language translations
5. **Create API** - Build REST API using PostgREST for web access

---

## Summary Statistics

Based on sample data:

- **Total Works**: 3 (Thirukkural, Kambaramayanam, Silapathikaram)
- **Total Verses**: 6
- **Total Lines**: 15
- **Total Words**: 57
- **Unique Root Words**: ~40
- **Words Appearing in Multiple Works**: 5 key words
- **Words Appearing in Multiple Verses (Same Work)**: 1 (உலகு in Thirukkural)

This demonstrates the database's power to track word usage at granular level while maintaining relationships across the entire literary corpus.
