# Tamil Literary Words Search - Web Application

A full-stack web application for searching Tamil words across classical Tamil literature with detailed context and filtering options.

## Project Structure

```
webapp/
├── backend/           # Python FastAPI backend
│   ├── main.py       # API endpoints
│   ├── database.py   # Database queries
│   └── requirements.txt
├── frontend/         # Vue.js 3 frontend
│   ├── src/
│   │   ├── App.vue   # Main component
│   │   ├── api.js    # API client
│   │   └── style.css # Styles
│   └── package.json
└── README.md         # This file
```

## Features

### Search Capabilities
- **Partial Match**: Find words containing the search term
- **Exact Match**: Find exact word matches
- **Multi-work Search**: Search across all 5 classical works
- **Work Filtering**: Filter results by specific works

### Display Features
- **Word Details**: Root form, part of speech, meaning, sandhi split
- **Line Context**: Complete line containing the word
- **Hierarchical Path**: Full path (Work → Section → Verse)
- **Tamil & English**: Bilingual display throughout
- **Pagination**: Load more results on demand

### User Interface
- **Two-Panel Layout**: Search controls on left, results on right
- **Responsive Design**: Works on all screen sizes
- **Clean & Modern**: Material-inspired design
- **Tamil Typography**: Proper Tamil font support

## Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- PostgreSQL 14+

### 1. Setup Database

```bash
# Navigate to project root
cd tamil-works-db

# Run the complete setup SQL
psql "postgresql://localhost/tamil_literature" -f sql/complete_setup.sql

# Verify setup
psql "postgresql://localhost/tamil_literature" -f verify_setup.sql
```

### 2. Start Backend

```bash
cd webapp/backend

# Install dependencies
pip install -r requirements.txt

# Create .env file (or set DATABASE_URL environment variable)
cp .env.example .env
# Edit .env with your database connection

# Run the server
python main.py
```

Backend will be available at: http://localhost:8000
API docs at: http://localhost:8000/docs

### 3. Start Frontend

```bash
cd webapp/frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

Frontend will be available at: http://localhost:5173

## API Endpoints

### Search Words
```
GET /search?q=அறம்&match_type=partial&limit=100
```

### Get Works
```
GET /works
```

### Get Word Roots
```
GET /roots?q=அற
```

### Get Verse Details
```
GET /verse/1
```

### Statistics
```
GET /stats
```

### Health Check
```
GET /health
```

## Tech Stack

**Backend:**
- FastAPI (Python web framework)
- psycopg2 (PostgreSQL adapter)
- Pydantic (Data validation)

**Frontend:**
- Vue.js 3 (Composition API)
- Vite (Build tool)
- Axios (HTTP client)

**Database:**
- PostgreSQL 14+
- Custom schema for Tamil literature

## Database Schema

The application uses the Tamil Literary Works database schema with:
- 5 works (Tolkāppiyam, Sangam, Thirukkural, Silapathikaram, Kambaramayanam)
- Hierarchical sections (flexible structure per work)
- Verses with complete metadata
- Word-level granularity with linguistic details
- Pre-computed views for efficient queries

## Development

### Backend Development
```bash
cd webapp/backend
uvicorn main:app --reload
```

Access interactive API docs at `/docs`

### Frontend Development
```bash
cd webapp/frontend
npm run dev
```

Hot reload enabled for both backend and frontend.

## Production Deployment

### Backend
```bash
cd webapp/backend
uvicorn main:app --host 0.0.0.0 --port 8000
```

Or use gunicorn:
```bash
gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app
```

### Frontend
```bash
cd webapp/frontend
npm run build
```

Serve the `dist/` directory with any static file server (nginx, Apache, etc.)

## Environment Variables

### Backend (.env)
```
DATABASE_URL=postgresql://user:pass@localhost:5432/tamil_literature
API_HOST=0.0.0.0
API_PORT=8000
```

### Frontend (.env)
```
VITE_API_URL=http://localhost:8000
```

## Troubleshooting

### Database Connection Issues
- Verify PostgreSQL is running
- Check DATABASE_URL is correct
- Ensure database exists and schema is loaded

### CORS Issues
- Backend is configured for localhost:5173, 3000, 8080
- Add your domain to allowed_origins in main.py

### No Results Found
- Verify database has data loaded
- Check /stats endpoint for data counts
- Try partial match instead of exact

## Future Enhancements

- [ ] User authentication
- [ ] Save search history
- [ ] Export search results
- [ ] Advanced filters (date, author, section)
- [ ] Audio pronunciation
- [ ] Verse-level commentary display
- [ ] Cross-reference navigation
- [ ] Mobile app (React Native/Flutter)

## License

MIT License - Feel free to use for educational and research purposes.

## Credits

- Classical Tamil texts from public domain sources
- Modern translations and commentaries properly attributed
- Tamil Unicode fonts from Google Fonts (Noto Sans Tamil)
