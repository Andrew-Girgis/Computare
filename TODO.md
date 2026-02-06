# Computare - TODO & Ideas

> Feature ideas, improvements, and technical debt tracking

---

## High Priority

### Portfolio Valuation Engine
- [ ] Build yfinance-based portfolio calculator
- [ ] Map WS symbols to yfinance tickers (NEO CDRs use `.NE` suffix)
- [ ] Track positions over time from transaction history
- [ ] Calculate unrealized gains/losses
- [ ] Handle FX conversion for USD positions
- [ ] Compare computed value vs actual WS balance

**Technical Notes:**
- NEO CDRs match closely: TSLA.NE (-0.1%), META.NE (-0.4%), NVDA.NE (-3.5%)
- US stocks need FX conversion (USD/CAD ~1.36)
- WS embeds ~1.5% spread in stock trades (not separately tracked)
- Crypto fees are explicit FEE transactions (~1.4%)

### Web Dashboard
- [ ] Next.js 15 + React 19 + Tailwind v4 + shadcn/ui
- [ ] Supabase Auth integration
- [ ] Transaction list with filters
- [ ] Spending by category charts
- [ ] Net worth timeline
- [ ] See `toasty-stirring-storm.md` plan file for full scaffolding details

---

## Medium Priority

### Tax Reporting
- [ ] Capital gains/losses calculation
- [ ] ACB (Adjusted Cost Base) tracking per symbol
- [ ] T5008 reconciliation helper
- [ ] Export to tax software format

### Budget Tracking
- [ ] Set monthly budgets per category
- [ ] Track spending vs budget
- [ ] Alerts when approaching/exceeding limits
- [ ] Rolling averages for variable categories

### Recurring Transaction Detection
- [ ] Identify subscriptions and recurring payments
- [ ] Group by merchant + amount pattern
- [ ] Track subscription costs over time
- [ ] Alert on price changes

### Net Worth Tracking
- [ ] Daily/weekly snapshots of all account balances
- [ ] Include investment market values
- [ ] Historical chart with milestones
- [ ] Asset allocation breakdown

---

## Low Priority / Nice to Have

### User-Defined Subcategories
- [ ] LLM-assisted subcategory proposals
- [ ] Custom subcategory creation UI
- [ ] Retroactive transaction updates
- [ ] Keyword-based auto-assignment
- See "Future Features" section in Project Overview for full spec

### Receipt Scanning
- [ ] OCR extraction from receipt photos
- [ ] Match to existing transactions
- [ ] Store receipt images in Supabase Storage
- [ ] Itemized purchase tracking

### Multi-Currency Support
- [ ] Track USD balances separately
- [ ] Historical FX rate lookups
- [ ] Currency conversion gains/losses

### Manual Transaction Entry
- [ ] Add/edit transactions manually via web UI
- [ ] Quick-add form (date, amount, merchant, category)
- [ ] Bulk import from spreadsheet (copy-paste or upload)

### Notification System
- [ ] Over-budget alerts (per category)
- [ ] Weekly/monthly spending summary digests
- [ ] Large transaction alerts (configurable threshold)
- [ ] Delivery: in-app notifications, email (Supabase Edge Functions)

### Financial Goals
- [ ] Monthly savings targets
- [ ] Emergency fund goal tracker
- [ ] Debt payoff targets with progress visualization
- [ ] Budget limits per category with rollover options

### Bank Connection (Plaid/Flinks)
- [ ] Auto-import transactions from connected accounts
- [ ] Real-time balance updates
- [ ] Reduced manual PDF/CSV processing

---

## Documentation

### YouTube Tutorials
- [ ] Create tutorial for each major feature (extraction, categorization, portfolio, dashboard)
- [ ] Setup guide walkthrough video (clone → configure → run)
- [ ] Web sign-up and onboarding walkthrough

### Setup Guide & CLI Wizard

Interactive terminal wizard (`computare setup`) that walks a new user through full configuration after cloning.

**Step 1 — Dependencies**
- [ ] Prompt: install Python + Node deps? (Yes → install via pip/pnpm, No → warn "required for local use; use the web app instead")

**Step 2 — Database**
- [ ] Prompt for Supabase project URL, anon key, service role key
- [ ] Validate connection and run migrations if needed

**Step 3 — AI Configuration**
- [ ] Option A: API key (OpenAI / Anthropic) → prompt for key → write to .env → validate
- [ ] Option B: Local model → offer Ollama download → confirm disk space → install + pull model
- [ ] Option C: No AI → warn "categorization limited to preset rules only — no personalized analysis or Tier 3 classification"

**Step 4 — Data Import**
- [ ] Option A: PDF bank statements → prompt for folder path or drag-and-drop
- [ ] Option B: CSV exports (Wealthsimple, Amex, etc.) → prompt for file paths
- [ ] Option C: Manual entry → open manual transaction entry UI (see new TODO below)
- [ ] Option D: Skip for now → warn "app needs transaction data to be useful"

**Step 5 — Run Pipeline**
- [ ] Execute extraction → normalization → DB load with progress indicators
- [ ] Show summary: X transactions imported, Y accounts detected

**Step 6 — Categories**
- [ ] Option A: AI-suggested personalized categories based on transaction history
- [ ] Option B: Preset defaults (current category set)
- [ ] Option C: Mix — start with presets, let AI suggest refinements

**Step 7 — User Profile**
- [ ] Name (for dashboard greeting & reports)
- [ ] Preferred currency (CAD / USD)
- [ ] Fiscal year start (calendar year vs custom)

**Step 8 — Financial Goals**
- [ ] Monthly savings target
- [ ] Emergency fund goal
- [ ] Debt payoff targets (credit cards, loans)
- [ ] Budget limits per category (or skip and set later in dashboard)

**Step 9 — Notification Preferences**
- [ ] Over-budget alerts
- [ ] Weekly/monthly spending summaries
- [ ] Large transaction alerts
- [ ] Delivery method: in-app, email, or both

**Step 10 — Summary & Launch**
- [ ] Recap all choices made
- [ ] Offer to start the web dashboard
- [ ] Link to YouTube tutorial playlist

**Web Onboarding**
- [ ] Web sign-up / onboarding flow (Supabase Auth) — mirrors wizard Steps 3-9 in a web UI

### Data Disclosure
- [ ] Create a data disclosure document covering Tier 3 categorisation (transaction descriptions sent to OpenAI GPT-4o-mini)
- [ ] Document what data is sent, when, and why (only uncategorised transactions that miss Tier 1 rules and Tier 2 merchant cache)
- [ ] Note that after initial categorisation, most transactions resolve from the local merchant cache at zero external calls
- [ ] Align with brand values: "Data ownership is non-negotiable" and "Transparency over convenience"

---

## Technical Debt

### Data Quality
- [ ] Fix early 2019 Scotiabank PDFs (33-78% confidence)
- [ ] Handle merchant name concatenation artifacts
- [ ] Reconcile negative positions (AC, ORAC) in investment data
- [ ] Investigate OPENL/W/Z spinoff warrants

### Code Improvements
- [ ] Add unit tests for extractors
- [ ] Type hints throughout codebase
- [ ] API documentation (FastAPI autodocs)
- [ ] Error handling improvements in parsers

### Database
- [ ] Enable RLS for multi-user support
- [ ] Optimize materialized view refresh
- [ ] Add indexes for common queries
- [ ] Partition transactions table by year

---

## Completed

- [x] PDF extraction for Scotiabank (chequing, credit card, investments)
- [x] CSV parsing for Wealthsimple (all account types)
- [x] CSV parsing for American Express
- [x] Supabase database schema
- [x] JSON → PostgreSQL loader
- [x] Transfer linking between accounts
- [x] LLM-based transaction categorization (GPT-4o-mini)
- [x] Merchant normalization rules
- [x] Category sync from DB to JSON files
- [x] Investment trade tracking with symbols/quantities

---

*Last updated: February 2026*
