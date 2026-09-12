-- ====================================================================
-- Query 15: Earthquake Count by Event Type
-- Description: Groups seismic events by physical phenomenon type 
--              (e.g., 'earthquake', 'quarry blast', 'ice quake', 'explosion').
-- NOTE: Uses backticks around `type` to avoid conflict with reserved keyword.
-- ====================================================================

SELECT
    `type`,
    COUNT(*) AS earthquake_count
FROM earthquakes
WHERE `type` IS NOT NULL
GROUP BY `type`
ORDER BY earthquake_count DESC;
