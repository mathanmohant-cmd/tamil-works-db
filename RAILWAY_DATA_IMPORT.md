# Railway Data Import Guide

Your backend is deployed and healthy, but the word search returns no results because the database is empty. You need to import the Tamil literature data.

## Current Status Check

Test your backend:
```bash
# Check works (should return empty array or works without verses)
curl https://your-backend.railway.app/works

# Check stats (should show 0 words)
curl https://your-backend.railway.app/stats
```

---

## Method 1: Import via Railway CLI (Recommended)

### Step 1: Install Railway CLI
```bash
npm install -g @railway/cli
```

### Step 2: Login and Link
```bash
railway login
railway link
```

### Step 3: Import Database Schema
```bash
# Make sure you're in the project root
cd C:\Claude\Projects\tamil-works-db

# Import schema
railway run psql $DATABASE_URL < sql/complete_setup.sql
```

### Step 4: Import Thirukkural Data (~3 seconds)
```bash
# Option A: Run script on Railway
railway run python scripts/thirukkural_bulk_import.py

# Option B: Run locally with Railway database
cd scripts
railway run python thirukkural_bulk_import.py
```

Expected output:
```
======================================================================
Thirukkural Bulk Import - Fast 2-Phase Import
======================================================================
Database: postgresql://...
  Creating Thirukkural work entry...
  Starting IDs: section=1, verse=1, line=1, word=1

Phase 1: Parsing திருக்குறள்.txt...
  Parsed 1330 kurals
  - Sections: 135
  - Verses: 1330
  - Lines: 2660
  - Words: 26000+

Phase 2: Bulk inserting into database...
  Inserting 135 sections...
  Inserting 1330 verses...
  Inserting 2660 lines...
  Inserting 26000+ words...
✓ Phase 2 complete: All data inserted

✓ Import complete!
```

### Step 5: Import Sangam Literature (~30 seconds, optional)
```bash
railway run python scripts/sangam_bulk_import.py
```

This imports 18 Sangam works (thousands of verses).

---

## Method 2: Import from Local Machine

### Prerequisites
- PostgreSQL client installed (`psql` command)
- Railway database connection string

### Step 1: Get Database URL
1. Go to Railway dashboard
2. Click PostgreSQL service
3. Go to "Connect" tab
4. Copy "Postgres Connection URL"

### Step 2: Import Schema
```bash
psql "YOUR_DATABASE_URL" < sql/complete_setup.sql
```

### Step 3: Import Data with Local Scripts
```bash
# Set DATABASE_URL environment variable
export DATABASE_URL="YOUR_DATABASE_URL"  # Mac/Linux
set DATABASE_URL=YOUR_DATABASE_URL       # Windows CMD
$env:DATABASE_URL="YOUR_DATABASE_URL"    # Windows PowerShell

# Import Thirukkural
cd scripts
python thirukkural_bulk_import.py

# Import Sangam (optional)
python sangam_bulk_import.py
```

---

## Verify Import Success

### Check via API
```bash
# Check statistics
curl https://your-backend.railway.app/stats

# Expected response:
{
  "total_works": 1,
  "total_verses": 1330,
  "total_lines": 2660,
  "total_words": 26000+,
  "distinct_words": 8000+,
  "unique_roots": 0
}

# Test search
curl "https://your-backend.railway.app/search?q=அறம்"

# Should return results with Tamil words
```

### Check via Database
```bash
railway run psql $DATABASE_URL

# Then run:
SELECT COUNT(*) FROM works;      -- Should be 1 (Thirukkural)
SELECT COUNT(*) FROM verses;     -- Should be 1330
SELECT COUNT(*) FROM words;      -- Should be ~26000
SELECT COUNT(DISTINCT word_text) FROM words;  -- Should be ~8000

# Exit psql
\q
```

---

## Troubleshooting

**Script can't find text files:**
```
FileNotFoundError: Tamil-Source-TamilConcordence/...
```
- Text files are NOT in git (they're in .gitignore)
- Download Tamil source files separately
- Place in project root: `Tamil-Source-TamilConcordence/`

**Connection timeout:**
```
psycopg2.OperationalError: server closed connection
```
- Use bulk import scripts (not the old parsers)
- `thirukkural_bulk_import.py` and `sangam_bulk_import.py` are optimized
- They complete in seconds, not minutes

**Permission denied:**
```
ERROR: permission denied for table works
```
- Check DATABASE_URL points to the correct database
- Verify Railway PostgreSQL service is running
- Re-copy the connection string from Railway

**Foreign key errors:**
```
ForeignKeyViolation: work_id not found
```
- Schema not loaded properly
- Re-run: `railway run psql $DATABASE_URL < sql/complete_setup.sql`
- Then import data again

---

## Quick Commands Summary

```bash
# 1. Setup (one time)
npm install -g @railway/cli
railway login
railway link

# 2. Import schema
railway run psql $DATABASE_URL < sql/complete_setup.sql

# 3. Import data
railway run python scripts/thirukkural_bulk_import.py

# 4. Verify
curl https://your-backend.railway.app/stats
```

---

## Data Source Files

The import scripts need these text files (NOT in git):
```
Tamil-Source-TamilConcordence/
├── 3_சங்க_இலக்கியம்_பதினெண்கீழ்க்கணக்கு/
│   └── திருக்குறள்.txt
└── 2_Sangam_Literature/
    ├── குறுந்தொகை.txt
    ├── நற்றிணை.txt
    ├── ஐங்குறுநூறு.txt
    └── ... (15 more files)
```

You need to have these files locally to run the import scripts.

---

## After Import

Once data is imported:
1. Test search API: `curl "https://your-backend.railway.app/search?q=அறம்"`
2. Frontend should work: `https://your-frontend.railway.app`
3. Search for Tamil words in the UI
4. Results should appear with verse context

If frontend still shows "No results":
- Check browser console for CORS errors
- Verify `VITE_API_URL` in frontend environment variables
- Ensure backend `ALLOWED_ORIGINS` includes frontend URL
