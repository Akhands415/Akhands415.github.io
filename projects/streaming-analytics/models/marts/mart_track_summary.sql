-- Track ranking with share of all streams and the platform each track leans on most.
WITH by_track AS (
    SELECT track_id, SUM(streams) AS streams FROM stg_streams GROUP BY track_id
),
by_track_platform AS (
    SELECT track_id, platform, SUM(streams) AS streams,
           ROW_NUMBER() OVER (PARTITION BY track_id ORDER BY SUM(streams) DESC) AS rn
    FROM stg_streams GROUP BY track_id, platform
)
SELECT
    t.track_id,
    t.streams,
    RANK() OVER (ORDER BY t.streams DESC) AS rank,
    ROUND(100.0 * t.streams / SUM(t.streams) OVER (), 2) AS share_pct,
    p.platform AS top_platform
FROM by_track t
JOIN by_track_platform p ON p.track_id = t.track_id AND p.rn = 1
