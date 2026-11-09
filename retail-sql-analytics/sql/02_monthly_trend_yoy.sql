-- Q2: Monthly sales with month-over-month and year-over-year growth (LAG window function)
WITH monthly AS (
  SELECT strftime('%Y-%m', order_date) AS month,
         ROUND(SUM(sales), 0) AS sales, ROUND(SUM(profit), 0) AS profit
  FROM fact_sales GROUP BY 1
)
SELECT month, sales, profit,
       ROUND(100.0 * (sales - LAG(sales, 1) OVER (ORDER BY month)) / LAG(sales, 1) OVER (ORDER BY month), 1) AS mom_growth_pct,
       ROUND(100.0 * (sales - LAG(sales, 12) OVER (ORDER BY month)) / LAG(sales, 12) OVER (ORDER BY month), 1) AS yoy_growth_pct
FROM monthly ORDER BY month;
