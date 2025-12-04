# Professor P. Pandiaraja's Word Segmentation Principles
## Summary for Database Import

Based on: http://tamilconcordance.in/Principles.html

---

## Key Principles for Our Parser

### 1. **Basic Word Separation**
- **Spaces separate words** - this is our primary delimiter
- Words are already properly segmented by Professor Pandiaraja
- We don't need complex Tamil NLP tokenization - the work is done!

### 2. **Special Characters**

#### **Underscore `_` - Compound Word Marker**
Indicates parts of a compound word that should be counted separately but are part of one semantic unit.

**Examples:**
- `மயிர்_குறை_கருவி` = மயிர் + குறை + கருவி (hair-cutting tool)
- `சில்_பத_உணவு` = சில் + பத + உணவு (special food)
- `அறு_கால்_பறவை` = அறு + கால் + பறவை (six-legged bird)

**Database Strategy:**
```sql
-- Store in words table:
word_text = 'மயிர்_குறை_கருவி'
sandhi_split = 'மயிர் + குறை + கருவி'

-- Also create separate word entries for:
-- மயிர், குறை், கருவி (for search purposes)
```

#### **Hyphen `-` - Particle/Suffix Marker**
Indicates grammatical particles (கட்டுருபன்) that cannot be separated.

**Examples:**
- `விடுநள்-மன்-கொல்லோ` = விடுநள் + particles
- `ஆற்றலர்-மன்னே` = ஆற்றலர் + emphatic particle
- `நாள்-தொறும்` = நாள் + distributive particle
- `செல்க-என` = செல்க + quotative particle

**Database Strategy:**
```sql
-- Store as single word:
word_text = 'விடுநள்-மன்-கொல்லோ'
-- Can extract base later for advanced features
```

### 3. **What NOT to Separate**

#### Already kept together:
- **Case markers (வேற்றுமை உருபுகள்)**: கண்ணை, கண்ணோடு, கண்ணால்
- **Tense markers**: வந்தான், வருகிறான்
- **Compound words**: நல்லோர், பெரியோர்
- **Reduplication**: ஊரூர், வழிவழி, மெல்மெல

### 4. **Parsing Strategy for Our Database**

```python
def parse_line_to_words(line_text):
    """
    Parse Tamil line into words following Pandiaraja's principles
    """
    words = []
    position = 1

    # Split by space
    for token in line_text.split():
        # Clean punctuation if needed
        token = token.strip('.,;!?')

        if not token:
            continue

        # Handle compound words with underscore
        if '_' in token:
            # Store full compound
            words.append({
                'word_text': token,
                'word_position': position,
                'sandhi_split': token.replace('_', ' + '),
                'is_compound': True
            })

            # Also store component words for search
            components = token.split('_')
            for comp in components:
                words.append({
                    'word_text': comp,
                    'word_position': position,
                    'is_component': True,
                    'parent_compound': token
                })

        # Handle particles with hyphen
        elif '-' in token:
            # Store as single word with particle
            words.append({
                'word_text': token,
                'word_position': position,
                'has_particle': True
            })

        # Simple word
        else:
            words.append({
                'word_text': token,
                'word_position': position
            })

        position += 1

    return words
```

---

## Simplified Import Strategy

### Phase 1: Basic Import (NOW)
```python
# For each line:
1. Split by spaces
2. Store each space-separated token as a word
3. Keep _ and - as-is in word_text
4. Position = order in line
```

**Database columns to fill now:**
- `word_text` - exact token (with _ or - if present)
- `word_position` - 1, 2, 3...
- `line_id` - foreign key

**Leave NULL for now:**
- `word_root` ❌
- `word_type` ❌
- `sandhi_split` ❌ (can extract from _ later)
- `meaning` ❌

### Phase 2: Enhanced (LATER)
```sql
-- Extract sandhi splits for compound words
UPDATE words
SET sandhi_split = REPLACE(word_text, '_', ' + ')
WHERE word_text LIKE '%_%';

-- Extract particles
UPDATE words
SET word_type = 'particle'
WHERE word_text LIKE '%-மன்%'
   OR word_text LIKE '%-கொல்%'
   OR word_text LIKE '%-தொறும்%';

-- Add word roots (requires Tamil NLP)
-- Add POS tags (requires Tamil NLP)
-- Add meanings (requires dictionary)
```

---

## Example Parsing

### Input Line:
```
கண்ணை-கொல் மயிர்_குறை_கருவி கொண்டு செல்லும் நாள்-தொறும்
```

### Output Words:
```python
[
    {'word_text': 'கண்ணை-கொல்', 'position': 1},
    {'word_text': 'மயிர்_குறை_கருவி', 'position': 2, 'sandhi_split': 'மயிர் + குறை + கருவி'},
    {'word_text': 'கொண்டு', 'position': 3},
    {'word_text': 'செல்லும்', 'position': 4},
    {'word_text': 'நாள்-தொறும்', 'position': 5}
]
```

### Database Inserts:
```sql
-- 5 word records
INSERT INTO words (line_id, word_position, word_text, sandhi_split) VALUES
(1, 1, 'கண்ணை-கொல்', NULL),
(1, 2, 'மயிர்_குறை_கருவி', 'மயிர் + குறை + கருவி'),
(1, 3, 'கொண்டு', NULL),
(1, 4, 'செல்லும்', NULL),
(1, 5, 'நாள்-தொறும்', NULL);
```

---

## Search Implications

### User searches for: "கண்ணை"
Should match:
- ✅ கண்ணை (exact)
- ✅ கண்ணை-கொல் (partial match with -kol particle)
- ✅ கண்ணைக் (with case marker - if exists)

### User searches for: "குறை"
Should match:
- ✅ குறை (standalone word)
- ✅ மயிர்_குறை_கருவி (compound word containing குறை)

### Implementation:
```sql
-- Simple search (current)
SELECT * FROM word_details
WHERE word_text LIKE '%குறை%';

-- Advanced search (later with _ split handling)
SELECT * FROM word_details
WHERE word_text = 'குறை'
   OR word_text LIKE '%_குறை%'
   OR word_text LIKE '%குறை_%'
   OR word_text LIKE '%_குறை_%';
```

---

## Summary

### ✅ What We Know:
1. **Space = word boundary** (primary rule)
2. **_ = compound parts** (store split in sandhi_split)
3. **- = particles** (keep together, mark for later analysis)
4. **No further tokenization needed** - Professor did the hard work!

### 🚀 What We'll Do:
1. **Split by spaces only**
2. **Store word_text exactly as-is**
3. **Extract sandhi_split from _ for compounds**
4. **Let search handle partial matches**

### 🎯 Result:
- **Simple parser** (30-50 lines of Python)
- **Fast import** (thousands of words per second)
- **Accurate data** (respects scholarly segmentation)
- **Search ready** (all words indexed and searchable)

---

## Ready to Code!

With these principles, we can now create:
1. ✅ Simple, robust parser
2. ✅ Fast bulk import
3. ✅ Immediate search functionality
4. ✅ Foundation for advanced features later

**Next step:** Create the parser scripts!
