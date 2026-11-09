-- Q3: Which categories/sub-categories make or lose money? (RANK within category)
SELECT p.category, p.sub_category,
       ROUND(SUM(f.sales), 0) AS sales, ROUND(SUM(f.profit), 0) AS profit,
       ROUND(100.0 * SUM(f.profit) / SUM(f.sales), 1) AS margin_pct,
       RANK() OVER (PARTITION BY p.category ORDER BY SUM(f.profit) DESC) AS rank_in_category
FROM fact_sales f JOIN dim_product p USING (product_id)
GROUP BY p.category, p.sub_category
ORDER BY p.category, rank_in_category;
