-- ================================================================
-- Computare — Initial Schema
-- ================================================================
-- Personal finance data extraction platform for Canadian banking.
-- Supports: Scotiabank, Wealthsimple, American Express.
--
-- Architecture:
--   13 top-level categories, 33 subcategories
--   3-tier categorization pipeline (description rules → merchant cache → LLM)
--   Materialized views for fast dashboard/agent queries
--   Row-level security for multi-user support
--
-- Tables: institutions, accounts, transactions, trade_details, holdings,
--         categories, statements, merchant_cache, subscriptions
-- ================================================================

-- ============================================
-- EXTENSIONS
-- ============================================
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================
-- 1. INSTITUTIONS
-- ============================================
CREATE TABLE institutions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL UNIQUE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_institutions_name ON institutions(name);

-- ============================================
-- 2. ACCOUNTS
-- ============================================
CREATE TABLE accounts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    institution_id UUID NOT NULL REFERENCES institutions(id) ON DELETE CASCADE,
    account_type TEXT NOT NULL,         -- chequing, credit_card, tfsa, rrsp, crypto, non_registered, spending
    name TEXT NOT NULL,                 -- "Scotiabank Chequing", "Wealthsimple TFSA"
    account_number_masked TEXT,         -- "****5080"
    currency TEXT DEFAULT 'CAD',
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),

    UNIQUE(institution_id, account_type, account_number_masked)
);

CREATE INDEX idx_accounts_institution ON accounts(institution_id);
CREATE INDEX idx_accounts_type ON accounts(account_type);
CREATE INDEX idx_accounts_active ON accounts(is_active);

-- ============================================
-- 3. SUBSCRIPTIONS
-- ============================================
-- Detected recurring charges. Created before transactions
-- so that transactions.subscription_id FK can reference it.
CREATE TABLE subscriptions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    -- Identity
    merchant TEXT NOT NULL,
    description TEXT,
    category TEXT,

    -- Billing
    current_amount DECIMAL(12,2),
    frequency TEXT NOT NULL CHECK (frequency IN ('weekly', 'bi-weekly', 'monthly', 'yearly')),
    billing_day INTEGER,

    -- Lifecycle
    started_at DATE NOT NULL,
    ended_at DATE,
    last_charged_at DATE NOT NULL,
    next_expected_at DATE,

    -- Status
    is_active BOOLEAN DEFAULT true,
    status TEXT DEFAULT 'detected' CHECK (status IN ('detected', 'confirmed', 'dismissed')),
    confidence DECIMAL(3,2),

    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_subscriptions_merchant ON subscriptions(merchant);
CREATE INDEX idx_subscriptions_active ON subscriptions(is_active);
CREATE INDEX idx_subscriptions_status ON subscriptions(status);
CREATE INDEX idx_subscriptions_category ON subscriptions(category);

-- ============================================
-- 4. TRANSACTIONS (unified for all account types)
-- ============================================
CREATE TABLE transactions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    account_id UUID NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    description TEXT NOT NULL,
    amount DECIMAL(12,2) NOT NULL,     -- Negative = outflow, Positive = inflow
    balance DECIMAL(12,2),             -- Running balance (nullable for credit cards)

    -- Type classification
    transaction_type TEXT NOT NULL CHECK (transaction_type IN ('credit', 'debit')),
    activity_type TEXT,                -- BUY, SELL, CONT, DIV, FEE, PURCHASE, PAYMENT, etc.

    -- Linked transaction (for transfers between accounts)
    linked_transaction_id UUID REFERENCES transactions(id),

    -- Merchant/location
    merchant TEXT,
    location TEXT,

    -- Categorization (13 categories + 33 subcategories, managed by Python pipeline)
    category TEXT,
    sub_category TEXT,

    -- Subscription link
    subscription_id UUID REFERENCES subscriptions(id),

    -- Source tracking
    source_file TEXT,
    raw_text TEXT,
    raw_data JSONB,                    -- Original parsed fields for AI agent access

    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_transactions_account ON transactions(account_id);
CREATE INDEX idx_transactions_date ON transactions(date);
CREATE INDEX idx_transactions_type ON transactions(transaction_type);
CREATE INDEX idx_transactions_activity ON transactions(activity_type);
CREATE INDEX idx_transactions_category ON transactions(category);
CREATE INDEX idx_transactions_linked ON transactions(linked_transaction_id);
CREATE INDEX idx_transactions_amount ON transactions(amount);
CREATE INDEX idx_transactions_subscription ON transactions(subscription_id);
CREATE INDEX idx_transactions_raw_data ON transactions USING GIN (raw_data);

-- ============================================
-- 5. TRADE DETAILS (investment-specific data)
-- ============================================
CREATE TABLE trade_details (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    transaction_id UUID UNIQUE NOT NULL REFERENCES transactions(id) ON DELETE CASCADE,
    symbol TEXT NOT NULL,               -- NVDA, BTC, ETH
    quantity DECIMAL(18,8),             -- Supports crypto precision
    unit_price DECIMAL(12,4),
    currency TEXT DEFAULT 'CAD',
    fx_rate DECIMAL(10,6),

    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_trade_details_symbol ON trade_details(symbol);
CREATE INDEX idx_trade_details_transaction ON trade_details(transaction_id);

-- ============================================
-- 6. HOLDINGS (point-in-time portfolio snapshot)
-- ============================================
CREATE TABLE holdings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    account_id UUID NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,
    symbol TEXT NOT NULL,
    quantity DECIMAL(18,8) NOT NULL,
    cost_basis DECIMAL(12,2),
    as_of_date DATE NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),

    UNIQUE(account_id, symbol, as_of_date)
);

CREATE INDEX idx_holdings_account ON holdings(account_id);
CREATE INDEX idx_holdings_symbol ON holdings(symbol);
CREATE INDEX idx_holdings_date ON holdings(as_of_date);

-- ============================================
-- 7. CATEGORIES (13 parents + 33 subcategories)
-- ============================================
-- UI metadata for categories and subcategories.
-- Categorization logic lives in the Python pipeline (computare/categorizer/),
-- this table provides colors and icons for the frontend.
CREATE TABLE categories (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL UNIQUE,
    parent_id UUID REFERENCES categories(id),
    color TEXT,
    icon TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_categories_parent ON categories(parent_id);

-- 13 top-level categories
INSERT INTO categories (name, color) VALUES
    ('Food & Dining',          '#FF6B6B'),
    ('Transportation',         '#4ECDC4'),
    ('Retail & Shopping',      '#45B7D1'),
    ('Bills & Utilities',      '#FFEAA7'),
    ('Healthcare',             '#E84393'),
    ('Entertainment',          '#96CEB4'),
    ('Housing',                '#FFD93D'),
    ('Income',                 '#6BCB77'),
    ('Transfers',              '#B07CC6'),
    ('Investment',             '#9B59B6'),
    ('Education',              '#3498DB'),
    ('Personal Care',          '#E91E63'),
    ('AI & Software Services', '#00BCD4');

-- 33 subcategories (parent_id references above)
-- Food & Dining (5)
INSERT INTO categories (name, parent_id, color) VALUES
    ('Coffee & Cafes',      (SELECT id FROM categories WHERE name = 'Food & Dining'), '#8D6E63'),
    ('Fast Food',           (SELECT id FROM categories WHERE name = 'Food & Dining'), '#FF5252'),
    ('Restaurants',         (SELECT id FROM categories WHERE name = 'Food & Dining'), '#D32F2F'),
    ('Delivery',            (SELECT id FROM categories WHERE name = 'Food & Dining'), '#FF8A65'),
    ('Convenience',         (SELECT id FROM categories WHERE name = 'Food & Dining'), '#FFAB91');

-- Transportation (4)
INSERT INTO categories (name, parent_id, color) VALUES
    ('Gas & Fuel',          (SELECT id FROM categories WHERE name = 'Transportation'), '#FF9800'),
    ('Parking',             (SELECT id FROM categories WHERE name = 'Transportation'), '#26A69A'),
    ('Ride-hailing',        (SELECT id FROM categories WHERE name = 'Transportation'), '#80CBC4'),
    ('Auto Maintenance',    (SELECT id FROM categories WHERE name = 'Transportation'), '#009688');

-- Retail & Shopping (8)
INSERT INTO categories (name, parent_id, color) VALUES
    ('Groceries',           (SELECT id FROM categories WHERE name = 'Retail & Shopping'), '#4CAF50'),
    ('Alcohol',             (SELECT id FROM categories WHERE name = 'Retail & Shopping'), '#795548'),
    ('Clothing',            (SELECT id FROM categories WHERE name = 'Retail & Shopping'), '#5C6BC0'),
    ('Electronics',         (SELECT id FROM categories WHERE name = 'Retail & Shopping'), '#29B6F6'),
    ('Online/General',      (SELECT id FROM categories WHERE name = 'Retail & Shopping'), '#42A5F5'),
    ('Dollar/Discount',     (SELECT id FROM categories WHERE name = 'Retail & Shopping'), '#66BB6A'),
    ('Home',                (SELECT id FROM categories WHERE name = 'Retail & Shopping'), '#A1887F'),
    ('Pet',                 (SELECT id FROM categories WHERE name = 'Retail & Shopping'), '#FF7043');

-- Bills & Utilities (5)
INSERT INTO categories (name, parent_id, color) VALUES
    ('Bank Fees',           (SELECT id FROM categories WHERE name = 'Bills & Utilities'), '#FFC107'),
    ('Phone Bill',          (SELECT id FROM categories WHERE name = 'Bills & Utilities'), '#FFD54F'),
    ('Utilities',           (SELECT id FROM categories WHERE name = 'Bills & Utilities'), '#FFB300'),
    ('Insurance',           (SELECT id FROM categories WHERE name = 'Bills & Utilities'), '#FFE082'),
    ('Loan Payments',       (SELECT id FROM categories WHERE name = 'Bills & Utilities'), '#F9A825');

-- Healthcare (5)
INSERT INTO categories (name, parent_id, color) VALUES
    ('Pharmacy',            (SELECT id FROM categories WHERE name = 'Healthcare'), '#F06292'),
    ('Physio & Rehab',      (SELECT id FROM categories WHERE name = 'Healthcare'), '#EC407A'),
    ('Medical',             (SELECT id FROM categories WHERE name = 'Healthcare'), '#AD1457'),
    ('Optometry',           (SELECT id FROM categories WHERE name = 'Healthcare'), '#F48FB1'),
    ('Other',               (SELECT id FROM categories WHERE name = 'Healthcare'), '#CE93D8');

-- Entertainment (5)
INSERT INTO categories (name, parent_id, color) VALUES
    ('Gaming',              (SELECT id FROM categories WHERE name = 'Entertainment'), '#9C27B0'),
    ('Movies',              (SELECT id FROM categories WHERE name = 'Entertainment'), '#7E57C2'),
    ('Streaming',           (SELECT id FROM categories WHERE name = 'Entertainment'), '#AB47BC'),
    ('Activities/Venues',   (SELECT id FROM categories WHERE name = 'Entertainment'), '#81C784'),
    ('Events',              (SELECT id FROM categories WHERE name = 'Entertainment'), '#AED581');

-- Housing (1)
INSERT INTO categories (name, parent_id, color) VALUES
    ('Home Maintenance',    (SELECT id FROM categories WHERE name = 'Housing'), '#FBC02D');

-- ============================================
-- 8. STATEMENTS (audit trail for imported files)
-- ============================================
CREATE TABLE statements (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    account_id UUID NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,
    file_name TEXT NOT NULL,
    year INTEGER NOT NULL CHECK (year >= 2000 AND year <= 2100),
    month INTEGER NOT NULL CHECK (month >= 1 AND month <= 12),
    opening_balance DECIMAL(12,2),
    closing_balance DECIMAL(12,2),
    total_debits DECIMAL(12,2),
    total_credits DECIMAL(12,2),
    transaction_count INTEGER,
    confidence DECIMAL(5,4),
    imported_at TIMESTAMPTZ DEFAULT NOW(),

    UNIQUE(account_id, year, month)
);

CREATE INDEX idx_statements_account ON statements(account_id);
CREATE INDEX idx_statements_date ON statements(year, month);

-- ============================================
-- 9. MERCHANT CACHE (AI categorization pipeline)
-- ============================================
-- Caches normalized merchant names + categories to avoid repeat LLM calls.
-- The 3-tier pipeline: description rules → merchant cache → LLM.
CREATE TABLE merchant_cache (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    raw_store TEXT NOT NULL,
    normalized_merchant TEXT NOT NULL,
    category TEXT NOT NULL,
    sub_category TEXT,
    confidence DECIMAL(3,2) DEFAULT 1.0,
    source TEXT DEFAULT 'llm',         -- llm, manual, rule
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE UNIQUE INDEX idx_merchant_cache_raw ON merchant_cache(raw_store);
CREATE INDEX idx_merchant_cache_merchant ON merchant_cache(normalized_merchant);
CREATE INDEX idx_merchant_cache_category ON merchant_cache(category);

-- ============================================
-- 10. MATERIALIZED VIEWS
-- ============================================
-- Pre-computed summaries refreshed after data loads.
-- Use refresh_all_summaries() to update.

-- Monthly spending breakdown by category
CREATE MATERIALIZED VIEW monthly_spending_by_category AS
SELECT
    DATE_TRUNC('month', t.date)::DATE as month,
    t.category,
    SUM(CASE WHEN t.amount < 0 THEN ABS(t.amount) ELSE 0 END) as spent,
    SUM(CASE WHEN t.amount > 0 THEN t.amount ELSE 0 END) as received,
    COUNT(*) as transaction_count,
    ROUND(AVG(CASE WHEN t.amount < 0 THEN ABS(t.amount) END), 2) as avg_transaction
FROM transactions t
JOIN accounts a ON t.account_id = a.id
WHERE a.account_type IN ('chequing', 'credit_card', 'spending')
  AND t.linked_transaction_id IS NULL
GROUP BY 1, 2
ORDER BY 1 DESC, 3 DESC
WITH NO DATA;

CREATE UNIQUE INDEX idx_mv_monthly_cat ON monthly_spending_by_category(month, category);

-- Monthly spending by account
CREATE MATERIALIZED VIEW monthly_spending_by_account AS
SELECT
    DATE_TRUNC('month', t.date)::DATE as month,
    a.name as account_name,
    a.account_type,
    SUM(CASE WHEN t.amount < 0 THEN ABS(t.amount) ELSE 0 END) as spent,
    SUM(CASE WHEN t.amount > 0 THEN t.amount ELSE 0 END) as received,
    SUM(t.amount) as net,
    COUNT(*) as transaction_count
FROM transactions t
JOIN accounts a ON t.account_id = a.id
GROUP BY 1, 2, 3
ORDER BY 1 DESC, 2
WITH NO DATA;

CREATE UNIQUE INDEX idx_mv_monthly_acct ON monthly_spending_by_account(month, account_name);

-- Yearly summary
CREATE MATERIALIZED VIEW yearly_summary AS
SELECT
    EXTRACT(YEAR FROM t.date)::INTEGER as year,
    a.name as account_name,
    SUM(CASE WHEN t.amount < 0 THEN ABS(t.amount) ELSE 0 END) as total_spent,
    SUM(CASE WHEN t.amount > 0 THEN t.amount ELSE 0 END) as total_received,
    SUM(t.amount) as net,
    COUNT(*) as transaction_count
FROM transactions t
JOIN accounts a ON t.account_id = a.id
GROUP BY 1, 2
ORDER BY 1 DESC, 2
WITH NO DATA;

CREATE UNIQUE INDEX idx_mv_yearly ON yearly_summary(year, account_name);

-- Net worth timeline
CREATE MATERIALIZED VIEW net_worth_timeline AS
SELECT
    t.date,
    SUM(CASE
        WHEN a.account_type = 'credit_card' THEN -COALESCE(t.balance, 0)
        ELSE COALESCE(t.balance, 0)
    END) as net_worth,
    COUNT(DISTINCT a.id) as accounts_with_data
FROM transactions t
JOIN accounts a ON t.account_id = a.id
WHERE t.balance IS NOT NULL
GROUP BY t.date
ORDER BY t.date
WITH NO DATA;

CREATE UNIQUE INDEX idx_mv_networth ON net_worth_timeline(date);

-- Investment activity summary
CREATE MATERIALIZED VIEW investment_activity AS
SELECT
    a.name as account_name,
    td.symbol,
    t.activity_type,
    SUM(td.quantity) as total_quantity,
    SUM(ABS(t.amount)) as total_value,
    COUNT(*) as trade_count
FROM transactions t
JOIN trade_details td ON t.id = td.transaction_id
JOIN accounts a ON t.account_id = a.id
GROUP BY 1, 2, 3
ORDER BY 1, 2, 3
WITH NO DATA;

CREATE UNIQUE INDEX idx_mv_invest ON investment_activity(account_name, symbol, activity_type);

-- Current portfolio holdings
CREATE MATERIALIZED VIEW current_holdings AS
SELECT DISTINCT ON (h.account_id, h.symbol)
    h.account_id,
    a.name as account_name,
    i.name as institution,
    h.symbol,
    h.quantity,
    h.cost_basis,
    h.as_of_date
FROM holdings h
JOIN accounts a ON h.account_id = a.id
JOIN institutions i ON a.institution_id = i.id
WHERE h.quantity > 0
ORDER BY h.account_id, h.symbol, h.as_of_date DESC
WITH NO DATA;

CREATE UNIQUE INDEX idx_mv_holdings ON current_holdings(account_id, symbol);

-- Transfer summary
CREATE MATERIALIZED VIEW transfer_summary AS
SELECT
    t1.id as transaction_id,
    t1.date,
    a1.name as from_account,
    a2.name as to_account,
    ABS(t1.amount) as amount,
    t1.description as from_description,
    t2.description as to_description
FROM transactions t1
JOIN transactions t2 ON t1.linked_transaction_id = t2.id
JOIN accounts a1 ON t1.account_id = a1.id
JOIN accounts a2 ON t2.account_id = a2.id
WHERE t1.amount < 0
ORDER BY t1.date DESC
WITH NO DATA;

CREATE UNIQUE INDEX idx_mv_transfers ON transfer_summary(transaction_id);

-- Merchant summary (top merchants, frequency, avg spend)
CREATE MATERIALIZED VIEW merchant_summary AS
SELECT
    COALESCE(t.merchant, t.description) as merchant_name,
    t.category,
    COUNT(*) as transaction_count,
    SUM(ABS(t.amount)) as total_spent,
    ROUND(AVG(ABS(t.amount)), 2) as avg_amount,
    MIN(t.date) as first_seen,
    MAX(t.date) as last_seen
FROM transactions t
JOIN accounts a ON t.account_id = a.id
WHERE t.amount < 0
  AND a.account_type IN ('chequing', 'credit_card', 'spending')
GROUP BY 1, 2
ORDER BY 4 DESC
WITH NO DATA;

CREATE UNIQUE INDEX idx_mv_merchant ON merchant_summary(merchant_name, category);

-- Category trends (month-over-month changes)
CREATE MATERIALIZED VIEW category_trends AS
SELECT
    curr.month,
    curr.category,
    curr.spent as current_spent,
    prev.spent as previous_spent,
    CASE
        WHEN prev.spent > 0 THEN ROUND(((curr.spent - prev.spent) / prev.spent) * 100, 1)
        ELSE NULL
    END as pct_change,
    curr.spent - COALESCE(prev.spent, 0) as absolute_change,
    curr.transaction_count
FROM (
    SELECT
        DATE_TRUNC('month', t.date)::DATE as month,
        t.category,
        SUM(CASE WHEN t.amount < 0 THEN ABS(t.amount) ELSE 0 END) as spent,
        COUNT(*) as transaction_count
    FROM transactions t
    JOIN accounts a ON t.account_id = a.id
    WHERE a.account_type IN ('chequing', 'credit_card', 'spending')
      AND t.linked_transaction_id IS NULL
    GROUP BY 1, 2
) curr
LEFT JOIN (
    SELECT
        DATE_TRUNC('month', t.date)::DATE as month,
        t.category,
        SUM(CASE WHEN t.amount < 0 THEN ABS(t.amount) ELSE 0 END) as spent
    FROM transactions t
    JOIN accounts a ON t.account_id = a.id
    WHERE a.account_type IN ('chequing', 'credit_card', 'spending')
      AND t.linked_transaction_id IS NULL
    GROUP BY 1, 2
) prev ON curr.category = prev.category
       AND prev.month = (curr.month - INTERVAL '1 month')::DATE
ORDER BY curr.month DESC, curr.spent DESC
WITH NO DATA;

CREATE UNIQUE INDEX idx_mv_trends ON category_trends(month, category);

-- ============================================
-- 11. SUBSCRIPTION VIEWS (regular — small dataset, always fast)
-- ============================================

-- Active subscriptions with charge stats
CREATE VIEW active_subscriptions AS
SELECT
    s.id,
    s.merchant,
    s.description,
    s.category,
    s.current_amount,
    s.frequency,
    s.billing_day,
    s.started_at,
    s.last_charged_at,
    s.next_expected_at,
    s.confidence,
    s.status,
    COUNT(t.id) as charge_count,
    SUM(ABS(t.amount)) as total_spent
FROM subscriptions s
LEFT JOIN transactions t ON t.subscription_id = s.id
WHERE s.is_active = true
  AND s.status != 'dismissed'
GROUP BY s.id
ORDER BY s.current_amount DESC;

-- Full subscription history with lifetime stats
CREATE VIEW subscription_history AS
SELECT
    s.id,
    s.merchant,
    s.description,
    s.category,
    s.current_amount,
    s.frequency,
    s.started_at,
    s.ended_at,
    s.last_charged_at,
    s.is_active,
    s.status,
    s.confidence,
    COUNT(t.id) as charge_count,
    SUM(ABS(t.amount)) as total_spent,
    MIN(ABS(t.amount)) as min_amount,
    MAX(ABS(t.amount)) as max_amount,
    EXTRACT(YEAR FROM AGE(COALESCE(s.ended_at, CURRENT_DATE), s.started_at)) * 12 +
    EXTRACT(MONTH FROM AGE(COALESCE(s.ended_at, CURRENT_DATE), s.started_at)) as months_active
FROM subscriptions s
LEFT JOIN transactions t ON t.subscription_id = s.id
GROUP BY s.id
ORDER BY s.is_active DESC, s.last_charged_at DESC;

-- Monthly subscription burn rate
CREATE VIEW monthly_subscription_cost AS
SELECT
    SUM(CASE
        WHEN frequency = 'monthly' THEN ABS(current_amount)
        WHEN frequency = 'yearly' THEN ABS(current_amount) / 12
        WHEN frequency = 'weekly' THEN ABS(current_amount) * 4.33
        WHEN frequency = 'bi-weekly' THEN ABS(current_amount) * 2.17
    END) as monthly_total,
    COUNT(*) as active_count
FROM subscriptions
WHERE is_active = true
  AND status != 'dismissed';

-- ============================================
-- 12. HELPER FUNCTIONS
-- ============================================

-- Get account balance at a specific date
CREATE OR REPLACE FUNCTION get_account_balance(p_account_id UUID, p_date DATE)
RETURNS DECIMAL AS $$
    SELECT COALESCE(
        (SELECT balance
         FROM transactions
         WHERE account_id = p_account_id
           AND date <= p_date
           AND balance IS NOT NULL
         ORDER BY date DESC, created_at DESC
         LIMIT 1),
        0
    );
$$ LANGUAGE SQL STABLE
SET search_path = public, pg_temp;

-- Get total balance across all accounts at a date
CREATE OR REPLACE FUNCTION get_total_balance(p_date DATE)
RETURNS DECIMAL AS $$
    SELECT COALESCE(SUM(
        CASE
            WHEN a.account_type = 'credit_card' THEN -get_account_balance(a.id, p_date)
            ELSE get_account_balance(a.id, p_date)
        END
    ), 0)
    FROM accounts a
    WHERE a.is_active = true;
$$ LANGUAGE SQL STABLE
SET search_path = public, pg_temp;

-- Calculate holdings from trade history
CREATE OR REPLACE FUNCTION calculate_holdings(p_account_id UUID, p_as_of_date DATE)
RETURNS TABLE(symbol TEXT, quantity DECIMAL, cost_basis DECIMAL) AS $$
    SELECT
        td.symbol,
        SUM(CASE
            WHEN t.activity_type IN ('BUY', 'CONT') THEN td.quantity
            WHEN t.activity_type = 'SELL' THEN -td.quantity
            ELSE 0
        END) as quantity,
        SUM(CASE
            WHEN t.activity_type IN ('BUY', 'CONT') THEN ABS(t.amount)
            ELSE 0
        END) as cost_basis
    FROM transactions t
    JOIN trade_details td ON t.id = td.transaction_id
    WHERE t.account_id = p_account_id
      AND t.date <= p_as_of_date
    GROUP BY td.symbol
    HAVING SUM(CASE
            WHEN t.activity_type IN ('BUY', 'CONT') THEN td.quantity
            WHEN t.activity_type = 'SELL' THEN -td.quantity
            ELSE 0
        END) > 0;
$$ LANGUAGE SQL STABLE
SET search_path = public, pg_temp;

-- Refresh all materialized views (call after data loads)
CREATE OR REPLACE FUNCTION refresh_all_summaries()
RETURNS void AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY monthly_spending_by_category;
    REFRESH MATERIALIZED VIEW CONCURRENTLY monthly_spending_by_account;
    REFRESH MATERIALIZED VIEW CONCURRENTLY yearly_summary;
    REFRESH MATERIALIZED VIEW CONCURRENTLY net_worth_timeline;
    REFRESH MATERIALIZED VIEW CONCURRENTLY merchant_summary;
    REFRESH MATERIALIZED VIEW CONCURRENTLY category_trends;
    REFRESH MATERIALIZED VIEW CONCURRENTLY investment_activity;
    REFRESH MATERIALIZED VIEW CONCURRENTLY current_holdings;
    REFRESH MATERIALIZED VIEW CONCURRENTLY transfer_summary;
END;
$$ LANGUAGE plpgsql
SET search_path = public, pg_temp;

-- ============================================
-- 13. ROW LEVEL SECURITY
-- ============================================
-- RLS restricts which rows a user can access.
-- With RLS enabled but no policies, the anon key sees NOTHING.
-- The service_role key always bypasses RLS (backend loader).
-- For now: authenticated users can read everything.
-- Scope to auth.uid() when adding multi-user support.

ALTER TABLE institutions ENABLE ROW LEVEL SECURITY;
ALTER TABLE accounts ENABLE ROW LEVEL SECURITY;
ALTER TABLE transactions ENABLE ROW LEVEL SECURITY;
ALTER TABLE trade_details ENABLE ROW LEVEL SECURITY;
ALTER TABLE holdings ENABLE ROW LEVEL SECURITY;
ALTER TABLE categories ENABLE ROW LEVEL SECURITY;
ALTER TABLE statements ENABLE ROW LEVEL SECURITY;
ALTER TABLE merchant_cache ENABLE ROW LEVEL SECURITY;
ALTER TABLE subscriptions ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Authenticated users can read institutions"
    ON institutions FOR SELECT TO authenticated USING (true);
CREATE POLICY "Authenticated users can read accounts"
    ON accounts FOR SELECT TO authenticated USING (true);
CREATE POLICY "Authenticated users can read transactions"
    ON transactions FOR SELECT TO authenticated USING (true);
CREATE POLICY "Authenticated users can read trade_details"
    ON trade_details FOR SELECT TO authenticated USING (true);
CREATE POLICY "Authenticated users can read holdings"
    ON holdings FOR SELECT TO authenticated USING (true);
CREATE POLICY "Authenticated users can read categories"
    ON categories FOR SELECT TO authenticated USING (true);
CREATE POLICY "Authenticated users can read statements"
    ON statements FOR SELECT TO authenticated USING (true);
CREATE POLICY "Authenticated users can read merchant_cache"
    ON merchant_cache FOR SELECT TO authenticated USING (true);
CREATE POLICY "Authenticated users can read subscriptions"
    ON subscriptions FOR SELECT TO authenticated USING (true);

-- Set security_invoker on regular views so RLS is respected
ALTER VIEW active_subscriptions SET (security_invoker = on);
ALTER VIEW subscription_history SET (security_invoker = on);
ALTER VIEW monthly_subscription_cost SET (security_invoker = on);
