-- ====================================================================
-- Query 30: Regions with Most Deep-Focus Earthquakes
-- Description: Groups and counts deep-focus earthquakes (depth > 300 km) 
--              by country/region, along with average depth and magnitude.
-- ====================================================================

SELECT
    country,
    COUNT(*) AS deep_earthquake_count,
    ROUND(AVG(depth_km), 2) AS avg_depth_km,
    ROUND(AVG(mag), 2) AS avg_magnitude
FROM earthquakes
WHERE depth_km > 300
  AND country IS NOT NULL
  AND country <> 'Unknown'
GROUP BY country
ORDER BY deep_earthquake_count DESC;
