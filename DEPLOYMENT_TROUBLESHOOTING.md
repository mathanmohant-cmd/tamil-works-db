# Railway Deployment Troubleshooting

## Common Issues and Solutions

### Issue: Missing DB Stats in Header / "All Works" Search Not Working

**Symptoms:**
- Database stats (22 Works | X Verses...) missing from header
- Search with "All works" returns no results
- Browser console shows: "Fallback: Computing word counts from paginated results - counts may be incomplete!"

**Root Cause:**
Stale frontend build on Railway. The deployed JavaScript bundle doesn't have the latest code that properly handles `unique_words` from the backend API.

**How to Verify:**
1. Test backend directly:
   ```bash
   curl "https://tamil-word-search-api-production.up.railway.app/stats"
   curl "https://tamil-word-search-api-production.up.railway.app/search?q=%E0%AE%85%E0%AE%B1%E0%AE%AE%E0%AF%8D&match_type=partial&limit=0"
   ```
2. Both should return valid data
3. Check browser DevTools → Console for the "Fallback" warning

**Solution:**
Redeploy the frontend to get the latest code:
- **Option A**: Railway Dashboard → Frontend Service → "Redeploy"
- **Option B**: Push any commit to main branch to trigger auto-deploy
- After redeployment: Hard refresh browser with `Ctrl+Shift+R`

**Technical Details:**
- Frontend expects `response.data.unique_words` array from backend
- When missing, it falls back to computing counts from paginated results (incorrect)
- Backend correctly returns `unique_words` in all search responses
- Issue was purely a stale frontend bundle cached on Railway

**Date Resolved:** 2024-12-19
**Fixed in:** Frontend v1.0.1

---

## Deployment Checklist

Before marking a deployment as complete:

- [ ] Test `/stats` endpoint
- [ ] Test `/search` with "All Works" filter
- [ ] Check browser console for errors
- [ ] Verify DB stats appear in header
- [ ] Test search results display correctly
- [ ] Hard refresh browser to clear any cached JS

---

## Railway URLs

- **Frontend:** https://tamil-word-search-ui-production.up.railway.app/
- **Backend API:** https://tamil-word-search-api-production.up.railway.app
- **API Docs:** https://tamil-word-search-api-production.up.railway.app/docs
- **Health Check:** https://tamil-word-search-api-production.up.railway.app/health
