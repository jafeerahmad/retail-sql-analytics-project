import sqlite3

import pandas as pd

from src import build_db
from src.generate_data import generate


def test_generator_outputs_valid_relational_data():
    customers, products, sales = generate(n_customers=60, n_orders=100, seed=5)
    assert len(customers) == 60
    assert len(products) == 120
    assert customers.customer_id.is_unique
    assert products.product_id.is_unique
    assert sales.line_id.is_unique
    assert set(sales.customer_id).issubset(set(customers.customer_id))
    assert set(sales.product_id).issubset(set(products.product_id))
    assert (sales.quantity > 0).all()
    assert sales.discount.between(0, 1).all()


def test_database_builder_creates_star_schema(tmp_path, monkeypatch):
    raw = tmp_path / "raw"
    raw.mkdir()
    customers, products, sales = generate(n_customers=60, n_orders=100, seed=9)
    customers.to_csv(raw / "customers.csv", index=False)
    products.to_csv(raw / "products.csv", index=False)
    sales.to_csv(raw / "sales.csv", index=False)

    database = tmp_path / "retail.db"
    monkeypatch.setattr(build_db, "RAW", raw)
    monkeypatch.setattr(build_db, "DB", database)
    build_db.main()

    with sqlite3.connect(database) as con:
        tables = {r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        assert {"fact_sales", "dim_customer", "dim_product", "dim_date"} <= tables
        fact_count = con.execute("SELECT COUNT(*) FROM fact_sales").fetchone()[0]
        assert fact_count == len(sales)
