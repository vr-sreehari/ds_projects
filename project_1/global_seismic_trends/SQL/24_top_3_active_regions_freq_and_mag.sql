-- ====================================================================
-- Query 24: Top 3 Most Seismically Active Regions (Frequency + Magnitude)
-- Description: Composite ranking giving 50% weight to normalized frequency 
--              and 50% weight to normalized average magnitude across countries.
-- ====================================================================

WITH country_stats AS (

    SELECT
        country,
        COUNT(*) AS frequency,
        AVG(mag) AS avg_magnitude

    FROM earthquakes

    WHERE country IS NOT NULL
      AND country <> 'Unknown'

    GROUP BY country
),

bounds AS (

    SELECT
        MIN(frequency) AS min_frequency,
        MAX(frequency) AS max_frequency,
        MIN(avg_magnitude) AS min_mag,
        MAX(avg_magnitude) AS max_mag

    FROM country_stats
)

SELECT
    cs.country,
    cs.frequency,
    ROUND(cs.avg_magnitude, 2) AS avg_magnitude,

    ROUND(
        (
            (
                cs.frequency - b.min_frequency
            ) /
            NULLIF(
                b.max_frequency - b.min_frequency,
                0
            )
        ) * 0.5

        +

        (
            (
                cs.avg_magnitude - b.min_mag
            ) /
            NULLIF(
                b.max_mag - b.min_mag,
                0
            )
        ) * 0.5,

        4
    ) AS seismic_activity_score

FROM country_stats cs
CROSS JOIN bounds b

ORDER BY seismic_activity_score DESC
LIMIT 3;
