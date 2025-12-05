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

# For Windows (using setup scripts)
setup_database.bat        # Batch script
setup_database.ps1        # PowerShell script
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

```bash
cd scripts

# Import Thirukkural (all 1,330 kurals)
python thirukkural_parser.py [database_url]

# Import Sangam literature (18 works)
python sangam_parser.py [database_url]

# Import Silapathikaram (epic in 3 Kandams)
python silapathikaram_parser.py [database_url]

# Import Kambaramayanam (epic in 6 Kandams)
python kambaramayanam_parser.py [database_url]

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

**Available Parsers:**
- `thirukkural_bulk_import.py` - 3 Paals → 10 Iyals → 133 Adhikarams → 1,330 Kurals
  - Reference implementation for bulk COPY pattern
- `thirukkural_parser.py` - Alternative row-by-row version (slower, avoid for new parsers)
- `sangam_parser.py` - 18 works with different formats (Thogai/Padal)
- `silapathikaram_parser.py` - 3 Kandams → Kaathais → Verses (uses bulk COPY)
  - Structure: $ marks Kandam, # marks Kaathai
  - Cleans ** markers and line numbers
- `kambaramayanam_parser.py` - 6 Kandams → Padalams → Verses (uses bulk COPY)
  - Structure: & marks Kandam, @ marks Padalam, # marks verse
  - Yuddha Kandam split into 4 parts (61-64) under parent section
  - Cleans ** and *** markers

**Schema Fields Reference (from sql/schema.sql):**
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

## Important File Locations

### Documentation
- `README.md` - Project overview and quick start
- `QUICK_START.md` - 5-minute setup guide
- `PROJECT_NOTES.md` - Development status and notes
- `NEON_SETUP_GUIDE.md` - Cloud database hosting guide
- `tamil_literature_database_guide.md` - Comprehensive DB documentation
- `scripts/WORD_SEGMENTATION_PRINCIPLES.md` - Word parsing guidelines

### Database
- `sql/schema.sql` - Core database schema
- `sql/complete_setup.sql` - Schema + sample data
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

1. Update `sql/schema.sql` with changes
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
