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

    def search_words(
        self,
        search_term: str,
        match_type: str = "partial",  # "exact" or "partial"
        word_position: str = "beginning",  # "beginning", "end", or "anywhere"
        work_ids: Optional[List[int]] = None,
        word_root: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
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
                else:  # partial - apply word_position
                    if word_position == "beginning":
                        query += " AND wd.word_text LIKE %s"
                        params.append(f"{search_term}%")
                    elif word_position == "end":
                        query += " AND wd.word_text LIKE %s"
                        params.append(f"%{search_term}")
                    else:  # anywhere
                        query += " AND wd.word_text LIKE %s"
                        params.append(f"%{search_term}%")

                # Add work filter
                if work_ids:
                    placeholders = ','.join(['%s'] * len(work_ids))
                    query += f" AND wd.work_name IN (SELECT work_name FROM works WHERE work_id IN ({placeholders}))"
                    params.extend(work_ids)

                # Add word root filter
                if word_root:
                    query += " AND wd.word_root = %s"
                    params.append(word_root)

                # Add ordering and pagination
                query += """
                    ORDER BY wd.work_name, wd.verse_id, wd.line_number, wd.word_position
                    LIMIT %s OFFSET %s
                """
                params.extend([limit, offset])

                # Execute search query
                cur.execute(query, params)
                results = cur.fetchall()

                # Get total count for pagination
                count_query = """
                    SELECT COUNT(*)
                    FROM word_details wd
                    WHERE 1=1
                """

                # Add the same filters as the main query
                if match_type == "exact":
                    count_query += " AND wd.word_text = %s"
                else:  # partial - apply word_position
                    if word_position == "beginning":
                        count_query += " AND wd.word_text LIKE %s"
                    elif word_position == "end":
                        count_query += " AND wd.word_text LIKE %s"
                    else:  # anywhere
                        count_query += " AND wd.word_text LIKE %s"

                if work_ids:
                    placeholders = ','.join(['%s'] * len(work_ids))
                    count_query += f" AND wd.work_name IN (SELECT work_name FROM works WHERE work_id IN ({placeholders}))"

                if word_root:
                    count_query += " AND wd.word_root = %s"

                cur.execute(count_query, params[:-2])  # Exclude limit and offset
                total_count = cur.fetchone()['count']

                # Get unique words with counts for the complete list (no pagination)
                words_query = """
                    SELECT
                        wd.word_text,
                        COUNT(*) as count
                    FROM word_details wd
                    WHERE 1=1
                """

                # Add the same filters as the main query
                words_params = []
                if match_type == "exact":
                    words_query += " AND wd.word_text = %s"
                    words_params.append(search_term)
                else:  # partial - apply word_position
                    if word_position == "beginning":
                        words_query += " AND wd.word_text LIKE %s"
                        words_params.append(f"{search_term}%")
                    elif word_position == "end":
                        words_query += " AND wd.word_text LIKE %s"
                        words_params.append(f"%{search_term}")
                    else:  # anywhere
                        words_query += " AND wd.word_text LIKE %s"
                        words_params.append(f"%{search_term}%")

                if work_ids:
                    placeholders = ','.join(['%s'] * len(work_ids))
                    words_query += f" AND wd.work_name IN (SELECT work_name FROM works WHERE work_id IN ({placeholders}))"
                    words_params.extend(work_ids)

                if word_root:
                    words_query += " AND wd.word_root = %s"
                    words_params.append(word_root)

                words_query += " GROUP BY wd.word_text ORDER BY wd.word_text"

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

    def get_works(self) -> List[Dict]:
        """Get all literary works"""
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT
                        work_id,
                        work_name,
                        work_name_tamil,
                        author,
                        author_tamil,
                        period,
                        description
                    FROM works
                    ORDER BY work_id
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

