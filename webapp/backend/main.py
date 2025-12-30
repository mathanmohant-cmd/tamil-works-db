"""
FastAPI backend for Tamil Words Search Application
"""
import os
from dotenv import load_dotenv
from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List
from pydantic import BaseModel
from database import Database

# Load environment variables from .env file
load_dotenv()

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

# Note: Admin user setup is handled lazily on first login attempt
# The ensure_admin_user_exists() is called when verifying credentials
# This prevents blocking startup if database is temporarily unavailable


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


class CollectionCreate(BaseModel):
    collection_name: str
    collection_name_tamil: Optional[str] = None
    collection_type: str = "custom"
    description: Optional[str] = None
    parent_collection_id: Optional[int] = None
    sort_order: Optional[int] = None


class CollectionUpdate(BaseModel):
    collection_name: Optional[str] = None
    collection_name_tamil: Optional[str] = None
    collection_type: Optional[str] = None
    description: Optional[str] = None
    parent_collection_id: Optional[int] = None
    sort_order: Optional[int] = None


class WorkAssignment(BaseModel):
    work_id: int
    position: Optional[int] = None
    is_primary: bool = False
    notes: Optional[str] = None


class LoginRequest(BaseModel):
    username: str
    password: str


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
    sort_by: str = Query("alphabetical", pattern="^(alphabetical|canonical|chronological|collection)$", description="Sort order: alphabetical, canonical (traditional order 1-22), chronological, or collection"),
    collection_id: Optional[int] = Query(None, description="Collection ID for collection-based sorting (required when sort_by=collection)")
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
    - **sort_by**: Sort order - "alphabetical" (default), "canonical" (traditional 1-22 order), "chronological", or "collection"
    - **collection_id**: Collection ID for custom ordering (required when sort_by="collection")
    """
    try:
        # Parse work_ids if provided
        work_id_list = None
        if work_ids:
            work_id_list = [int(x.strip()) for x in work_ids.split(",")]

        # Validate collection_id requirement
        if sort_by == "collection" and collection_id is None:
            raise HTTPException(status_code=400, detail="collection_id is required when sort_by=collection")

        # Search database
        results = db.search_words(
            search_term=q,
            match_type=match_type,
            word_position=word_position,
            work_ids=work_id_list,
            word_root=word_root,
            limit=limit,
            offset=offset,
            sort_by=sort_by,
            collection_id=collection_id
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


@app.get("/collections")
def get_public_collections():
    """
    Get all collections (public endpoint for sort options)

    Returns list of collections for use in sorting options
    """
    try:
        return db.get_collections(include_works=False)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/settings/designated_filter_collection")
def get_designated_filter_collection():
    """
    Get the designated collection ID for the filter UI

    Returns collection_id = 1 (Tamil Literature root collection)
    This collection is created by the schema and serves as the root for the filter hierarchy
    """
    return {"collection_id": 1}


@app.get("/collections/tree")
def get_collections_tree(root: int = Query(None, description="Root collection ID to filter tree")):
    """
    Get collections as a nested tree structure for filter navigation

    Args:
        root: Optional collection_id to use as root (returns only this subtree)

    Returns hierarchical collection tree with work counts
    """
    try:
        return db.get_collection_tree(root_collection_id=root)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/collections/{collection_id}/works")
def get_collection_works(collection_id: int):
    """
    Get all works in a specific collection

    Args:
        collection_id: The collection ID

    Returns list of works in the collection
    """
    try:
        return db.get_works_by_collection(collection_id)
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


# =========================================================================
# Admin Authentication
# =========================================================================

@app.post("/admin/login")
def admin_login(credentials: LoginRequest):
    """
    Authenticate admin user

    Returns user info if credentials are valid
    """
    try:
        # Ensure admin user exists (creates table and default user if needed)
        db.ensure_admin_user_exists()

        user = db.verify_admin_user(credentials.username, credentials.password)
        if not user:
            raise HTTPException(status_code=401, detail="Invalid username or password")
        return {"success": True, "user": user}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# =========================================================================
# Admin Collection Endpoints
# =========================================================================

@app.get("/admin/collections")
def get_collections(
    include_works: bool = Query(False, description="Include works in each collection"),
    tree: bool = Query(False, description="Return as nested tree structure")
):
    """
    Get all collections

    - **include_works**: Include works assigned to each collection
    - **tree**: Return as nested tree structure instead of flat list
    """
    try:
        if tree:
            return db.get_collection_tree()
        return db.get_collections(include_works=include_works)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/admin/collections/{collection_id}")
def get_collection(collection_id: int):
    """Get a single collection with its works and children"""
    try:
        collection = db.get_collection(collection_id)
        if not collection:
            raise HTTPException(status_code=404, detail="Collection not found")
        return collection
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/admin/collections", status_code=201)
def create_collection(collection: CollectionCreate):
    """Create a new collection"""
    try:
        return db.create_collection(collection.model_dump())
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/admin/collections/{collection_id}")
def update_collection(collection_id: int, collection: CollectionUpdate):
    """Update an existing collection"""
    try:
        result = db.update_collection(collection_id, collection.model_dump(exclude_unset=True))
        if not result:
            raise HTTPException(status_code=404, detail="Collection not found")
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/admin/collections/{collection_id}")
def delete_collection(collection_id: int):
    """Delete a collection"""
    try:
        if not db.delete_collection(collection_id):
            raise HTTPException(status_code=404, detail="Collection not found")
        return {"message": "Collection deleted"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/admin/collections/{collection_id}/works")
def add_work_to_collection(collection_id: int, assignment: WorkAssignment):
    """Add a work to a collection"""
    try:
        return db.add_work_to_collection(
            collection_id=collection_id,
            work_id=assignment.work_id,
            position=assignment.position,
            is_primary=assignment.is_primary,
            notes=assignment.notes
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/admin/collections/{collection_id}/works/{work_id}")
def remove_work_from_collection(collection_id: int, work_id: int):
    """Remove a work from a collection"""
    try:
        if not db.remove_work_from_collection(collection_id, work_id):
            raise HTTPException(status_code=404, detail="Work not found in collection")
        return {"message": "Work removed from collection"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.patch("/admin/collections/{collection_id}/works/{work_id}/position")
def update_work_position(collection_id: int, work_id: int, position: int = Query(...)):
    """Update a work's position within a collection"""
    try:
        if not db.update_work_position(collection_id, work_id, position):
            raise HTTPException(status_code=404, detail="Work not found in collection")
        return {"message": "Position updated"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
