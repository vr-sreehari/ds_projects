-- ====================================================================
-- Query 04: Average Depth Per Continent
-- Description: Aggregates average earthquake depth across continents.
-- NOTE: Requires the 'continent' derived/mapped column in your table.
-- ====================================================================

SELECT
    continent,
    ROUND(AVG(depth_km), 2) AS avg_depth_km,
    COUNT(*) AS earthquake_count
FROM earthquakes
WHERE continent IS NOT NULL
GROUP BY continent
ORDER BY avg_depth_km DESC;
