WITH word_counts AS (
    SELECT
		wk.work_id,
        wk.work_name_tamil,
        word_text,
        COUNT(*) AS freq,
        ROW_NUMBER() OVER (
            PARTITION BY wk.work_name_tamil
            ORDER BY COUNT(*) DESC
        ) AS rn
    FROM word_details wd
	join works wk on wk.work_name=wd.work_name
    GROUP BY work_id,word_text, wk.work_name_tamil
)
SELECT work_id,work_name_tamil, word_text, freq
FROM word_counts
WHERE rn <= 10
ORDER BY work_id, freq DESC;
