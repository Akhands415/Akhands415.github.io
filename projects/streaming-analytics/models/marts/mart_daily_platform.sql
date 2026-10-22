-- Daily streams per platform with a 7-day rolling average.
WITH daily AS (
    SELECT stream_date, platform, SUM(streams) AS streams
    FROM stg_streams
    GROUP BY stream_date, platform
)
SELECT
    stream_date,
    platform,
    streams,
    AVG(streams) OVER (
        PARTITION BY platform ORDER BY stream_date
        ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
    ) AS streams_7d_avg
FROM daily
