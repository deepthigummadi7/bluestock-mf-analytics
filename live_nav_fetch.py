"""
live_nav_fetch.py
-----------------
Day 1 Tasks 4 & 5: Fetch live NAV data from mfapi.in for 6 key schemes
and save each as a raw CSV under data/raw/.
 
Run from project root:
    python live_nav_fetch.py
 
API: https://api.mfapi.in/mf/{scheme_code}
Response schema:
    {
      "meta": { "fund_house": ..., "scheme_name": ..., ... },
      "data": [ {"date": "DD-MM-YYYY", "nav": "123.456"}, ... ]
    }
"""
 
import os
import time
import requests
import pandas as pd
from datetime import datetime
 
# ── Config ─────────────────────────────────────────────────────────────────────
RAW_DIR = os.path.join(os.path.dirname(__file__), "data", "raw")
os.makedirs(RAW_DIR, exist_ok=True)
 
BASE_URL = "https://api.mfapi.in/mf/{}"
REQUEST_DELAY = 1.0          # seconds between requests (be polite to the API)
REQUEST_TIMEOUT = 15         # seconds
 
# ── Scheme registry ────────────────────────────────────────────────────────────
# Task 4: HDFC Top 100 Direct
# Task 5: 5 key bluechip schemes
SCHEMES = {
    125497: "HDFC Top 100 Fund Direct",
    119551: "SBI Bluechip Fund",
    120503: "ICICI Pru Bluechip Fund",
    118632: "Nippon India Large Cap Fund",
    119092: "Axis Bluechip Fund",
    120841: "Kotak Bluechip Fund",
}
 
 
def fetch_nav(scheme_code: int) -> dict | None:
    """
    Fetch NAV history for one scheme.
    Returns the parsed JSON dict or None on failure.
    """
    url = BASE_URL.format(scheme_code)
    try:
        response = requests.get(
            url,
            timeout=REQUEST_TIMEOUT,
            headers={"User-Agent": "BluestockMF-Research/1.0"},
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        print(f"  ✗  HTTP error for {scheme_code}: {e}")
    except requests.exceptions.ConnectionError:
        print(f"  ✗  Connection failed for {scheme_code} — check network")
    except requests.exceptions.Timeout:
        print(f"  ✗  Timeout for {scheme_code}")
    except requests.exceptions.JSONDecodeError:
        print(f"  ✗  Invalid JSON for {scheme_code}")
    return None
 
 
def parse_to_dataframe(data: dict, scheme_code: int) -> pd.DataFrame:
    """Convert raw API response to a clean DataFrame."""
    meta = data.get("meta", {})
    nav_records = data.get("data", [])
 
    df = pd.DataFrame(nav_records)                        # columns: date, nav
    df["nav"]  = pd.to_numeric(df["nav"], errors="coerce")
    df["date"] = pd.to_datetime(df["date"], format="%d-%m-%Y", errors="coerce")
    df.sort_values("date", inplace=True)
    df.reset_index(drop=True, inplace=True)
 
    # Add metadata columns for traceability
    df.insert(0, "amfi_code",    scheme_code)
    df.insert(1, "scheme_name",  meta.get("scheme_name", ""))
    df.insert(2, "fund_house",   meta.get("fund_house",  ""))
    df.insert(3, "scheme_type",  meta.get("scheme_type", ""))
    df.insert(4, "scheme_category", meta.get("scheme_category", ""))
 
    return df
 
 
def print_summary(df: pd.DataFrame, scheme_code: int, scheme_label: str):
    """Print a concise profile of the fetched NAV data."""
    print(f"\n  ── {scheme_label} ({scheme_code}) ──")
    print(f"     Rows          : {len(df):,}")
    print(f"     Date range    : {df['date'].min().date()}  →  {df['date'].max().date()}")
    print(f"     Latest NAV    : ₹{df['nav'].iloc[-1]:.4f}  (as of {df['date'].iloc[-1].date()})")
    print(f"     NAV range     : ₹{df['nav'].min():.4f}  –  ₹{df['nav'].max():.4f}")
    print(f"     Null NAVs     : {df['nav'].isna().sum()}")
    print(f"     Sample:")
    print(df[["date", "nav"]].tail(3).to_string(index=False))
 
 
def main():
    print("\n" + "═" * 70)
    print("  BLUESTOCK MF — Live NAV Fetch  (mfapi.in)")
    print(f"  Run at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("═" * 70)
 
    fetched = []
    failed  = []
 
    for scheme_code, scheme_label in SCHEMES.items():
        print(f"\n  Fetching: {scheme_label} [{scheme_code}]")
        raw = fetch_nav(scheme_code)
 
        if raw is None:
            failed.append((scheme_code, scheme_label))
            continue
 
        df = parse_to_dataframe(raw, scheme_code)
        print_summary(df, scheme_code, scheme_label)
 
        # Save individual scheme CSV
        filename = f"live_nav_{scheme_code}.csv"
        save_path = os.path.join(RAW_DIR, filename)
        df.to_csv(save_path, index=False)
        print(f"     ✓ Saved → {save_path}")
 
        fetched.append((scheme_code, scheme_label, df))
 
        # Polite delay between requests
        if scheme_code != list(SCHEMES.keys())[-1]:
            time.sleep(REQUEST_DELAY)
 
    # ── Combine all successfully fetched schemes into one file ─────────────────
    if fetched:
        combined = pd.concat([df for _, _, df in fetched], ignore_index=True)
        combined_path = os.path.join(RAW_DIR, "live_nav_all_schemes.csv")
        combined.to_csv(combined_path, index=False)
        print(f"\n  ✓ Combined file saved → {combined_path}")
        print(f"    Total rows: {len(combined):,}  |  Schemes: {combined['amfi_code'].nunique()}")
 
    # ── Final report ───────────────────────────────────────────────────────────
    print("\n" + "─" * 70)
    print(f"  Fetched : {len(fetched)}/{len(SCHEMES)} schemes")
    if failed:
        print(f"  Failed  : {len(failed)} schemes")
        for code, label in failed:
            print(f"    • {code}  {label}")
    print("─" * 70 + "\n")
 
 
if __name__ == "__main__":
    main()