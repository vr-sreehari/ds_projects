-- ====================================================================
-- Query 14: Reviewed vs Automatic Events
-- Description: Compares seismologist-reviewed events against automated 
--              machine-detected events (status column).
-- ====================================================================

SELECT
    status,
    COUNT(*) AS earthquake_count
FROM earthquakes
WHERE status IS NOT NULL
GROUP BY status
ORDER BY earthquake_count DESC;
