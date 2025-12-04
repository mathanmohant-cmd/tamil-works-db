# Tamil Words Search - Backend API

FastAPI backend for searching Tamil words across classical literature.

## Setup

1. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure database:**
   ```bash
   cp .env.example .env
   # Edit .env with your database connection string
   ```

3. **Run the API server:**
   ```bash
   python main.py
   ```
   Or with uvicorn directly:
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

4. **Access the API:**
   - API: http://localhost:8000
   - Interactive docs: http://localhost:8000/docs
   - Alternative docs: http://localhost:8000/redoc

## API Endpoints

### Search Words
```
GET /search?q=அறம்&match_type=partial&limit=100
```

Parameters:
- `q` (required): Tamil word to search
- `match_type`: "exact" or "partial" (default: "partial")
- `work_ids`: Filter by work IDs (comma-separated)
- `word_root`: Filter by word root
- `limit`: Results per page (1-500, default: 100)
- `offset`: Pagination offset (default: 0)

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

### Get Statistics
```
GET /stats
```

### Health Check
```
GET /health
```

## Database Schema

Expects PostgreSQL database with the schema from `sql/complete_setup.sql`.

## Development

Run with auto-reload:
```bash
uvicorn main:app --reload
```

Access interactive API documentation at `/docs` endpoint.
