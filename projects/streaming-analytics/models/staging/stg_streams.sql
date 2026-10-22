-- Staging: remove invalid rows and collapse duplicates to one row per day, platform and track.
SELECT
    stream_date,
    platform,
    track_id,
    MAX(streams) AS streams
FROM raw_streams
WHERE track_id IS NOT NULL
  AND streams >= 0
GROUP BY stream_date, platform, track_id
