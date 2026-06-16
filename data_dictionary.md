# Bluestock MF — Data Dictionary

## dim_fund

**Source:** 01_fund_master.csv | **Rows:** 40

| Column             | Type         | Description                                               |
| ------------------ | ------------ | --------------------------------------------------------- |
| amfi_code          | INTEGER (PK) | Unique AMFI scheme code e.g. 125497 = HDFC Top 100 Direct |
| fund_house         | TEXT         | Asset Management Company name                             |
| scheme_name        | TEXT         | Full official AMFI scheme name                            |
| category           | TEXT         | Equity or Debt                                            |
| sub_category       | TEXT         | Large Cap / Mid Cap / Small Cap / Liquid / Gilt etc.      |
| plan               | TEXT         | Regular or Direct                                         |
| launch_date        | DATE         | Date the scheme was launched                              |
| benchmark          | TEXT         | Official benchmark index                                  |
| expense_ratio_pct  | REAL         | Annual expense ratio % (range 0.55–1.64%)                 |
| exit_load_pct      | REAL         | Exit load % (0 for Liquid/Index funds)                    |
| min_sip_amount     | INTEGER      | Minimum SIP investment in INR                             |
| min_lumpsum_amount | INTEGER      | Minimum lumpsum investment in INR                         |
| fund_manager       | TEXT         | Primary fund manager name                                 |
| risk_category      | TEXT         | Low / Moderate / Moderately High / High / Very High       |
| sebi_category_code | TEXT         | EC01=Large Cap, EC03=Small Cap, DC01=Liquid etc.          |

---

## dim_date

**Source:** Generated from fact_nav date range | **Rows:** 1,608

| Column      | Type      | Description              |
| ----------- | --------- | ------------------------ |
| date_id     | TEXT (PK) | YYYY-MM-DD format        |
| date        | DATE      | Calendar date            |
| year        | INTEGER   | Calendar year            |
| month       | INTEGER   | Month number 1–12        |
| quarter     | INTEGER   | Quarter 1–4              |
| month_name  | TEXT      | January, February etc.   |
| day_of_week | TEXT      | Monday, Tuesday etc.     |
| is_weekday  | INTEGER   | 1 = weekday, 0 = weekend |

---

## fact_nav

**Source:** 02_nav_history.csv | **Rows:** 46,000

| Column           | Type         | Description                                     |
| ---------------- | ------------ | ----------------------------------------------- |
| id               | INTEGER (PK) | Auto-increment row ID                           |
| amfi_code        | INTEGER (FK) | References dim_fund                             |
| date             | DATE         | NAV date (business days only)                   |
| nav              | REAL         | Net Asset Value in INR, validated > 0           |
| daily_return_pct | REAL         | Day-over-day % change, computed during cleaning |

**Notes:** No missing business days found. No duplicates or negative NAVs.

---

## fact_transactions

**Source:** 08_investor_transactions.csv | **Rows:** 32,778

| Column             | Type         | Description                                |
| ------------------ | ------------ | ------------------------------------------ |
| tx_id              | INTEGER (PK) | Auto-increment transaction ID              |
| investor_id        | TEXT         | INV000001 to INV005000                     |
| transaction_date   | DATE         | Date of the transaction                    |
| amfi_code          | INTEGER (FK) | References dim_fund                        |
| transaction_type   | TEXT         | SIP / Lumpsum / Redemption                 |
| amount_inr         | INTEGER      | Transaction amount in INR, validated > 0   |
| state              | TEXT         | Investor's Indian state                    |
| city               | TEXT         | Investor's city                            |
| city_tier          | TEXT         | T30 (Top 30 cities) or B30 (Beyond Top 30) |
| age_group          | TEXT         | 18-25 / 26-35 / 36-45 / 46-55 / 56+        |
| gender             | TEXT         | Male / Female                              |
| annual_income_lakh | REAL         | Annual income in INR lakh                  |
| payment_mode       | TEXT         | UPI / Net Banking / Mandate / Cheque       |
| kyc_status         | TEXT         | Verified (30,146) or Pending (2,632)       |

**Notes:** SIP=19,716 transactions, Lumpsum=8,095, Redemption=4,967.

---

## fact_performance

**Source:** 07_scheme_performance.csv | **Rows:** 40

| Column             | Type            | Description                                        |
| ------------------ | --------------- | -------------------------------------------------- |
| amfi_code          | INTEGER (PK/FK) | References dim_fund                                |
| return_1yr_pct     | REAL            | 1-year absolute return %                           |
| return_3yr_pct     | REAL            | 3-year CAGR %                                      |
| return_5yr_pct     | REAL            | 5-year CAGR %                                      |
| benchmark_3yr_pct  | REAL            | Benchmark 3yr CAGR for comparison                  |
| alpha              | REAL            | Excess return over benchmark                       |
| beta               | REAL            | Market sensitivity (1.0 = moves with market)       |
| sharpe_ratio       | REAL            | Risk-adjusted return, higher is better             |
| sortino_ratio      | REAL            | Like Sharpe but penalises only downside volatility |
| std_dev_ann_pct    | REAL            | Annualised standard deviation of daily returns %   |
| max_drawdown_pct   | REAL            | Worst peak-to-trough decline (negative value)      |
| aum_crore          | INTEGER         | Assets under management in INR crore               |
| expense_ratio_pct  | REAL            | Annual expense ratio %                             |
| morningstar_rating | INTEGER         | 1–5 star rating                                    |
| risk_grade         | TEXT            | SEBI risk category                                 |

**Notes:** Sharpe range 0.80–7.68. Expense ratios all within 0.1–2.5%. No anomalies.

---

## fact_aum

**Source:** 03_aum_by_fund_house.csv | **Rows:** 90

| Column         | Type         | Description                   |
| -------------- | ------------ | ----------------------------- |
| id             | INTEGER (PK) | Auto-increment                |
| date           | DATE         | Quarter-end date              |
| fund_house     | TEXT         | AMC name                      |
| aum_lakh_crore | REAL         | AUM in INR lakh crore         |
| aum_crore      | INTEGER      | AUM in INR crore              |
| num_schemes    | INTEGER      | Number of schemes by this AMC |

---

## fact_sip_industry

**Source:** 04_monthly_sip_inflows.csv | **Rows:** 48

| Column                    | Type      | Description                                        |
| ------------------------- | --------- | -------------------------------------------------- |
| month                     | DATE (PK) | YYYY-MM-01 format                                  |
| sip_inflow_crore          | INTEGER   | Total SIP inflows in INR crore                     |
| active_sip_accounts_crore | REAL      | Active SIP accounts in crore                       |
| new_sip_accounts_lakh     | REAL      | New SIP registrations in lakh                      |
| sip_aum_lakh_crore        | REAL      | Total SIP AUM in INR lakh crore                    |
| yoy_growth_pct            | REAL      | YoY growth % (NULL for first 12 months — expected) |

---

## fact_category_inflows

**Source:** 05_category_inflows.csv | **Rows:** 144

| Column           | Type         | Description                                          |
| ---------------- | ------------ | ---------------------------------------------------- |
| id               | INTEGER (PK) | Auto-increment                                       |
| month            | DATE         | YYYY-MM-01 format                                    |
| category         | TEXT         | Large Cap / Mid Cap / Small Cap / ELSS / Liquid etc. |
| net_inflow_crore | REAL         | Net inflow for that category that month in INR crore |

---

## fact_folio_count

**Source:** 06_industry_folio_count.csv | **Rows:** 21

| Column              | Type      | Description                            |
| ------------------- | --------- | -------------------------------------- |
| month               | DATE (PK) | Quarter date                           |
| total_folios_crore  | REAL      | Total MF folios industry-wide in crore |
| equity_folios_crore | REAL      | Equity scheme folios in crore          |
| debt_folios_crore   | REAL      | Debt scheme folios in crore            |
| hybrid_folios_crore | REAL      | Hybrid scheme folios in crore          |
| others_folios_crore | REAL      | Other scheme folios in crore           |

---

## fact_portfolio

**Source:** 09_portfolio_holdings.csv | **Rows:** 322

| Column            | Type         | Description                                 |
| ----------------- | ------------ | ------------------------------------------- |
| id                | INTEGER (PK) | Auto-increment                              |
| amfi_code         | INTEGER (FK) | References dim_fund                         |
| stock_symbol      | TEXT         | NSE/BSE ticker symbol                       |
| stock_name        | TEXT         | Full company name                           |
| sector            | TEXT         | Banking / IT / Utilities / Diversified etc. |
| weight_pct        | REAL         | Portfolio weight as %                       |
| market_value_cr   | REAL         | Market value in INR crore                   |
| current_price_inr | REAL         | Stock price in INR                          |
| portfolio_date    | DATE         | As of Dec 2025                              |

---

## Source Summary

| Table                 | Raw File                     | Source                         |
| --------------------- | ---------------------------- | ------------------------------ |
| dim_fund              | 01_fund_master.csv           | AMFI India scheme master       |
| fact_nav              | 02_nav_history.csv           | mfapi.in (real NAV anchors)    |
| fact_aum              | 03_aum_by_fund_house.csv     | AMFI quarterly reports         |
| fact_sip_industry     | 04_monthly_sip_inflows.csv   | AMFI Monthly Notes             |
| fact_category_inflows | 05_category_inflows.csv      | AMFI category flow data        |
| fact_folio_count      | 06_industry_folio_count.csv  | AMFI / Business Standard       |
| fact_performance      | 07_scheme_performance.csv    | Computed from NAV history      |
| fact_transactions     | 08_investor_transactions.csv | Synthetic (real distributions) |
| fact_portfolio        | 09_portfolio_holdings.csv    | Top holdings Dec 2025          |
