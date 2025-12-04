# Railway.app Deployment Guide

## Prerequisites
1. GitHub account
2. Railway account (sign up at railway.app)
3. Your code pushed to GitHub

## Step 1: Prepare Your Project

### A. Create requirements.txt for backend
```bash
cd webapp/backend
pip freeze > requirements.txt
```

### B. Create Procfile (tells Railway how to start your app)
Create `webapp/backend/Procfile`:
```
web: uvicorn main:app --host 0.0.0.0 --port $PORT
```

### C. Create railway.json (optional config)
Create `railway.json` in project root:
```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "uvicorn main:app --host 0.0.0.0 --port $PORT",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

## Step 2: Push to GitHub

```bash
# Initialize git repository
git init
git add .
git commit -m "Initial commit - Tamil Literary Words Search"

# Create GitHub repo and push
git remote add origin https://github.com/YOUR_USERNAME/tamil-works-db.git
git branch -M main
git push -u origin main
```

## Step 3: Deploy on Railway

### A. Create New Project
1. Go to https://railway.app
2. Click "Start a New Project"
3. Select "Deploy from GitHub repo"
4. Choose your `tamil-works-db` repository

### B. Add PostgreSQL Database
1. In your Railway project, click "+ New"
2. Select "Database" → "PostgreSQL"
3. Railway will automatically create a database
4. Get the connection string from the PostgreSQL service

### C. Configure Backend Service
1. Click on your backend service
2. Go to "Variables" tab
3. Add environment variables:
   ```
   DATABASE_URL=${{Postgres.DATABASE_URL}}
   PORT=8000
   ```
4. Railway will auto-detect your Python app and deploy

### D. Configure Frontend Service
1. Click "+ New" → "GitHub Repo" (select your repo again)
2. Set root directory: `webapp/frontend`
3. Build command: `npm install && npm run build`
4. Start command: `npm run preview`
5. Add environment variable:
   ```
   VITE_API_URL=https://YOUR-BACKEND.railway.app
   ```

## Step 4: Setup Database Schema

### Option A: Use Railway's PostgreSQL client
1. Click on PostgreSQL service
2. Click "Data" tab
3. Run your schema SQL

### Option B: Connect from local machine
```bash
# Get connection string from Railway
psql "postgresql://..."

# Run schema
\i sql/complete_setup.sql
```

## Step 5: Update Frontend API URL

Update `webapp/frontend/src/api.js`:
```javascript
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export default {
  searchWords: (params) => axios.get(`${API_BASE_URL}/search`, { params }),
  getWorks: () => axios.get(`${API_BASE_URL}/works`),
  getStatistics: () => axios.get(`${API_BASE_URL}/stats`)
}
```

## Step 6: Configure CORS

Update `webapp/backend/main.py`:
```python
# Get allowed origins from environment or use default
ALLOWED_ORIGINS = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:5173,http://localhost:3000"
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

Add to Railway variables:
```
ALLOWED_ORIGINS=https://YOUR-FRONTEND.railway.app,http://localhost:5173
```

## Step 7: Deploy!

Railway will automatically:
1. Detect your Python/Node.js apps
2. Install dependencies
3. Build and deploy
4. Give you public URLs

## Monitoring & Scaling

### Check Logs
- Click on any service → "Deployments" → "View Logs"

### Monitor Usage
- Dashboard shows CPU, Memory, Network usage
- Costs are displayed in real-time

### Scale Up (when needed)
- Railway automatically scales
- You can upgrade resources in project settings

## Custom Domain (Optional)

1. Go to service "Settings"
2. Click "Generate Domain" for free railway.app subdomain
3. Or add your custom domain

## Estimated Costs

For your app:
- Backend (FastAPI): ~$2-3/month
- Frontend (Node.js): ~$2-3/month  
- PostgreSQL: ~$2-5/month
- **Total: ~$5-10/month**

Free trial credit covers first month!

## Troubleshooting

### Build Fails
- Check build logs in Railway
- Verify requirements.txt is complete
- Check Python version compatibility

### Database Connection Issues
- Verify DATABASE_URL variable is set
- Check database service is running
- Use Railway's internal URL (not public)

### CORS Errors
- Add your Railway frontend URL to ALLOWED_ORIGINS
- Redeploy backend after changing variables

## Maintenance

### Update Code
```bash
git add .
git commit -m "Update feature"
git push
```
Railway auto-deploys on git push!

### Database Backup
- Railway provides automatic backups
- Or use pg_dump manually

### View Database
- Use Railway's built-in PostgreSQL client
- Or connect with any PostgreSQL client using connection string

## Next Steps After Deployment

1. Test all features on production URLs
2. Set up custom domain
3. Monitor usage and costs
4. Scale as needed
5. Add more Tamil literature data!

## Support

- Railway Docs: https://docs.railway.app
- Discord: https://discord.gg/railway
- Status: https://status.railway.app
