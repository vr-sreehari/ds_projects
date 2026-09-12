-- ====================================================================
-- Query 13: Average Economic Loss by Alert Level
-- Description: Measures average monetary loss across PAGER alert color levels.
-- IMPORTANT NOTE: Requires retaining 'alert' (green, yellow, orange, red) 
--                 from USGS API and joining an external 'economic_loss_usd' field.
-- ====================================================================

SELECT
    alert,
    ROUND(AVG(economic_loss_usd), 2) AS avg_economic_loss
FROM earthquakes
WHERE alert IS NOT NULL
  AND economic_loss_usd IS NOT NULL
GROUP BY alert
ORDER BY avg_economic_loss DESC;
