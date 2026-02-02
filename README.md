# Computare

Open-source personal finance platform that extracts transactions from Canadian bank statements, categorizes them with AI, detects recurring subscriptions, and stores everything in a structured PostgreSQL database.

Built for Scotiabank, Wealthsimple, and American Express &mdash; with an architecture designed to support additional institutions.

## Architecture

```
DATA SOURCES                         EXTRACTION LAYER
 Scotiabank PDFs ──┐                ┌─ pdfplumber (fast, local)
 Wealthsimple CSVs ┼───────────────┤
 American Express CSVs ┘            └─ Claude AI (vision fallback)
                                              │
                                              ▼
                                     CATEGORIZATION
                                    ┌─ Tier 1: Description rules (free)
                                    ├─ Tier 2: Merchant cache (free)
                                    └─ Tier 3: GPT-4o-mini (batched)
                                              │
                                              ▼
                                      Supabase (PostgreSQL)
                                     ┌────────────────────┐
                                     │ institutions       │
                                     │ accounts           │
                                     │ transactions       │
                                     │ categories (13+33) │
                                     │ subscriptions      │
                                     │ receipts           │
                                     │ merchant_cache     │
                                     │ 9 materialized     │
                                     │   views            │
                                     └────────────────────┘
                                              │
                                              ▼
                                     FastAPI REST API
                                     /categorize
                                     /merchants
                                     /categories
                                     /health
```

## Features

- **PDF extraction** for Scotiabank chequing, credit card, and iTRADE investment statements using position-based word extraction
- **CSV parsing** for all Wealthsimple account types (TFSA, Spending, Credit Card, Crypto) and American Express year-end summaries
- **3-tier AI categorization** into 13 categories and 33 subcategories: description rules -> merchant cache -> GPT-4o-mini. After initial run, most transactions resolve from cache at zero cost
- **Subscription detection** algorithm that identifies recurring charges by merchant, frequency, and amount regularity
- **Receipt infrastructure** (schema ready, OCR pipeline planned) with split-payment support, item-level categorization, and orphan receipt handling
- **Transfer linking** between accounts (e.g., chequing outflow matched to TFSA contribution)
- **Hybrid extraction** with confidence scoring &mdash; falls back to Claude AI vision when pdfplumber confidence drops below threshold
- **Materialized views** for fast dashboard queries: monthly spending, yearly summaries, net worth timeline, portfolio holdings
- **Row Level Security** enabled on all tables

## Project Structure

```
computare/
├── extractors/           # PDF extraction (pdfplumber, Claude AI, bank-specific)
├── parsers/              # CSV parsers (Wealthsimple)
├── categorizer/          # 3-tier categorization pipeline (LangChain + GPT-4o-mini)
├── subscriptions/        # Recurring charge detection
├── database/             # Supabase loader and transfer linker
├── api/                  # FastAPI REST API
│   └── routes/           # /categorize, /merchants, /categories, /health
├── models.py             # Transaction, ExtractionResult dataclasses
├── validators.py         # Balance reconciliation and validation
├── batch_processor.py    # Multi-PDF batch processing
└── config.py             # Environment-based configuration

scripts/
├── run_extraction.py           # Test PDF extraction
├── run_categorization.py       # Batch categorize transactions
├── run_subscription_detection.py
├── export_for_database.py
├── analyze_statements.py       # Statement discrepancy analysis
├── analyze_amex.py
└── analyze_wealthsimple.py

supabase/
├── config.toml
└── migrations/
    ├── 20260201000000_initial_schema.sql   # Core schema (10 tables, 9 views)
    └── 20260201000001_add_receipts.sql     # Receipt infrastructure (3 tables)

tests/
└── integration/
    └── test_pdf_extraction.py
```

## Categories

13 top-level categories with 33 subcategories:

| Category | Subcategories |
|----------|---------------|
| Food & Dining | Coffee & Cafes, Fast Food, Restaurants, Delivery, Convenience |
| Transportation | Gas & Fuel, Ride Share, Public Transit, Parking |
| Retail & Shopping | Clothing, Electronics, Home & Garden, Online Shopping, Department Stores, Pet, Sporting Goods, General Merchandise |
| Bills & Utilities | Phone & Internet, Insurance, Subscriptions & Memberships, Government & Tax, Bank Fees |
| Healthcare | Pharmacy, Medical, Dental, Vision, Veterinary |
| Entertainment | Gaming, Streaming, Events & Attractions, Sports & Fitness, Alcohol |
| Housing | Rent & Mortgage |
| Income | |
| Transfers | |
| Investment | |
| Education | |
| Personal Care | |
| AI & Software Services | |

## Database Schema

The database uses two migrations that build the full schema from scratch:

**Core tables:** `institutions`, `accounts`, `transactions`, `trade_details`, `holdings`, `categories`, `statements`, `subscriptions`, `merchant_cache`

**Receipt tables:** `receipts`, `receipt_transactions` (junction), `receipt_items`

**Materialized views:** `monthly_spending_by_category`, `monthly_spending_by_account`, `yearly_summary`, `net_worth_timeline`, `investment_activity`, `current_holdings`, `transfer_summary`, `merchant_summary`, `category_trends`

All tables have RLS enabled. Materialized views refresh via `SELECT refresh_all_summaries()`.

## Setup

### Prerequisites

- Python 3.11+
- [Supabase CLI](https://supabase.com/docs/guides/cli) (for local database)
- Tesseract OCR (optional, for scanned document fallback)

### Install

```bash
git clone https://github.com/YOUR_USERNAME/Computare.git
cd Computare
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

### Configure

```bash
cp .env.example .env
# Edit .env with your API keys
```

Required environment variables:

| Variable | Purpose |
|----------|---------|
| `SUPABASE_URL` | Supabase project URL or `http://127.0.0.1:54321` for local |
| `SUPABASE_KEY` | Supabase service role key |
| `OPENAI_API_KEY` | GPT-4o-mini for transaction categorization |
| `ANTHROPIC_API_KEY` | Claude AI for PDF extraction fallback (optional) |
| `LANGTRACE_API_KEY` | LangTrace observability (optional) |

### Database

```bash
# Start local Supabase
supabase start

# Migrations run automatically, or apply manually:
supabase db reset
```

### Run

```bash
# Extract transactions from PDFs
python scripts/run_extraction.py

# Categorize transactions in database
python scripts/run_categorization.py

# Detect subscriptions
python scripts/run_subscription_detection.py

# Start the API
uvicorn computare.api.app:app --reload
```

## API

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Health check (cache size, DB status) |
| `GET` | `/categories` | List all 13 categories |
| `GET` | `/merchants` | List cached merchant mappings (paginated, filterable) |
| `PUT` | `/merchants/{raw_store}` | Override a merchant's category |
| `POST` | `/categorize/` | Categorize transactions from request body |
| `POST` | `/categorize/from-db` | Batch categorize uncategorized transactions from DB |

## Tech Stack

- **Extraction:** pdfplumber, pdf2image, Pillow, pytesseract
- **AI:** Anthropic Claude (vision), OpenAI GPT-4o-mini, LangChain
- **API:** FastAPI, Uvicorn, Pydantic
- **Database:** Supabase (PostgreSQL 17), Row Level Security
- **Observability:** LangTrace

## Adding a New Institution

1. Create an extractor in `computare/extractors/` extending `BaseExtractor`
2. Implement `extract(pdf_path, year)` returning an `ExtractionResult`
3. Add bank detection patterns to `computare/config.py`
4. Register the extractor in `HybridExtractor`
5. Add institution and accounts to the database

## License

[MIT](LICENSE)
