-- ============================================================
-- ONLINE FOOD DELIVERY ANALYSIS
-- Complete SQL Analysis File
-- Database: online_food_delivery
-- Table: food_delivery_orders
--
-- Assumptions used in the cleaned analytical dataset:
--   1. Revenue = Final_Amount for Delivered orders, otherwise 0.
--   2. Is_Cancelled = 1 for Cancelled orders, otherwise 0.
--   3. Estimated_Profit = Revenue * Profit_Margin.
--   4. Unknown categorical values are stored as 'Unknown'.
--   5. Cancelled orders have NULL Delivery_Rating.
-- ============================================================

USE online_food_delivery;

-- ============================================================
-- 0. DATA / TABLE VALIDATION
-- ============================================================

SELECT COUNT(*) AS total_rows
FROM food_delivery_orders;

SELECT COUNT(DISTINCT Order_ID) AS total_unique_orders
FROM food_delivery_orders;

SELECT COUNT(DISTINCT Customer_ID) AS total_customers
FROM food_delivery_orders;

SELECT COUNT(DISTINCT Restaurant_ID) AS total_restaurants
FROM food_delivery_orders;

SELECT
    Order_Status,
    COUNT(*) AS total_orders,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM food_delivery_orders), 2) AS percentage
FROM food_delivery_orders
GROUP BY Order_Status
ORDER BY total_orders DESC;


-- ============================================================
-- 1. DASHBOARD KPI SUMMARY
-- ============================================================

SELECT
    COUNT(DISTINCT Order_ID) AS total_orders,
    ROUND(SUM(Revenue), 2) AS total_revenue,
    ROUND(
        AVG(CASE WHEN Order_Status = 'Delivered' THEN Revenue ELSE NULL END),
        2
    ) AS average_order_value,
    ROUND(
        AVG(CASE WHEN Order_Status = 'Delivered' THEN Delivery_Time_Min ELSE NULL END),
        2
    ) AS average_delivery_time_min,
    ROUND(
        SUM(CASE WHEN Order_Status = 'Cancelled' THEN 1 ELSE 0 END)
        * 100.0 / COUNT(*),
        2
    ) AS cancellation_rate_percent,
    ROUND(
        AVG(CASE WHEN Order_Status = 'Delivered' THEN Delivery_Rating ELSE NULL END),
        2
    ) AS average_delivery_rating,
    ROUND(
        SUM(Estimated_Profit) * 100.0 / NULLIF(SUM(Revenue), 0),
        2
    ) AS overall_profit_margin_percent
FROM food_delivery_orders;


-- ============================================================
-- 2. CUSTOMER & ORDER ANALYSIS
-- ============================================================

-- 2.1 Top-spending customers
SELECT
    Customer_ID,
    COUNT(*) AS total_orders,
    SUM(CASE WHEN Order_Status = 'Delivered' THEN 1 ELSE 0 END) AS delivered_orders,
    SUM(CASE WHEN Order_Status = 'Cancelled' THEN 1 ELSE 0 END) AS cancelled_orders,
    ROUND(SUM(Revenue), 2) AS total_spending,
    ROUND(AVG(Order_Value), 2) AS average_order_value
FROM food_delivery_orders
GROUP BY Customer_ID
ORDER BY total_spending DESC
LIMIT 10;


-- 2.2 Age group vs order value
SELECT
    Age_Group,
    COUNT(*) AS total_orders,
    ROUND(AVG(Order_Value), 2) AS average_order_value,
    ROUND(AVG(Final_Amount), 2) AS average_final_amount,
    ROUND(SUM(Revenue), 2) AS total_revenue
FROM food_delivery_orders
WHERE Age_Group IS NOT NULL
  AND Age_Group <> 'Unknown'
GROUP BY Age_Group
ORDER BY average_order_value DESC;


-- 2.3 Weekend vs weekday order patterns
SELECT
    Order_Day,
    COUNT(*) AS total_orders,
    ROUND(
        COUNT(*) * 100.0 / (SELECT COUNT(*) FROM food_delivery_orders),
        2
    ) AS order_percentage,
    ROUND(AVG(Order_Value), 2) AS average_order_value,
    ROUND(SUM(Revenue), 2) AS total_revenue,
    ROUND(AVG(Delivery_Time_Min), 2) AS average_delivery_time_min,
    ROUND(AVG(Is_Cancelled) * 100, 2) AS cancellation_rate_percent
FROM food_delivery_orders
GROUP BY Order_Day
ORDER BY total_orders DESC;


-- Better comparison: average orders per calendar day
WITH daily_orders AS (
    SELECT
        Order_Date,
        Order_Day,
        COUNT(*) AS orders_per_day
    FROM food_delivery_orders
    WHERE Order_Date IS NOT NULL
    GROUP BY Order_Date, Order_Day
)
SELECT
    Order_Day,
    ROUND(AVG(orders_per_day), 2) AS average_orders_per_day
FROM daily_orders
GROUP BY Order_Day
ORDER BY average_orders_per_day DESC;


-- ============================================================
-- 3. REVENUE & PROFIT ANALYSIS
-- ============================================================

-- 3.1 Monthly revenue trends
SELECT
    Order_Month_Number,
    Order_Month,
    COUNT(*) AS total_orders,
    SUM(CASE WHEN Order_Status = 'Delivered' THEN 1 ELSE 0 END) AS delivered_orders,
    ROUND(SUM(Revenue), 2) AS total_revenue,
    ROUND(SUM(Estimated_Profit), 2) AS estimated_profit,
    ROUND(AVG(Order_Value), 2) AS average_order_value
FROM food_delivery_orders
WHERE Order_Date IS NOT NULL
GROUP BY Order_Month_Number, Order_Month
ORDER BY Order_Month_Number;


-- 3.2 Impact of discounts on profit
SELECT
    Discount_Applied,
    COUNT(*) AS total_orders,
    ROUND(AVG(Revenue), 2) AS average_revenue,
    ROUND(AVG(Estimated_Profit), 2) AS average_estimated_profit,
    ROUND(SUM(Estimated_Profit), 2) AS total_estimated_profit
FROM food_delivery_orders
GROUP BY Discount_Applied
ORDER BY Discount_Applied;


-- Discount bands for easier interpretation
SELECT
    CASE
        WHEN Discount_Applied = 0 THEN 'No Discount'
        WHEN Discount_Applied <= 50 THEN 'Low Discount'
        WHEN Discount_Applied <= 100 THEN 'Medium Discount'
        ELSE 'High Discount'
    END AS discount_band,
    COUNT(*) AS total_orders,
    ROUND(AVG(Discount_Applied), 2) AS average_discount,
    ROUND(AVG(Revenue), 2) AS average_revenue,
    ROUND(AVG(Estimated_Profit), 2) AS average_estimated_profit,
    ROUND(SUM(Estimated_Profit), 2) AS total_estimated_profit
FROM food_delivery_orders
GROUP BY
    CASE
        WHEN Discount_Applied = 0 THEN 'No Discount'
        WHEN Discount_Applied <= 50 THEN 'Low Discount'
        WHEN Discount_Applied <= 100 THEN 'Medium Discount'
        ELSE 'High Discount'
    END
ORDER BY average_discount;


-- 3.3 High-revenue cities
SELECT
    City,
    COUNT(*) AS total_orders,
    ROUND(SUM(Revenue), 2) AS total_revenue,
    ROUND(AVG(Order_Value), 2) AS average_order_value,
    ROUND(SUM(Estimated_Profit), 2) AS estimated_profit
FROM food_delivery_orders
WHERE City IS NOT NULL
  AND City <> 'Unknown'
GROUP BY City
ORDER BY total_revenue DESC;


-- 3.4 High-revenue cuisines
SELECT
    Cuisine_Type,
    COUNT(*) AS total_orders,
    ROUND(SUM(Revenue), 2) AS total_revenue,
    ROUND(AVG(Order_Value), 2) AS average_order_value,
    ROUND(SUM(Estimated_Profit), 2) AS estimated_profit
FROM food_delivery_orders
WHERE Cuisine_Type IS NOT NULL
  AND Cuisine_Type <> 'Unknown'
GROUP BY Cuisine_Type
ORDER BY total_revenue DESC;


-- ============================================================
-- 4. DELIVERY PERFORMANCE
-- ============================================================

-- 4.1 Average delivery time by city
SELECT
    City,
    COUNT(*) AS total_orders,
    ROUND(AVG(Delivery_Time_Min), 2) AS average_delivery_time_min,
    ROUND(MIN(Delivery_Time_Min), 2) AS minimum_delivery_time_min,
    ROUND(MAX(Delivery_Time_Min), 2) AS maximum_delivery_time_min
FROM food_delivery_orders
WHERE City IS NOT NULL
  AND City <> 'Unknown'
GROUP BY City
ORDER BY average_delivery_time_min DESC;


-- 4.2 Distance vs delivery delay: distance buckets
SELECT
    CASE
        WHEN Distance_km <= 5 THEN '0-5 km'
        WHEN Distance_km <= 10 THEN '5-10 km'
        WHEN Distance_km <= 20 THEN '10-20 km'
        WHEN Distance_km <= 30 THEN '20-30 km'
        ELSE '30+ km'
    END AS distance_band,
    COUNT(*) AS total_orders,
    ROUND(AVG(Distance_km), 2) AS average_distance_km,
    ROUND(AVG(Delivery_Time_Min), 2) AS average_delivery_time_min
FROM food_delivery_orders
WHERE Distance_km IS NOT NULL
  AND Delivery_Time_Min IS NOT NULL
GROUP BY
    CASE
        WHEN Distance_km <= 5 THEN '0-5 km'
        WHEN Distance_km <= 10 THEN '5-10 km'
        WHEN Distance_km <= 20 THEN '10-20 km'
        WHEN Distance_km <= 30 THEN '20-30 km'
        ELSE '30+ km'
    END
ORDER BY average_distance_km;


-- Pearson correlation: Distance vs Delivery Time
SELECT
    ROUND(
        (
            COUNT(*) * SUM(Distance_km * Delivery_Time_Min)
            - SUM(Distance_km) * SUM(Delivery_Time_Min)
        )
        /
        NULLIF(
            SQRT(
                (
                    COUNT(*) * SUM(POW(Distance_km, 2))
                    - POW(SUM(Distance_km), 2)
                )
                *
                (
                    COUNT(*) * SUM(POW(Delivery_Time_Min, 2))
                    - POW(SUM(Delivery_Time_Min), 2)
                )
            ),
            0
        ),
        4
    ) AS distance_delivery_time_correlation
FROM food_delivery_orders
WHERE Distance_km IS NOT NULL
  AND Delivery_Time_Min IS NOT NULL;


-- 4.3 Delivery rating vs delivery time
SELECT
    Delivery_Rating,
    COUNT(*) AS delivered_orders,
    ROUND(AVG(Delivery_Time_Min), 2) AS average_delivery_time_min
FROM food_delivery_orders
WHERE Order_Status = 'Delivered'
  AND Delivery_Rating IS NOT NULL
GROUP BY Delivery_Rating
ORDER BY Delivery_Rating;


-- Pearson correlation: Delivery Rating vs Delivery Time
SELECT
    ROUND(
        (
            COUNT(*) * SUM(Delivery_Rating * Delivery_Time_Min)
            - SUM(Delivery_Rating) * SUM(Delivery_Time_Min)
        )
        /
        NULLIF(
            SQRT(
                (
                    COUNT(*) * SUM(POW(Delivery_Rating, 2))
                    - POW(SUM(Delivery_Rating), 2)
                )
                *
                (
                    COUNT(*) * SUM(POW(Delivery_Time_Min, 2))
                    - POW(SUM(Delivery_Time_Min), 2)
                )
            ),
            0
        ),
        4
    ) AS rating_delivery_time_correlation
FROM food_delivery_orders
WHERE Order_Status = 'Delivered'
  AND Delivery_Rating IS NOT NULL
  AND Delivery_Time_Min IS NOT NULL;


-- ============================================================
-- 5. RESTAURANT PERFORMANCE
-- ============================================================

-- 5.1 Top-rated restaurants
-- Minimum 50 orders to reduce small-sample distortion.
SELECT
    Restaurant_ID,
    Restaurant_Name,
    COUNT(*) AS total_orders,
    ROUND(AVG(Restaurant_Rating), 2) AS average_restaurant_rating,
    ROUND(SUM(Revenue), 2) AS total_revenue
FROM food_delivery_orders
GROUP BY Restaurant_ID, Restaurant_Name
HAVING COUNT(*) >= 50
ORDER BY average_restaurant_rating DESC, total_orders DESC
LIMIT 10;


-- 5.2 Cancellation rate by restaurant
SELECT
    Restaurant_ID,
    Restaurant_Name,
    COUNT(*) AS total_orders,
    SUM(CASE WHEN Order_Status = 'Cancelled' THEN 1 ELSE 0 END) AS cancelled_orders,
    ROUND(
        SUM(CASE WHEN Order_Status = 'Cancelled' THEN 1 ELSE 0 END)
        * 100.0 / COUNT(*),
        2
    ) AS cancellation_rate_percent
FROM food_delivery_orders
GROUP BY Restaurant_ID, Restaurant_Name
HAVING COUNT(*) >= 50
ORDER BY cancellation_rate_percent DESC, total_orders DESC
LIMIT 10;


-- 5.3 Cuisine-wise performance
SELECT
    Cuisine_Type,
    COUNT(*) AS total_orders,
    ROUND(SUM(Revenue), 2) AS total_revenue,
    ROUND(AVG(Order_Value), 2) AS average_order_value,
    ROUND(AVG(Delivery_Time_Min), 2) AS average_delivery_time_min,
    ROUND(AVG(Restaurant_Rating), 2) AS average_restaurant_rating,
    ROUND(AVG(Is_Cancelled) * 100, 2) AS cancellation_rate_percent,
    ROUND(SUM(Estimated_Profit), 2) AS estimated_profit
FROM food_delivery_orders
WHERE Cuisine_Type IS NOT NULL
  AND Cuisine_Type <> 'Unknown'
GROUP BY Cuisine_Type
ORDER BY total_revenue DESC;


-- ============================================================
-- 6. OPERATIONAL INSIGHTS
-- ============================================================

-- 6.1 Peak-hour demand analysis
SELECT
    Peak_Hour,
    COUNT(*) AS total_orders,
    ROUND(AVG(Order_Value), 2) AS average_order_value,
    ROUND(AVG(Delivery_Time_Min), 2) AS average_delivery_time_min,
    ROUND(AVG(Is_Cancelled) * 100, 2) AS cancellation_rate_percent,
    ROUND(SUM(Revenue), 2) AS total_revenue
FROM food_delivery_orders
WHERE Peak_Hour IS NOT NULL
  AND Peak_Hour <> 'Unknown'
GROUP BY Peak_Hour
ORDER BY total_orders DESC;


-- 6.2 Payment mode preferences
SELECT
    Payment_Mode,
    COUNT(*) AS total_orders,
    ROUND(
        COUNT(*) * 100.0 / NULLIF(SUM(COUNT(*)) OVER (), 0),
        2
    ) AS order_percentage,
    ROUND(SUM(Revenue), 2) AS total_revenue,
    ROUND(AVG(Order_Value), 2) AS average_order_value
FROM food_delivery_orders
WHERE Payment_Mode IS NOT NULL
  AND Payment_Mode <> 'Unknown'
GROUP BY Payment_Mode
ORDER BY total_orders DESC;


-- 6.3 Cancellation reason analysis
SELECT
    Cancellation_Reason,
    COUNT(*) AS cancelled_orders,
    ROUND(
        COUNT(*) * 100.0 / NULLIF(SUM(COUNT(*)) OVER (), 0),
        2
    ) AS cancellation_percentage
FROM food_delivery_orders
WHERE Order_Status = 'Cancelled'
  AND Cancellation_Reason IS NOT NULL
GROUP BY Cancellation_Reason
ORDER BY cancelled_orders DESC;


-- ============================================================
-- 7. ADDITIONAL CORRELATION ANALYSIS
-- ============================================================

-- 7.1 Discount vs Estimated Profit
SELECT
    ROUND(
        (
            COUNT(*) * SUM(Discount_Applied * Estimated_Profit)
            - SUM(Discount_Applied) * SUM(Estimated_Profit)
        )
        /
        NULLIF(
            SQRT(
                (
                    COUNT(*) * SUM(POW(Discount_Applied, 2))
                    - POW(SUM(Discount_Applied), 2)
                )
                *
                (
                    COUNT(*) * SUM(POW(Estimated_Profit, 2))
                    - POW(SUM(Estimated_Profit), 2)
                )
            ),
            0
        ),
        4
    ) AS discount_profit_correlation
FROM food_delivery_orders
WHERE Discount_Applied IS NOT NULL
  AND Estimated_Profit IS NOT NULL;


-- 7.2 Order Value vs Estimated Profit
SELECT
    ROUND(
        (
            COUNT(*) * SUM(Order_Value * Estimated_Profit)
            - SUM(Order_Value) * SUM(Estimated_Profit)
        )
        /
        NULLIF(
            SQRT(
                (
                    COUNT(*) * SUM(POW(Order_Value, 2))
                    - POW(SUM(Order_Value), 2)
                )
                *
                (
                    COUNT(*) * SUM(POW(Estimated_Profit, 2))
                    - POW(SUM(Estimated_Profit), 2)
                )
            ),
            0
        ),
        4
    ) AS order_value_profit_correlation
FROM food_delivery_orders
WHERE Order_Value IS NOT NULL
  AND Estimated_Profit IS NOT NULL;


-- ============================================================
-- 8. EXTRA BUSINESS SUMMARY QUERIES
-- ============================================================

-- 8.1 City-wise complete performance
SELECT
    City,
    COUNT(*) AS total_orders,
    ROUND(SUM(Revenue), 2) AS total_revenue,
    ROUND(AVG(Order_Value), 2) AS average_order_value,
    ROUND(AVG(Delivery_Time_Min), 2) AS average_delivery_time_min,
    ROUND(AVG(Is_Cancelled) * 100, 2) AS cancellation_rate_percent,
    ROUND(AVG(Restaurant_Rating), 2) AS average_restaurant_rating
FROM food_delivery_orders
WHERE City IS NOT NULL
  AND City <> 'Unknown'
GROUP BY City
ORDER BY total_revenue DESC;


-- 8.2 Delivery performance category summary
SELECT
    Delivery_Performance,
    COUNT(*) AS total_orders,
    ROUND(
        COUNT(*) * 100.0 / (SELECT COUNT(*) FROM food_delivery_orders),
        2
    ) AS order_percentage,
    ROUND(AVG(Delivery_Time_Min), 2) AS average_delivery_time_min,
    ROUND(AVG(Is_Cancelled) * 100, 2) AS cancellation_rate_percent
FROM food_delivery_orders
WHERE Delivery_Performance IS NOT NULL
GROUP BY Delivery_Performance
ORDER BY average_delivery_time_min;


-- 8.3 Delivered vs cancelled revenue comparison
SELECT
    Order_Status,
    COUNT(*) AS total_orders,
    ROUND(SUM(Final_Amount), 2) AS final_amount_total,
    ROUND(SUM(Revenue), 2) AS recognized_revenue
FROM food_delivery_orders
GROUP BY Order_Status;


-- ============================================================
-- END OF ANALYSIS FILE
-- ============================================================
