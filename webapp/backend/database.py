"""
Database connection and query functions for Tamil Words Search
"""
import os
from typing import List, Dict, Optional
import psycopg2
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager


class Database:
    def __init__(self, connection_string: str = None):
        """Initialize database connection"""
        self.connection_string = connection_string or os.getenv(
            "DATABASE_URL",
            "postgresql://postgres:postgres@localhost:5432/tamil_literature"
        )

    @contextmanager
    def get_connection(self):
        """Context manager for database connections"""
        conn = psycopg2.connect(self.connection_string)
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def _escape_like_pattern(self, pattern: str) -> str:
        """
        Escape special SQL LIKE characters (%, _) in search pattern
        """
        # Escape backslash first, then % and _
        return pattern.replace('\\', '\\\\').replace('%', '\\%').replace('_', '\\_')

    def search_words(
        self,
        search_term: str,
        match_type: str = "partial",  # "exact" or "partial"
        word_position: str = "beginning",  # "beginning", "end", or "anywhere"
        work_ids: Optional[List[int]] = None,
        word_root: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
        sort_by: str = "alphabetical"  # "alphabetical", "canonical", or "chronological"
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
                        wd.hierarchy_path_tamil
                    FROM word_details wd
                    WHERE 1=1
                """

                params = []

                # Add search term condition based on match_type and word_position
                if match_type == "exact":
                    query += " AND wd.word_text = %s"
                    params.append(search_term)
                else:  # partial - apply word_position with escaped pattern
                    escaped_term = self._escape_like_pattern(search_term)
                    if word_position == "beginning":
                        query += " AND wd.word_text LIKE %s ESCAPE '\\'"
                        params.append(f"{escaped_term}%")
                    elif word_position == "end":
                        query += " AND wd.word_text LIKE %s ESCAPE '\\'"
                        params.append(f"%{escaped_term}")
                    else:  # anywhere
                        query += " AND wd.word_text LIKE %s ESCAPE '\\'"
                        params.append(f"%{escaped_term}%")

                # Add work filter
                if work_ids:
                    placeholders = ','.join(['%s'] * len(work_ids))
                    query += f" AND wd.work_name IN (SELECT work_name FROM works WHERE work_id IN ({placeholders}))"
                    params.extend(work_ids)

                # Add word root filter
                if word_root:
                    query += " AND wd.word_root = %s"
                    params.append(word_root)

                # Determine ORDER BY clause based on sort_by parameter
                if sort_by == "canonical":
                    # Sort by canonical position (from Traditional Canon collection)
                    order_clause = """
                        ORDER BY wd.canonical_position ASC NULLS LAST,
                                 wd.work_name, wd.verse_id, wd.line_number, wd.word_position
                    """
                elif sort_by == "chronological":
                    # Sort by chronological order (would need chronology fields in word_details view)
                    # For now, fall back to work_name as proxy
                    order_clause = """
                        ORDER BY wd.work_name, wd.verse_id, wd.line_number, wd.word_position
                    """
                else:  # alphabetical (default)
                    order_clause = """
                        ORDER BY wd.work_name, wd.verse_id, wd.line_number, wd.word_position
                    """

                # Add ordering and pagination
                query += f"{order_clause} LIMIT %s OFFSET %s"
                params.extend([limit, offset])

                # Execute search query
                cur.execute(query, params)
                raw_results = cur.fetchall()

                # Convert to regular dicts to ensure all fields are included
                results = [dict(row) for row in raw_results]

                # Debug
                if results:
                    import sys
                    sys.stderr.write(f"\nDEBUG Keys: {list(results[0].keys())}\n")
                    sys.stderr.flush()

                # Get total count for pagination
                count_query = """
                    SELECT COUNT(*)
                    FROM word_details wd
                    WHERE 1=1
                """

                # Add the same filters as the main query
                if match_type == "exact":
                    count_query += " AND wd.word_text = %s"
                else:  # partial - apply word_position with escaped pattern
                    if word_position == "beginning":
                        count_query += " AND wd.word_text LIKE %s ESCAPE '\\'"
                    elif word_position == "end":
                        count_query += " AND wd.word_text LIKE %s ESCAPE '\\'"
                    else:  # anywhere
                        count_query += " AND wd.word_text LIKE %s ESCAPE '\\'"

                if work_ids:
                    placeholders = ','.join(['%s'] * len(work_ids))
                    count_query += f" AND wd.work_name IN (SELECT work_name FROM works WHERE work_id IN ({placeholders}))"

                if word_root:
                    count_query += " AND wd.word_root = %s"

                cur.execute(count_query, params[:-2])  # Exclude limit and offset
                total_count = cur.fetchone()['count']

                # Get unique words with counts, work breakdown, and verse count for the complete list (no pagination)
                words_query = """
                    WITH word_stats AS (
                        SELECT
                            word_text,
                            COUNT(*) as count,
                            COUNT(DISTINCT verse_id) as verse_count
                        FROM word_details
                        WHERE 1=1
                """

                # Add the same filters as the main query
                words_params = []
                if match_type == "exact":
                    words_query += " AND word_text = %s"
                    words_params.append(search_term)
                else:  # partial - apply word_position with escaped pattern
                    escaped_term = self._escape_like_pattern(search_term)
                    if word_position == "beginning":
                        words_query += " AND word_text LIKE %s ESCAPE '\\'"
                        words_params.append(f"{escaped_term}%")
                    elif word_position == "end":
                        words_query += " AND word_text LIKE %s ESCAPE '\\'"
                        words_params.append(f"%{escaped_term}")
                    else:  # anywhere
                        words_query += " AND word_text LIKE %s ESCAPE '\\'"
                        words_params.append(f"%{escaped_term}%")

                if work_ids:
                    placeholders = ','.join(['%s'] * len(work_ids))
                    words_query += f" AND work_name IN (SELECT work_name FROM works WHERE work_id IN ({placeholders}))"
                    words_params.extend(work_ids)

                if word_root:
                    words_query += " AND word_root = %s"
                    words_params.append(word_root)

                words_query += """
                        GROUP BY word_text
                    ),
                    work_breakdown_stats AS (
                        SELECT
                            word_text,
                            work_name,
                            work_name_tamil,
                            COUNT(*) as work_count
                        FROM word_details
                        WHERE 1=1
                """

                # Add the same filters for the work breakdown subquery
                if match_type == "exact":
                    words_query += " AND word_text = %s"
                    words_params.append(search_term)
                else:
                    escaped_term = self._escape_like_pattern(search_term)
                    if word_position == "beginning":
                        words_query += " AND word_text LIKE %s ESCAPE '\\'"
                        words_params.append(f"{escaped_term}%")
                    elif word_position == "end":
                        words_query += " AND word_text LIKE %s ESCAPE '\\'"
                        words_params.append(f"%{escaped_term}")
                    else:
                        words_query += " AND word_text LIKE %s ESCAPE '\\'"
                        words_params.append(f"%{escaped_term}%")

                if work_ids:
                    placeholders = ','.join(['%s'] * len(work_ids))
                    words_query += f" AND work_name IN (SELECT work_name FROM works WHERE work_id IN ({placeholders}))"
                    words_params.extend(work_ids)

                if word_root:
                    words_query += " AND word_root = %s"
                    words_params.append(word_root)

                words_query += """
                        GROUP BY word_text, work_name, work_name_tamil
                    )
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

                cur.execute(words_query, words_params)
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
                    # Sort by position in Traditional Canon collection (ID=100)
                    order_clause = """
                        ORDER BY wc_canon.position_in_collection ASC NULLS LAST, w.work_name
                    """
                    from_clause = """
                        FROM works w
                        LEFT JOIN work_collections wc_canon ON w.work_id = wc_canon.work_id
                            AND wc_canon.collection_id = 100
                    """
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
                        w.primary_collection_id,
                        wc_canon.position_in_collection as canonical_position
                    {from_clause}
                    LEFT JOIN work_collections wc_canon ON w.work_id = wc_canon.work_id
                        AND wc_canon.collection_id = 100
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
                # Get verse info
                cur.execute("""
                    SELECT
                        v.verse_id,
                        v.verse_number,
                        v.verse_type,
                        vh.verse_type_tamil,
                        vh.work_name,
                        vh.work_name_tamil,
                        vh.hierarchy_path,
                        vh.hierarchy_path_tamil
                    FROM verses v
                    JOIN verse_hierarchy vh ON v.verse_id = vh.verse_id
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
                cur.execute("SELECT COALESCE(MAX(collection_id), 0) + 1 FROM collections")
                next_id = cur.fetchone()['coalesce']

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

    def get_collection_tree(self) -> List[Dict]:
        """Get collections as a nested tree structure"""
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

        return root_collections

