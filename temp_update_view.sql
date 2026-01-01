DROP VIEW IF EXISTS word_details CASCADE;

CREATE VIEW word_details AS
WITH work_verse_counts AS (
    SELECT
        work_id,
        COUNT(DISTINCT verse_id) as work_verse_count
    FROM verses
    GROUP BY work_id
)
SELECT
    w.word_id,
    w.word_text,
    w.word_text_transliteration,
    w.word_root,
    w.word_type,
    w.word_position,
    w.sandhi_split,
    w.meaning,
    l.line_id,
    l.line_number,
    l.line_text,
    v.verse_id,
    v.verse_number,
    v.work_id,
    v.total_lines,
    vh.verse_type,
    vh.verse_type_tamil,
    vh.work_name,
    vh.work_name_tamil,
    vh.canonical_position,
    vh.hierarchy_path,
    vh.hierarchy_path_tamil,
    wvc.work_verse_count
FROM words w
INNER JOIN lines l ON w.line_id = l.line_id
INNER JOIN verses v ON l.verse_id = v.verse_id
INNER JOIN verse_hierarchy vh ON v.verse_id = vh.verse_id
INNER JOIN work_verse_counts wvc ON v.work_id = wvc.work_id;
