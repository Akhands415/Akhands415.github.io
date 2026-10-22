-- Monthly market share of each platform within this dataset.
WITH monthly AS (
    SELECT SUBSTR(stream_date, 1, 7) AS month, platform, SUM(streams) AS streams
    FROM stg_streams
    GROUP BY 1, 2
)
SELECT
    month,
    platform,
    streams,
    ROUND(100.0 * streams / SUM(streams) OVER (PARTITION BY month), 2) AS share_pct
FROM monthly
