-- ====================================================================
-- Query 02: Top 10 Deepest Earthquakes
-- Description: Retrieves the 10 deepest earthquakes recorded by focal depth.
-- ====================================================================

SELECT
    id,
    time,
    place,
    country,
    mag,
    depth_km
FROM earthquakes
WHERE depth_km IS NOT NULL
ORDER BY depth_km DESC
LIMIT 10;
