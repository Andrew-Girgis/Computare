-- ================================================================
-- Computare — Receipt Infrastructure
-- ================================================================
-- Adds receipt scanning, item-level categorization, and receipt-to-transaction linking.
-- Designed for grocery stores, retail, and any receipt-worthy purchase.
--
-- Key design decisions:
--   - 1 receipt can link to N transactions (split payments across cards)
--   - 1 transaction links to at most 1 receipt (enforced via UNIQUE)
--   - Orphan receipts allowed (cash/gift card purchases)
--   - Tax and discounts stored at receipt level (not per-item)
--   - Item-level category/sub_category uses same 13/33 taxonomy as transactions
--   - Receipt is source of truth for merchant name and date
--
-- Matching flow (implemented in application layer):
--   1. OCR extracts total, subtotal, date, merchant
--   2. Match by ABS(amount) = receipt.total AND date ±3 days
--   3. Fallback: try ABS(amount) = receipt.subtotal (tip added after)
--   4. Fallback: show user nearest candidates for manual linking
--   5. User can mark as cash/gift card purchase (no transaction link)
-- ================================================================

-- ============================================
-- 1. RECEIPTS TABLE
-- ============================================
CREATE TABLE receipts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    account_id UUID NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,

    -- File storage (Supabase Storage for now, migrate to R2/S3 later)
    image_path TEXT NOT NULL,
    ocr_raw_text TEXT,                          -- Raw OCR output for debugging
    ocr_structured_json JSONB,                  -- Parsed/structured extraction

    -- Merchant info (extracted from receipt — source of truth)
    merchant_name TEXT,
    store_address TEXT,

    -- Timing
    receipt_date DATE,
    receipt_time TIME,

    -- Financials (all receipt-level)
    subtotal NUMERIC(10,2),
    tax_amount NUMERIC(10,2),
    tip_amount NUMERIC(10,2),
    discount_amount NUMERIC(10,2),
    total NUMERIC(10,2),
    currency TEXT DEFAULT 'CAD',

    -- Payment info as shown on receipt
    payment_method_raw TEXT,

    -- Processing state
    match_status TEXT NOT NULL DEFAULT 'unmatched'
        CHECK (match_status IN ('auto_matched', 'manual_matched', 'unmatched', 'cash_purchase')),
    processing_status TEXT NOT NULL DEFAULT 'pending'
        CHECK (processing_status IN ('pending', 'ocr_complete', 'items_extracted', 'categorized', 'failed')),

    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_receipts_account ON receipts(account_id);
CREATE INDEX idx_receipts_date ON receipts(receipt_date);
CREATE INDEX idx_receipts_match_status ON receipts(match_status);
CREATE INDEX idx_receipts_processing_status ON receipts(processing_status);

-- ============================================
-- 2. RECEIPT ↔ TRANSACTION JUNCTION TABLE
-- ============================================
-- Supports split payments: 1 receipt paid across 2 cards = 2 rows.
-- UNIQUE on transaction_id enforces 1 transaction : at most 1 receipt.
CREATE TABLE receipt_transactions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    receipt_id UUID NOT NULL REFERENCES receipts(id) ON DELETE CASCADE,
    transaction_id UUID NOT NULL REFERENCES transactions(id) ON DELETE CASCADE,
    amount_attributed NUMERIC(10,2),

    created_at TIMESTAMPTZ DEFAULT NOW(),

    UNIQUE(receipt_id, transaction_id),
    UNIQUE(transaction_id)              -- Drop this constraint later if multi-receipt needed
);

CREATE INDEX idx_receipt_txn_receipt ON receipt_transactions(receipt_id);
CREATE INDEX idx_receipt_txn_transaction ON receipt_transactions(transaction_id);

-- ============================================
-- 3. RECEIPT ITEMS (line-level detail)
-- ============================================
-- Each item gets its own category/sub_category from the same 13/33 taxonomy.
-- A single Walmart receipt might have items in Groceries, Electronics, and Pet.
CREATE TABLE receipt_items (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    receipt_id UUID NOT NULL REFERENCES receipts(id) ON DELETE CASCADE,

    item_name_raw TEXT,                         -- Exactly as OCR'd
    item_name TEXT,                             -- Normalized/cleaned
    quantity NUMERIC(10,3) DEFAULT 1,           -- Supports fractional (kg produce)
    line_total NUMERIC(10,2) NOT NULL,

    -- Categorization (same taxonomy as transactions)
    category TEXT,
    sub_category TEXT,

    sort_order INT,                             -- Position on receipt

    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_receipt_items_receipt ON receipt_items(receipt_id);
CREATE INDEX idx_receipt_items_category ON receipt_items(category);
CREATE INDEX idx_receipt_items_sub_category ON receipt_items(sub_category);

-- ============================================
-- 4. ADD has_receipt FLAG TO TRANSACTIONS
-- ============================================
ALTER TABLE transactions ADD COLUMN has_receipt BOOLEAN DEFAULT FALSE;
CREATE INDEX idx_transactions_has_receipt ON transactions(has_receipt) WHERE has_receipt = TRUE;

-- ============================================
-- 5. ROW LEVEL SECURITY
-- ============================================
ALTER TABLE receipts ENABLE ROW LEVEL SECURITY;
ALTER TABLE receipt_transactions ENABLE ROW LEVEL SECURITY;
ALTER TABLE receipt_items ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Authenticated users can read receipts"
    ON receipts FOR SELECT TO authenticated USING (true);
CREATE POLICY "Authenticated users can read receipt_transactions"
    ON receipt_transactions FOR SELECT TO authenticated USING (true);
CREATE POLICY "Authenticated users can read receipt_items"
    ON receipt_items FOR SELECT TO authenticated USING (true);

-- ============================================
-- 6. TRIGGERS
-- ============================================

-- Auto-update receipts.updated_at on row change
CREATE OR REPLACE FUNCTION update_receipts_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql
SET search_path = public, pg_temp;

CREATE TRIGGER trigger_receipts_updated_at
    BEFORE UPDATE ON receipts
    FOR EACH ROW
    EXECUTE FUNCTION update_receipts_updated_at();

-- Auto-sync transactions.has_receipt when receipt links are created/removed
CREATE OR REPLACE FUNCTION sync_has_receipt()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        UPDATE transactions SET has_receipt = TRUE WHERE id = NEW.transaction_id;
        RETURN NEW;
    ELSIF TG_OP = 'DELETE' THEN
        UPDATE transactions SET has_receipt = FALSE WHERE id = OLD.transaction_id;
        RETURN OLD;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql
SET search_path = public, pg_temp;

CREATE TRIGGER trigger_sync_has_receipt
    AFTER INSERT OR DELETE ON receipt_transactions
    FOR EACH ROW
    EXECUTE FUNCTION sync_has_receipt();
