"""
FastAPI backend for Tamil Words Search Application
"""
import os
from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List
from pydantic import BaseModel
from database import Database

# Initialize FastAPI app
app = FastAPI(
    title="Tamil Literary Works Search API",
    description="API for searching Tamil words across classical Tamil literature",
    version="1.0.0"
)

# Configure CORS - support both local and production origins
ALLOWED_ORIGINS = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:5173,http://localhost:3000,http://localhost:8080"
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database
db = Database()


# Pydantic models for request/response
class SearchResponse(BaseModel):
    results: List[dict]
    unique_words: List[dict]
    total_count: int
    limit: int
    offset: int
    search_term: str
    match_type: str


class Work(BaseModel):
    work_id: int
    work_name: str
    work_name_tamil: str
    author: Optional[str]
    author_tamil: Optional[str]
    period: Optional[str]
    description: Optional[str]
    primary_collection_id: Optional[int]
    canonical_position: Optional[int]  # Position in Traditional Canon collection (if applicable)
    chronology_start_year: Optional[int]
    chronology_end_year: Optional[int]
    chronology_confidence: Optional[str]
    chronology_notes: Optional[str]


class Statistics(BaseModel):
    total_works: int
    total_verses: int
    total_lines: int
    total_words: int
    distinct_words: int
    unique_roots: int


# API Endpoints

@app.get("/")
def root():
    """API root endpoint"""
    return {
        "message": "Tamil Literary Works Search API",
        "version": "1.0.0",
        "endpoints": {
            "/search": "Search for words",
            "/works": "Get all works",
            "/roots": "Get word roots",
            "/verse/{verse_id}": "Get verse details",
            "/stats": "Get database statistics"
        }
    }


@app.get("/search", response_model=SearchResponse)
def search_words(
    q: str = Query(..., min_length=1, description="Search term (Tamil word)"),
    match_type: str = Query("partial", pattern="^(exact|partial)$", description="Match type: exact or partial"),
    word_position: str = Query("beginning", pattern="^(beginning|end|anywhere)$", description="Word position: beginning, end, or anywhere"),
    work_ids: Optional[str] = Query(None, description="Comma-separated work IDs to filter"),
    word_root: Optional[str] = Query(None, description="Filter by word root"),
    limit: int = Query(100, ge=0, le=500, description="Maximum results per page"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
    sort_by: str = Query("alphabetical", pattern="^(alphabetical|canonical|chronological)$", description="Sort order: alphabetical, canonical (traditional order 1-22), or chronological")
):
    """
    Search for Tamil words across all literary works

    - **q**: Tamil word to search for (required)
    - **match_type**: "exact" for exact match, "partial" for substring match
    - **word_position**: "beginning" for words starting with search term, "end" for words ending with it, "anywhere" for substring match
    - **work_ids**: Filter by specific works (comma-separated IDs)
    - **word_root**: Filter by word root
    - **limit**: Maximum number of results (1-500)
    - **offset**: Pagination offset
    - **sort_by**: Sort order - "alphabetical" (default), "canonical" (traditional 1-22 order), or "chronological"
    """
    try:
        # Parse work_ids if provided
        work_id_list = None
        if work_ids:
            work_id_list = [int(x.strip()) for x in work_ids.split(",")]

        # Search database
        results = db.search_words(
            search_term=q,
            match_type=match_type,
            word_position=word_position,
            work_ids=work_id_list,
            word_root=word_root,
            limit=limit,
            offset=offset,
            sort_by=sort_by
        )

        return results

    except Exception as e:
        import traceback
        import sys
        # Log the full error to stderr for Railway logs
        sys.stderr.write(f"\n{'='*70}\n")
        sys.stderr.write(f"ERROR in /search endpoint:\n")
        sys.stderr.write(f"Search term: {q}\n")
        sys.stderr.write(f"Match type: {match_type}\n")
        sys.stderr.write(f"Word position: {word_position}\n")
        sys.stderr.write(f"Work IDs: {work_ids}\n")
        sys.stderr.write(f"Limit: {limit}, Offset: {offset}\n")
        sys.stderr.write(f"Error: {str(e)}\n")
        sys.stderr.write(f"Traceback:\n")
        traceback.print_exc(file=sys.stderr)
        sys.stderr.write(f"{'='*70}\n")
        sys.stderr.flush()
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/works", response_model=List[Work])
def get_works(
    sort_by: str = Query("alphabetical", pattern="^(alphabetical|canonical|chronological)$",
                        description="Sort order: alphabetical (by name), canonical (traditional 1-22 order), or chronological (by date)")
):
    """
    Get all literary works in the database

    Returns list of works with metadata

    - **sort_by**: Sort order - "alphabetical", "canonical" (traditional 1-22 order), or "chronological"
    """
    try:
        return db.get_works(sort_by=sort_by)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/roots")
def get_word_roots(
    q: Optional[str] = Query(None, description="Filter roots by search term")
):
    """
    Get distinct word roots, optionally filtered

    - **q**: Optional search term to filter roots
    """
    try:
        return db.get_word_roots(search_term=q)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/verse/{verse_id}")
def get_verse(verse_id: int):
    """
    Get complete verse with all lines and context

    - **verse_id**: ID of the verse to retrieve
    """
    try:
        verse = db.get_verse_context(verse_id)
        if not verse:
            raise HTTPException(status_code=404, detail="Verse not found")
        return verse
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/test_verse_type")
def test_verse_type():
    """Test endpoint to check verse_type_tamil"""
    import psycopg2
    from psycopg2.extras import RealDictCursor
    conn = psycopg2.connect(db.connection_string)
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT verse_type, verse_type_tamil FROM word_details WHERE work_name = 'Thirukkural' LIMIT 1")
    result = dict(cur.fetchone())
    cur.close()
    conn.close()
    return {"keys": list(result.keys()), "has_verse_type_tamil": "verse_type_tamil" in result, "data": result}


@app.get("/stats", response_model=Statistics)
def get_statistics():
    """
    Get database statistics

    Returns counts of works, verses, lines, words, and unique roots
    """
    try:
        return db.get_statistics()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Health check endpoint
@app.get("/health")
def health_check():
    """Health check endpoint"""
    try:
        stats = db.get_statistics()
        return {
            "status": "healthy",
            "database": "connected",
            "stats": stats
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e)
        }


@app.get("/debug/sample-words")
def debug_sample_words():
    """Debug endpoint - get sample words from database"""
    try:
        with db.get_connection() as conn:
            with conn.cursor() as cur:
                # Check if word_details view exists
                cur.execute("""
                    SELECT table_name
                    FROM information_schema.views
                    WHERE table_name = 'word_details'
                """)
                view_exists = cur.fetchone()

                # Get sample words directly from words table
                cur.execute("""
                    SELECT word_id, word_text, line_id
                    FROM words
                    LIMIT 10
                """)
                sample_words = [dict(zip(['word_id', 'word_text', 'line_id'], row)) for row in cur.fetchall()]

                # Try querying word_details view
                word_details_sample = []
                if view_exists:
                    cur.execute("SELECT * FROM word_details LIMIT 5")
                    columns = [desc[0] for desc in cur.description]
                    word_details_sample = [dict(zip(columns, row)) for row in cur.fetchall()]

                return {
                    "word_details_view_exists": bool(view_exists),
                    "sample_words_from_table": sample_words,
                    "sample_from_word_details_view": word_details_sample
                }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
