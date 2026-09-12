-- ====================================================================
-- Query 25: Average Depth Within ±5° Latitude of Equator
-- Description: Measures seismic depth characteristics for nations in the 
--              equatorial band (latitude between -5 and +5 degrees).
-- ====================================================================

SELECT
    country,
    ROUND(AVG(depth_km), 2) AS avg_depth_km,
    COUNT(*) AS earthquake_count
FROM earthquakes
WHERE latitude BETWEEN -5 AND 5
  AND country IS NOT NULL
  AND country <> 'Unknown'
GROUP BY country
ORDER BY avg_depth_km DESC;
