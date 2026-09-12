-- ====================================================================
-- Query 17: Average RMS and Gap Per Continent
-- Description: Measures seismic network quality metrics (residual travel time RMS
--              and azimuthal station gap in degrees) across continents.
-- NOTE: Requires the derived 'continent' column.
-- ====================================================================

SELECT
    continent,
    ROUND(AVG(rms), 3) AS avg_rms,
    ROUND(AVG(gap), 2) AS avg_gap,
    COUNT(*) AS earthquake_count
FROM earthquakes
WHERE continent IS NOT NULL
GROUP BY continent
ORDER BY avg_rms DESC;
