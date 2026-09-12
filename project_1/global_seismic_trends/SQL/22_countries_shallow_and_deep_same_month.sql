-- ====================================================================
-- Query 22: Countries with Both Shallow and Deep Earthquakes in Same Month
-- Description: Identifies regions experiencing both shallow (< 70 km) and 
--              deep (> 300 km) seismicity within the same calendar month,
--              indicating active subduction zone dynamics.
-- ====================================================================

SELECT
    country,
    YEAR(time) AS earthquake_year,
    MONTH(time) AS earthquake_month,

    SUM(
        CASE
            WHEN depth_km < 70 THEN 1
            ELSE 0
        END
    ) AS shallow_count,

    SUM(
        CASE
            WHEN depth_km > 300 THEN 1
            ELSE 0
        END
    ) AS deep_count

FROM earthquakes

WHERE country IS NOT NULL
  AND country <> 'Unknown'
  AND time IS NOT NULL

GROUP BY
    country,
    YEAR(time),
    MONTH(time)

HAVING shallow_count > 0
   AND deep_count > 0

ORDER BY
    earthquake_year,
    earthquake_month,
    country;
