-- ====================================================================
-- Query 16: Number of Earthquakes by Associated Data Type
-- Description: Recursively parses and splits comma-separated values in 
--              the 'types' field (e.g., origin, phase-data, dyfi, shakemap,
--              moment-tensor) and counts distinct earthquakes offering each data product.
-- ====================================================================

WITH RECURSIVE type_split AS (

    SELECT
        id,

        TRIM(
            SUBSTRING_INDEX(
                TRIM(BOTH ',' FROM types),
                ',',
                1
            )
        ) AS data_type,

        CASE
            WHEN INSTR(
                TRIM(BOTH ',' FROM types),
                ','
            ) > 0

            THEN SUBSTRING(
                TRIM(BOTH ',' FROM types),
                INSTR(
                    TRIM(BOTH ',' FROM types),
                    ','
                ) + 1
            )

            ELSE ''
        END AS remaining

    FROM earthquakes

    WHERE types IS NOT NULL
      AND TRIM(BOTH ',' FROM types) <> ''

    UNION ALL

    SELECT
        id,

        TRIM(
            SUBSTRING_INDEX(
                remaining,
                ',',
                1
            )
        ),

        CASE
            WHEN INSTR(remaining, ',') > 0
            THEN SUBSTRING(
                remaining,
                INSTR(remaining, ',') + 1
            )
            ELSE ''
        END

    FROM type_split

    WHERE remaining <> ''
)

SELECT
    data_type,
    COUNT(DISTINCT id) AS earthquake_count
FROM type_split
WHERE data_type <> ''
GROUP BY data_type
ORDER BY earthquake_count DESC;
