# Railway Deployment Fix Guide

## Problem

The `/search` endpoint returns 500 errors on Railway because:
1. Parser scripts for Silapathikaram and Kambaramayanam were updated to set `verse_type='poem'` and `verse_type_tamil='பாடல்'`
2. Railway database was imported before these script updates
3. Views need to be refreshed to pick up the new data

## Clean Solution

Run this single, idempotent migration script on Railway:

```bash
psql $DATABASE_URL -f migrations/2025-12-11_complete_fix.sql
```

This script:
- ✓ Uses work names instead of hardcoded IDs
- ✓ Is idempotent (safe to run multiple times)
- ✓ Updates data and refreshes views in correct order
- ✓ Provides verification output
- ✓ Uses proper PL/pgSQL with error handling

## What It Does

1. **Updates verse_type fields** for Silapathikaram and Kambaramayanam (only NULL values)
2. **Refreshes views** (verse_hierarchy, word_details) to pick up the changes
3. **Verifies** the fix with summary queries

## Deploy Updated Backend

After running the migration, deploy the updated backend code to Railway:

```bash
git add webapp/backend/main.py
git commit -m "Add detailed error logging to search endpoint"
git push
```

The updated `main.py` includes detailed error logging to help diagnose future issues.

## Verification

After deployment, test the search endpoint:

```bash
curl "https://your-app.railway.app/search?q=சொல்&match_type=exact&word_position=beginning&limit=0"
```

Should return a valid JSON response with:
- `results`: []
- `unique_words`: [array of words]
- `total_count`: number

## Alternative: Fresh Import (if issues persist)

If the migration doesn't resolve the issue, the cleanest approach is to re-import the data:

1. Drop and recreate Railway database
2. Run schema setup: `psql $DATABASE_URL -f sql/schema.sql`
3. Re-run all parser scripts (they now have correct verse_type values)

## Lessons Learned

**Avoid these patterns:**
- ❌ Hardcoding work IDs (use work names in queries)
- ❌ Quick fixes without testing
- ❌ Multiple migration scripts for same issue

**Follow these patterns:**
- ✓ Single, comprehensive migration script
- ✓ Idempotent operations (safe to re-run)
- ✓ Use work names or other stable identifiers
- ✓ Include verification queries
- ✓ Test locally before deploying
- ✓ Document the "why" not just the "how"

## Related Files

- `migrations/2025-12-11_complete_fix.sql` - Single migration to fix everything
- `scripts/diagnose_railway_error.py` - Diagnostic tool (fixed GROUP BY error)
- `webapp/backend/main.py` - Updated with error logging
- `scripts/silapathikaram_bulk_import.py` - Updated parser
- `scripts/kambaramayanam_bulk_import.py` - Updated parser
