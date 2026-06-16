"""
data_cleaning.py
----------------
Day 2 Task: Clean all 10 datasets and save to data/processed/.
Run from project root: python data_cleaning.py
"""

import os
import pandas as pd
import numpy as np

RAW_DIR       = os.path.join(os.path.dirname(__file__), "data", "raw")
PROCESSED_DIR = os.path.join(os.path.dirname(__file__), "data", "processed")
os.makedirs(PROCESSED_DIR, exist_ok=True)


def divider(title=""):
    pad = (72 - len(title) - 2) // 2
    print("\n" + "─" * pad + f" {title} " + "─" * pad)


def save(df, filename):
    path = os.path.join(PROCESSED_DIR, filename)
    df.to_csv(path, index=False, encoding="utf-8")
    print(f"  Saved -> data/processed/{filename}  ({len(df):,} rows)")


def clean_nav_history():
    divider("nav_history")
    df = pd.read_csv(os.path.join(RAW_DIR, "02_nav_history.csv"))
    before = len(df)
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df.dropna(subset=["date"])
    df = df.sort_values(["amfi_code", "date"]).reset_index(drop=True)

    filled_rows = 0
    frames = []
    for code, group in df.groupby("amfi_code"):
        group = group.set_index("date")
        full_idx = pd.date_range(group.index.min(), group.index.max(), freq="B")
        group = group.reindex(full_idx)
        group["amfi_code"] = code
        missing = group["nav"].isna().sum()
        if missing:
            group["nav"] = group["nav"].ffill()
            filled_rows += missing
        frames.append(group.reset_index().rename(columns={"index": "date"}))

    df = pd.concat(frames, ignore_index=True)
    if filled_rows:
        print(f"  Forward-filled {filled_rows} missing NAV values")
    else:
        print("  No missing NAV gaps — data is complete")

    dupes = df.duplicated(subset=["amfi_code", "date"]).sum()
    df = df.drop_duplicates(subset=["amfi_code", "date"])
    if dupes:
        print(f"  Removed {dupes} duplicate rows")

    df = df[df["nav"] > 0]
    df = df.sort_values(["amfi_code", "date"])
    df["daily_return_pct"] = df.groupby("amfi_code")["nav"].pct_change() * 100
    df["daily_return_pct"] = df["daily_return_pct"].round(6)

    print(f"  Rows: {before:,} -> {len(df):,} | daily_return_pct column added")
    save(df, "clean_nav_history.csv")


def clean_investor_transactions():
    divider("investor_transactions")
    df = pd.read_csv(os.path.join(RAW_DIR, "08_investor_transactions.csv"))
    before = len(df)

    df["transaction_date"] = pd.to_datetime(df["transaction_date"], errors="coerce")
    df = df.dropna(subset=["transaction_date"])

    type_map = {
        "sip": "SIP", "SIP": "SIP",
        "lumpsum": "Lumpsum", "Lumpsum": "Lumpsum", "LUMPSUM": "Lumpsum",
        "redemption": "Redemption", "Redemption": "Redemption", "REDEMPTION": "Redemption",
    }
    df["transaction_type"] = df["transaction_type"].str.strip().map(type_map).fillna(df["transaction_type"])

    df = df[df["amount_inr"] > 0]
    print(f"  KYC status: {df['kyc_status'].value_counts().to_dict()}")
    print(f"  Transaction types: {df['transaction_type'].value_counts().to_dict()}")

    str_cols = df.select_dtypes(include="object").columns
    for col in str_cols:
        df[col] = df[col].str.strip()

    df = df.drop_duplicates()
    print(f"  Rows: {before:,} -> {len(df):,}")
    save(df, "clean_investor_transactions.csv")


def clean_scheme_performance():
    divider("scheme_performance")
    df = pd.read_csv(os.path.join(RAW_DIR, "07_scheme_performance.csv"))

    return_cols = ["return_1yr_pct", "return_3yr_pct", "return_5yr_pct",
                   "benchmark_3yr_pct", "alpha", "beta", "sharpe_ratio",
                   "sortino_ratio", "std_dev_ann_pct", "max_drawdown_pct"]
    for col in return_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    print(f"  Expense ratio range: {df['expense_ratio_pct'].min()}% - {df['expense_ratio_pct'].max()}%  OK")
    print(f"  Sharpe ratio range: {df['sharpe_ratio'].min():.2f} to {df['sharpe_ratio'].max():.2f}")
    print(f"  Max drawdown range: {df['max_drawdown_pct'].min():.2f}% to {df['max_drawdown_pct'].max():.2f}%")

    out_of_range = df[(df["expense_ratio_pct"] < 0.1) | (df["expense_ratio_pct"] > 2.5)]
    if len(out_of_range):
        print(f"  FLAG: {len(out_of_range)} funds outside 0.1-2.5% expense ratio range")
    else:
        print("  All expense ratios within 0.1-2.5% range")

    save(df, "clean_scheme_performance.csv")


def clean_standard(filename, out_name, date_cols):
    name = out_name.replace("clean_", "").replace(".csv", "")
    divider(name)
    df = pd.read_csv(os.path.join(RAW_DIR, filename))

    for col in date_cols:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")

    str_cols = df.select_dtypes(include="object").columns
    for col in str_cols:
        df[col] = df[col].str.strip()

    dupes = df.duplicated().sum()
    if dupes:
        df = df.drop_duplicates()
        print(f"  Removed {dupes} duplicate rows")
    else:
        print("  No duplicates found")

    print(f"  Total nulls: {df.isna().sum().sum()}")
    save(df, out_name)


def main():
    print("\n" + "=" * 72)
    print("  BLUESTOCK MF — Day 2: Data Cleaning")
    print("=" * 72)

    clean_nav_history()
    clean_investor_transactions()
    clean_scheme_performance()
    clean_standard("01_fund_master.csv",          "clean_fund_master.csv",          ["launch_date"])
    clean_standard("03_aum_by_fund_house.csv",    "clean_aum_by_fund_house.csv",    ["date"])
    clean_standard("04_monthly_sip_inflows.csv",  "clean_monthly_sip_inflows.csv",  ["month"])
    clean_standard("05_category_inflows.csv",     "clean_category_inflows.csv",     ["month"])
    clean_standard("06_industry_folio_count.csv", "clean_industry_folio_count.csv", ["month"])
    clean_standard("09_portfolio_holdings.csv",   "clean_portfolio_holdings.csv",   ["portfolio_date"])
    clean_standard("10_benchmark_indices.csv",    "clean_benchmark_indices.csv",    ["date"])

    print("\n" + "=" * 72)
    print("  Cleaning complete. All files saved to data/processed/")
    print("=" * 72 + "\n")


if __name__ == "__main__":
    main()