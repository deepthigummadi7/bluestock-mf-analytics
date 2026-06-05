"""
data_ingestion.py
-----------------
Day 1 Task: Load all 10 CSV datasets, profile each one, and validate
AMFI code consistency between fund_master and nav_history.
 
Run from project root:
    python data_ingestion.py
"""
 
import os
import pandas as pd
import numpy as np
 
# ── Paths ──────────────────────────────────────────────────────────────────────
RAW_DIR = os.path.join(os.path.dirname(__file__), "data", "raw")
PROCESSED_DIR = os.path.join(os.path.dirname(__file__), "data", "processed")
os.makedirs(PROCESSED_DIR, exist_ok=True)
 
# ── Dataset registry ───────────────────────────────────────────────────────────
DATASETS = {
    "fund_master":          "01_fund_master.csv",
    "nav_history":          "02_nav_history.csv",
    "aum_by_fund_house":    "03_aum_by_fund_house.csv",
    "monthly_sip_inflows":  "04_monthly_sip_inflows.csv",
    "category_inflows":     "05_category_inflows.csv",
    "industry_folio_count": "06_industry_folio_count.csv",
    "scheme_performance":   "07_scheme_performance.csv",
    "investor_transactions":"08_investor_transactions.csv",
    "portfolio_holdings":   "09_portfolio_holdings.csv",
    "benchmark_indices":    "10_benchmark_indices.csv",
}
 
# ── Date columns per dataset (parsed during load) ──────────────────────────────
DATE_COLS = {
    "fund_master":          ["launch_date"],
    "nav_history":          ["date"],
    "aum_by_fund_house":    ["date"],
    "monthly_sip_inflows":  ["month"],
    "category_inflows":     ["month"],
    "industry_folio_count": ["month"],
    "investor_transactions":["transaction_date"],
    "portfolio_holdings":   ["portfolio_date"],
    "benchmark_indices":    ["date"],
}
 
 
def divider(title=""):
    width = 80
    if title:
        pad = (width - len(title) - 2) // 2
        print("\n" + "─" * pad + f" {title} " + "─" * pad)
    else:
        print("─" * width)
 
 
def load_dataset(name: str, filename: str) -> pd.DataFrame:
    """Load one CSV; parse known date columns; return DataFrame."""
    path = os.path.join(RAW_DIR, filename)
    parse_dates = DATE_COLS.get(name, [])
    df = pd.read_csv(path, parse_dates=parse_dates)
    return df
 
 
def profile_dataset(name: str, df: pd.DataFrame) -> dict:
    """Print shape, dtypes, head, nulls; return anomaly summary dict."""
    divider(name)
    print(f"  File  : {DATASETS[name]}")
    print(f"  Shape : {df.shape[0]:,} rows × {df.shape[1]} columns\n")
 
    # dtypes
    print("  dtypes:")
    for col, dtype in df.dtypes.items():
        null_count = df[col].isna().sum()
        null_pct   = null_count / len(df) * 100
        null_flag  = f"  ← {null_count:,} nulls ({null_pct:.1f}%)" if null_count else ""
        print(f"    {col:<35} {str(dtype):<20}{null_flag}")
 
    # head
    print("\n  head(3):")
    print(df.head(3).to_string(index=False))
 
    # anomaly detection
    anomalies = []
 
    # 1. missing values
    null_series = df.isna().sum()
    bad_nulls = null_series[null_series > 0]
    if not bad_nulls.empty:
        for col, cnt in bad_nulls.items():
            anomalies.append(f"  ⚠  {col}: {cnt:,} nulls ({cnt/len(df)*100:.1f}%)")
 
    # 2. duplicate rows
    dupes = df.duplicated().sum()
    if dupes:
        anomalies.append(f"  ⚠  {dupes:,} fully duplicate rows")
 
    # 3. negative values in numeric columns that should be positive
    amount_cols = [c for c in df.columns if any(k in c for k in
                   ["nav", "aum", "amount", "inflow", "value", "price", "ratio"])]
    for col in amount_cols:
        if pd.api.types.is_numeric_dtype(df[col]):
            neg = (df[col] < 0).sum()
            if neg:
                anomalies.append(f"  ⚠  {col}: {neg:,} negative values")
 
    # 4. amfi_code range sanity (AMFI codes are 6-digit integers)
    if "amfi_code" in df.columns:
        invalid = df["amfi_code"].apply(
            lambda x: not (100000 <= int(x) <= 999999) if pd.notna(x) else True
        ).sum()
        if invalid:
            anomalies.append(f"  ⚠  amfi_code: {invalid} codes outside 6-digit range")
 
    if anomalies:
        print("\n  Anomalies:")
        for a in anomalies:
            print(a)
    else:
        print("\n  ✓ No anomalies detected")
 
    print()
    return {"name": name, "shape": df.shape, "anomalies": anomalies}
 
 
def explore_fund_master(df: pd.DataFrame):
    """Task 6 – Explore unique fund houses, categories, sub-categories, risk grades."""
    divider("Fund Master — Exploration")
 
    print("  Unique Fund Houses:")
    for fh in sorted(df["fund_house"].dropna().unique()):
        print(f"    • {fh}")
 
    print(f"\n  Categories ({df['category'].nunique()}):")
    for cat in sorted(df["category"].dropna().unique()):
        print(f"    • {cat}")
 
    print(f"\n  Sub-categories ({df['sub_category'].nunique()}):")
    for sub in sorted(df["sub_category"].dropna().unique()):
        print(f"    • {sub}")
 
    print(f"\n  Risk Grades ({df['risk_category'].nunique()}):")
    for r in sorted(df["risk_category"].dropna().unique()):
        count = (df["risk_category"] == r).sum()
        print(f"    • {r:<15} — {count} schemes")
 
    print(f"\n  SEBI Category Codes ({df['sebi_category_code'].nunique()}):")
    code_counts = df["sebi_category_code"].value_counts()
    for code, cnt in code_counts.items():
        print(f"    • {code:<8} — {cnt} schemes")
 
    print(f"\n  Plan split:")
    print(df["plan"].value_counts().to_string())
 
 
def validate_amfi_codes(fund_master: pd.DataFrame, nav_history: pd.DataFrame) -> str:
    """
    Task 7 – Confirm every AMFI code in fund_master exists in nav_history.
    Returns a formatted data quality summary string.
    """
    divider("AMFI Code Validation")
 
    fm_codes  = set(fund_master["amfi_code"].dropna().astype(int))
    nav_codes = set(nav_history["amfi_code"].dropna().astype(int))
 
    missing_in_nav  = fm_codes - nav_codes
    extra_in_nav    = nav_codes - fm_codes
    matched         = fm_codes & nav_codes
 
    lines = [
        "  ┌─ AMFI Code Validation Report ─────────────────────────────────┐",
        f"  │  fund_master unique codes   : {len(fm_codes):>6}                          │",
        f"  │  nav_history unique codes   : {len(nav_codes):>6}                          │",
        f"  │  Codes present in both      : {len(matched):>6}  ✓                        │",
        f"  │  In fund_master, NOT in nav : {len(missing_in_nav):>6}  {'✓' if not missing_in_nav else '⚠'}                        │",
        f"  │  In nav, NOT in fund_master : {len(extra_in_nav):>6}  {'✓' if not extra_in_nav else '⚠'}                        │",
        "  └────────────────────────────────────────────────────────────────┘",
    ]
    report = "\n".join(lines)
    print(report)
 
    if missing_in_nav:
        print(f"\n  ⚠  Codes in fund_master missing from nav_history ({len(missing_in_nav)}):")
        for code in sorted(missing_in_nav):
            scheme = fund_master.loc[fund_master["amfi_code"] == code, "scheme_name"].values
            print(f"     {code}  →  {scheme[0] if len(scheme) else 'unknown'}")
 
    if extra_in_nav:
        print(f"\n  ⚠  {len(extra_in_nav)} codes in nav_history have no matching fund_master entry")
        print(f"     Sample: {sorted(extra_in_nav)[:10]}")
 
    # Overall quality verdict
    total_checks = 5
    pass_count = sum([
        len(missing_in_nav) == 0,
        len(extra_in_nav) == 0,
        fund_master["amfi_code"].notna().all(),
        nav_history["amfi_code"].notna().all(),
        nav_history["nav"].notna().all(),
    ])
    verdict = "PASS" if pass_count == total_checks else f"PARTIAL ({pass_count}/{total_checks} checks passed)"
    print(f"\n  Data Quality Verdict: {verdict}")
 
    return report
 
 
def main():
    print("\n" + "═" * 80)
    print("  BLUESTOCK MUTUAL FUND ANALYTICS — Day 1: Data Ingestion")
    print("═" * 80)
 
    dataframes = {}
    quality_log = []
 
    # ── Load & profile all 10 datasets ────────────────────────────────────────
    for name, filename in DATASETS.items():
        df = load_dataset(name, filename)
        dataframes[name] = df
        summary = profile_dataset(name, df)
        quality_log.append(summary)
 
    # ── Task 6: Explore fund master ────────────────────────────────────────────
    explore_fund_master(dataframes["fund_master"])
 
    # ── Task 7: Validate AMFI codes ────────────────────────────────────────────
    validate_amfi_codes(dataframes["fund_master"], dataframes["nav_history"])
 
    # ── Write data quality summary to reports/ ─────────────────────────────────
    divider("Writing data quality summary")
    report_path = os.path.join(
        os.path.dirname(__file__), "reports", "data_quality_summary.txt"
    )
    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("BLUESTOCK MF — DATA QUALITY SUMMARY (Day 1)\n")
        f.write("=" * 60 + "\n\n")
        for s in quality_log:
            f.write(f"Dataset : {s['name']}\n")
            f.write(f"Shape   : {s['shape'][0]:,} rows × {s['shape'][1]} columns\n")
            if s["anomalies"]:
                f.write("Anomalies:\n")
                for a in s["anomalies"]:
                    f.write(f"  {a}\n")
            else:
                f.write("  No anomalies\n")
            f.write("\n")
 
    print(f"  ✓ Saved: {report_path}")
    print("\n  Day 1 ingestion complete. Next: run live_nav_fetch.py\n")
 
 
if __name__ == "__main__":
    main()