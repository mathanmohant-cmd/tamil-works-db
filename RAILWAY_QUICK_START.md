# Railway Quick Start Guide

## ✅ Your Project is Ready for Railway!

All necessary files have been created:
- ✅ `webapp/backend/requirements.txt` - Python dependencies
- ✅ `webapp/backend/Procfile` - Tells Railway how to start backend
- ✅ `railway.json` - Railway configuration
- ✅ `.gitignore` - Git ignore rules
- ✅ CORS configured for production
- ✅ API URL configured via environment variables

## 🚀 Deploy in 5 Steps

### Step 1: Sign up for Railway
1. Go to https://railway.app
2. Click "Start a New Project"
3. Sign in with GitHub

### Step 2: Create GitHub Repository
```bash
cd C:\Claude\Projects\tamil-works-db

# Initialize git
git init
git add .
git commit -m "Initial commit - Tamil Literary Words Search App"

# Create repo on GitHub and push
git remote add origin https://github.com/YOUR_USERNAME/tamil-works-db.git
git branch -M main
git push -u origin main
```

### Step 3: Deploy Backend on Railway
1. In Railway, click "+ New Project"
2. Select "Deploy from GitHub repo"
3. Choose your `tamil-works-db` repository
4. Railway will detect Python and auto-deploy

### Step 4: Add PostgreSQL Database
1. In your Railway project, click "+ New"
2. Select "Database" → "PostgreSQL"
3. Railway creates the database automatically
4. Copy the connection string

### Step 5: Configure Environment Variables

#### Backend Service Variables:
1. Click on your backend service
2. Go to "Variables" tab
3. Add these variables:
```
DATABASE_URL=${{Postgres.DATABASE_URL}}
ALLOWED_ORIGINS=https://YOUR-FRONTEND.up.railway.app
```

#### Setup Database Schema:
Option 1 - Use Railway CLI:
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Link to your project
railway link

# Connect to database and run schema
railway run psql $DATABASE_URL < sql/complete_setup.sql
```

Option 2 - Manual:
1. Click PostgreSQL service → "Data" tab
2. Copy your connection string
3. Connect from local:
```bash
psql "postgresql://..." -f sql/complete_setup.sql
```

### Step 6: Deploy Frontend (Optional - if separate)
1. Click "+ New" → "GitHub Repo"
2. Select same repo
3. Set root directory: `webapp/frontend`
4. Railway auto-detects Vite
5. Add variable:
```
VITE_API_URL=https://YOUR-BACKEND.up.railway.app
```

OR just serve frontend from backend (simpler):
- Build frontend locally
- Serve static files from FastAPI

## 📊 Your URLs

After deployment, Railway gives you:
- **Backend**: `https://YOUR-PROJECT.up.railway.app`
- **Frontend**: Can deploy separately or serve from backend
- **Database**: Internal Railway URL (not public)

## 💰 Costs

**Free Trial**: $5 credit (no credit card needed)

**After trial** (pay-as-you-go):
- Backend: ~$2-3/month
- PostgreSQL: ~$2-5/month
- Frontend: ~$2-3/month (if separate)
- **Total: ~$5-10/month**

## 🔧 Useful Commands

### View Logs
```bash
railway logs
```

### Run Commands on Railway
```bash
railway run python manage.py migrate
```

### Local Development with Railway Database
```bash
railway run uvicorn main:app --reload
```

## 🎯 Post-Deployment Checklist

- [ ] Backend is running
- [ ] Database schema loaded
- [ ] Frontend can connect to backend
- [ ] Search works
- [ ] Autocomplete works
- [ ] Export functions work
- [ ] Add custom domain (optional)
- [ ] Monitor usage and costs

## 🆘 Troubleshooting

**Build fails?**
- Check build logs in Railway
- Verify all files committed to Git
- Check requirements.txt is complete

**Database connection error?**
- Verify DATABASE_URL variable is set
- Use Railway's internal database URL
- Check database service is running

**CORS errors?**
- Add frontend URL to ALLOWED_ORIGINS
- Format: `https://your-app.up.railway.app`
- Redeploy backend after changing

**App sleeps?**
- Free tier apps may sleep after inactivity
- First request wakes it up (may be slow)
- Upgrade to prevent sleeping

## 📚 Resources

- Railway Docs: https://docs.railway.app
- Railway Discord: https://discord.gg/railway
- Your Dashboard: https://railway.app/dashboard

## 🎉 You're Ready!

Your app is production-ready. Just push to GitHub and Railway will handle the rest!

Questions? Check RAILWAY_DEPLOYMENT.md for detailed instructions.
