# Tamil Literary Works Database

A comprehensive PostgreSQL database schema for storing and analyzing five major Tamil literary works with word-level granularity and hierarchical structure.

## Supported Works

1. **Tolkāppiyam** (தொல்காப்பியம்) - Ancient Tamil grammar text
2. **Sangam Literature** (சங்க இலக்கியம்) - Classical Tamil poetry collections
3. **Thirukkural** (திருக்குறள்) - Classic Tamil couplets on ethics, politics, and love
4. **Silapathikaram** (சிலப்பதிகாரம்) - Epic narrative of Kannagi and Kovalan
5. **Kambaramayanam** (கம்பராமாயணம்) - Tamil version of the Ramayana

## Project Structure

```
tamil-works-db/
├── README.md                  # This file
├── sql/
│   ├── schema.sql            # Complete database schema with sample data
│   └── queries.sql           # 100+ saved queries organized by category
├── docs/
│   ├── database_guide.md     # Comprehensive database documentation
│   └── neon_setup.md         # Step-by-step Neon setup guide
└── scripts/
    └── quick_setup.sh        # Quick setup script
```

## Features

### Flexible Hierarchical Structure
- Supports different organizational levels for each work
- Self-referencing sections table for unlimited depth
- Examples:
  - Thirukkural: Paal → Iyal → Adhikaram → Kural → Line
  - Kambaramayanam: Kandam → Padalam → Verse → Line

### Word-Level Analysis
Every word is stored with:
- Position in line
- Root/base form
- Part of speech
- Sandhi split information (for compound words)
- Meaning/definition

### Powerful Querying
- Find any word with complete hierarchical context
- Word frequency and co-occurrence analysis
- Search by word root to find all derived forms
- Retrieve entire sections with proper ordering
- Compare usage across different works

## Quick Start

### 1. Set Up Neon Database

Follow the detailed guide in `docs/neon_setup.md`:

```bash
# Quick version:
# 1. Create account at https://neon.tech
# 2. Create project named "tamil-literature-db"
# 3. Get connection string
# 4. Set environment variable
export NEON_DB_URL="postgresql://user:pass@host/db?sslmode=require"
```

### 2. Create Database Schema

```bash
# Install the schema
psql $NEON_DB_URL -f sql/schema.sql

# Verify installation
psql $NEON_DB_URL -c "\dt"
```

### 3. Run Sample Queries

```bash
# View all works
psql $NEON_DB_URL -c "SELECT * FROM works;"

# View sample data
psql $NEON_DB_URL -c "SELECT * FROM word_details WHERE work_name = 'Thirukkural' LIMIT 5;"

# Or use the interactive shell
psql $NEON_DB_URL
```

## Database Schema Overview

### Core Tables

- **works** - Literary works (5 records)
- **sections** - Hierarchical structure (paal, kandam, adhikaram, etc.)
- **verses** - Atomic textual units (kurals, poems, sutras)
- **lines** - Individual lines within verses
- **words** - Every word with position information

### Helper Tables

- **commentaries** - Traditional commentaries on verses
- **cross_references** - Links between related verses

### Views

- **verse_hierarchy** - Pre-computed hierarchical paths
- **word_details** - Complete context for every word

## Common Use Cases

### Find a Word

```sql
SELECT word_text, line_text, work_name, hierarchy_path
FROM word_details
WHERE word_text = 'அறம்';
```

### Get Complete Text of a Section

```sql
SELECT vh.hierarchy_path, l.line_text
FROM verses v
JOIN verse_hierarchy vh ON v.verse_id = vh.verse_id
JOIN lines l ON v.verse_id = l.verse_id
WHERE v.section_id = 6
ORDER BY v.verse_number, l.line_number;
```

### Word Frequency Analysis

```sql
SELECT word_text, COUNT(*) as frequency
FROM word_details
WHERE work_name = 'Thirukkural'
GROUP BY word_text
ORDER BY frequency DESC
LIMIT 20;
```

See `sql/queries.sql` for 100+ more queries!

## Documentation

- **`docs/database_guide.md`** - Complete database documentation including:
  - Detailed table descriptions
  - Hierarchical structures for all works
  - Query patterns and examples
  - Performance optimization tips

- **`docs/neon_setup.md`** - Step-by-step setup guide including:
  - Account creation
  - Database connection
  - Client installation
  - Troubleshooting

- **`sql/queries.sql`** - Saved queries organized by:
  - Basic queries
  - Word search
  - Line and verse queries
  - Hierarchical queries
  - Statistical analysis
  - Advanced analysis
  - Cross-references
  - Maintenance
  - Export queries

## Sample Data

The schema includes sample data for:
- All 5 literary works (metadata)
- Thirukkural: First kural (complete with words)
- Kambaramayanam: Structure outline

## Next Steps

1. **Populate the database** with complete texts
2. **Create indexes** based on your query patterns
3. **Build an API** using PostgREST or similar
4. **Add translations** in multiple languages
5. **Include audio** files for recitations

## Data Entry

To add more content, follow this order:

1. Insert work into `works` table
2. Create hierarchical structure in `sections` table
3. Add verses to `verses` table
4. Insert lines into `lines` table
5. Break down and insert words into `words` table

Example:

```sql
-- Add a new kural
INSERT INTO verses (work_id, section_id, verse_number, verse_type, total_lines, sort_order)
VALUES (3, 6, 2, 'kural', 2, 2);

-- Add lines
INSERT INTO lines (verse_id, line_number, line_text)
VALUES (2, 1, 'கற்றதனால் ஆய பயனென்கொல் வாலறிவன்');

-- Add words (for each word in the line)
INSERT INTO words (line_id, word_position, word_text, word_root, word_type)
VALUES (3, 1, 'கற்றதனால்', 'கல்', 'verb');
```

## Database Requirements

- **Database**: PostgreSQL 14+
- **Storage**: ~50-200 MB for all 5 works (text only)
- **Hosting**: Neon (recommended), AWS RDS, DigitalOcean, etc.

## Free Tier Hosting

Neon free tier includes:
- 3 GB storage (plenty for text data)
- Unlimited API requests
- Auto-suspend when inactive
- 10 database branches for testing

## Contributing

To contribute data or improvements:

1. Ensure Tamil text accuracy against authoritative sources
2. Use consistent transliteration (ISO 15919 recommended)
3. Maintain proper `sort_order` for reading sequence
4. Document word roots and sandhi splits
5. Test queries before committing

## License

The database structure is provided as-is. When using this system:
- Respect copyright of original texts
- Provide proper attribution to classical works
- Acknowledge modern translations and commentaries

## Resources

- Neon Documentation: https://neon.tech/docs
- PostgreSQL Documentation: https://www.postgresql.org/docs/
- Tamil Virtual Academy: https://www.tamilvu.org

## Support

For issues or questions:
- Check `docs/database_guide.md` for detailed documentation
- Review `docs/neon_setup.md` for setup troubleshooting
- Examine `sql/queries.sql` for query examples

---

**Project Created**: 2025
**Database Type**: PostgreSQL
**Encoding**: UTF-8 (full Tamil Unicode support)
