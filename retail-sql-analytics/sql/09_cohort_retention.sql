-- Q9: Monthly cohort retention (customers still buying N months after first purchase)
WITH first_m AS (
  SELECT customer_id, strftime('%Y-%m', MIN(order_date)) AS cohort FROM fact_sales GROUP BY customer_id
), act AS (
  SELECT DISTINCT customer_id, strftime('%Y-%m', order_date) AS m FROM fact_sales
), joined AS (
  SELECT f.cohort, a.customer_id,
         (CAST(substr(a.m, 1, 4) AS INT) - CAST(substr(f.cohort, 1, 4) AS INT)) * 12
         + CAST(substr(a.m, 6, 2) AS INT) - CAST(substr(f.cohort, 6, 2) AS INT) AS months_since
  FROM first_m f JOIN act a USING (customer_id)
)
SELECT cohort, months_since, COUNT(DISTINCT customer_id) AS active_customers,
       ROUND(100.0 * COUNT(DISTINCT customer_id) /
             FIRST_VALUE(COUNT(DISTINCT customer_id)) OVER (PARTITION BY cohort ORDER BY months_since), 1) AS retention_pct
FROM joined GROUP BY cohort, months_since ORDER BY cohort, months_since;
