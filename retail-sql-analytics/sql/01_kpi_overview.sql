-- Q1: Headline business KPIs
SELECT ROUND(SUM(sales), 0) AS total_sales,
       ROUND(SUM(profit), 0) AS total_profit,
       ROUND(100.0 * SUM(profit) / SUM(sales), 2) AS profit_margin_pct,
       COUNT(DISTINCT order_id) AS orders,
       COUNT(DISTINCT customer_id) AS customers,
       ROUND(SUM(sales) / COUNT(DISTINCT order_id), 0) AS avg_order_value
FROM fact_sales;
