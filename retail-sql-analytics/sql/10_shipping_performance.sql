-- Q10: Order-to-ship elapsed time by ship mode (ship_date is not delivery_date)
SELECT ship_mode,
       ROUND(AVG(julianday(ship_date) - julianday(order_date)), 1) AS avg_ship_days,
       ROUND(100.0 * SUM(CASE WHEN julianday(ship_date) - julianday(order_date) > 5 THEN 1 ELSE 0 END) / COUNT(*), 1) AS pct_over_5_days,
       COUNT(*) AS line_items
FROM fact_sales GROUP BY ship_mode ORDER BY avg_ship_days;
