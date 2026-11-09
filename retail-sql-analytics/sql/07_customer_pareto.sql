-- Q7: Pareto analysis - how concentrated is revenue? (running total window)
WITH cust AS (
  SELECT customer_id, SUM(sales) AS sales FROM fact_sales GROUP BY customer_id
), ranked AS (
  SELECT customer_id, sales,
         ROW_NUMBER() OVER (ORDER BY sales DESC) AS rn,
         COUNT(*) OVER () AS n,
         SUM(sales) OVER (ORDER BY sales DESC ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS running,
         SUM(sales) OVER () AS total
  FROM cust
)
SELECT customer_id, ROUND(sales, 0) AS sales, rn AS rank,
       ROUND(100.0 * rn / n, 1) AS pct_of_customers,
       ROUND(100.0 * running / total, 1) AS cum_sales_pct
FROM ranked ORDER BY rn;
