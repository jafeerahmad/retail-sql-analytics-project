-- Q6: Regional performance with share of total (window over aggregate)
SELECT c.region,
       ROUND(SUM(f.sales), 0) AS sales, ROUND(SUM(f.profit), 0) AS profit,
       ROUND(100.0 * SUM(f.profit) / SUM(f.sales), 1) AS margin_pct,
       ROUND(100.0 * SUM(f.sales) / SUM(SUM(f.sales)) OVER (), 1) AS sales_share_pct
FROM fact_sales f JOIN dim_customer c USING (customer_id)
GROUP BY c.region ORDER BY sales DESC;
