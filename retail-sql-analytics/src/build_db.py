"""Builds a star-schema SQLite database from data/raw/*.csv."""
import sqlite3
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
RAW, DB = ROOT / "data" / "raw", ROOT / "data" / "retail.db"


def main():
    DB.unlink(missing_ok=True)
    cust = pd.read_csv(RAW / "customers.csv")
    prod = pd.read_csv(RAW / "products.csv")
    fact = pd.read_csv(RAW / "sales.csv", parse_dates=["order_date", "ship_date"])

    required = {
        "customers": {"customer_id", "customer_name", "segment", "region", "state"},
        "products": {"product_id", "product_name", "category", "sub_category", "unit_price"},
        "sales": {"line_id", "order_id", "order_date", "ship_date", "ship_mode", "customer_id",
                  "product_id", "quantity", "discount", "sales", "profit"},
    }
    for label, frame, expected in [("customers", cust, required["customers"]),
                                   ("products", prod, required["products"]),
                                   ("sales", fact, required["sales"])]:
        missing = sorted(expected - set(frame.columns))
        if missing:
            raise ValueError(f"{label}.csv is missing required columns: {', '.join(missing)}")
        if frame.empty:
            raise ValueError(f"{label}.csv contains no rows.")
        if frame[list(expected)].isna().any().any():
            raise ValueError(f"{label}.csv contains missing values in required columns.")

    if cust.customer_id.duplicated().any() or prod.product_id.duplicated().any() or fact.line_id.duplicated().any():
        raise ValueError("Duplicate primary keys found in customers, products or sales data.")
    if not set(fact.customer_id).issubset(set(cust.customer_id)):
        raise ValueError("sales.csv contains customer_id values missing from customers.csv.")
    if not set(fact.product_id).issubset(set(prod.product_id)):
        raise ValueError("sales.csv contains product_id values missing from products.csv.")
    if (fact.quantity <= 0).any() or (fact.sales < 0).any() or ((fact.discount < 0) | (fact.discount > 1)).any():
        raise ValueError("Sales data must have positive quantities, non-negative sales and discounts from 0 to 1.")
    if fact.order_date.isna().any() or fact.ship_date.isna().any():
        raise ValueError("Invalid order_date or ship_date values found in sales.csv.")
    if (fact.ship_date < fact.order_date).any():
        raise ValueError("ship_date cannot be earlier than order_date.")

    d = pd.date_range(fact.order_date.min().normalize(), fact.order_date.max().normalize())
    dim_date = pd.DataFrame({"date": d.strftime("%Y-%m-%d"), "year": d.year, "quarter": d.quarter,
                             "month": d.month, "month_name": d.strftime("%b"),
                             "weekday": d.strftime("%a")})
    fact["order_date"] = fact.order_date.dt.strftime("%Y-%m-%d")
    fact["ship_date"] = fact.ship_date.dt.strftime("%Y-%m-%d")

    con = sqlite3.connect(DB)
    cust.to_sql("dim_customer", con, index=False)
    prod.to_sql("dim_product", con, index=False)
    dim_date.to_sql("dim_date", con, index=False)
    fact.to_sql("fact_sales", con, index=False)
    for ix in ["fact_sales(customer_id)", "fact_sales(product_id)", "fact_sales(order_date)",
               "fact_sales(order_id)", "dim_customer(customer_id)", "dim_product(product_id)"]:
        con.execute(f"CREATE INDEX IF NOT EXISTS idx_{ix.replace('(', '_').replace(')', '')} ON {ix}")
    con.commit(); con.close()
    print(f"Built {DB.name}: fact_sales={len(fact)} rows")


if __name__ == "__main__":
    main()
