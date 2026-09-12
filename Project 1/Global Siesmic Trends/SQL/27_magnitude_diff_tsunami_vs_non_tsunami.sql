-- ====================================================================
-- Query 27: Magnitude Difference Between Tsunami and Non-Tsunami Earthquakes
-- Description: Compares average earthquake magnitudes between tsunami-generating
--              events (tsunami = 1) and non-tsunami events (tsunami = 0).
-- ====================================================================

SELECT
    ROUND(
        AVG(
            CASE
                WHEN tsunami = 1
                THEN mag
            END
        ),
        2
    ) AS tsunami_avg_mag,

    ROUND(
        AVG(
            CASE
                WHEN tsunami = 0
                THEN mag
            END
        ),
        2
    ) AS non_tsunami_avg_mag,

    ROUND(
        AVG(
            CASE
                WHEN tsunami = 1
                THEN mag
            END
        )
        -
        AVG(
            CASE
                WHEN tsunami = 0
                THEN mag
            END
        ),
        2
    ) AS avg_magnitude_difference

FROM earthquakes;
