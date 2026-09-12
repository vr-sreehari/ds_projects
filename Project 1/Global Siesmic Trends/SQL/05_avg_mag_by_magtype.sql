-- ====================================================================
-- Query 05: Average Magnitude by magType
-- Description: Evaluates the mean magnitude and frequency across different 
--              magnitude calculation formulas (e.g., mb, ml, mww, mwr).
-- ====================================================================

SELECT
    magType,
    ROUND(AVG(mag), 2) AS avg_magnitude,
    COUNT(*) AS earthquake_count
FROM earthquakes
WHERE magType IS NOT NULL
GROUP BY magType
ORDER BY avg_magnitude DESC;
