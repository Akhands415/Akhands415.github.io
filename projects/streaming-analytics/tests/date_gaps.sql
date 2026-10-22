-- Returns one row per platform and missing date between that platform's first and last date.
WITH RECURSIVE bounds AS (
    SELECT platform, MIN(stream_date) AS d0, MAX(stream_date) AS d1 FROM stg_streams GROUP BY platform
),
cal AS (
    SELECT platform, d0 AS d, d1 FROM bounds
    UNION ALL
    SELECT platform, DATE(d, '+1 day'), d1 FROM cal WHERE d < d1
)
SELECT cal.platform, cal.d AS missing_date
FROM cal
LEFT JOIN (SELECT DISTINCT platform, stream_date FROM stg_streams) s
       ON s.platform = cal.platform AND s.stream_date = cal.d
WHERE s.stream_date IS NULL
ORDER BY 1, 2
