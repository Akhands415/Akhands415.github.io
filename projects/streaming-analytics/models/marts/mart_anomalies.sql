-- Flag days where a track's streams on a platform exceed 3x its trailing 7-day average.
WITH w AS (
    SELECT
        stream_date, platform, track_id, streams,
        AVG(streams) OVER (
            PARTITION BY platform, track_id ORDER BY stream_date
            ROWS BETWEEN 7 PRECEDING AND 1 PRECEDING
        ) AS trailing_avg
    FROM stg_streams
)
SELECT stream_date, platform, track_id, streams,
       ROUND(trailing_avg, 0) AS trailing_avg,
       ROUND(streams / trailing_avg, 2) AS ratio
FROM w
WHERE trailing_avg > 0 AND streams > 3 * trailing_avg
