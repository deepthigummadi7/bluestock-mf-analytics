DROP TABLE IF EXISTS fact_portfolio;
DROP TABLE IF EXISTS fact_performance;
DROP TABLE IF EXISTS fact_transactions;
DROP TABLE IF EXISTS fact_nav;
DROP TABLE IF EXISTS fact_aum;
DROP TABLE IF EXISTS fact_sip_industry;
DROP TABLE IF EXISTS fact_category_inflows;
DROP TABLE IF EXISTS fact_folio_count;
DROP TABLE IF EXISTS dim_date;
DROP TABLE IF EXISTS dim_fund;

CREATE TABLE dim_fund (
    amfi_code           INTEGER     PRIMARY KEY,
    fund_house          TEXT        NOT NULL,
    scheme_name         TEXT        NOT NULL,
    category            TEXT        NOT NULL,
    sub_category        TEXT,
    plan                TEXT,
    launch_date         DATE,
    benchmark           TEXT,
    expense_ratio_pct   REAL,
    exit_load_pct       REAL,
    min_sip_amount      INTEGER,
    min_lumpsum_amount  INTEGER,
    fund_manager        TEXT,
    risk_category       TEXT,
    sebi_category_code  TEXT
);

CREATE TABLE dim_date (
    date_id     TEXT    PRIMARY KEY,
    date        DATE    NOT NULL,
    year        INTEGER NOT NULL,
    month       INTEGER NOT NULL,
    quarter     INTEGER NOT NULL,
    month_name  TEXT    NOT NULL,
    day_of_week TEXT    NOT NULL,
    is_weekday  INTEGER NOT NULL
);

CREATE TABLE fact_nav (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    amfi_code           INTEGER NOT NULL REFERENCES dim_fund(amfi_code),
    date                DATE    NOT NULL,
    nav                 REAL    NOT NULL CHECK (nav > 0),
    daily_return_pct    REAL,
    UNIQUE (amfi_code, date)
);

CREATE TABLE fact_transactions (
    tx_id               INTEGER PRIMARY KEY AUTOINCREMENT,
    investor_id         TEXT    NOT NULL,
    transaction_date    DATE    NOT NULL,
    amfi_code           INTEGER NOT NULL REFERENCES dim_fund(amfi_code),
    transaction_type    TEXT    NOT NULL CHECK (transaction_type IN ('SIP','Lumpsum','Redemption')),
    amount_inr          INTEGER NOT NULL CHECK (amount_inr > 0),
    state               TEXT,
    city                TEXT,
    city_tier           TEXT    CHECK (city_tier IN ('T30','B30')),
    age_group           TEXT,
    gender              TEXT,
    annual_income_lakh  REAL,
    payment_mode        TEXT,
    kyc_status          TEXT    CHECK (kyc_status IN ('Verified','Pending'))
);

CREATE TABLE fact_performance (
    amfi_code           INTEGER PRIMARY KEY REFERENCES dim_fund(amfi_code),
    scheme_name         TEXT,
    fund_house          TEXT,
    category            TEXT,
    plan                TEXT,
    return_1yr_pct      REAL,
    return_3yr_pct      REAL,
    return_5yr_pct      REAL,
    benchmark_3yr_pct   REAL,
    alpha               REAL,
    beta                REAL,
    sharpe_ratio        REAL,
    sortino_ratio       REAL,
    std_dev_ann_pct     REAL,
    max_drawdown_pct    REAL,
    aum_crore           INTEGER,
    expense_ratio_pct   REAL,
    morningstar_rating  INTEGER,
    risk_grade          TEXT
);

CREATE TABLE fact_aum (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    date            DATE    NOT NULL,
    fund_house      TEXT    NOT NULL,
    aum_lakh_crore  REAL,
    aum_crore       INTEGER,
    num_schemes     INTEGER,
    UNIQUE (date, fund_house)
);

CREATE TABLE fact_sip_industry (
    month                       DATE    PRIMARY KEY,
    sip_inflow_crore            INTEGER,
    active_sip_accounts_crore   REAL,
    new_sip_accounts_lakh       REAL,
    sip_aum_lakh_crore          REAL,
    yoy_growth_pct              REAL
);

CREATE TABLE fact_category_inflows (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    month            DATE    NOT NULL,
    category         TEXT    NOT NULL,
    net_inflow_crore REAL,
    UNIQUE (month, category)
);

CREATE TABLE fact_folio_count (
    month                   DATE    PRIMARY KEY,
    total_folios_crore      REAL,
    equity_folios_crore     REAL,
    debt_folios_crore       REAL,
    hybrid_folios_crore     REAL,
    others_folios_crore     REAL
);

CREATE TABLE fact_portfolio (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    amfi_code           INTEGER NOT NULL REFERENCES dim_fund(amfi_code),
    stock_symbol        TEXT,
    stock_name          TEXT,
    sector              TEXT,
    weight_pct          REAL,
    market_value_cr     REAL,
    current_price_inr   REAL,
    portfolio_date      DATE,
    UNIQUE (amfi_code, stock_symbol, portfolio_date)
);

CREATE INDEX idx_nav_date       ON fact_nav(date);
CREATE INDEX idx_nav_fund       ON fact_nav(amfi_code);
CREATE INDEX idx_tx_date        ON fact_transactions(transaction_date);
CREATE INDEX idx_tx_fund        ON fact_transactions(amfi_code);
CREATE INDEX idx_tx_state       ON fact_transactions(state);
CREATE INDEX idx_tx_type        ON fact_transactions(transaction_type);
CREATE INDEX idx_perf_sharpe    ON fact_performance(sharpe_ratio);
CREATE INDEX idx_aum_date       ON fact_aum(date);
CREATE INDEX idx_portfolio_fund ON fact_portfolio(amfi_code);