# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Tamil literature database and search application that stores and analyzes five major Tamil literary works with word-level granularity. The system consists of:
- PostgreSQL database with hierarchical data model
- FastAPI REST API backend
- Vue.js 3 frontend with Vite
- Python parsers for importing Tamil literature texts

**Supported Works:**
1. Tolkāppiyam (தொல்காப்பியம்) - Ancient grammar text
2. Sangam Literature (சங்க இலக்கியம்) - Classical poetry
3. Thirukkural (திருக்குறள்) - 1,330 ethical couplets
4. Silapathikaram (சிலப்பதிகாரம்) - Epic narrative
5. Kambaramayanam (கம்பராமாயணம்) - Tamil Ramayana

**Note:** Experimental grammar analysis tools (morphology analyzer, pronunciation evaluator) are located in `tamil-grammar-tools/` directory. These are separate side projects for future exploration and not part of the main search application.

## Common Commands

### Database Setup

```bash
# Local PostgreSQL setup
createdb tamil_literature
psql tamil_literature -f sql/complete_setup.sql

# Verify database
psql tamil_literature -f verify_setup.sql

# Connect to database
psql tamil_literature

# For Windows (using Python setup script)
python scripts/setup_database.py
```

### Backend (FastAPI)

```bash
cd webapp/backend

# Install dependencies
pip install -r requirements.txt

# Configure database connection
# Create .env file with: DATABASE_URL=postgresql://localhost/tamil_literature

# Run development server (port 8000)
python main.py

# Test API health
curl http://localhost:8000/health

# View API documentation
# http://localhost:8000/docs (Swagger UI)
# http://localhost:8000/redoc (ReDoc)
```

### Frontend (Vue.js)

```bash
cd webapp/frontend

# Install dependencies
npm install

# Run development server (port 5173)
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

### Data Import Scripts

**IMPORTANT: All parsers use the 2-phase bulk COPY pattern for optimal performance (1000x faster than row-by-row INSERT).**

```bash
cd scripts

# Import Thirukkural (all 1,330 kurals)
python thirukkural_bulk_import.py [database_url]

# Import Sangam literature (18 works)
python sangam_bulk_import.py [database_url]

# Import Silapathikaram (epic in 3 Kandams)
python silapathikaram_bulk_import.py [database_url]

# Import Manimegalai (epic with 1 Pathigam and 30 Kathais)
python manimegalai_bulk_import.py [database_url]

# Import Seevaka Sinthamani (epic in 14 Ilampagams)
python seevaka_sinthamani_bulk_import.py [database_url]

# Import Valayapathi (fragmentary epic - 72 verses)
python valayapathi_bulk_import.py [database_url]

# Import Kundalakesi (fragmentary epic - 19 verses)
python kundalakesi_bulk_import.py [database_url]

# Import Kambaramayanam (epic in 6 Kandams)
python kambaramayanam_bulk_import.py [database_url]

# ===== MASTER IMPORT SCRIPTS =====
# Import all Eighteen Lesser Texts at once (பதினெண்கீழ்க்கணக்கு)
python import_eighteen_lesser_texts.py [database_url]
# Includes: Thirukkural + 17 other works (2,161 total verses)

# All parsers support:
# - DATABASE_URL environment variable
# - Command line argument for database URL
# - Default: postgresql://postgres:postgres@localhost/tamil_literature

# Generate ER diagram
python generate_er_diagram.py

# General database setup
python setup_database.py
```

### Running Tests

```bash
# Test database views
psql tamil_literature -f test_views.sql

# Verify complete setup
psql tamil_literature -f verify_setup.sql
```

## Architecture Overview

### Database Schema Architecture

The database uses a **flexible hierarchical model** that accommodates different organizational structures for each literary work:

```
Work (meta-level)
  └─> Sections (recursive hierarchy)
       └─> Verses (atomic textual units)
            └─> Lines
                 └─> Words (with linguistic metadata)
```

**Key Design Principles:**
- Self-referencing `sections` table allows unlimited hierarchical depth
- Each work has its own hierarchy (Thirukkural: Paal→Iyal→Adhikaram, Kambaramayanam: Kandam→Padalam)
- Every word stored with position, root form, part of speech, and sandhi split
- Pre-computed views (`verse_hierarchy`, `word_details`) for fast queries

**Core Tables:**
- `works` - 5 literary works with metadata
- `sections` - Flexible hierarchical structure (paal, kandam, adhikaram, padalam, etc.)
- `verses` - Atomic textual units (kurals, poems, sutras)
- `lines` - Individual lines within verses
- `words` - Every word with position and linguistic analysis
- `commentaries` - Traditional commentaries
- `cross_references` - Links between related verses

### Backend Architecture (FastAPI)

Located in `webapp/backend/`:

**main.py** - FastAPI application with endpoints:
- `/search` - Word search with filters (exact/partial, by work, by root)
- `/works` - List all works
- `/roots` - Get word roots
- `/verse/{id}` - Get complete verse with context
- `/stats` - Database statistics
- `/health` - Health check

**database.py** - Database abstraction layer:
- Connection pooling via psycopg2
- SQL query construction for searches
- Hierarchical data retrieval
- Word frequency analysis

**Configuration:**
- Database URL via `.env` file (use `.env.example` as template)
- CORS configured for Vue.js dev server (localhost:5173, 3000, 8080)
- API runs on port 8000 by default

### Frontend Architecture (Vue.js)

Located in `webapp/frontend/`:

**Tech Stack:**
- Vue 3 (Composition API)
- Vite (build tool and dev server)
- Axios (HTTP client)

**Key Files:**
- `src/App.vue` - Main search interface component
- `src/style.css` - Global styles
- `index.html` - Entry HTML
- `vite.config.js` - Vite configuration

### Data Import Architecture

**IMPORTANT: All parsers MUST use the 2-phase bulk COPY import pattern for optimal performance (1000x faster than individual INSERTs).**

Parser scripts in `scripts/` directory follow this pattern:

**Phase 1: Parse into memory**
1. **Load structural metadata** from JSON files (e.g., `thirukkural_structure.json`)
2. **Parse concordance files** into memory as lists of dictionaries
3. **Apply word segmentation** following Professor P. Pandiaraja's principles
4. **Build complete hierarchy** in memory - works → sections → verses → lines → words
5. **Pre-allocate all IDs** using `SELECT COALESCE(MAX(id), 0) + 1` pattern

**Phase 2: Bulk insert using PostgreSQL COPY**
1. Use `psycopg2.cursor.copy_from()` with StringIO buffers
2. Insert in order: sections → verses → lines → words
3. Single commit after all data inserted

**Key Parser Features:**
- 2-phase bulk COPY pattern (NOT row-by-row INSERTs)
- Pre-allocated ID ranges for all tables
- In-memory data structures (lists of dicts)
- PostgreSQL COPY command for bulk insert
- Word root extraction and part-of-speech tagging
- Sandhi split analysis for compound words
- Single transaction for data integrity

**CRITICAL ID Allocation Patterns (lessons from 2025-12-05):**
1. **Query MAX IDs at initialization**: ALWAYS query `SELECT COALESCE(MAX(id), 0) + 1` for ALL tables (sections, verses, lines, words) at the start of `__init__()` or before parsing
2. **NEVER hardcode IDs to 1**: Parsers must work when run in any order after other works have been imported
3. **For multiple works in one script** (like Sangam with 18 works):
   - Query MAX(work_id) ONCE before the loop
   - Increment manually: `next_work_id += 1` after each new work
   - DO NOT query MAX inside the loop (causes duplicate work_ids)
4. **Schema has no auto-sequences**: The schema uses `INTEGER PRIMARY KEY` (not SERIAL), so parsers must manually manage IDs
5. **Drop sequences when resetting**: The `setup_railway_db.py` script drops sequences when dropping tables to ensure clean state

**Available Parsers (all use bulk COPY pattern):**
- `thirukkural_bulk_import.py` - 3 Paals → 10 Iyals → 133 Adhikarams → 1,330 Kurals
  - Reference implementation for bulk COPY pattern
- `sangam_bulk_import.py` - 18 works with different formats (Thogai/Padal)
  - Improved: Ignores dots, line count numbers, keeps only Tamil + - and _
- `silapathikaram_bulk_import.py` - 3 Kandams → Kaathais → Verses
  - Structure: $ marks Kandam, # marks Kaathai
  - Cleans ** markers and line numbers
- `manimegalai_bulk_import.py` - 1 Pathigam + 30 Kathais (each Kathai = ONE verse)
  - Structure: # marks sections (Pathigam #0, Kathais #1-#30)
  - IMPORTANT: Each Kathai is ONE complete verse (blank lines are for readability)
  - Cleans line numbers (multiples of 5)
- `seevaka_sinthamani_bulk_import.py` - 14 Ilampagams → 3,146 verses
  - Structure: @ marks Ilampagams, # marks verses
  - Each # section is ONE complete verse (typically 4 lines)
  - Cleans line numbers and alignment dots
- `valayapathi_bulk_import.py` - 72 verses (fragmentary, no hierarchical structure)
  - Structure: # marks verses (simple flat structure)
  - Creates default section to hold all verses
  - Lost epic, only fragments survive
- `kundalakesi_bulk_import.py` - 19 verses (fragmentary, no hierarchical structure)
  - Structure: # marks verses (simple flat structure)
  - Creates default section to hold all verses
  - Lost Buddhist epic, only fragments survive
- `kambaramayanam_bulk_import.py` - 6 Kandams → Padalams → Verses
  - Structure: & marks Kandam, @ marks Padalam, # marks verse
  - Yuddha Kandam split into 4 parts (61-64) under parent section
  - Cleans ** and *** markers

**Schema Fields Reference (from sql/complete_setup.sql):**
- **sections**: section_id, work_id, parent_section_id, level_type, level_type_tamil, section_number, section_name, section_name_tamil, sort_order
- **verses**: verse_id, work_id, section_id, verse_number, verse_type, verse_type_tamil, total_lines, sort_order
- **lines**: line_id, verse_id, line_number, line_text (NO sort_order column)
- **words**: word_id, line_id, word_position, word_text, sandhi_split (NO sort_order column, use word_position not word_number)

## Key Patterns and Conventions

### Database Queries

When querying words, always use the `word_details` view instead of joining tables manually:

```sql
-- Good: Use pre-computed view
SELECT * FROM word_details WHERE word_text = 'அறம்';

-- Avoid: Manual joins (slower and error-prone)
SELECT w.*, l.*, v.*, s.*
FROM words w
JOIN lines l ON w.line_id = l.line_id
-- ... multiple joins ...
```

### Hierarchical Queries

Use `verse_hierarchy` view for getting full hierarchical paths:

```sql
SELECT vh.hierarchy_path, l.line_text
FROM verses v
JOIN verse_hierarchy vh ON v.verse_id = vh.verse_id
JOIN lines l ON v.verse_id = l.verse_id
WHERE v.section_id = 6
ORDER BY v.verse_number, l.line_number;
```

### Adding New Data

Always insert in this order to maintain referential integrity:
1. Insert into `works` (if new work)
2. Create hierarchy in `sections` (top-level first)
3. Add verses to `verses`
4. Insert lines into `lines`
5. Break down and insert words into `words`

### Word Segmentation

Follow the principles documented in `scripts/WORD_SEGMENTATION_PRINCIPLES.md`:
- Respect traditional Tamil grammar rules
- Split compound words appropriately
- Tag word roots consistently
- Document sandhi transformations

### Frontend Sort Order Preservation (CRITICAL)

**NEVER merge or concatenate search results on the frontend.** The backend returns results in the correct sort order based on the `sort_by` parameter (alphabetical/canonical/chronological/collection). Any client-side array operations will destroy this ordering.

**Anti-pattern (WRONG):**
```javascript
// DON'T DO THIS - destroys backend sort order
const existingResults = searchResults.value.results.filter(r => r.word_text !== wordText)
searchResults.value.results = [...existingResults, ...response.data.results]
```

**Correct pattern:**
```javascript
// ALWAYS use ONLY the new results from backend
searchResults.value = {
  ...searchResults.value,
  results: response.data.results  // Backend-sorted, do not merge
}
```

**Why this matters:**
- Collection order sorting requires JOINs with `work_collections` table to get `position_in_collection`
- Backend performs complex SQL ORDER BY with multiple fallback levels
- Frontend has no access to this ordering metadata
- Merging arrays concatenates them sequentially, losing the intended order

**Common bug locations:**
1. **App.vue `selectWordFromList`** (lines ~700-709): Don't merge `[...existingResults, ...newResults]`
2. **App.vue `getSortedWordOccurrences`** (lines ~1170-1176): Don't re-sort the results, backend already sorted them

**Test to verify:**
Search for "சொல்" with "Collection Order" (Sangam Literature), expand a word, verify தொல்காப்பியம் (position 1) appears first.

See `TESTING_CHECKLIST.md` for complete test scenarios.

## Important File Locations

### Documentation
- `README.md` - Project overview and quick start
- `QUICK_START.md` - 5-minute setup guide
- `PROJECT_NOTES.md` - Development status and notes
- `NEON_SETUP_GUIDE.md` - Cloud database hosting guide
- `tamil_literature_database_guide.md` - Comprehensive DB documentation
- `scripts/WORD_SEGMENTATION_PRINCIPLES.md` - Word parsing guidelines

### Database
- `sql/complete_setup.sql` - Core database schema (canonical)
- `sql/queries.sql` - 100+ example queries
- `sql/sample_word_data.sql` - Sample word-level data
- `verify_setup.sql` - Database verification queries
- `test_views.sql` - View testing

### Configuration
- `webapp/backend/.env` - Backend database connection (not in git)
- `webapp/backend/.env.example` - Template for .env file
- `webapp/backend/requirements.txt` - Python dependencies
- `webapp/frontend/package.json` - Node.js dependencies
- `webapp/frontend/vite.config.js` - Vite build configuration

### Data Files
- `*conc_full.txt` - Concordance files for each work
- `scripts/thirukkural_structure.json` - Thirukkural hierarchy metadata

## Development Workflow

### Setting Up New Development Environment

1. Clone repository
2. Set up PostgreSQL database (local or Neon cloud)
3. Run `sql/complete_setup.sql` to create schema
4. Configure backend `.env` with database URL
5. Install backend dependencies: `pip install -r webapp/backend/requirements.txt`
6. Install frontend dependencies: `npm install` in `webapp/frontend/`
7. Start backend: `python webapp/backend/main.py`
8. Start frontend: `npm run dev` in `webapp/frontend/`

### Adding New Literary Work

1. Add work metadata to `works` table
2. Create hierarchical structure in `sections` table
3. Create parser script in `scripts/` directory
4. Follow existing parser patterns (see `thirukkural_parser.py`)
5. Test with small dataset first
6. Run full import with transaction support

### Making Database Schema Changes

1. Update `sql/complete_setup.sql` with changes
2. Update views if affected (`verse_hierarchy`, `word_details`)
3. Update `database.py` queries if table structure changed
4. Test with `verify_setup.sql`
5. Document changes in comments

### API Development

1. Add endpoint to `webapp/backend/main.py`
2. Add database query method to `database.py`
3. Define Pydantic models for request/response
4. Test via `/docs` endpoint (Swagger UI)
5. Update frontend to consume new endpoint

## Database Hosting

**Neon (Recommended):**
- Free tier: 3GB storage, unlimited requests
- Auto-suspend when inactive
- 10 database branches for testing
- See `NEON_SETUP_GUIDE.md` for setup

**Alternative Hosting:**
- AWS RDS PostgreSQL
- DigitalOcean Managed PostgreSQL
- Heroku Postgres
- Local PostgreSQL 14+

## Performance Considerations

- Indexes already created on foreign keys and search columns
- Use `word_details` and `verse_hierarchy` views for common queries
- For large result sets, use pagination (limit/offset)
- Consider full-text search indexes for production (commented in schema)
- Connection pooling handled by psycopg2

## Tamil Text Handling

- All tables use UTF-8 encoding for full Tamil Unicode support
- Use Tamil input methods for entering search terms
- Transliteration fields available but optional
- Respect traditional orthography in data entry

## Frontend UI/UX Terminology and Design Patterns

**IMPORTANT: Use this established vocabulary when discussing the search interface.**

### Search Results Interface Terminology

- **Found Words Summary** = The overall search statistics displayed at the top showing the format: "X Works | Y Verses | Z Distinct Words | W Usage"
  - **Works** = Number of unique literary works containing the search results
  - **Verses** = Total number of verses containing the search results
  - **Distinct Words** = Number of unique word forms found
  - **Usage** = Total number of word occurrences across all works

- **Found Words Summary Header** = The top bar area containing:
  - Found Words Summary (statistics text)
  - "Export Words" button (exports the list of unique words with counts)

- **Found Words Rows** = The numbered list of found words displayed below the header, where each row shows:
  - Sequential number (1., 2., 3., ...)
  - Word text in Tamil
  - Usage count badge
  - Dictionary lookup icon (📖)
  - Expand/Collapse button

- **Selected Word Summary Area** = The expanded section that appears when a user clicks "Expand" on a word, containing:
  - Word-specific statistics: "X Works | Y Verses | Z Usage"
  - "Export Lines" button (exports all line occurrences for that word)
  - List of line occurrences with full context

### Search Interface Design Pattern

**Layout:** Single-panel collapsible design (NOT two-panel)
- Do not use side-by-side panels for words and occurrences
- Use expandable/collapsible rows for each word

**Data Loading Strategy:**
1. Initial search uses `limit=0` to fetch only word counts and metadata (no line occurrences)
2. Backend returns `unique_words` array with `verse_count` and `work_breakdown` for each word
3. When user expands a word, batch load 100 occurrences at a time
4. "Load More" button appears if more than 100 occurrences exist
5. Each "Load More" click fetches the next 100 occurrences and appends to the list

**Mobile Responsiveness:**
- Match Type and Word Position filter groups stack vertically on mobile (max-width: 968px)
- Found Words Rows adapt to smaller screens
- Selected Word Summary Area uses vertical layout on mobile

**Export Functionality:**
- **"Export Words"** button (in Found Words Summary Header): Exports CSV of all unique words with their usage counts
- **"Export Lines"** button (in Selected Word Summary Area): Exports CSV of all line occurrences for the specific expanded word

### Frontend Implementation Details

- **Framework:** Vue.js 3 with Composition API
- **Build Tool:** Vite (includes Hot Module Replacement for instant updates during development)
- **HTTP Client:** Axios for API calls
- **State Management:**
  - `expandedWords` = Set of currently expanded word texts
  - `loadedOccurrences` = Object tracking offset and hasMore status for each word
  - `searchResults.unique_words` = Array of word metadata from backend (includes verse_count, work_breakdown)

### Backend API Response Structure

When searching with `limit=0`:
```json
{
  "results": [],  // Empty initially
  "unique_words": [
    {
      "word_text": "அறம்",
      "count": 213,  // Total usage count
      "verse_count": 213,  // Number of verses containing this word
      "work_breakdown": [  // Array of works (may have duplicates, aggregate on frontend)
        {"work_name": "Thirukkural", "work_name_tamil": "திருக்குறள்", "count": 1},
        // ... more entries
      ]
    }
  ],
  "total_count": 213,
  "limit": 0,
  "offset": 0
}
```

**Note:** The `work_breakdown` array contains one entry per verse (not per work), so the frontend must aggregate by `work_name` to get unique work counts and total usage per work.
