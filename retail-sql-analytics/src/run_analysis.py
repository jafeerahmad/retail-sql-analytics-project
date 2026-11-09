"""Runs every query in sql/, exports CSVs for Power BI, draws charts, writes findings."""
import sqlite3
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
DB, SQL, OUT, REP = ROOT / "data" / "retail.db", ROOT / "sql", ROOT / "exports", ROOT / "reports"


def run_queries(con) -> dict:
    OUT.mkdir(exist_ok=True)
    res = {}
    for f in sorted(SQL.glob("*.sql")):
        df = pd.read_sql_query(f.read_text(), con)
        df.to_csv(OUT / f"{f.stem}.csv", index=False)
        res[f.stem] = df
        print(f"{f.stem}: {len(df)} rows")
    for t in ["fact_sales", "dim_customer", "dim_product", "dim_date"]:  # Power BI model
        pd.read_sql_query(f"SELECT * FROM {t}", con).to_csv(OUT / f"{t}.csv", index=False)
    return res


def charts(res):
    """Export reproducible chart images from the SQL result dataframes."""
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print("matplotlib not installed - skipping charts")
        return
    d = REP / "charts"
    d.mkdir(parents=True, exist_ok=True)

    def save(fig, name):
        fig.tight_layout()
        fig.savefig(d / name, dpi=160, bbox_inches="tight")
        plt.close(fig)

    # Monthly trend
    m = res["02_monthly_trend_yoy"]
    fig, ax = plt.subplots(figsize=(10, 4.5))
    ax.plot(m.month, m.sales / 1e5, marker="o", ms=3, linewidth=1.6)
    ax.set_title("Monthly sales trend")
    ax.set_ylabel("Sales (INR lakh)")
    ax.set_xlabel("Month")
    ax.set_xticks(range(0, len(m), 6))
    ax.set_xticklabels(m.month.iloc[::6], rotation=45, ha="right")
    ax.grid(True, alpha=0.25)
    save(fig, "monthly_sales.png")

    # Profitability by sub-category
    s = res["03_category_subcategory_profit"].sort_values("margin_pct")
    fig, ax = plt.subplots(figsize=(8, 5.5))
    ax.barh(s.sub_category, s.margin_pct)
    ax.axvline(0, color="black", linewidth=0.8)
    ax.set_title("Profit margin by sub-category")
    ax.set_xlabel("Profit margin (%)")
    ax.set_ylabel("Sub-category")
    save(fig, "margin_by_subcategory.png")

    # Discount impact
    x = res["04_discount_impact"]
    fig, ax = plt.subplots(figsize=(7.5, 4.5))
    ax.bar(x.discount_band, x.margin_pct)
    ax.axhline(0, color="black", linewidth=0.8)
    ax.set_title("Profit margin by discount band")
    ax.set_xlabel("Discount band")
    ax.set_ylabel("Profit margin (%)")
    save(fig, "discount_vs_margin.png")

    # Customer Pareto curve
    p = res["07_customer_pareto"]
    fig, ax = plt.subplots(figsize=(7.5, 4.5))
    ax.plot(p.pct_of_customers, p.cum_sales_pct, linewidth=2)
    ax.axvline(20, linestyle="--", color="grey", label="Top 20% of customers")
    ax.axhline(80, linestyle=":", color="grey", label="80% of sales reference")
    ax.set_xlabel("Cumulative share of customers (%)")
    ax.set_ylabel("Cumulative share of sales (%)")
    ax.set_title("Customer revenue concentration (Pareto curve)")
    ax.legend()
    ax.grid(True, alpha=0.2)
    save(fig, "pareto.png")

    # Regional sales share and profitability
    reg = res["06_region_performance"].sort_values("sales_share_pct", ascending=False)
    fig, ax = plt.subplots(figsize=(8, 4.8))
    bars = ax.bar(reg.region, reg.sales_share_pct)
    ax.set_title("Sales share by region")
    ax.set_xlabel("Region")
    ax.set_ylabel("Share of total sales (%)")
    ax.bar_label(bars, fmt="%.1f%%", padding=2)
    ax.tick_params(axis="x", rotation=20)
    save(fig, "regional_sales_share.png")

    # Shipping is order-to-ship elapsed time, not delivery lateness.
    sh = res["10_shipping_performance"].sort_values("avg_ship_days")
    fig, ax = plt.subplots(figsize=(8, 4.8))
    bars = ax.bar(sh.ship_mode, sh.avg_ship_days)
    ax.set_title("Average order-to-ship time by shipping mode")
    ax.set_xlabel("Shipping mode")
    ax.set_ylabel("Average days from order to ship")
    ax.bar_label(bars, fmt="%.1f d", padding=2)
    ax.tick_params(axis="x", rotation=20)
    save(fig, "order_to_ship_days.png")

    # Cohort retention heatmap
    coh = res["09_cohort_retention"].pivot(index="cohort", columns="months_since", values="retention_pct")
    fig, ax = plt.subplots(figsize=(10, 6))
    im = ax.imshow(coh.values, aspect="auto", interpolation="nearest", vmin=0, vmax=100)
    ax.set_title("Monthly cohort retention (%)")
    ax.set_xlabel("Months since first purchase")
    ax.set_ylabel("First-purchase cohort")
    ax.set_xticks(range(len(coh.columns)))
    ax.set_xticklabels(coh.columns)
    ax.set_yticks(range(len(coh.index)))
    ax.set_yticklabels(coh.index, fontsize=7)
    fig.colorbar(im, ax=ax, label="Active customers (%)")
    save(fig, "cohort_retention_heatmap.png")

    # Segment share by quarter (100% stacked bars)
    seg = res["12_segment_quarterly_share"].pivot(
        index="quarter", columns="segment", values="share_of_quarter_pct").fillna(0)
    fig, ax = plt.subplots(figsize=(10, 5))
    seg.plot(kind="bar", stacked=True, ax=ax)
    ax.set_title("Customer-segment share of sales by quarter")
    ax.set_xlabel("Quarter")
    ax.set_ylabel("Share of quarterly sales (%)")
    ax.legend(title="Segment", bbox_to_anchor=(1.02, 1), loc="upper left")
    ax.tick_params(axis="x", rotation=45)
    save(fig, "segment_quarterly_share.png")


def findings(res) -> str:
    k = res["01_kpi_overview"].iloc[0]
    reg = res["06_region_performance"]
    sub = res["03_category_subcategory_profit"].sort_values("margin_pct")
    disc = res["04_discount_impact"]
    par = res["07_customer_pareto"]
    top20 = par[par.pct_of_customers <= 20].cum_sales_pct.max()
    rep = res["11_repeat_rate"].iloc[0]
    ship = res["10_shipping_performance"].sort_values("pct_over_5_days", ascending=False).iloc[0]
    yoy = res["02_monthly_trend_yoy"].dropna(subset=["yoy_growth_pct"]).iloc[-1]
    neg = disc[disc.margin_pct < 0]
    loss_subs = sub[sub.margin_pct < 0].sub_category.tolist()
    L = ["# Key findings (auto-generated from the SQL results)\n",
         "> Based on synthetic data. Re-run on real data before quoting any figure.\n",
         f"1. **Overall:** ₹{k.total_sales:,.0f} sales, ₹{k.total_profit:,.0f} profit "
         f"({k.profit_margin_pct}% margin) across {int(k.orders):,} orders and {int(k.customers):,} customers.",
         f"2. **Growth:** latest month ({yoy.month}) sales are {yoy.yoy_growth_pct:+.1f}% vs the same month last year.",
         f"3. **Regions:** {reg.iloc[0].region} leads with {reg.iloc[0].sales_share_pct}% of sales; "
         f"{reg.sort_values('margin_pct').iloc[0].region} has the lowest margin ({reg.margin_pct.min()}%).",
         f"4. **Loss-making sub-categories:** {', '.join(loss_subs) if loss_subs else 'none'}; "
         f"lowest margin is {sub.iloc[0].sub_category} ({sub.iloc[0].margin_pct}%).",
         f"5. **Discounts:** margin falls from {disc.iloc[0].margin_pct}% at 0% discount to {disc.iloc[-1].margin_pct}% "
         f"in the {disc.iloc[-1].discount_band} band"
         + (f"; margins turn negative from the {neg.iloc[0].discount_band} band." if len(neg) else "."),
         f"6. **Concentration:** the top 20% of customers generate {top20}% of sales.",
         f"7. **Retention:** {rep.repeat_rate_pct}% of customers ordered more than once (avg {rep.avg_orders} orders).",
         f"8. **Shipping:** {ship.ship_mode} has the highest share of line items with more than 5 days between order and ship dates ({ship.pct_over_5_days}%). This is an order-to-ship measure, not confirmed delivery lateness.",
         "\n## Recommendations (template - adapt to real data)",
         "- Cap discounts on loss-making sub-categories or reprice them.",
         "- Protect and reward the top-20% customer group; run win-back campaigns on 'At Risk' RFM segments (query 08).",
         "- Investigate the lowest-margin region and the shipping mode with the longest order-to-ship time; the source data does not include a delivery timestamp."]
    return "\n".join(L)


def main():
    con = sqlite3.connect(DB)
    res = run_queries(con)
    charts(res)
    REP.mkdir(exist_ok=True)
    (REP / "findings.md").write_text(findings(res), encoding="utf-8")
    print("\n" + (REP / "findings.md").read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
