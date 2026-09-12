-- ====================================================================
-- Query 18: Events with High Station Coverage
-- Description: Identifies earthquakes detected by an exceptionally high 
--              number of seismic reporting stations (nst > threshold).
-- ====================================================================

SET @nst_threshold = 100;

SELECT
    id,
    time,
    place,
    mag,
    nst
FROM earthquakes
WHERE nst > @nst_threshold
ORDER BY nst DESC;
