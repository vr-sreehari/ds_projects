-- ====================================================================
-- Query 09: Earthquakes Per Hour
-- Description: Analyzes diurnal cycle distribution across the 24 hours of UTC day.
-- ====================================================================

SELECT
    HOUR(time) AS hour_of_day,
    COUNT(*) AS earthquake_count
FROM earthquakes
WHERE time IS NOT NULL
GROUP BY HOUR(time)
ORDER BY hour_of_day;
