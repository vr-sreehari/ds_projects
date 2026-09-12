-- ====================================================================
-- Query 21: Top 5 Countries with Highest Average Magnitude in Past 5 Years
-- Description: Ranks countries by mean earthquake magnitude over the last 
--              5 years, enforcing a minimum sample size of 10 events.
-- ====================================================================

SELECT
    country,
    ROUND(AVG(mag), 2) AS avg_magnitude,
    COUNT(*) AS earthquake_count
FROM earthquakes
WHERE time >= DATE_SUB(UTC_TIMESTAMP(), INTERVAL 5 YEAR)
  AND country IS NOT NULL
  AND country <> 'Unknown'
GROUP BY country
HAVING COUNT(*) >= 10
ORDER BY avg_magnitude DESC
LIMIT 5;
