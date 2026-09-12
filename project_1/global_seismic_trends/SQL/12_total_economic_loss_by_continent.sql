-- ====================================================================
-- Query 12: Total Economic Loss by Continent
-- Description: Aggregates estimated monetary disaster damages by continent.
-- IMPORTANT NOTE: The USGS dataset does NOT contain economic loss data.
-- PREREQUISITE: Requires an external disaster loss field (e.g. 'economic_loss_usd')
--               and the derived 'continent' mapping column.
-- ====================================================================

SELECT
    continent,
    SUM(economic_loss_usd) AS total_economic_loss
FROM earthquakes
WHERE continent IS NOT NULL
  AND economic_loss_usd IS NOT NULL
GROUP BY continent
ORDER BY total_economic_loss DESC;
