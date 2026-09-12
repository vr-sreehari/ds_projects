-- ====================================================================
-- Query 20: Earthquake Count by Alert Level
-- Description: Groups events by USGS PAGER hazard impact color 
--              (green, yellow, orange, red).
-- NOTE: Requires the 'alert' column retained from the USGS API.
-- ====================================================================

SELECT
    LOWER(alert) AS alert_level,
    COUNT(*) AS earthquake_count
FROM earthquakes
WHERE alert IS NOT NULL
GROUP BY LOWER(alert)
ORDER BY earthquake_count DESC;
