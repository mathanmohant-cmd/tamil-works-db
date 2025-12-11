# Deploying Database Changes to Railway

## Changes Required
This deployment updates the `word_details` view to display Tamil verse types correctly and fixes Kambaramayanam data.

## Option 1: Using Railway CLI (Recommended)

### Prerequisites
```bash
# Install Railway CLI (if not already installed)
npm install -g @railway/cli

# Login to Railway
railway login

# Link to your project
railway link
```

### Apply Migration
```bash
# Run the migration script
railway run psql $DATABASE_URL < migrations/2025-12-11_fix_verse_type_tamil.sql
```

### Restart Backend
After applying the migration, restart your backend service in Railway dashboard to clear cached view metadata.

## Option 2: Using Railway Dashboard PostgreSQL Client

1. Go to your Railway project dashboard
2. Click on the **PostgreSQL** service
3. Click on the **Data** tab
4. Copy the contents of `migrations/2025-12-11_fix_verse_type_tamil.sql`
5. Paste into the SQL query editor
6. Click **Run Query**
7. Restart the backend service

## Option 3: Using psql from Local Machine

### Get Database URL
1. Go to Railway dashboard
2. Click on PostgreSQL service
3. Click on **Connect** tab
4. Copy the **Database Connection URL**

### Run Migration
```bash
# Replace YOUR_RAILWAY_DATABASE_URL with the actual URL
psql "YOUR_RAILWAY_DATABASE_URL" < migrations/2025-12-11_fix_verse_type_tamil.sql
```

## Verification

After applying the migration, verify it worked:

### Test 1: Check API Response
```bash
# Replace YOUR_BACKEND_URL with your Railway backend URL
curl "https://YOUR_BACKEND_URL/search?q=அறம்&limit=1" | jq '.results[0].verse_type_tamil'

# Should return: "குறள்" or "பாடல்" or "நூற்பா" (not null or missing)
```

### Test 2: Check in Browser
1. Open your deployed frontend
2. Search for any word (e.g., "அறம்")
3. Expand a word to see occurrences
4. Verify hierarchy shows Tamil verse types:
   - திருக்குறள் shows "குறள்" (not "kural")
   - அகநானூறு shows "பாடல்" (not "poem")
   - தொல்காப்பியம் shows "நூற்பா" (not "nurpaa")

### Test 3: Query Database Directly
```sql
-- In Railway PostgreSQL Data tab or via psql
SELECT verse_type, verse_type_tamil, work_name
FROM word_details
WHERE work_name IN ('Thirukkural', 'Kambaramayanam', 'Tolkappiyam')
LIMIT 3;

-- Should show verse_type_tamil with Tamil text
```

## Important Notes

1. **No Data Loss**: This migration only updates views and fixes existing data, it does not delete anything.

2. **Backend Restart Required**: After applying the migration, you MUST restart the backend service in Railway:
   - Go to backend service in Railway dashboard
   - Click on the **⋮** menu
   - Select **Restart**
   - This clears psycopg2's cached view metadata

3. **Frontend Cache**: Users may need to hard refresh (Ctrl+Shift+R) to see changes.

4. **Rollback**: If needed, you can rollback by recreating the old view:
   ```sql
   DROP VIEW IF EXISTS word_details CASCADE;

   CREATE VIEW word_details AS
   SELECT
       w.word_id,
       w.word_text,
       w.word_text_transliteration,
       w.word_root,
       w.word_type,
       w.word_position,
       w.sandhi_split,
       w.meaning,
       l.line_id,
       l.line_number,
       l.line_text,
       v.verse_id,
       v.verse_number,
       v.verse_type,           -- OLD: from verses table
       v.verse_type_tamil,     -- OLD: from verses table
       vh.work_name,
       vh.work_name_tamil,
       vh.hierarchy_path,
       vh.hierarchy_path_tamil
   FROM words w
   INNER JOIN lines l ON w.line_id = l.line_id
   INNER JOIN verses v ON l.verse_id = v.verse_id
   INNER JOIN verse_hierarchy vh ON v.verse_id = vh.verse_id;
   ```

## Troubleshooting

### Issue: verse_type_tamil still showing as null in API
**Solution**: Restart the backend service in Railway dashboard. psycopg2 caches view metadata.

### Issue: Migration fails with "relation does not exist"
**Solution**: Ensure you've run the schema setup first (`sql/schema.sql` or `sql/complete_setup.sql`)

### Issue: Kambaramayanam still shows wrong verse type
**Solution**: The UPDATE might have failed. Run just the UPDATE part:
```sql
UPDATE verses
SET verse_type = 'verse', verse_type_tamil = 'பாடல்'
WHERE work_id IN (SELECT work_id FROM works WHERE work_name = 'Kambaramayanam');
```

## Timeline
- **Migration Time**: ~1-2 seconds
- **Backend Restart**: ~30 seconds
- **Total Downtime**: None (view updates are atomic, restart causes brief interruption)

## Checklist

- [ ] Migration file created: `migrations/2025-12-11_fix_verse_type_tamil.sql`
- [ ] Migration applied to Railway database
- [ ] Verification queries show verse_type_tamil columns
- [ ] Backend service restarted in Railway
- [ ] API test shows verse_type_tamil in response
- [ ] Frontend displays Tamil verse types correctly
- [ ] All works tested (திருக்குறள், தொல்காப்பியம், அகநானூறு, கம்பராமாயணம்)
