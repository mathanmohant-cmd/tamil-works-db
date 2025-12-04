# Railway Configuration Guide

## Current Issue
Railway was failing with "webapp/backend not found" because it was trying to build from the repository root.

## Solution
Configure each service with its own **Root Directory** in Railway dashboard.

---

## Step-by-Step Configuration

### Backend Service Configuration

1. Go to your Railway project
2. Click on your **Backend** service
3. Click **Settings** tab
4. Scroll down to **Source** section
5. Find **Root Directory** field
6. Enter: `webapp/backend`
7. Click **Save** or it saves automatically
8. Railway will redeploy automatically

**What this does:**
- Railway builds from `webapp/backend/` directory
- Finds `Dockerfile` in that directory
- `COPY . .` in Dockerfile copies files from `webapp/backend/`

### Frontend Service Configuration

1. Go to your Railway project
2. Click on your **Frontend** service
3. Click **Settings** tab
4. Scroll down to **Source** section
5. Find **Root Directory** field
6. Enter: `webapp/frontend`
7. Click **Save**
8. Railway will redeploy automatically

**What this does:**
- Railway builds from `webapp/frontend/` directory
- Finds `Dockerfile` in that directory
- `COPY . .` in Dockerfile copies files from `webapp/frontend/`

---

## File Structure (for reference)

```
tamil-works-db/                    # Repository root
├── webapp/
│   ├── backend/
│   │   ├── Dockerfile            # Backend Dockerfile
│   │   ├── .dockerignore
│   │   ├── requirements.txt
│   │   ├── main.py
│   │   └── database.py
│   │
│   └── frontend/
│       ├── Dockerfile            # Frontend Dockerfile
│       ├── .dockerignore
│       ├── nginx.conf
│       ├── package.json
│       └── src/
│
├── scripts/                       # Import scripts
├── sql/                          # Database schema
└── README.md
```

---

## Environment Variables (Reminder)

### Backend Service
```
DATABASE_URL=${{Postgres.DATABASE_URL}}
ALLOWED_ORIGINS=*
```
(Update ALLOWED_ORIGINS after frontend deploys)

### Frontend Service
```
VITE_API_URL=https://your-backend-url.up.railway.app
```

---

## Troubleshooting

**Build still fails?**
- Verify Root Directory is exactly: `webapp/backend` (no leading or trailing slashes)
- Check that Dockerfile exists in `webapp/backend/Dockerfile` on GitHub
- Force redeploy: Settings → Redeploy

**Wrong files being copied?**
- Check .dockerignore in service directory
- Verify COPY command in Dockerfile is `COPY . .`

---

## Why This Approach?

**Alternative 1: Separate Git Repos**
- ❌ More complex: Need to manage 2+ repos
- ❌ Shared code duplication
- ✅ Simplest Railway config

**Alternative 2: Monorepo with Root Directory (Current)**
- ✅ Single repo for everything
- ✅ Shared scripts and documentation
- ✅ Easy local development
- ⚠️ Requires Root Directory configuration in Railway

**Alternative 3: Dockerfile in root with complex paths**
- ❌ Build context issues (what we were experiencing)
- ❌ Complex COPY paths
- ❌ Harder to maintain

**Winner:** Monorepo with service-level Dockerfiles + Railway Root Directory config

---

## Next Steps

1. Configure Backend Root Directory: `webapp/backend`
2. Configure Frontend Root Directory: `webapp/frontend`
3. Wait for automatic redeployment
4. Check build logs for success
5. Test endpoints once deployed
