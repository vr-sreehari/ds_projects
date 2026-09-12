-- ====================================================================
-- Query 10: Most Active Reporting Network
-- Description: Finds the data contributor network (e.g., ak, us, ci, nc) 
--              responsible for reporting the greatest number of seismic events.
-- ====================================================================

SELECT
    net,
    COUNT(*) AS earthquake_count
FROM earthquakes
WHERE net IS NOT NULL
GROUP BY net
ORDER BY earthquake_count DESC
LIMIT 1;
