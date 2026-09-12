-- ====================================================================
-- Query 11: Top 5 Places with Highest Casualties
-- Description: Aggregates human casualties by location.
-- IMPORTANT NOTE: The standard USGS Earthquake API dataset does NOT 
--                 include casualty figures. Do NOT substitute 'sig' 
--                 (significance score) for casualties.
-- PREREQUISITE: Requires joining an external impact/humanitarian dataset 
--               or adding a 'casualties' column to the earthquakes table.
-- ====================================================================

SELECT
    place,
    SUM(casualties) AS total_casualties
FROM earthquakes
WHERE casualties IS NOT NULL
GROUP BY place
ORDER BY total_casualties DESC
LIMIT 5;
