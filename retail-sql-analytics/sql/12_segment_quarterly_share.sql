-- Q12: Customer-segment share of sales by quarter
WITH q AS (
  SELECT strftime('%Y', f.order_date) || '-Q' || ((CAST(strftime('%m', f.order_date) AS INT) + 2) / 3) AS quarter,
         c.segment, SUM(f.sales) AS sales
  FROM fact_sales f JOIN dim_customer c USING (customer_id)
  GROUP BY quarter, c.segment
)
SELECT quarter, segment, ROUND(sales, 0) AS sales,
       ROUND(100.0 * sales / SUM(sales) OVER (PARTITION BY quarter), 1) AS share_of_quarter_pct
FROM q ORDER BY quarter, segment;
