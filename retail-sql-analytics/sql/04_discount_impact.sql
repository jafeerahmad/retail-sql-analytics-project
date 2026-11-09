-- Q4: How do discounts affect profitability?
SELECT CASE WHEN discount = 0 THEN '0%'
            WHEN discount <= 0.10 THEN '1-10%'
            WHEN discount <= 0.20 THEN '11-20%'
            WHEN discount <= 0.30 THEN '21-30%'
            ELSE '31%+' END AS discount_band,
       COUNT(*) AS line_items,
       ROUND(SUM(sales), 0) AS sales, ROUND(SUM(profit), 0) AS profit,
       ROUND(100.0 * SUM(profit) / SUM(sales), 1) AS margin_pct,
       ROUND(100.0 * SUM(CASE WHEN profit < 0 THEN 1 ELSE 0 END) / COUNT(*), 1) AS pct_loss_making_lines
FROM fact_sales
GROUP BY discount_band
ORDER BY MIN(discount);
