-- ====================================================================
-- Query 23: Year-Over-Year Growth Rate
-- Description: Computes annual percentage change in global earthquake frequency 
--              using the LAG() analytic window function in MySQL 8.0.
-- ====================================================================

WITH yearly_counts AS (

    SELECT
        YEAR(time) AS earthquake_year,
        COUNT(*) AS earthquake_count
    FROM earthquakes
    WHERE time IS NOT NULL
    GROUP BY YEAR(time)

),

growth AS (

    SELECT
        earthquake_year,
        earthquake_count,

        LAG(earthquake_count)
        OVER (
            ORDER BY earthquake_year
        ) AS previous_year_count

    FROM yearly_counts
)

SELECT
    earthquake_year,
    earthquake_count,
    previous_year_count,

    ROUND(
        (
            earthquake_count - previous_year_count
        ) / NULLIF(previous_year_count, 0)
        * 100,
        2
    ) AS yoy_growth_percentage

FROM growth

ORDER BY earthquake_year;
