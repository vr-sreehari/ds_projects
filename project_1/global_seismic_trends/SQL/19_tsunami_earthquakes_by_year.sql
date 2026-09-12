-- ====================================================================
-- Query 19: Tsunami-Triggering Earthquakes by Year
-- Description: Aggregates annual counts of high-impact earthquakes that 
--              triggered oceanic tsunami warnings (tsunami = 1).
-- ====================================================================

SELECT
    YEAR(time) AS earthquake_year,
    COUNT(*) AS tsunami_earthquakes
FROM earthquakes
WHERE tsunami = 1
  AND time IS NOT NULL
GROUP BY YEAR(time)
ORDER BY earthquake_year;
