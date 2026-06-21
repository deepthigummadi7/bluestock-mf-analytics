"""
recommender.py
--------------
Day 6: Simple fund recommender based on investor risk appetite.
Run: python recommender.py
"""

import pandas as pd
import os

os.chdir(os.path.dirname(os.path.abspath(__file__)))

fm   = pd.read_csv('data/processed/clean_fund_master.csv')
perf = pd.read_csv('data/processed/clean_scheme_performance.csv')

RISK_MAP = {
    'Low'     : ['Low'],
    'Moderate': ['Moderate', 'Moderately High'],
    'High'    : ['High', 'Very High'],
}

def recommend_funds(risk_appetite: str) -> pd.DataFrame:
    grades   = RISK_MAP.get(risk_appetite, [])
    eligible = fm[fm['risk_category'].isin(grades)]['amfi_code'].tolist()
    result   = (perf[perf['amfi_code'].isin(eligible)]
                .sort_values('sharpe_ratio', ascending=False)
                .head(3)[['scheme_name','sharpe_ratio','return_3yr_pct',
                           'max_drawdown_pct','expense_ratio_pct']])
    return result

def main():
    print("\nBluestock MF — Fund Recommender")
    print("=" * 60)
    appetite = input("Enter risk appetite (Low / Moderate / High): ").strip().capitalize()
    if appetite not in RISK_MAP:
        print("Invalid input. Choose: Low, Moderate, or High")
        return

    print(f"\nTop 3 Funds for {appetite} Risk Investor:")
    print("-" * 60)
    result = recommend_funds(appetite)
    for i, (_, row) in enumerate(result.iterrows(), 1):
        print(f"\n  {i}. {row['scheme_name']}")
        print(f"     Sharpe Ratio  : {row['sharpe_ratio']:.2f}")
        print(f"     3yr Return    : {row['return_3yr_pct']:.1f}%")
        print(f"     Max Drawdown  : {row['max_drawdown_pct']:.1f}%")
        print(f"     Expense Ratio : {row['expense_ratio_pct']:.2f}%")
    print()

if __name__ == "__main__":
    main()