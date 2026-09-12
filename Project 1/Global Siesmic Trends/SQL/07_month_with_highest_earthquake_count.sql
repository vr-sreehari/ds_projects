-- ====================================================================
-- Query 07: Month with Highest Earthquake Count
-- Description: Identifies the seasonal peak month across all recorded years.
-- ====================================================================

SELECT
    MONTH(time) AS month_number,
    MONTHNAME(time) AS month_name,
    COUNT(*) AS earthquake_count
FROM earthquakes
WHERE time IS NOT NULL
GROUP BY MONTH(time), MONTHNAME(time)
ORDER BY earthquake_count DESC
LIMIT 1;
