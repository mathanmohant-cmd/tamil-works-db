# Tamil Words Search - Quick Start Guide

Get the web application running in 5 minutes!

## Prerequisites Check

```bash
# Check Python
python --version  # Should be 3.8+

# Check Node.js
node --version    # Should be 16+

# Check PostgreSQL
psql --version    # Should be 14+
```

## Step 1: Setup Database (2 minutes)

```bash
# Create database
createdb tamil_literature

# Load schema and sample data
psql tamil_literature -f sql/complete_setup.sql

# Verify (should show 5 works, multiple verses, words)
psql tamil_literature -f verify_setup.sql
```

## Step 2: Start Backend (1 minute)

```bash
cd webapp/backend

# Install Python packages
pip install -r requirements.txt

# Create config
echo "DATABASE_URL=postgresql://localhost/tamil_literature" > .env

# Start server (http://localhost:8000)
python main.py
```

In a new terminal, verify backend is running:
```bash
curl http://localhost:8000/health
```

## Step 3: Start Frontend (1 minute)

```bash
cd webapp/frontend

# Install Node packages
npm install

# Start dev server (http://localhost:5173)
npm run dev
```

## Step 4: Use the Application

1. Open browser: http://localhost:5173
2. Enter a Tamil word: `அறம்` or `உலகு`
3. Click "Search"
4. View results with context!

## Quick Test Searches

Try these Tamil words:
- `அறம்` (virtue) - appears in multiple works
- `உலகு` (world) - common across texts
- `முதல்` (first) - in different contexts
- `இன்பம்` (happiness)
- `அன்பு` (love)

## Troubleshooting

### Backend won't start
```bash
# Check database connection
psql tamil_literature -c "SELECT COUNT(*) FROM works;"

# Should return 5
```

### No results found
```bash
# Check if data loaded
curl http://localhost:8000/stats

# Should show total_words > 0
```

### Frontend can't connect
- Make sure backend is running on port 8000
- Check browser console for errors
- Verify CORS settings in backend/main.py

## API Documentation

Once backend is running, visit:
- **Interactive Docs**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc

## Next Steps

1. **Add More Data**: Use the sample data scripts to add more verses
2. **Customize Styling**: Edit `webapp/frontend/src/style.css`
3. **Add Features**: Check webapp/README.md for enhancement ideas
4. **Deploy**: See deployment guides in individual README files

## File Structure

```
tamil-works-db/
├── sql/
│   ├── complete_setup.sql     # ← Run this first
│   └── verify_setup.sql       # ← Check setup
├── webapp/
│   ├── backend/
│   │   ├── main.py           # ← Backend API
│   │   ├── database.py       # ← DB queries
│   │   └── requirements.txt  # ← Python deps
│   └── frontend/
│       ├── src/
│       │   ├── App.vue       # ← Main UI
│       │   └── style.css     # ← Styles
│       └── package.json      # ← Node deps
└── QUICK_START.md            # ← This file
```

## Common Commands

```bash
# Backend
cd webapp/backend
python main.py                 # Start server
pip install -r requirements.txt # Install deps

# Frontend
cd webapp/frontend
npm run dev                    # Start dev server
npm run build                  # Build for production

# Database
psql tamil_literature          # Connect to DB
psql tamil_literature -f sql/complete_setup.sql  # Reset DB
```

## Support

- Backend issues: Check `webapp/backend/README.md`
- Frontend issues: Check `webapp/frontend/README.md`
- Database issues: Check `docs/database_guide.md`
- Full guide: Check `webapp/README.md`

Happy searching! 🎉
