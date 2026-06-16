"""
db_load.py
----------
Day 2 Task: Load all cleaned CSVs into SQLite (bluestock_mf.db).
Run from project root: python db_load.py
"""

import os
import pandas as pd
from sqlalchemy import create_engine, text

BASE_DIR      = os.path.dirname(__file__)
PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")
DB_PATH       = os.path.join(BASE_DIR, "data", "bluestock_mf.db")
SCHEMA_PATH   = os.path.join(BASE_DIR, "sql", "schema.sql")


def divider(title=""):
    pad = (68 - len(title) - 2) // 2
    print("\n" + "─" * pad + f" {title} " + "─" * pad)


def get_engine():
    return create_engine(f"sqlite:///{DB_PATH}", echo=False)


def apply_schema(engine):
    divider("Applying Schema")
    with open(SCHEMA_PATH, "r") as f:
        sql = f.read()
    with engine.connect() as conn:
        for statement in sql.split(";"):
            stmt = statement.strip()
            if stmt:
                conn.execute(text(stmt))
        conn.commit()
    print("  Schema applied successfully")


def load_table(engine, csv_filename, table_name, date_cols=None):
    path = os.path.join(PROCESSED_DIR, csv_filename)
    df = pd.read_csv(path, encoding="utf-8")
    if date_cols:
        for col in date_cols:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors="coerce").dt.strftime("%Y-%m-%d")
    df.to_sql(table_name, engine, if_exists="replace", index=False)
    with engine.connect() as conn:
        db_count = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}")).scalar()
    status = "OK" if db_count == len(df) else f"MISMATCH (CSV={len(df)}, DB={db_count})"
    print(f"  {table_name:<30} CSV: {len(df):>6,}  |  DB: {db_count:>6,}  |  {status}")


def build_dim_date(engine):
    divider("Building dim_date")
    with engine.connect() as conn:
        result = conn.execute(text("SELECT MIN(date), MAX(date) FROM fact_nav"))
        min_date, max_date = result.fetchone()
    dates = pd.date_range(start=min_date, end=max_date, freq="D")
    df = pd.DataFrame({"date": dates})
    df["date_id"]     = df["date"].dt.strftime("%Y-%m-%d")
    df["year"]        = df["date"].dt.year
    df["month"]       = df["date"].dt.month
    df["quarter"]     = df["date"].dt.quarter
    df["month_name"]  = df["date"].dt.strftime("%B")
    df["day_of_week"] = df["date"].dt.strftime("%A")
    df["is_weekday"]  = (df["date"].dt.dayofweek < 5).astype(int)
    df["date"]        = df["date"].dt.strftime("%Y-%m-%d")
    df.to_sql("dim_date", engine, if_exists="replace", index=False)
    with engine.connect() as conn:
        count = conn.execute(text("SELECT COUNT(*) FROM dim_date")).scalar()
    print(f"  dim_date: {count:,} calendar days ({min_date} to {max_date})")


def verify_fk(engine):
    divider("FK Integrity Check")
    checks = [
        ("fact_nav",          "amfi_code"),
        ("fact_transactions", "amfi_code"),
        ("fact_performance",  "amfi_code"),
        ("fact_portfolio",    "amfi_code"),
    ]
    with engine.connect() as conn:
        for table, col in checks:
            orphans = conn.execute(text(f"""
                SELECT COUNT(*) FROM {table}
                WHERE {col} NOT IN (SELECT amfi_code FROM dim_fund)
            """)).scalar()
            status = "OK" if orphans == 0 else f"FAIL - {orphans} orphan rows"
            print(f"  {table}.{col} -> dim_fund.amfi_code : {status}")


def main():
    print("\n" + "=" * 68)
    print("  BLUESTOCK MF — Day 2: SQLite DB Load")
    print("=" * 68)

    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        print(f"  Removed existing DB")

    engine = get_engine()
    apply_schema(engine)

    divider("Loading Tables")
    load_table(engine, "clean_fund_master.csv",           "dim_fund",              ["launch_date"])
    load_table(engine, "clean_nav_history.csv",           "fact_nav",              ["date"])
    load_table(engine, "clean_investor_transactions.csv", "fact_transactions",     ["transaction_date"])
    load_table(engine, "clean_scheme_performance.csv",    "fact_performance",      [])
    load_table(engine, "clean_aum_by_fund_house.csv",     "fact_aum",              ["date"])
    load_table(engine, "clean_monthly_sip_inflows.csv",   "fact_sip_industry",     ["month"])
    load_table(engine, "clean_category_inflows.csv",      "fact_category_inflows", ["month"])
    load_table(engine, "clean_industry_folio_count.csv",  "fact_folio_count",      ["month"])
    load_table(engine, "clean_portfolio_holdings.csv",    "fact_portfolio",        ["portfolio_date"])

    build_dim_date(engine)
    verify_fk(engine)

    divider("Database Summary")
    db_size_mb = os.path.getsize(DB_PATH) / (1024 * 1024)
    print(f"  Database : {DB_PATH}")
    print(f"  Size     : {db_size_mb:.2f} MB")
    with engine.connect() as conn:
        tables = conn.execute(text(
            "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
        )).fetchall()
        print(f"  Tables   : {len(tables)}")
        for (t,) in tables:
            count = conn.execute(text(f"SELECT COUNT(*) FROM {t}")).scalar()
            print(f"    {t:<30} {count:>8,} rows")

    print("\n  Day 2 DB load complete.\n")


if __name__ == "__main__":
    main()