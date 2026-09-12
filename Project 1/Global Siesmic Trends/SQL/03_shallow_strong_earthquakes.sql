-- ====================================================================
-- Query 03: Shallow Earthquakes Below 50 km with Magnitude > 7.5
-- Description: Identifies shallow, high-magnitude seismic events that 
--              often present the greatest risk for intense surface shaking.
-- ====================================================================

SELECT
    id,
    time,
    place,
    country,
    mag,
    depth_km
FROM earthquakes
WHERE depth_km < 50
  AND mag > 7.5
ORDER BY mag DESC;
