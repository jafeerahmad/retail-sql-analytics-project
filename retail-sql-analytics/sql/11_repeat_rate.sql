-- Q11: Repeat purchase rate
WITH o AS (SELECT customer_id, COUNT(DISTINCT order_id) AS orders FROM fact_sales GROUP BY customer_id)
SELECT COUNT(*) AS customers,
       SUM(CASE WHEN orders > 1 THEN 1 ELSE 0 END) AS repeat_customers,
       ROUND(100.0 * SUM(CASE WHEN orders > 1 THEN 1 ELSE 0 END) / COUNT(*), 1) AS repeat_rate_pct,
       ROUND(AVG(orders), 1) AS avg_orders
FROM o;
