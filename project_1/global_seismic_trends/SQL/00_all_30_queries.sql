-- ====================================================================
-- GLOBAL SEISMIC TRENDS - 30 SQL ANALYTICAL QUERIES
-- Target RDBMS: MySQL 8.0+
-- Database: global_seismic_trends
-- Table: earthquakes
-- ====================================================================


-- --------------------------------------------------------------------
-- 01. Top 10 strongest earthquakes
-- --------------------------------------------------------------------
SELECT
    id,
    time,
    place,
    country,
    mag,
    depth_km
FROM earthquakes
WHERE mag IS NOT NULL
ORDER BY mag DESC
LIMIT 10;


-- --------------------------------------------------------------------
-- 02. Top 10 deepest earthquakes
-- --------------------------------------------------------------------
SELECT
    id,
    time,
    place,
    country,
    mag,
    depth_km
FROM earthquakes
WHERE depth_km IS NOT NULL
ORDER BY depth_km DESC
LIMIT 10;


-- --------------------------------------------------------------------
-- 03. Shallow earthquakes below 50 km with magnitude > 7.5
-- --------------------------------------------------------------------
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


-- --------------------------------------------------------------------
-- 04. Average depth per continent
-- NOTE: Requires 'continent' column
-- --------------------------------------------------------------------
SELECT
    continent,
    ROUND(AVG(depth_km), 2) AS avg_depth_km,
    COUNT(*) AS earthquake_count
FROM earthquakes
WHERE continent IS NOT NULL
GROUP BY continent
ORDER BY avg_depth_km DESC;


-- --------------------------------------------------------------------
-- 05. Average magnitude by magType
-- --------------------------------------------------------------------
SELECT
    magType,
    ROUND(AVG(mag), 2) AS avg_magnitude,
    COUNT(*) AS earthquake_count
FROM earthquakes
WHERE magType IS NOT NULL
GROUP BY magType
ORDER BY avg_magnitude DESC;


-- --------------------------------------------------------------------
-- 06. Year with most earthquakes
-- --------------------------------------------------------------------
SELECT
    YEAR(time) AS earthquake_year,
    COUNT(*) AS earthquake_count
FROM earthquakes
WHERE time IS NOT NULL
GROUP BY YEAR(time)
ORDER BY earthquake_count DESC
LIMIT 1;


-- --------------------------------------------------------------------
-- 07. Month with highest earthquake count
-- --------------------------------------------------------------------
SELECT
    MONTH(time) AS month_number,
    MONTHNAME(time) AS month_name,
    COUNT(*) AS earthquake_count
FROM earthquakes
WHERE time IS NOT NULL
GROUP BY MONTH(time), MONTHNAME(time)
ORDER BY earthquake_count DESC
LIMIT 1;


-- --------------------------------------------------------------------
-- 08. Day of week with most earthquakes
-- --------------------------------------------------------------------
SELECT
    DAYNAME(time) AS day_of_week,
    COUNT(*) AS earthquake_count
FROM earthquakes
WHERE time IS NOT NULL
GROUP BY DAYNAME(time)
ORDER BY earthquake_count DESC;


-- --------------------------------------------------------------------
-- 09. Earthquakes per hour
-- --------------------------------------------------------------------
SELECT
    HOUR(time) AS hour_of_day,
    COUNT(*) AS earthquake_count
FROM earthquakes
WHERE time IS NOT NULL
GROUP BY HOUR(time)
ORDER BY hour_of_day;


-- --------------------------------------------------------------------
-- 10. Most active reporting network
-- --------------------------------------------------------------------
SELECT
    net,
    COUNT(*) AS earthquake_count
FROM earthquakes
WHERE net IS NOT NULL
GROUP BY net
ORDER BY earthquake_count DESC
LIMIT 1;


-- --------------------------------------------------------------------
-- 11. Top 5 places with highest casualties
-- NOTE: Requires external 'casualties' column
-- --------------------------------------------------------------------
SELECT
    place,
    SUM(casualties) AS total_casualties
FROM earthquakes
WHERE casualties IS NOT NULL
GROUP BY place
ORDER BY total_casualties DESC
LIMIT 5;


-- --------------------------------------------------------------------
-- 12. Total economic loss by continent
-- NOTE: Requires external 'economic_loss_usd' and 'continent' columns
-- --------------------------------------------------------------------
SELECT
    continent,
    SUM(economic_loss_usd) AS total_economic_loss
FROM earthquakes
WHERE continent IS NOT NULL
  AND economic_loss_usd IS NOT NULL
GROUP BY continent
ORDER BY total_economic_loss DESC;


-- --------------------------------------------------------------------
-- 13. Average economic loss by alert level
-- NOTE: Requires external 'economic_loss_usd' and 'alert' columns
-- --------------------------------------------------------------------
SELECT
    alert,
    ROUND(AVG(economic_loss_usd), 2) AS avg_economic_loss
FROM earthquakes
WHERE alert IS NOT NULL
  AND economic_loss_usd IS NOT NULL
GROUP BY alert
ORDER BY avg_economic_loss DESC;


-- --------------------------------------------------------------------
-- 14. Reviewed vs automatic events
-- --------------------------------------------------------------------
SELECT
    status,
    COUNT(*) AS earthquake_count
FROM earthquakes
WHERE status IS NOT NULL
GROUP BY status
ORDER BY earthquake_count DESC;


-- --------------------------------------------------------------------
-- 15. Earthquake count by event type
-- --------------------------------------------------------------------
SELECT
    `type`,
    COUNT(*) AS earthquake_count
FROM earthquakes
WHERE `type` IS NOT NULL
GROUP BY `type`
ORDER BY earthquake_count DESC;


-- --------------------------------------------------------------------
-- 16. Number of earthquakes by associated data type
-- --------------------------------------------------------------------
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


-- --------------------------------------------------------------------
-- 17. Average RMS and gap per continent
-- NOTE: Requires 'continent' column
-- --------------------------------------------------------------------
SELECT
    continent,
    ROUND(AVG(rms), 3) AS avg_rms,
    ROUND(AVG(gap), 2) AS avg_gap,
    COUNT(*) AS earthquake_count
FROM earthquakes
WHERE continent IS NOT NULL
GROUP BY continent
ORDER BY avg_rms DESC;


-- --------------------------------------------------------------------
-- 18. Events with high station coverage
-- --------------------------------------------------------------------
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


-- --------------------------------------------------------------------
-- 19. Tsunami-triggering earthquakes by year
-- --------------------------------------------------------------------
SELECT
    YEAR(time) AS earthquake_year,
    COUNT(*) AS tsunami_earthquakes
FROM earthquakes
WHERE tsunami = 1
  AND time IS NOT NULL
GROUP BY YEAR(time)
ORDER BY earthquake_year;


-- --------------------------------------------------------------------
-- 20. Earthquake count by alert level
-- NOTE: Requires 'alert' column retained from API
-- --------------------------------------------------------------------
SELECT
    LOWER(alert) AS alert_level,
    COUNT(*) AS earthquake_count
FROM earthquakes
WHERE alert IS NOT NULL
GROUP BY LOWER(alert)
ORDER BY earthquake_count DESC;


-- --------------------------------------------------------------------
-- 21. Top 5 countries with highest average magnitude in past 5 years
-- --------------------------------------------------------------------
SELECT
    country,
    ROUND(AVG(mag), 2) AS avg_magnitude,
    COUNT(*) AS earthquake_count
FROM earthquakes
WHERE time >= DATE_SUB(UTC_TIMESTAMP(), INTERVAL 5 YEAR)
  AND country IS NOT NULL
  AND country <> 'Unknown'
GROUP BY country
HAVING COUNT(*) >= 10
ORDER BY avg_magnitude DESC
LIMIT 5;


-- --------------------------------------------------------------------
-- 22. Countries with both shallow and deep earthquakes in same month
-- --------------------------------------------------------------------
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


-- --------------------------------------------------------------------
-- 23. Year-over-year growth rate
-- --------------------------------------------------------------------
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


-- --------------------------------------------------------------------
-- 24. Top 3 most seismically active regions (frequency + magnitude)
-- --------------------------------------------------------------------
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


-- --------------------------------------------------------------------
-- 25. Average depth within ±5° latitude of equator
-- --------------------------------------------------------------------
SELECT
    country,
    ROUND(AVG(depth_km), 2) AS avg_depth_km,
    COUNT(*) AS earthquake_count
FROM earthquakes
WHERE latitude BETWEEN -5 AND 5
  AND country IS NOT NULL
  AND country <> 'Unknown'
GROUP BY country
ORDER BY avg_depth_km DESC;


-- --------------------------------------------------------------------
-- 26. Countries with highest shallow-to-deep ratio
-- --------------------------------------------------------------------
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


-- --------------------------------------------------------------------
-- 27. Magnitude difference between tsunami and non-tsunami earthquakes
-- --------------------------------------------------------------------
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


-- --------------------------------------------------------------------
-- 28. Events with lowest data reliability (gap + rms)
-- --------------------------------------------------------------------
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


-- --------------------------------------------------------------------
-- 29. Consecutive earthquakes within 50 km and one hour
-- --------------------------------------------------------------------
WITH ordered_events AS (

    SELECT
        id,
        time,
        place,
        latitude,
        longitude,
        mag,

        LAG(id) OVER (
            ORDER BY time
        ) AS previous_id,

        LAG(time) OVER (
            ORDER BY time
        ) AS previous_time,

        LAG(place) OVER (
            ORDER BY time
        ) AS previous_place,

        LAG(latitude) OVER (
            ORDER BY time
        ) AS previous_latitude,

        LAG(longitude) OVER (
            ORDER BY time
        ) AS previous_longitude,

        LAG(mag) OVER (
            ORDER BY time
        ) AS previous_mag

    FROM earthquakes
    WHERE time IS NOT NULL
      AND latitude IS NOT NULL
      AND longitude IS NOT NULL
),

distances AS (

    SELECT
        *,

        6371 * 2 * ASIN(
            SQRT(

                POWER(
                    SIN(
                        RADIANS(
                            latitude - previous_latitude
                        ) / 2
                    ),
                    2
                )

                +

                COS(RADIANS(previous_latitude))
                *
                COS(RADIANS(latitude))
                *
                POWER(
                    SIN(
                        RADIANS(
                            longitude - previous_longitude
                        ) / 2
                    ),
                    2
                )
            )
        ) AS distance_km

    FROM ordered_events

    WHERE previous_id IS NOT NULL
)

SELECT
    previous_id,
    id AS current_id,

    previous_time,
    time AS current_time,

    previous_place,
    place AS current_place,

    previous_mag,
    mag AS current_mag,

    ROUND(distance_km, 2) AS distance_km,

    TIMESTAMPDIFF(
        MINUTE,
        previous_time,
        time
    ) AS minutes_apart

FROM distances

WHERE distance_km <= 50

  AND TIMESTAMPDIFF(
        SECOND,
        previous_time,
        time
      ) BETWEEN 0 AND 3600

ORDER BY time;


-- --------------------------------------------------------------------
-- 30. Regions with most deep-focus earthquakes
-- --------------------------------------------------------------------
SELECT
    country,
    COUNT(*) AS deep_earthquake_count,
    ROUND(AVG(depth_km), 2) AS avg_depth_km,
    ROUND(AVG(mag), 2) AS avg_magnitude
FROM earthquakes
WHERE depth_km > 300
  AND country IS NOT NULL
  AND country <> 'Unknown'
GROUP BY country
ORDER BY deep_earthquake_count DESC;
