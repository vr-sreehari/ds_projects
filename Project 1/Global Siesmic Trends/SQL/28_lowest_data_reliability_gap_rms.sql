-- ====================================================================
-- Query 28: Events with Lowest Data Reliability (Normalized Gap + RMS)
-- Description: Constructs an unreliability score by min-max normalizing 
--              azimuthal gap and root-mean-square (rms) travel time residuals.
--              Higher score = poorer measurement reliability.
-- ====================================================================

WITH bounds AS (

    SELECT
        MIN(gap) AS min_gap,
        MAX(gap) AS max_gap,
        MIN(rms) AS min_rms,
        MAX(rms) AS max_rms
    FROM earthquakes
    WHERE gap IS NOT NULL
      AND rms IS NOT NULL

),

reliability AS (

    SELECT
        e.id,
        e.time,
        e.place,
        e.mag,
        e.gap,
        e.rms,

        (
            (
                e.gap - b.min_gap
            ) /
            NULLIF(
                b.max_gap - b.min_gap,
                0
            )

            +

            (
                e.rms - b.min_rms
            ) /
            NULLIF(
                b.max_rms - b.min_rms,
                0
            )
        ) / 2 AS unreliability_score

    FROM earthquakes e
    CROSS JOIN bounds b

    WHERE e.gap IS NOT NULL
      AND e.rms IS NOT NULL
)

SELECT
    id,
    time,
    place,
    mag,
    gap,
    rms,
    ROUND(unreliability_score, 4) AS unreliability_score

FROM reliability

ORDER BY unreliability_score DESC
LIMIT 20;
