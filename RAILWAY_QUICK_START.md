# Railway Quick Start Guide

## ✅ Your Project is Ready for Railway!

All necessary files have been created:

**Backend:**
- ✅ `webapp/backend/requirements.txt` - Python dependencies
- ✅ `Dockerfile` - Backend container configuration
- ✅ `railway.json` - Railway configuration
- ✅ CORS configured for production

**Frontend:**
- ✅ `webapp/frontend/Dockerfile` - Frontend container configuration
- ✅ `webapp/frontend/nginx.conf` - Nginx server configuration
- ✅ `webapp/frontend/.dockerignore` - Build optimization
- ✅ `webapp/frontend/.env.example` - Environment variables template

**General:**
- ✅ `.gitignore` - Git ignore rules
- ✅ API URL configured via environment variables

## 🚀 Deploy in 7 Steps

### Step 1: Sign up for Railway
1. Go to https://railway.app
2. Click "Start a New Project"
3. Sign in with GitHub

### Step 2: Create GitHub Repository (if not done)
```bash
cd C:\Claude\Projects\tamil-works-db

# Check git status
git status

# If changes exist, commit them
git add .
git commit -m "Ready for Railway deployment"

# Push to GitHub
git push
```

### Step 3: Add PostgreSQL Database First
1. In Railway, click "+ New Project" → "Provision PostgreSQL"
2. Railway creates the database automatically
3. Note: Database must be created first so backend can reference it

### Step 4: Deploy Backend on Railway
1. In the same Railway project, click "+ New"
2. Select "GitHub Repo"
3. Choose your `tamil-works-db` repository
4. Railway will show deployment configuration
5. **IMPORTANT**: Configure backend service settings:
   - Click on the service → **Settings** tab
   - Scroll to **Source** section
   - Set **Root Directory**: `webapp/backend`
   - Railway will auto-detect the Dockerfile
   - Click **Deploy** if not already deploying

#### Backend Environment Variables:
Click on backend service → "Variables" tab → Add:
```
DATABASE_URL=${{Postgres.DATABASE_URL}}
ALLOWED_ORIGINS=*
```
Note: Update `ALLOWED_ORIGINS` with your actual frontend URL after Step 6

### Step 5: Setup Database Schema
Use Railway CLI to populate database:
```bash
# Install Railway CLI (if not installed)
npm install -g @railway/cli

# Login to Railway
railway login

# Link to your project
railway link

# Select the PostgreSQL service when prompted
# Then run schema setup
railway run psql $DATABASE_URL < sql/complete_setup.sql

# Import Thirukkural data (optional - takes ~3 seconds)
railway run python scripts/thirukkural_bulk_import.py

# Import Sangam literature (optional - takes ~30 seconds)
railway run python scripts/sangam_bulk_import.py
```

Alternative - Manual database setup:
1. Click PostgreSQL service → "Connect" tab
2. Copy the "Database Connection URL"
3. From your local machine:
```bash
psql "YOUR_DATABASE_URL" -f sql/complete_setup.sql
```

### Step 6: Deploy Frontend on Railway
1. In the same Railway project, click "+ New"
2. Select "GitHub Repo"
3. Choose your `tamil-works-db` repository again
4. Railway will show deployment configuration
5. **IMPORTANT**: Configure frontend service settings:
   - Click on the service → **Settings** tab
   - Scroll to **Source** section
   - Set **Root Directory**: `webapp/frontend`
   - Railway will auto-detect the Dockerfile
   - Click **Deploy** if not already deploying

#### Frontend Environment Variables:
Click on frontend service → "Variables" tab → Add:
```
VITE_API_URL=https://YOUR-BACKEND-URL.up.railway.app
```

**To get your backend URL:**
- Go to backend service
- Click "Settings" tab
- Find "Public Networking" section
- Copy the generated domain (e.g., `https://backend-production-xxxx.up.railway.app`)
- Paste it as `VITE_API_URL` value in frontend variables

Railway will automatically:
- Detect the Dockerfile
- Build with the VITE_API_URL variable
- Deploy the frontend

### Step 7: Update Backend CORS Settings
Now that you have both URLs:
1. Go to backend service → "Variables" tab
2. Update `ALLOWED_ORIGINS` to your frontend URL:
```
ALLOWED_ORIGINS=https://YOUR-FRONTEND-URL.up.railway.app
```
3. Save and redeploy backend

## 📊 Your URLs

After deployment, Railway gives you:
- **Backend API**: `https://backend-production-xxxx.up.railway.app`
  - API docs: `https://backend-production-xxxx.up.railway.app/docs`
  - Health check: `https://backend-production-xxxx.up.railway.app/health`
- **Frontend**: `https://frontend-production-xxxx.up.railway.app`
- **Database**: Internal Railway URL (not public)

Access your frontend URL in a browser to use the Tamil word search application!

## 💰 Costs

**Free Trial**: $5 credit (no credit card needed)

**After trial** (pay-as-you-go):
- Backend: ~$2-3/month
- PostgreSQL: ~$5/month (includes storage for full Tamil corpus)
- Frontend: ~$2-3/month
- **Total: ~$9-11/month**

To minimize costs:
- Services sleep after inactivity on free tier
- Only pay for actual usage (CPU time + bandwidth)
- Can pause services when not in use

## 🔧 Useful Railway CLI Commands

### View Logs
```bash
# View backend logs
railway logs --service backend

# View frontend logs
railway logs --service frontend

# Follow logs in real-time
railway logs --service backend --follow
```

### Run Commands on Railway
```bash
# Import data
railway run python scripts/thirukkural_bulk_import.py
railway run python scripts/sangam_bulk_import.py

# Access database
railway run psql $DATABASE_URL
```

### Local Development with Railway Database
```bash
# Backend with Railway database
cd webapp/backend
railway run uvicorn main:app --reload --host 0.0.0.0

# Frontend with local backend
cd webapp/frontend
npm run dev
```

## 🎯 Post-Deployment Checklist

- [ ] PostgreSQL database is running
- [ ] Backend service deployed successfully
- [ ] Frontend service deployed successfully
- [ ] Database schema loaded (`sql/complete_setup.sql`)
- [ ] Backend can connect to database (check `/health` endpoint)
- [ ] Frontend can connect to backend
- [ ] Data imported (Thirukkural and/or Sangam literature)
- [ ] Search functionality works
- [ ] Autocomplete works
- [ ] Export to CSV works
- [ ] Work filtering works
- [ ] CORS properly configured (no console errors)
- [ ] Add custom domain (optional)
- [ ] Monitor usage and costs in Railway dashboard

## 🆘 Troubleshooting

**Backend build fails?**
- Check build logs in Railway dashboard
- Verify `Dockerfile` is in repository root
- Check `requirements.txt` in `webapp/backend/`
- Ensure all files are committed and pushed to GitHub

**Frontend build fails?**
- Verify root directory is set to `webapp/frontend`
- Check that `VITE_API_URL` variable is set
- Look for build errors in Railway logs
- Ensure `Dockerfile`, `nginx.conf` are in `webapp/frontend/`

**Database connection error?**
- Verify `DATABASE_URL=${{Postgres.DATABASE_URL}}` is set in backend variables
- Use Railway's reference syntax: `${{Postgres.DATABASE_URL}}`
- Check PostgreSQL service is running
- Test connection: `railway run psql $DATABASE_URL`

**Frontend can't connect to backend?**
- Check `VITE_API_URL` matches backend URL exactly
- Verify backend `/health` endpoint responds: `curl https://your-backend.up.railway.app/health`
- Check browser console for CORS errors
- Ensure backend `ALLOWED_ORIGINS` includes frontend URL

**CORS errors in browser console?**
- Add frontend URL to backend `ALLOWED_ORIGINS` variable
- Format: `https://frontend-production-xxxx.up.railway.app`
- Or use `*` for testing (not recommended for production)
- Redeploy backend after changing variables

**Empty search results?**
- Verify database schema was loaded: `railway run psql $DATABASE_URL -c "\dt"`
- Check if data was imported: `railway run psql $DATABASE_URL -c "SELECT COUNT(*) FROM verses"`
- Import data using bulk import scripts (see Step 5)

**App sleeps or responds slowly?**
- Free tier services sleep after 5 minutes of inactivity
- First request wakes service (10-30 seconds delay)
- Check service status in Railway dashboard
- Consider upgrading to prevent sleeping

**"Root directory not found" error?**
- For frontend: Verify root directory is set to `webapp/frontend` in service settings
- For backend: Root directory should be `/` (repository root)
- Settings → Service → Root Directory

## 📚 Resources

- Railway Docs: https://docs.railway.app
- Railway Discord: https://discord.gg/railway
- Your Dashboard: https://railway.app/dashboard

## 🎉 You're Ready!

Your full-stack Tamil word search application is production-ready with:
- ✅ FastAPI backend with PostgreSQL
- ✅ Vue.js frontend with Nginx
- ✅ Dockerized deployments
- ✅ Automatic builds and deployments via Railway

Just push your code to GitHub, follow the 7 steps above, and Railway will handle the rest!

## 📋 Quick Reference

**Three Railway Services in Your Project:**
1. **PostgreSQL** - Database service
2. **Backend** - FastAPI application
   - Root Directory: `webapp/backend`
   - Dockerfile: `webapp/backend/Dockerfile`
3. **Frontend** - Vue.js + Nginx
   - Root Directory: `webapp/frontend`
   - Dockerfile: `webapp/frontend/Dockerfile`

**Key Variables:**
- Backend: `DATABASE_URL`, `ALLOWED_ORIGINS`
- Frontend: `VITE_API_URL`

**Data Import Order:**
1. Setup schema: `sql/complete_setup.sql`
2. Import Thirukkural: `scripts/thirukkural_bulk_import.py`
3. Import Sangam: `scripts/sangam_bulk_import.py`
