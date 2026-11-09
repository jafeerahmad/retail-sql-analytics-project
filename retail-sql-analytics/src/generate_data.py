"""Synthetic retail data (Indian regions, INR) in a Superstore-like schema.
Built-in patterns: Nov-Dec peak, yearly growth, Pareto customers, heavy discounting on
Tables/Binders/Machines (which destroys profit), slower shipping in the East.
Replace data/raw/*.csv with real data (same columns) to analyse your own dataset."""
import numpy as np
import pandas as pd
from pathlib import Path

RAW = Path(__file__).resolve().parent.parent / "data" / "raw"

CATALOG = {  # category -> sub_category -> (base price INR, cost ratio)
    "Furniture": {"Chairs": (8000, .62), "Tables": (15000, .88), "Bookcases": (9000, .70), "Furnishings": (2500, .60)},
    "Technology": {"Phones": (18000, .72), "Accessories": (1800, .58), "Machines": (30000, .80), "Copiers": (45000, .65)},
    "Office Supplies": {"Paper": (400, .55), "Binders": (900, .80), "Storage": (2200, .68), "Art": (350, .52)},
}
STATES = {
    "South": ["Andhra Pradesh", "Telangana", "Karnataka", "Tamil Nadu", "Kerala"],
    "West": ["Maharashtra", "Gujarat", "Rajasthan", "Goa"],
    "North": ["Delhi", "Punjab", "Uttar Pradesh", "Haryana"],
    "East": ["West Bengal", "Odisha", "Bihar", "Assam"],
    "Central": ["Madhya Pradesh", "Chhattisgarh"],
}
DISC = [0, .05, .10, .15, .20, .30, .40, .50]
DISC_NORMAL = [.35, .12, .15, .10, .12, .08, .05, .03]
DISC_HEAVY = [.15, .05, .10, .10, .15, .20, .15, .10]
HEAVY = {"Tables", "Binders", "Machines"}


def generate(n_customers=800, n_orders=6000, seed=11):
    r = np.random.default_rng(seed)
    prods = []
    for cat, subs in CATALOG.items():
        for sub, (price, cr) in subs.items():
            for i in range(10):
                prods.append((len(prods) + 1, f"{sub} Model {i+1:02d}", cat, sub,
                              round(price * r.lognormal(0, .25), 2),
                              round(float(np.clip(cr + r.normal(0, .03), .4, .95)), 3)))
    prod = pd.DataFrame(prods, columns=["product_id", "product_name", "category", "sub_category",
                                        "unit_price", "cost_ratio"])
    regions = r.choice(list(STATES), n_customers, p=[.28, .27, .22, .15, .08])
    cust = pd.DataFrame({
        "customer_id": [f"CUST-{i+1:04d}" for i in range(n_customers)],
        "customer_name": [f"Customer {i+1}" for i in range(n_customers)],
        "segment": r.choice(["Consumer", "Corporate", "Home Office"], n_customers, p=[.52, .30, .18]),
        "region": regions,
        "state": [r.choice(STATES[x]) for x in regions]})
    cw = 1 / np.arange(1, n_customers + 1) ** 0.8
    r.shuffle(cw); cw /= cw.sum()

    dates = pd.date_range("2023-01-01", "2026-10-31")
    w = (1 + 0.6 * dates.month.isin([11, 12]) + 0.1 * (dates.dayofweek >= 5)) * np.linspace(1, 1.8, len(dates))
    w = np.asarray(w, float); w /= w.sum()
    modes = ["Standard Class", "Second Class", "First Class", "Same Day"]
    ship_rng = {"Standard Class": (4, 8), "Second Class": (2, 5), "First Class": (1, 4), "Same Day": (0, 2)}
    reg_of = cust.set_index("customer_id").region

    rows, line = [], 0
    for o in range(n_orders):
        cid = cust.customer_id[r.choice(n_customers, p=cw)]
        od = dates[r.choice(len(dates), p=w)]
        mode = r.choice(modes, p=[.6, .2, .15, .05])
        lo, hi = ship_rng[mode]
        sd = od + pd.Timedelta(days=int(r.integers(lo, hi)) + (1 if reg_of[cid] == "East" else 0))
        for pid in r.choice(len(prod), int(r.integers(1, 5)), replace=False):
            p = prod.iloc[pid]
            qty = int(r.integers(1, 6))
            d = r.choice(DISC, p=DISC_HEAVY if p.sub_category in HEAVY else DISC_NORMAL)
            sales = p.unit_price * qty * (1 - d)
            profit = sales - p.unit_price * p.cost_ratio * qty
            line += 1
            rows.append((line, f"ORD-{o+1:05d}", od.date().isoformat(), sd.date().isoformat(), mode, cid,
                         int(p.product_id), qty, d, round(sales, 2), round(profit, 2)))
    sales = pd.DataFrame(rows, columns=["line_id", "order_id", "order_date", "ship_date", "ship_mode",
                                        "customer_id", "product_id", "quantity", "discount", "sales", "profit"])
    return cust, prod.drop(columns="cost_ratio"), sales


def main():
    RAW.mkdir(parents=True, exist_ok=True)
    c, p, s = generate()
    c.to_csv(RAW / "customers.csv", index=False)
    p.to_csv(RAW / "products.csv", index=False)
    s.to_csv(RAW / "sales.csv", index=False)
    print(f"Generated {len(c)} customers, {len(p)} products, {len(s)} sales lines")


if __name__ == "__main__":
    main()
