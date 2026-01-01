"""
Database connection and query functions for Tamil Words Search
"""
import os
import time
import logging
from typing import List, Dict, Optional
import psycopg2
from psycopg2 import pool
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager
import bcrypt

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Database:
    def __init__(self, connection_string: str = None):
        """Initialize database connection pool"""
        self.connection_string = connection_string or os.getenv(
            "DATABASE_URL",
            "postgresql://postgres:postgres@localhost:5432/tamil_literature"
        )

        # Initialize connection pool
        # minconn=2: Keep at least 2 connections alive
        # maxconn=10: Allow up to 10 concurrent connections
        try:
            self.connection_pool = pool.SimpleConnectionPool(
                minconn=2,
                maxconn=10,
                dsn=self.connection_string
            )
            if self.connection_pool:
                print("✓ Connection pool created successfully")
        except (Exception, psycopg2.DatabaseError) as error:
            print(f"✗ Error creating connection pool: {error}")
            raise

    @contextmanager
    def get_connection(self):
        """Context manager for database connections from the pool"""
        conn = self.connection_pool.getconn()
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            # Return connection to pool instead of closing
            self.connection_pool.putconn(conn)

    def close_all_connections(self):
        """Close all connections in the pool (call on shutdown)"""
        if self.connection_pool:
            self.connection_pool.closeall()
            print("✓ All database connections closed")

    def _escape_like_pattern(self, pattern: str) -> str:
        """
        Escape special SQL LIKE characters (%, _) in search pattern
        """
        # Escape backslash first, then % and _
        return pattern.replace('\\', '\\\\').replace('%', '\\%').replace('_', '\\_')

    def _build_search_filters(self, search_term: str, match_type: str, word_position: str,
                              work_ids: Optional[List[int]] = None, word_root: Optional[str] = None) -> tuple:
        """
        Build WHERE clause and parameters for search queries

        Args:
            search_term: The word to search for
            match_type: "exact" or "partial"
            word_position: "beginning", "end", or "anywhere"
            work_ids: Optional list of work IDs to filter by
            word_root: Optional word root to filter by

        Returns:
            Tuple of (where_clause, params)
        """
        where_clauses = []
        params = []

        # Add search term filter
        if match_type == "exact":
            where_clauses.append("word_text = %s")
            params.append(search_term)
        else:  # partial - apply word_position with escaped pattern
            escaped_term = self._escape_like_pattern(search_term)
            if word_position == "beginning":
                where_clauses.append("word_text LIKE %s ESCAPE '\\'")
                params.append(f"{escaped_term}%")
            elif word_position == "end":
                where_clauses.append("word_text LIKE %s ESCAPE '\\'")
                params.append(f"%{escaped_term}")
            else:  # anywhere
                where_clauses.append("word_text LIKE %s ESCAPE '\\'")
                params.append(f"%{escaped_term}%")

        # Add work filter
        if work_ids:
            placeholders = ','.join(['%s'] * len(work_ids))
            where_clauses.append(f"work_name IN (SELECT work_name FROM works WHERE work_id IN ({placeholders}))")
            params.extend(work_ids)

        # Add word root filter
        if word_root:
            where_clauses.append("word_root = %s")
            params.append(word_root)

        where_clause = " AND ".join(where_clauses) if where_clauses else "1=1"
        return where_clause, params

    def _execute_query_with_timing(self, cursor, query: str, params=None, query_name: str = "query"):
        """
        Execute a query and log its execution time

        Args:
            cursor: Database cursor
            query: SQL query string
            params: Query parameters (optional)
            query_name: Name for logging (e.g., "main_search", "count")

        Returns:
            float: Elapsed time in milliseconds
        """
        start_time = time.time()

        # Run EXPLAIN ANALYZE if enabled (development only)
        if os.getenv('ENABLE_QUERY_ANALYSIS') == 'true':
            try:
                explain_query = f"EXPLAIN ANALYZE {query}"
                cursor.execute(explain_query, params)
                plan = cursor.fetchall()
                logger.info(f"\n=== EXPLAIN ANALYZE for {query_name} ===")
                for row in plan:
                    logger.info(row[0] if isinstance(row, tuple) else row)
                logger.info("=" * 50)
                # Reset cursor for actual query execution
                cursor.connection.rollback()
            except Exception as e:
                logger.warning(f"EXPLAIN ANALYZE failed for {query_name}: {e}")

        # Execute actual query
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)

        elapsed_ms = (time.time() - start_time) * 1000

        # Log slow queries (>100ms threshold)
        if elapsed_ms > 100:
            logger.warning(f"⚠️  Slow query ({elapsed_ms:.2f}ms) - {query_name}: {query[:150]}...")
        else:
            logger.info(f"✓ Query completed ({elapsed_ms:.2f}ms) - {query_name}")

        return elapsed_ms

    def search_words(
        self,
        search_term: str,
        match_type: str = "partial",  # "exact" or "partial"
        word_position: str = "beginning",  # "beginning", "end", or "anywhere"
        work_ids: Optional[List[int]] = None,
        word_root: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
        sort_by: str = "alphabetical",  # "alphabetical", "canonical", "chronological", or "collection"
        collection_id: Optional[int] = None
    ) -> Dict:
        """
        Search for words in the database

        Args:
            search_term: The word to search for
            match_type: "exact" or "partial" matching
            word_position: "beginning", "end", or "anywhere" - position of search term in word
            work_ids: Filter by specific work IDs
            word_root: Filter by word root
            limit: Maximum number of results
            offset: Pagination offset

        Returns:
            Dictionary with results and metadata
        """
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                # Build the query dynamically based on filters
                # Canonical and chronological sorting use fields from word_details view
                if sort_by in ("canonical", "chronological"):
                    # All fields now available in word_details view (no joins needed)
                    query = """
                        SELECT
                            wd.word_id,
                            wd.word_text,
                            wd.word_text_transliteration,
                            wd.word_root,
                            wd.word_type,
                            wd.word_position,
                            wd.sandhi_split,
                            wd.meaning,
                            wd.line_id,
                            wd.line_number,
                            wd.line_text,
                            wd.verse_id,
                            wd.verse_number,
                            wd.verse_type,
                            wd.verse_type_tamil,
                            wd.work_name,
                            wd.work_name_tamil,
                            wd.hierarchy_path,
                            wd.hierarchy_path_tamil,
                            wd.canonical_position,
                            wd.total_lines,
                            wd.work_verse_count,
                            wd.chronology_start_year,
                            wd.chronology_end_year,
                            wd.chronology_confidence,
                            wd.work_id,
                            wd.section_id,
                            wd.section_sort_order,
                            wd.verse_sort_order,
                            COUNT(*) OVER() as total_count
                        FROM word_details wd
                        WHERE 1=1
                    """
                    params = []
                elif sort_by == "collection" and collection_id:
                    # Join work_collections for collection position only
                    query = """
                        SELECT
                            wd.word_id,
                            wd.word_text,
                            wd.word_text_transliteration,
                            wd.word_root,
                            wd.word_type,
                            wd.word_position,
                            wd.sandhi_split,
                            wd.meaning,
                            wd.line_id,
                            wd.line_number,
                            wd.line_text,
                            wd.verse_id,
                            wd.verse_number,
                            wd.verse_type,
                            wd.verse_type_tamil,
                            wd.work_name,
                            wd.work_name_tamil,
                            wd.hierarchy_path,
                            wd.hierarchy_path_tamil,
                            wd.canonical_position,
                            wd.total_lines,
                            wd.work_verse_count,
                            wd.chronology_start_year,
                            wd.chronology_end_year,
                            wd.chronology_confidence,
                            wd.work_id,
                            wd.section_id,
                            wc.position_in_collection,
                            wd.section_sort_order,
                            wd.verse_sort_order,
                            COUNT(*) OVER() as total_count
                        FROM word_details wd
                        LEFT JOIN work_collections wc ON wd.work_id = wc.work_id AND wc.collection_id = %s
                        WHERE 1=1
                    """
                    params = [collection_id]
                else:
                    # Alphabetical - all needed fields are in word_details view (no joins needed)
                    query = """
                        SELECT
                            wd.word_id,
                            wd.word_text,
                            wd.word_text_transliteration,
                            wd.word_root,
                            wd.word_type,
                            wd.word_position,
                            wd.sandhi_split,
                            wd.meaning,
                            wd.line_id,
                            wd.line_number,
                            wd.line_text,
                            wd.verse_id,
                            wd.verse_number,
                            wd.verse_type,
                            wd.verse_type_tamil,
                            wd.work_name,
                            wd.work_name_tamil,
                            wd.hierarchy_path,
                            wd.hierarchy_path_tamil,
                            wd.canonical_position,
                            wd.total_lines,
                            wd.work_verse_count,
                            wd.chronology_start_year,
                            wd.chronology_end_year,
                            wd.chronology_confidence,
                            wd.work_id,
                            wd.section_id,
                            wd.section_sort_order,
                            wd.verse_sort_order,
                            COUNT(*) OVER() as total_count
                        FROM word_details wd
                        WHERE 1=1
                    """
                    params = []

                # Add search filters using helper method
                filter_where, filter_params = self._build_search_filters(
                    search_term, match_type, word_position, work_ids, word_root
                )
                query += f" AND {filter_where}"
                params.extend(filter_params)

                # Determine ORDER BY clause based on sort_by parameter
                # Default is now hierarchical (canonical) sorting
                if sort_by == "alphabetical":
                    # Alphabetical by work name, then hierarchical within work
                    order_clause = """
                        ORDER BY wd.work_name ASC,
                                 wd.section_sort_order ASC NULLS LAST,
                                 wd.verse_sort_order ASC NULLS LAST,
                                 wd.line_number ASC,
                                 wd.word_position ASC
                    """
                elif sort_by == "chronological":
                    # Sort by estimated chronological composition date, then hierarchical within work
                    order_clause = """
                        ORDER BY wd.chronology_start_year ASC NULLS LAST,
                                 wd.section_sort_order ASC NULLS LAST,
                                 wd.verse_sort_order ASC NULLS LAST,
                                 wd.line_number ASC,
                                 wd.word_position ASC
                    """
                elif sort_by == "collection" and collection_id:
                    # Sort by position in collection, then hierarchical within work
                    order_clause = """
                        ORDER BY wc.position_in_collection ASC NULLS LAST,
                                 wd.section_sort_order ASC NULLS LAST,
                                 wd.verse_sort_order ASC NULLS LAST,
                                 wd.line_number ASC,
                                 wd.word_position ASC
                    """
                else:  # canonical (default - hierarchical by literary canon order)
                    # Sort by traditional Tamil literary canon order, then hierarchical within work
                    order_clause = """
                        ORDER BY wd.canonical_position ASC NULLS LAST,
                                 wd.section_sort_order ASC NULLS LAST,
                                 wd.verse_sort_order ASC NULLS LAST,
                                 wd.line_number ASC,
                                 wd.word_position ASC
                    """

                # Add ordering and pagination
                query += f"{order_clause} LIMIT %s OFFSET %s"
                params.extend([limit, offset])

                # Execute search query with timing
                self._execute_query_with_timing(cur, query, params, "main_search")
                raw_results = cur.fetchall()

                # Convert to regular dicts to ensure all fields are included
                results = [dict(row) for row in raw_results]

                # Extract total_count from window function (same for all rows, just get from first)
                # If no results, total_count is 0
                if results:
                    total_count = results[0].get('total_count', 0)
                    # Remove total_count from results (not part of API response schema)
                    for row in results:
                        row.pop('total_count', None)

                    # Debug
                    import sys
                    sys.stderr.write(f"\nDEBUG Keys: {list(results[0].keys())}\n")
                    sys.stderr.flush()
                else:
                    total_count = 0

                # Get unique words with counts, work breakdown, and verse count for the complete list (no pagination)
                # Build filters once using helper method
                filter_where, filter_params = self._build_search_filters(
                    search_term, match_type, word_position, work_ids, word_root
                )

                words_query = f"""
                    WITH word_stats AS (
                        SELECT
                            word_text,
                            COUNT(*) as count,
                            COUNT(DISTINCT verse_id) as verse_count
                        FROM word_details
                        WHERE {filter_where}
                        GROUP BY word_text
                    ),
                    work_breakdown_stats AS (
                        SELECT
                            word_text,
                            work_name,
                            work_name_tamil,
                            COUNT(*) as work_count
                        FROM word_details
                        WHERE {filter_where}
                        GROUP BY word_text, work_name, work_name_tamil
                    )
                """

                # Duplicate filter params for both CTEs
                words_params = filter_params + filter_params

                words_query += """
                    SELECT
                        ws.word_text,
                        ws.count,
                        ws.verse_count,
                        json_agg(json_build_object(
                            'work_name', wbs.work_name,
                            'work_name_tamil', wbs.work_name_tamil,
                            'count', wbs.work_count
                        )) as work_breakdown
                    FROM word_stats ws
                    JOIN work_breakdown_stats wbs ON ws.word_text = wbs.word_text
                    GROUP BY ws.word_text, ws.count, ws.verse_count
                    ORDER BY ws.word_text
                """

                self._execute_query_with_timing(cur, words_query, words_params, "unique_words")
                unique_words = [dict(row) for row in cur.fetchall()]

                return {
                    "results": [dict(row) for row in results],
                    "unique_words": unique_words,
                    "total_count": total_count,
                    "limit": limit,
                    "offset": offset,
                    "search_term": search_term,
                    "match_type": match_type
                }

    def get_works(self, sort_by: str = "alphabetical") -> List[Dict]:
        """
        Get all literary works with optional sorting

        Args:
            sort_by: Sort order - "alphabetical", "canonical", or "chronological"
        """
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                # Determine ORDER BY clause
                if sort_by == "canonical":
                    # Sort by traditional Tamil canon using canonical_order field
                    order_clause = """
                        ORDER BY w.canonical_order ASC NULLS LAST, w.work_name
                    """
                    from_clause = "FROM works w"
                elif sort_by == "chronological":
                    # Sort by midpoint of date range (average of start and end year)
                    order_clause = """
                        ORDER BY (w.chronology_start_year + w.chronology_end_year) / 2 ASC NULLS LAST, w.work_id
                    """
                    from_clause = "FROM works w"
                else:  # alphabetical (default)
                    order_clause = "ORDER BY w.work_name ASC"
                    from_clause = "FROM works w"

                cur.execute(f"""
                    SELECT
                        w.work_id,
                        w.work_name,
                        w.work_name_tamil,
                        w.author,
                        w.author_tamil,
                        w.period,
                        w.description,
                        w.chronology_start_year,
                        w.chronology_end_year,
                        w.chronology_confidence,
                        w.chronology_notes,
                        w.canonical_order as canonical_position
                    {from_clause}
                    {order_clause}
                """)
                return [dict(row) for row in cur.fetchall()]

    def get_word_roots(self, search_term: Optional[str] = None) -> List[Dict]:
        """Get distinct word roots, optionally filtered by search term"""
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                query = """
                    SELECT DISTINCT
                        word_root,
                        COUNT(*) as usage_count
                    FROM words
                    WHERE word_root IS NOT NULL
                """
                params = []

                if search_term:
                    query += " AND word_root LIKE %s"
                    params.append(f"%{search_term}%")

                query += """
                    GROUP BY word_root
                    ORDER BY usage_count DESC, word_root
                    LIMIT 50
                """

                cur.execute(query, params)
                return [dict(row) for row in cur.fetchall()]

    def get_verse_context(self, verse_id: int) -> Dict:
        """Get complete verse with all lines"""
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                # Get verse info with work_verse_count
                cur.execute("""
                    WITH work_verse_counts AS (
                        SELECT
                            work_id,
                            COUNT(DISTINCT verse_id) as work_verse_count
                        FROM verses
                        GROUP BY work_id
                    )
                    SELECT
                        v.verse_id,
                        v.verse_number,
                        v.verse_type,
                        v.total_lines,
                        vh.verse_type_tamil,
                        vh.work_name,
                        vh.work_name_tamil,
                        vh.hierarchy_path,
                        vh.hierarchy_path_tamil,
                        wvc.work_verse_count
                    FROM verses v
                    JOIN verse_hierarchy vh ON v.verse_id = vh.verse_id
                    JOIN work_verse_counts wvc ON v.work_id = wvc.work_id
                    WHERE v.verse_id = %s
                """, [verse_id])
                verse = dict(cur.fetchone())

                # Get all lines
                cur.execute("""
                    SELECT
                        line_id,
                        line_number,
                        line_text,
                        line_text_transliteration,
                        line_text_translation
                    FROM lines
                    WHERE verse_id = %s
                    ORDER BY line_number
                """, [verse_id])
                verse['lines'] = [dict(row) for row in cur.fetchall()]

                return verse

    def get_statistics(self) -> Dict:
        """Get database statistics"""
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT
                        (SELECT COUNT(*) FROM works) as total_works,
                        (SELECT COUNT(*) FROM verses) as total_verses,
                        (SELECT COUNT(*) FROM lines) as total_lines,
                        (SELECT COUNT(*) FROM words) as total_words,
                        (SELECT COUNT(DISTINCT word_text) FROM words) as distinct_words,
                        (SELECT COUNT(DISTINCT word_root) FROM words WHERE word_root IS NOT NULL) as unique_roots
                """)
                return dict(cur.fetchone())

    # =========================================================================
    # Collection Management Methods
    # =========================================================================

    def get_collections(self, include_works: bool = False) -> List[Dict]:
        """
        Get all collections with hierarchy information

        Args:
            include_works: If True, include works assigned to each collection
        """
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT
                        c.collection_id,
                        c.collection_name,
                        c.collection_name_tamil,
                        c.collection_type,
                        c.description,
                        c.parent_collection_id,
                        c.sort_order,
                        pc.collection_name as parent_name,
                        pc.collection_name_tamil as parent_name_tamil,
                        (SELECT COUNT(*) FROM work_collections wc WHERE wc.collection_id = c.collection_id) as work_count
                    FROM collections c
                    LEFT JOIN collections pc ON c.parent_collection_id = pc.collection_id
                    ORDER BY c.sort_order NULLS LAST, c.collection_name
                """)
                collections = [dict(row) for row in cur.fetchall()]

                if include_works:
                    for coll in collections:
                        cur.execute("""
                            SELECT
                                w.work_id,
                                w.work_name,
                                w.work_name_tamil,
                                wc.position_in_collection,
                                wc.is_primary,
                                wc.notes
                            FROM work_collections wc
                            JOIN works w ON wc.work_id = w.work_id
                            WHERE wc.collection_id = %s
                            ORDER BY wc.position_in_collection NULLS LAST, w.work_name
                        """, [coll['collection_id']])
                        coll['works'] = [dict(row) for row in cur.fetchall()]

                return collections

    def get_collection(self, collection_id: int) -> Optional[Dict]:
        """Get a single collection by ID with its works"""
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT
                        c.collection_id,
                        c.collection_name,
                        c.collection_name_tamil,
                        c.collection_type,
                        c.description,
                        c.parent_collection_id,
                        c.sort_order,
                        pc.collection_name as parent_name,
                        pc.collection_name_tamil as parent_name_tamil
                    FROM collections c
                    LEFT JOIN collections pc ON c.parent_collection_id = pc.collection_id
                    WHERE c.collection_id = %s
                """, [collection_id])
                row = cur.fetchone()
                if not row:
                    return None

                collection = dict(row)

                # Get works in this collection
                cur.execute("""
                    SELECT
                        w.work_id,
                        w.work_name,
                        w.work_name_tamil,
                        wc.position_in_collection,
                        wc.is_primary,
                        wc.notes
                    FROM work_collections wc
                    JOIN works w ON wc.work_id = w.work_id
                    WHERE wc.collection_id = %s
                    ORDER BY wc.position_in_collection NULLS LAST, w.work_name
                """, [collection_id])
                collection['works'] = [dict(row) for row in cur.fetchall()]

                # Get child collections
                cur.execute("""
                    SELECT collection_id, collection_name, collection_name_tamil
                    FROM collections
                    WHERE parent_collection_id = %s
                    ORDER BY sort_order NULLS LAST, collection_name
                """, [collection_id])
                collection['children'] = [dict(row) for row in cur.fetchall()]

                return collection

    def create_collection(self, data: Dict) -> Dict:
        """Create a new collection"""
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                # Get next collection_id
                cur.execute("SELECT COALESCE(MAX(collection_id), 0) + 1 AS next_id FROM collections")
                next_id = cur.fetchone()['next_id']

                cur.execute("""
                    INSERT INTO collections (
                        collection_id, collection_name, collection_name_tamil,
                        collection_type, description, parent_collection_id, sort_order
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                    RETURNING *
                """, [
                    next_id,
                    data['collection_name'],
                    data.get('collection_name_tamil'),
                    data.get('collection_type', 'custom'),
                    data.get('description'),
                    data.get('parent_collection_id'),
                    data.get('sort_order')
                ])
                return dict(cur.fetchone())

    def update_collection(self, collection_id: int, data: Dict) -> Optional[Dict]:
        """Update an existing collection"""
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                # Check if collection exists
                cur.execute("SELECT 1 FROM collections WHERE collection_id = %s", [collection_id])
                if not cur.fetchone():
                    return None

                # Prevent circular parent reference
                if data.get('parent_collection_id') == collection_id:
                    raise ValueError("Collection cannot be its own parent")

                cur.execute("""
                    UPDATE collections SET
                        collection_name = COALESCE(%s, collection_name),
                        collection_name_tamil = %s,
                        collection_type = COALESCE(%s, collection_type),
                        description = %s,
                        parent_collection_id = %s,
                        sort_order = %s
                    WHERE collection_id = %s
                    RETURNING *
                """, [
                    data.get('collection_name'),
                    data.get('collection_name_tamil'),
                    data.get('collection_type'),
                    data.get('description'),
                    data.get('parent_collection_id'),
                    data.get('sort_order'),
                    collection_id
                ])
                return dict(cur.fetchone())

    def delete_collection(self, collection_id: int) -> bool:
        """Delete a collection (and unlink its works)"""
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                # Check if collection exists
                cur.execute("SELECT 1 FROM collections WHERE collection_id = %s", [collection_id])
                if not cur.fetchone():
                    return False

                # Update children to have no parent (orphan them)
                cur.execute("""
                    UPDATE collections SET parent_collection_id = NULL
                    WHERE parent_collection_id = %s
                """, [collection_id])

                # Delete work associations (CASCADE should handle this, but be explicit)
                cur.execute("DELETE FROM work_collections WHERE collection_id = %s", [collection_id])

                # Delete the collection
                cur.execute("DELETE FROM collections WHERE collection_id = %s", [collection_id])
                return True

    def add_work_to_collection(self, collection_id: int, work_id: int,
                                position: Optional[int] = None,
                                is_primary: bool = False,
                                notes: Optional[str] = None) -> Dict:
        """Add a work to a collection"""
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                # If no position provided, auto-assign next available position
                if position is None:
                    cur.execute("""
                        SELECT COALESCE(MAX(position_in_collection), 0) + 1
                        FROM work_collections
                        WHERE collection_id = %s
                    """, [collection_id])
                    position = cur.fetchone()[0]

                # If setting as primary, unset other primaries for this work
                if is_primary:
                    cur.execute("""
                        UPDATE work_collections SET is_primary = FALSE
                        WHERE work_id = %s
                    """, [work_id])

                cur.execute("""
                    INSERT INTO work_collections (work_id, collection_id, position_in_collection, is_primary, notes)
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT (work_id, collection_id) DO UPDATE SET
                        position_in_collection = EXCLUDED.position_in_collection,
                        is_primary = EXCLUDED.is_primary,
                        notes = EXCLUDED.notes
                    RETURNING *
                """, [work_id, collection_id, position, is_primary, notes])
                return dict(cur.fetchone())

    def remove_work_from_collection(self, collection_id: int, work_id: int) -> bool:
        """Remove a work from a collection"""
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    DELETE FROM work_collections
                    WHERE collection_id = %s AND work_id = %s
                """, [collection_id, work_id])
                return cur.rowcount > 0

    def update_work_position(self, collection_id: int, work_id: int, position: int) -> bool:
        """Update a work's position within a collection"""
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    UPDATE work_collections
                    SET position_in_collection = %s
                    WHERE collection_id = %s AND work_id = %s
                """, [position, collection_id, work_id])
                return cur.rowcount > 0

    def get_collection_tree(self, root_collection_id: int = None) -> List[Dict]:
        """
        Get collections as a nested tree structure

        Args:
            root_collection_id: Optional collection ID to use as root (returns only this subtree)

        Returns:
            List of collection trees with work counts
        """
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT
                        c.collection_id,
                        c.collection_name,
                        c.collection_name_tamil,
                        c.collection_type,
                        c.description,
                        c.parent_collection_id,
                        c.sort_order,
                        (SELECT COUNT(*) FROM work_collections wc WHERE wc.collection_id = c.collection_id) as work_count
                    FROM collections c
                    ORDER BY c.sort_order NULLS LAST, c.collection_name
                """)
                all_collections = [dict(row) for row in cur.fetchall()]

        # Build tree structure
        collection_map = {c['collection_id']: {**c, 'children': []} for c in all_collections}
        root_collections = []

        for coll in all_collections:
            coll_with_children = collection_map[coll['collection_id']]
            parent_id = coll['parent_collection_id']
            if parent_id and parent_id in collection_map:
                collection_map[parent_id]['children'].append(coll_with_children)
            else:
                root_collections.append(coll_with_children)

        # If root_collection_id specified, return only that subtree
        if root_collection_id and root_collection_id in collection_map:
            return [collection_map[root_collection_id]]

        return root_collections

    def get_works_by_collection(self, collection_id: int) -> List[Dict]:
        """
        Get all works in a specific collection

        Args:
            collection_id: The collection ID

        Returns:
            List of works in the collection with their position
        """
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT
                        w.work_id,
                        w.work_name,
                        w.work_name_tamil,
                        w.author,
                        w.author_tamil,
                        w.period,
                        wc.position_in_collection,
                        wc.is_primary
                    FROM works w
                    JOIN work_collections wc ON w.work_id = wc.work_id
                    WHERE wc.collection_id = %s
                    ORDER BY wc.position_in_collection NULLS LAST, w.work_name_tamil
                """, [collection_id])
                return [dict(row) for row in cur.fetchall()]

    # =========================================================================
    # Authentication Methods
    # =========================================================================

    def verify_admin_user(self, username: str, password: str) -> Optional[Dict]:
        """
        Verify admin user credentials

        Args:
            username: The username to verify
            password: The plain text password to check

        Returns:
            User dict if valid, None if invalid
        """
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT user_id, username, password_hash
                    FROM admin_users
                    WHERE username = %s
                """, [username])
                user = cur.fetchone()

                if not user:
                    return None

                # Verify password using bcrypt
                if bcrypt.checkpw(password.encode('utf-8'), user['password_hash'].encode('utf-8')):
                    return {
                        'user_id': user['user_id'],
                        'username': user['username']
                    }
                return None

    def create_admin_user(self, username: str, password: str) -> Dict:
        """
        Create a new admin user (for setup purposes)

        Args:
            username: The username
            password: The plain text password (will be hashed)

        Returns:
            Created user dict
        """
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                # Hash the password
                password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

                cur.execute("""
                    INSERT INTO admin_users (username, password_hash)
                    VALUES (%s, %s)
                    RETURNING user_id, username, created_at
                """, [username, password_hash])
                return dict(cur.fetchone())

    def ensure_admin_user_exists(self):
        """
        Ensure the default admin user exists (for initial setup)
        Creates admin user with default password if not exists
        """
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                # Check if admin_users table exists
                cur.execute("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables
                        WHERE table_name = 'admin_users'
                    )
                """)
                if not cur.fetchone()['exists']:
                    # Create the table
                    cur.execute("""
                        CREATE TABLE IF NOT EXISTS admin_users (
                            user_id SERIAL PRIMARY KEY,
                            username VARCHAR(50) NOT NULL UNIQUE,
                            password_hash VARCHAR(255) NOT NULL,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        )
                    """)
                    cur.execute("CREATE INDEX IF NOT EXISTS idx_admin_users_username ON admin_users(username)")

                # Check if admin user exists
                cur.execute("SELECT 1 FROM admin_users WHERE username = 'admin'")
                if not cur.fetchone():
                    # Create default admin user with password TKsltk#123
                    password_hash = bcrypt.hashpw('TKsltk#123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                    cur.execute("""
                        INSERT INTO admin_users (username, password_hash)
                        VALUES ('admin', %s)
                    """, [password_hash])

