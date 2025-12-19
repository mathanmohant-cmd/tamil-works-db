# Beta Release Plan
**Tamil Literature Search Application**
**Timeline:** 1-2 Weeks (January 2-9, 2026)
**Target Launch Date:** January 9, 2026

---

## 🎯 Beta Release Goals

### Primary Goals
1. ✅ Deploy production-ready application to Railway.app
2. ✅ Validate core search functionality with real users
3. ✅ Gather feedback from Tamil literature community
4. ✅ Identify and fix critical bugs
5. ✅ Build initial user base (50+ users)

### Success Criteria
- [ ] Zero critical security vulnerabilities
- [ ] 99%+ uptime during beta period
- [ ] 500+ searches performed
- [ ] 10+ user feedback submissions
- [ ] 3+ positive testimonials

---

## 📅 Week-by-Week Plan

## **WEEK 1: Preparation & Deployment** (Jan 2-5, 2026)

### Day 1 (Thursday, Jan 2) - Security & Config ⏱️ 3 hours

#### Morning: Security Hardening
- [ ] **Install password hashing library**
  ```bash
  cd webapp/backend
  echo "passlib[bcrypt]==1.7.4" >> requirements.txt
  pip install passlib[bcrypt]
  ```

- [ ] **Generate secure password hash**
  ```bash
  python -c "from passlib.hash import bcrypt; print(bcrypt.hash('YOUR_SECURE_PASSWORD_HERE'))"
  # Save this hash securely
  ```

- [ ] **Update admin authentication in `main.py`**
  ```python
  import os
  from passlib.context import CryptContext

  pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

  ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
  ADMIN_PASSWORD_HASH = os.getenv("ADMIN_PASSWORD_HASH")

  @app.post("/admin/login")
  async def admin_login(credentials: AdminCredentials):
      if credentials.username == ADMIN_USERNAME and \
         pwd_context.verify(credentials.password, ADMIN_PASSWORD_HASH):
          # Generate session token
          return {"success": True, "user": {"username": ADMIN_USERNAME}}
      raise HTTPException(status_code=401, detail="Invalid credentials")
  ```

- [ ] **Create `.env.example` template**
  ```
  # Database
  DATABASE_URL=postgresql://user:password@host:port/database

  # Admin Authentication
  ADMIN_USERNAME=admin
  ADMIN_PASSWORD_HASH=$2b$12$YOUR_BCRYPT_HASH_HERE

  # Security
  SECRET_KEY=your-secret-key-here-generate-with-openssl-rand

  # CORS
  CORS_ORIGINS=["http://localhost:5173","https://yourdomain.com"]

  # Application
  DEBUG=False
  ```

- [ ] **Test authentication locally**
  ```bash
  # Set environment variables
  export ADMIN_PASSWORD_HASH="your_hash_here"
  python main.py
  # Test login via API
  ```

#### Afternoon: Deployment Configuration
- [ ] **Create `Procfile`** (project root)
  ```
  web: cd webapp/backend && uvicorn main:app --host 0.0.0.0 --port $PORT
  ```

- [ ] **Create `runtime.txt`** (project root)
  ```
  python-3.11.0
  ```

- [ ] **Create `railway.json`** (project root)
  ```json
  {
    "$schema": "https://railway.app/railway.schema.json",
    "build": {
      "builder": "NIXPACKS"
    },
    "deploy": {
      "startCommand": "cd webapp/backend && uvicorn main:app --host 0.0.0.0 --port $PORT",
      "restartPolicyType": "ON_FAILURE",
      "restartPolicyMaxRetries": 10,
      "healthcheckPath": "/health",
      "healthcheckTimeout": 100
    }
  }
  ```

- [ ] **Update CORS settings in `main.py`**
  ```python
  # Allow Railway domain
  origins = [
      "http://localhost:5173",
      "http://localhost:3000",
      "https://*.railway.app",  # Railway preview URLs
      "https://tamilconcordance.in",  # Your domain
  ]
  ```

- [ ] **Test Procfile locally**
  ```bash
  # Install Railway CLI (optional)
  npm install -g @railway/cli

  # Or test manually
  cd webapp/backend && uvicorn main:app --host 0.0.0.0 --port 8000
  ```

**Estimated Time:** 3 hours
**Deliverable:** Secure, deployment-ready codebase

---

### Day 2 (Friday, Jan 3) - Railway Deployment ⏱️ 4 hours

#### Morning: Railway Setup
- [ ] **Create Railway account** (if not exists)
  - Visit https://railway.app
  - Sign up with GitHub
  - Connect GitHub repository

- [ ] **Create new project**
  - "New Project" → "Deploy from GitHub repo"
  - Select `tamil-works-db` repository
  - Railway auto-detects Python app

- [ ] **Add PostgreSQL database**
  - Click "New" → "Database" → "Add PostgreSQL"
  - Railway provisions managed Postgres
  - Note: `DATABASE_URL` is auto-set

#### Afternoon: Environment Configuration
- [ ] **Set environment variables in Railway**
  - Navigate to project → Variables
  - Add:
    - `ADMIN_USERNAME=admin`
    - `ADMIN_PASSWORD_HASH=<your_hash>`
    - `SECRET_KEY=<generate_with_openssl>`
    - `CORS_ORIGINS=["https://your-app.railway.app"]`
    - `DEBUG=False`

- [ ] **Generate SECRET_KEY**
  ```bash
  openssl rand -hex 32
  # Add to Railway environment variables
  ```

- [ ] **Deploy initial version**
  - Push code to GitHub main branch
  - Railway auto-deploys
  - Monitor deployment logs

- [ ] **Verify deployment**
  ```bash
  curl https://your-app.railway.app/health
  # Should return: {"status": "healthy"}
  ```

**Estimated Time:** 4 hours
**Deliverable:** Live application on Railway

---

### Day 3 (Saturday, Jan 4) - Database Migration ⏱️ 3 hours

#### Morning: Database Setup
- [ ] **Get Railway database connection string**
  - Railway dashboard → PostgreSQL service → Connect
  - Copy `DATABASE_URL`

- [ ] **Run schema setup**
  ```bash
  # Option 1: Via Railway CLI
  railway run python scripts/setup_railway_db.py

  # Option 2: Connect directly
  psql $DATABASE_URL -f sql/complete_setup.sql
  ```

- [ ] **Verify schema**
  ```bash
  railway run python -c "
  from webapp.backend.database import Database
  db = Database()
  print(db.get_statistics())
  "
  ```

#### Afternoon: Data Import
- [ ] **Import all works** (in order)
  ```bash
  railway run python scripts/thirukkural_bulk_import.py
  railway run python scripts/tolkappiyam_bulk_import.py
  railway run python scripts/sangam_bulk_import.py
  railway run python scripts/silapathikaram_bulk_import.py
  railway run python scripts/kambaramayanam_bulk_import.py
  ```

- [ ] **Verify data import**
  ```bash
  railway run python -c "
  from webapp.backend.database import Database
  db = Database()
  stats = db.get_statistics()
  print(f'Works: {stats[\"total_works\"]}')
  print(f'Verses: {stats[\"total_verses\"]}')
  print(f'Words: {stats[\"total_words\"]}')
  "
  # Expected: 5 works, ~130K+ verses, ~600K+ words
  ```

- [ ] **Create collections** (via Admin UI)
  - Login to admin panel
  - Create collections from `CANONICAL_CHRONOLOGICAL_SORTING.md`

**Estimated Time:** 3 hours
**Deliverable:** Fully populated production database

---

### Day 4 (Sunday, Jan 5) - Testing & Monitoring ⏱️ 3 hours

#### Morning: Error Monitoring Setup
- [ ] **Create Sentry account**
  - Visit https://sentry.io
  - Create free account (5K events/month)
  - Create new project → Python/FastAPI

- [ ] **Add Sentry to backend**
  ```bash
  cd webapp/backend
  echo "sentry-sdk[fastapi]==1.39.1" >> requirements.txt
  pip install sentry-sdk[fastapi]
  ```

- [ ] **Configure Sentry in `main.py`**
  ```python
  import sentry_sdk
  from sentry_sdk.integrations.fastapi import FastApiIntegration

  if not DEBUG:
      sentry_sdk.init(
          dsn=os.getenv("SENTRY_DSN"),
          integrations=[FastApiIntegration()],
          traces_sample_rate=0.1,
          profiles_sample_rate=0.1,
          environment="production"
      )
  ```

- [ ] **Add SENTRY_DSN to Railway env vars**
- [ ] **Test error reporting**
  ```python
  # Trigger test error
  @app.get("/test-error")
  async def test_error():
      raise Exception("Test error for Sentry")
  ```

#### Afternoon: Comprehensive Testing
- [ ] **Functional testing checklist**
  - [ ] Search works (partial, exact)
  - [ ] Word position filters (beginning, end, anywhere)
  - [ ] Work filters (all, select specific)
  - [ ] Sort options (canonical, alphabetical)
  - [ ] Word expansion with pagination
  - [ ] Export (CSV, TXT)
  - [ ] Verse view
  - [ ] Admin login
  - [ ] Collections management
  - [ ] Drag-and-drop reordering

- [ ] **Performance testing**
  - [ ] Search response time < 2 seconds
  - [ ] Page load < 3 seconds
  - [ ] Large result sets (1000+ words)

- [ ] **Mobile testing**
  - [ ] iPhone Safari
  - [ ] Android Chrome
  - [ ] Tablet responsive layout

- [ ] **Browser compatibility**
  - [ ] Chrome (latest)
  - [ ] Firefox (latest)
  - [ ] Safari (latest)
  - [ ] Edge (latest)

**Estimated Time:** 3 hours
**Deliverable:** Fully tested, monitored application

---

## **WEEK 2: Launch & Feedback** (Jan 6-9, 2026)

### Day 5 (Monday, Jan 6) - Pre-Launch Preparation ⏱️ 2 hours

#### Morning: Final Checks
- [ ] **Review all content pages**
  - [ ] Home page loads correctly
  - [ ] About Us (newly updated content)
  - [ ] Word Segmentation Principles
  - [ ] Our Inspiration
  - [ ] Ensure all Tamil text renders correctly

- [ ] **SEO basics**
  - [ ] Update page title: "Tamil Literature Search | தமிழ் இலக்கிய சொல் தேடல்"
  - [ ] Add meta description
  - [ ] Verify favicon displays

- [ ] **Create backup**
  - [ ] Railway auto-backup enabled
  - [ ] Manual snapshot of database
  - [ ] Export data as CSV (safety backup)

#### Afternoon: Launch Materials
- [ ] **Prepare announcement email** (for Chicago Tamil Sangam)
  ```
  Subject: Beta Launch: Tamil Literature Search Tool 🎉

  Dear Tamil Sangam Community,

  I'm excited to share a new tool for exploring Tamil literature:

  🔎 Search across 5 major classical works
  📚 Find word patterns and connections
  ⚡ Free, fast, and easy to use

  Try it: https://your-app.railway.app

  This is a beta version - your feedback is invaluable!

  [More details...]
  ```

- [ ] **Create feedback form** (Google Forms)
  - What did you search for?
  - Did you find what you were looking for?
  - What features would you like?
  - Any bugs or issues?
  - Would you recommend this tool?

- [ ] **Prepare social media posts**
  - Twitter/X announcement
  - LinkedIn post (if applicable)
  - Community forum posts

**Estimated Time:** 2 hours
**Deliverable:** Launch-ready materials

---

### Day 6 (Tuesday, Jan 7) - BETA LAUNCH DAY 🚀 ⏱️ 3 hours

#### Morning: Soft Launch
- [ ] **9:00 AM - Final deployment check**
  - [ ] All services running
  - [ ] Database accessible
  - [ ] No errors in logs

- [ ] **10:00 AM - Send announcement email**
  - Chicago Tamil Sangam mailing list
  - Personal network (10-20 contacts)

- [ ] **11:00 AM - Social media posts**
  - Share announcement
  - Tag relevant accounts
  - Use hashtags: #Tamil #TamilLiterature #Sangam

#### Afternoon: Monitor Launch
- [ ] **Monitor metrics**
  - Railway dashboard (traffic, errors)
  - Sentry (error reports)
  - Database performance

- [ ] **Be responsive**
  - Answer questions promptly
  - Fix critical bugs immediately
  - Collect feedback

- [ ] **Track initial metrics**
  - Unique visitors (Railway analytics)
  - Search queries performed
  - Most searched words
  - Error rate

**Estimated Time:** 3 hours (plus ongoing monitoring)
**Deliverable:** Live beta with initial users

---

### Day 7-8 (Wed-Thu, Jan 8-9) - Iteration & Support ⏱️ 2-4 hours/day

#### Daily Tasks
- [ ] **Morning: Check metrics**
  - Review Railway logs
  - Check Sentry errors
  - Read user feedback

- [ ] **Afternoon: Respond & Fix**
  - Reply to feedback
  - Fix bugs (priority: critical > high > medium)
  - Deploy hotfixes if needed

- [ ] **Evening: Document**
  - Log all issues in GitHub Issues
  - Track feature requests
  - Update FAQ based on questions

#### Specific Activities
- [ ] **Gather testimonials**
  - Ask satisfied users for quotes
  - Screenshot positive feedback
  - Prepare for full launch

- [ ] **Content updates**
  - Fix typos discovered
  - Clarify confusing UI elements
  - Update help text

- [ ] **Performance tuning**
  - Identify slow queries
  - Add indexes if needed
  - Optimize heavy operations

**Estimated Time:** 2-4 hours per day
**Deliverable:** Stable, improved beta version

---

## 📊 Metrics to Track

### Daily Metrics (Track in Spreadsheet)
| Date | Visitors | Searches | Errors | Feedback | Uptime |
|------|----------|----------|--------|----------|--------|
| Jan 7 | | | | | |
| Jan 8 | | | | | |
| Jan 9 | | | | | |

### Key Performance Indicators (KPIs)
- **Unique Visitors:** Target 50+ in first week
- **Search Queries:** Target 500+ in first week
- **Error Rate:** < 1% of requests
- **Uptime:** > 99%
- **Feedback Submissions:** Target 10+
- **Positive Feedback:** Target 80%+

### Tools for Tracking
- **Railway Dashboard:** Traffic, uptime, resource usage
- **Sentry:** Error tracking, performance monitoring
- **Google Forms:** User feedback
- **Spreadsheet:** Manual tracking of metrics

---

## 🐛 Bug Triage Process

### Severity Levels
1. **Critical** (Fix immediately)
   - Site down
   - Data loss
   - Security vulnerability

2. **High** (Fix within 24 hours)
   - Major feature broken
   - Affects many users
   - Workaround not available

3. **Medium** (Fix within 1 week)
   - Minor feature broken
   - Workaround available
   - Affects few users

4. **Low** (Fix when possible)
   - Cosmetic issues
   - Nice-to-have improvements
   - Edge cases

### Bug Workflow
1. User reports bug (email, form, social media)
2. Log in GitHub Issues with:
   - Description
   - Steps to reproduce
   - Severity level
   - Screenshots/logs
3. Assign to sprint based on severity
4. Fix → Test → Deploy → Notify user
5. Close issue with resolution notes

---

## 💬 Communication Plan

### Channels
1. **Email:** Primary for announcements, updates
2. **GitHub Issues:** Technical bug reports
3. **Google Forms:** General feedback
4. **Social Media:** Updates, highlights, engagement

### Communication Schedule
- **Launch Day (Jan 7):** Announcement email + social posts
- **Day 2-3 (Jan 8-9):** Daily update post (if significant news)
- **End of Week 1 (Jan 9):** Summary email to beta testers
- **Weekly:** Ongoing updates to community

### Response Time Commitments
- **Critical bugs:** < 4 hours
- **General feedback:** < 24 hours
- **Feature requests:** Acknowledge within 48 hours

---

## ✅ Pre-Launch Checklist

### Technical Readiness
- [ ] Security: Admin password hashed and in env vars
- [ ] Deployment: Procfile, runtime.txt, railway.json created
- [ ] Database: Schema deployed, data imported
- [ ] Monitoring: Sentry configured and tested
- [ ] Testing: All core features work on production
- [ ] Performance: Response times acceptable
- [ ] Mobile: Responsive design works
- [ ] Backups: Automated backups enabled

### Content Readiness
- [ ] About Us page updated with new content
- [ ] All typos fixed
- [ ] Contact email verified (thamizh.words@gmail.com)
- [ ] Attributions correct (Prof. Pandiaraja, etc.)

### Launch Materials
- [ ] Announcement email drafted
- [ ] Feedback form created
- [ ] Social media posts prepared
- [ ] FAQ document started

### Legal/Compliance
- [ ] Data attribution clear
- [ ] Privacy policy (if collecting user data)
- [ ] Terms of service (optional for beta)

---

## 🎉 Success Celebration Milestones

### Day 1
- [ ] First 10 users
- [ ] First 100 searches
- [ ] First positive feedback

### Week 1
- [ ] 50+ unique visitors
- [ ] 500+ searches
- [ ] Zero critical bugs
- [ ] First testimonial

### Week 2
- [ ] 100+ users
- [ ] 1000+ searches
- [ ] 3+ testimonials
- [ ] Feature mention (blog, social media)

---

## 🔄 Post-Beta Plans

### Week 3-4: Full Launch Preparation
- [ ] Incorporate beta feedback
- [ ] Fix all high-priority bugs
- [ ] Add most-requested features (if feasible)
- [ ] Custom domain setup (tamilconcordance.in)
- [ ] SEO optimization
- [ ] Analytics setup (Plausible/Google Analytics)

### Month 2: Public Launch
- [ ] Press release to Tamil media
- [ ] Academic community outreach
- [ ] University libraries (resource submission)
- [ ] Social media campaign
- [ ] Video tutorial creation

### Month 3-6: Growth
- [ ] Feature additions (dictionary, commentaries)
- [ ] Performance improvements (caching, CDN)
- [ ] Mobile app exploration
- [ ] Community features

---

## 📞 Support & Contact

### Beta Support
- **Email:** thamizh.words@gmail.com
- **Feedback Form:** [Google Forms Link]
- **GitHub Issues:** For technical bugs
- **Response Time:** < 24 hours

### Emergency Contact
- **Critical Issues:** Direct message on primary communication channel
- **After Hours:** Best effort response

---

## 📚 Resources

### Documentation
- `PRODUCTION_READINESS_ASSESSMENT.md` - Full technical assessment
- `DEPLOYMENT.md` - Step-by-step deployment guide (to be created)
- `.env.example` - Environment variable template
- `CLAUDE.md` - Project overview and conventions

### External Resources
- Railway Documentation: https://docs.railway.app
- Sentry Documentation: https://docs.sentry.io
- FastAPI Documentation: https://fastapi.tiangolo.com
- Vue.js Documentation: https://vuejs.org

---

## 🙏 Acknowledgments

This beta launch is made possible by:
- **Prof. Dr. P. Pandiyaraja** - Tamil Concordance development
- **Mrs. Vaidehi Herbert** - Sangam Literature teaching
- **Prof. Dr. Ku. Ve. Balasubramanian** - Classical Tamil scholarship
- **Chicago Tamil Sangam** - Community support
- **Beta Testers** - Early feedback and encouragement

---

**Let's make Tamil literature accessible to the world! 🎉**

**Next Step:** Begin Day 1 tasks → Security hardening & configuration
