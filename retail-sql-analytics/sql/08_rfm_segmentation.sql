-- Q8: RFM scoring with NTILE and rule-based segments
WITH base AS (
  SELECT customer_id, MAX(order_date) AS last_order,
         COUNT(DISTINCT order_id) AS frequency, SUM(sales) AS monetary
  FROM fact_sales GROUP BY customer_id
), ref AS (SELECT MAX(order_date) AS max_date FROM fact_sales),
scored AS (
  SELECT b.customer_id,
         CAST(julianday(r.max_date) - julianday(b.last_order) AS INT) AS recency_days,
         b.frequency, ROUND(b.monetary, 0) AS monetary,
         NTILE(4) OVER (ORDER BY julianday(r.max_date) - julianday(b.last_order) DESC) AS r_score,
         NTILE(4) OVER (ORDER BY b.frequency) AS f_score,
         NTILE(4) OVER (ORDER BY b.monetary) AS m_score
  FROM base b, ref r
)
SELECT *,
       CASE WHEN r_score >= 3 AND f_score >= 3 AND m_score >= 3 THEN 'Champions'
            WHEN r_score >= 3 AND f_score >= 2 THEN 'Loyal'
            WHEN r_score <= 2 AND f_score >= 3 THEN 'At Risk'
            WHEN r_score = 1 AND f_score <= 2 THEN 'Lost'
            ELSE 'Potential' END AS segment
FROM scored ORDER BY monetary DESC;
