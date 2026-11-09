-- Q5: Top 10 products with the biggest total losses
SELECT p.product_name, p.sub_category,
       ROUND(SUM(f.sales), 0) AS sales, ROUND(SUM(f.profit), 0) AS profit,
       ROUND(AVG(f.discount) * 100, 1) AS avg_discount_pct
FROM fact_sales f JOIN dim_product p USING (product_id)
GROUP BY p.product_id, p.product_name, p.sub_category
HAVING SUM(f.profit) < 0
ORDER BY profit ASC LIMIT 10;
