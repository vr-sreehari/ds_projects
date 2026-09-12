-- ====================================================================
-- Query 08: Day of Week with Most Earthquakes
-- Description: Analyzes earthquake event distribution by day of the week.
-- ====================================================================

SELECT
    DAYNAME(time) AS day_of_week,
    COUNT(*) AS earthquake_count
FROM earthquakes
WHERE time IS NOT NULL
GROUP BY DAYNAME(time)
ORDER BY earthquake_count DESC;
