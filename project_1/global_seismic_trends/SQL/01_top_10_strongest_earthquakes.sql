-- ====================================================================
-- Query 01: Top 10 Strongest Earthquakes
-- Description: Retrieves the 10 highest magnitude earthquakes recorded.
-- ====================================================================

SELECT
    id,
    time,
    place,
    country,
    mag,
    depth_km
FROM earthquakes
WHERE mag IS NOT NULL
ORDER BY mag DESC
LIMIT 10;
