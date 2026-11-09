# Power BI Dashboard Guide (build time: ~2-3 hours)

## 1. Load data
Power BI Desktop -> **Get Data -> Text/CSV** -> load these from `exports/`:
`fact_sales.csv`, `dim_customer.csv`, `dim_product.csv`, `dim_date.csv`
(Check each date column is type **Date**.)

## 2. Model (star schema, Model view)
| From (many) | To (one) | Column |
|---|---|---|
| fact_sales | dim_customer | customer_id |
| fact_sales | dim_product | product_id |
| fact_sales | dim_date | order_date -> date |

Right-click `dim_date` -> **Mark as date table** (column `date`). All relationships: single direction, one-to-many.

## 3. DAX measures (create in a `_Measures` table)
```DAX
Total Sales = SUM(fact_sales[sales])
Total Profit = SUM(fact_sales[profit])
Profit Margin % = DIVIDE([Total Profit], [Total Sales])
Orders = DISTINCTCOUNT(fact_sales[order_id])
Customers = DISTINCTCOUNT(fact_sales[customer_id])
Avg Order Value = DIVIDE([Total Sales], [Orders])
Sales LY = CALCULATE([Total Sales], SAMEPERIODLASTYEAR(dim_date[date]))
YoY Growth % = DIVIDE([Total Sales] - [Sales LY], [Sales LY])
Loss-making Lines = CALCULATE(COUNTROWS(fact_sales), fact_sales[profit] < 0)
Loss-making Lines % = DIVIDE([Loss-making Lines], COUNTROWS(fact_sales))
Avg Order-to-Ship Days = AVERAGEX(fact_sales, DATEDIFF(fact_sales[order_date], fact_sales[ship_date], DAY))
```
Calculated column on `fact_sales` for the discount analysis:
```DAX
Discount Band =
SWITCH(TRUE(),
  fact_sales[discount] = 0, "0%",
  fact_sales[discount] <= 0.10, "1-10%",
  fact_sales[discount] <= 0.20, "11-20%",
  fact_sales[discount] <= 0.30, "21-30%",
  "31%+")
```

## 4. Report pages
**Page 1 - Executive Summary**
- KPI cards: Total Sales, Total Profit, Profit Margin %, Orders, Customers, YoY Growth %
- Line chart: Total Sales + Total Profit by month (dim_date)
- Map / bar: sales and margin by region and state
- Slicers: Year, Region, Segment, Category

**Page 2 - Profitability**
- Bar: Profit Margin % by sub-category (conditional colour: red if negative)
- Column chart: Margin % by Discount Band (identify the bands with negative aggregate margins)
- Table: top 10 loss-making products (Top N filter on Total Profit)
- Scatter: Sales (x) vs Profit (y), detail = product, size = quantity

**Page 3 - Customers**
- Pareto chart (sales by customer ranked + cumulative %)
- RFM segment donut: load `08_rfm_segmentation.csv`
- Cohort retention matrix: load `09_cohort_retention.csv` (rows=cohort, columns=months_since, values=retention_pct, heatmap colours)

**Page 4 - Operations**
- Avg Order-to-Ship Days and Loss-making Lines % by ship mode / region

> **Shipping data note:** `ship_date` is the date the order is shipped, not delivered. The sample does not include a delivery date or promised-delivery date, so do not label this metric as late deliveries or on-time delivery performance.

## 5. Polish checklist (what recruiters notice)
- One consistent colour theme; titles that state the insight ("Discount bands above 20% show negative aggregate margins")
- Tooltips, drill-through from region to state, bookmarks for navigation
- Export a PDF + screenshots of every page into `powerbi/screenshots/`
- Save the .pbix in `powerbi/` (keep it under GitHub's 100 MB limit)
