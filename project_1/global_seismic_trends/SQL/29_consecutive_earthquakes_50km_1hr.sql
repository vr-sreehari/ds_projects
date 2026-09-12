-- ====================================================================
-- Query 29: Consecutive Earthquakes Within 50 km and One Hour
-- Description: Uses LAG() window function over chronological time, then applies 
--              the Haversine formula to compute great-circle distance (km) between 
--              consecutive events occurring within 1 hour (3600 seconds).
-- ====================================================================

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
