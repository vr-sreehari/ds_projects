-- ====================================================================
-- Query 06: Year with Most Earthquakes
-- Description: Finds the calendar year with the highest recorded earthquake volume.
-- ====================================================================

SELECT
    YEAR(time) AS earthquake_year,
    COUNT(*) AS earthquake_count
FROM earthquakes
WHERE time IS NOT NULL
GROUP BY YEAR(time)
ORDER BY earthquake_count DESC
LIMIT 1;
