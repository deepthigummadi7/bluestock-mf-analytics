-- Query 1: Top 5 funds by AUM
SELECT scheme_name, fund_house, aum_crore
FROM fact_performance
ORDER BY aum_crore DESC
LIMIT 5;

-- Query 2: Average NAV per month (SBI Bluechip)
SELECT strftime('%Y-%m', date) AS month, ROUND(AVG(nav), 2) AS avg_nav
FROM fact_nav
WHERE amfi_code = 119551
GROUP BY month
ORDER BY month;

-- Query 3: SIP inflow YoY growth (recent 5 months)
SELECT month, sip_inflow_crore, yoy_growth_pct
FROM fact_sip_industry
ORDER BY month DESC
LIMIT 5;

-- Query 4: Transactions by state (top 5)
SELECT state, COUNT(*) AS tx_count, SUM(amount_inr) AS total_amount
FROM fact_transactions
GROUP BY state
ORDER BY total_amount DESC
LIMIT 5;

-- Query 5: Funds with expense_ratio < 1%
SELECT scheme_name, fund_house, expense_ratio_pct
FROM dim_fund
WHERE expense_ratio_pct < 1.0
ORDER BY expense_ratio_pct;

-- Query 6: Top 5 funds by Sharpe ratio
SELECT scheme_name, fund_house, sharpe_ratio, return_3yr_pct
FROM fact_performance
ORDER BY sharpe_ratio DESC
LIMIT 5;

-- Query 7: SIP vs Lumpsum vs Redemption split
SELECT transaction_type, COUNT(*) AS tx_count, SUM(amount_inr) AS total_amount
FROM fact_transactions
GROUP BY transaction_type
ORDER BY total_amount DESC;

-- Query 8: AUM by fund house (latest quarter)
SELECT fund_house, aum_crore, num_schemes
FROM fact_aum
WHERE date = (SELECT MAX(date) FROM fact_aum)
ORDER BY aum_crore DESC;

-- Query 9: Category-wise net inflows (full period)
SELECT category, ROUND(SUM(net_inflow_crore), 2) AS total_inflow_crore
FROM fact_category_inflows
GROUP BY category
ORDER BY total_inflow_crore DESC;

-- Query 10: Average SIP amount by age group
SELECT age_group, COUNT(*) AS tx_count, ROUND(AVG(amount_inr), 2) AS avg_amount
FROM fact_transactions
WHERE transaction_type = 'SIP'
GROUP BY age_group
ORDER BY avg_amount DESC;