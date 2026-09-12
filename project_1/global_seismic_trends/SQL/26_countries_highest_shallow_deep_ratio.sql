-- ====================================================================
-- Query 26: Countries with Highest Shallow-to-Deep Ratio
-- Description: Calculates the ratio of shallow (< 70 km) to deep (> 300 km) 
--              earthquakes for each country with at least one deep event.
-- ====================================================================

SELECT
    country,

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
    ) AS deep_count,

    ROUND(
        SUM(
            CASE
                WHEN depth_km < 70 THEN 1
                ELSE 0
            END
        )
        /
        NULLIF(
            SUM(
                CASE
                    WHEN depth_km > 300 THEN 1
                    ELSE 0
                END
            ),
            0
        ),
        2
    ) AS shallow_deep_ratio

FROM earthquakes

WHERE country IS NOT NULL
  AND country <> 'Unknown'

GROUP BY country

HAVING deep_count > 0

ORDER BY shallow_deep_ratio DESC;
