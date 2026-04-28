import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Documentation",
  description:
    "Learn how to set up, self-host, and use Computare — the open-source personal finance platform for Canadians.",
};

export default function DocsPage() {
  return (
    <main className="bg-paper text-ink min-h-screen">
      <nav className="border-b border-ash-200 bg-paper">
        <div className="max-w-3xl mx-auto px-5 py-4 flex items-center justify-between">
          <a href="/" className="font-serif italic text-lg">
            Computare
          </a>
          <span className="text-xs text-ash-400 tracking-[0.2em] uppercase">
            Documentation
          </span>
        </div>
      </nav>

      <div className="max-w-3xl mx-auto px-5 py-12 md:py-20 space-y-20">
        {/* ── Getting Started ── */}
        <section>
          <h1 className="font-serif text-3xl md:text-4xl tracking-[-0.02em] mb-4">
            Getting Started
          </h1>
          <p className="text-ash-600 leading-relaxed mb-6">
            Computare is an open-source personal finance platform that extracts
            transactions from Canadian bank statements, categorizes them with
            AI, and stores everything in a structured PostgreSQL database you
            control.
          </p>
          <div className="bg-ink text-paper p-6 font-code text-sm leading-relaxed rounded">
            <p className="text-ash-400">
              <span className="text-sage">$</span> git clone
              https://github.com/Andrew-Girgis/Computare
            </p>
            <p className="text-ash-400">
              <span className="text-sage">$</span> cd Computare
            </p>
            <p className="text-ash-400">
              <span className="text-sage">$</span> computare init
            </p>
          </div>
          <p className="text-ash-400 text-sm mt-4">
            Requires Python 3.11+, a Supabase project (or self-hosted
            PostgreSQL), and API keys for AI categorization (optional).
          </p>
        </section>

        {/* ── Supported Imports ── */}
        <section>
          <h2 className="font-serif text-2xl md:text-3xl tracking-[-0.02em] mb-4">
            Supported Imports
          </h2>
          <p className="text-ash-600 leading-relaxed mb-6">
            Computare currently supports the following Canadian financial
            institutions and statement formats.
          </p>
          <div className="space-y-4">
            {[
              {
                name: "Scotiabank",
                formats: "PDF statements (chequing, credit card, iTRADE)",
                method:
                  "Position-based word extraction with pdfplumber. Falls back to Claude AI vision when confidence is below threshold.",
                coverage: "2018 – present",
              },
              {
                name: "Wealthsimple",
                formats: "CSV exports (TFSA, Spending, Credit Card, Crypto)",
                method:
                  "Direct CSV parsing. Clean structured data with no ambiguity.",
                coverage: "2021 – present",
              },
              {
                name: "American Express",
                formats: "Year-end CSV summaries",
                method:
                  "Direct CSV parsing of annual statement summaries.",
                coverage: "2024 – present",
              },
            ].map((inst) => (
              <div key={inst.name} className="border border-ash-200 p-5">
                <h3 className="font-serif text-lg mb-1">{inst.name}</h3>
                <p className="text-ash-400 text-xs mb-3">
                  {inst.formats} &middot; {inst.coverage}
                </p>
                <p className="text-ash-600 text-[15px] leading-relaxed">
                  {inst.method}
                </p>
              </div>
            ))}
          </div>
        </section>

        {/* ── Categorization ── */}
        <section>
          <h2 className="font-serif text-2xl md:text-3xl tracking-[-0.02em] mb-4">
            Categorization Pipeline
          </h2>
          <p className="text-ash-600 leading-relaxed mb-6">
            Transactions are categorized through a 3-tier pipeline. After the
            initial run, most transactions resolve from cache at zero cost.
          </p>
          <div className="space-y-4">
            {[
              {
                tier: "1",
                name: "Description Rules",
                desc: 'Pattern matching on transaction descriptions. Handles known formats like "INTERAC E-TRANSFER" or "MB-Transferto". Zero cost, instant.',
              },
              {
                tier: "2",
                name: "Merchant Cache",
                desc: "Lookup against a growing database of known merchants and their default categories. Zero cost after first encounter.",
              },
              {
                tier: "3",
                name: "LLM (GPT-4o-mini)",
                desc: "Only fires when rules and cache both miss. Sends only the transaction description — no amounts, no account numbers, no personal info. Covers roughly 15% of new transactions.",
              },
            ].map((t) => (
              <div key={t.tier} className="border-l-2 border-forest pl-4">
                <h3 className="font-medium mb-1">
                  <span className="text-gold font-code text-sm mr-2">
                    Tier {t.tier}
                  </span>
                  {t.name}
                </h3>
                <p className="text-ash-600 text-[15px] leading-relaxed">
                  {t.desc}
                </p>
              </div>
            ))}
          </div>
          <p className="text-ash-400 text-sm mt-4">
            13 top-level categories with 33 subcategories including Food &amp;
            Dining, Retail &amp; Shopping, Transportation, Bills &amp;
            Utilities, and more.
          </p>
        </section>

        {/* ── Self-Hosting ── */}
        <section>
          <h2 className="font-serif text-2xl md:text-3xl tracking-[-0.02em] mb-4">
            Self-Hosting
          </h2>
          <p className="text-ash-600 leading-relaxed mb-6">
            Computare is designed to be self-hosted. You control the database,
            the extraction pipeline, and all of your financial data.
          </p>
          <div className="space-y-3 text-[15px]">
            {[
              {
                label: "Database",
                desc: "Supabase (managed PostgreSQL) or self-hosted PostgreSQL. All tables have Row Level Security enabled.",
              },
              {
                label: "Extraction",
                desc: "Python package runs locally. PDF parsing uses pdfplumber. AI fallback uses Claude API (optional).",
              },
              {
                label: "API",
                desc: "FastAPI REST API for categorization, merchant normalization, and health checks. Runs alongside your database.",
              },
              {
                label: "Frontend",
                desc: "Next.js App Router with Supabase auth. Self-host on Vercel, Cloudflare, or any Node.js runtime.",
              },
            ].map((item) => (
              <div key={item.label} className="flex gap-3">
                <span className="text-forest font-code text-sm shrink-0 mt-0.5">
                  {item.label}
                </span>
                <span className="text-ash-600 leading-relaxed">
                  {item.desc}
                </span>
              </div>
            ))}
          </div>
        </section>

        {/* ── Privacy ── */}
        <section>
          <h2 className="font-serif text-2xl md:text-3xl tracking-[-0.02em] mb-4">
            Privacy &amp; Data Flow
          </h2>
          <p className="text-ash-600 leading-relaxed mb-6">
            Data ownership is non-negotiable. Here is exactly what happens to
            your data.
          </p>
          <div className="grid md:grid-cols-3 gap-6">
            <div className="border border-ash-200 p-5">
              <h3 className="font-serif text-lg mb-2 text-sage">
                Always local
              </h3>
              <ul className="text-ash-600 text-[15px] leading-relaxed space-y-1.5">
                <li>Your bank statements and CSV files</li>
                <li>Transaction data in your database</li>
                <li>Category rules &amp; merchant cache</li>
                <li>Dashboard &amp; visualizations</li>
              </ul>
            </div>
            <div className="border border-ash-200 p-5">
              <h3 className="font-serif text-lg mb-2 text-gold">
                Sent to LLM
              </h3>
              <ul className="text-ash-600 text-[15px] leading-relaxed space-y-1.5">
                <li>Transaction descriptions only</li>
                <li>No amounts or account numbers</li>
                <li>Only for cache misses (~15%)</li>
                <li>Optional — can disable Tier 3</li>
              </ul>
            </div>
            <div className="border border-ash-200 p-5">
              <h3 className="font-serif text-lg mb-2 text-ink">
                Never shared
              </h3>
              <ul className="text-ash-600 text-[15px] leading-relaxed space-y-1.5">
                <li>Bank credentials</li>
                <li>Full transaction amounts</li>
                <li>Personally identifiable info</li>
                <li>Anything you don&apos;t upload</li>
              </ul>
            </div>
          </div>
        </section>

        {/* ── Architecture ── */}
        <section>
          <h2 className="font-serif text-2xl md:text-3xl tracking-[-0.02em] mb-4">
            Architecture
          </h2>
          <div className="bg-ink text-paper p-6 font-code text-sm leading-relaxed rounded overflow-x-auto">
            <pre className="whitespace-pre">{`DATA SOURCES              EXTRACTION
 Scotiabank PDFs ──┐      ┌─ pdfplumber (local)
 Wealthsimple CSVs ─┼──────┤
 Amex CSVs ─────────┘      └─ Claude AI (fallback)
                                  │
                                  ▼
                         CATEGORIZATION
                    ┌─ Tier 1: Description rules (free)
                    ├─ Tier 2: Merchant cache (free)
                    └─ Tier 3: GPT-4o-mini (batched)
                                  │
                                  ▼
                          Supabase (PostgreSQL)
                    ┌────────────────────────┐
                    │ institutions  accounts │
                    │ transactions  categories│
                    │ subscriptions receipts │
                    │ merchant_cache         │
                    │ 9 materialized views   │
                    └────────────────────────┘`}</pre>
          </div>
        </section>

        {/* ── Links ── */}
        <section className="pt-8 border-t border-ash-200">
          <div className="flex flex-col sm:flex-row gap-4">
            <a
              href="https://github.com/Andrew-Girgis/Computare"
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center justify-center bg-forest text-paper px-6 py-3 text-sm hover:bg-forest/90 transition-colors duration-150"
            >
              View on GitHub
            </a>
            <a
              href="/"
              className="inline-flex items-center justify-center border border-ash-200 text-ink px-6 py-3 text-sm hover:border-ash-400 transition-colors duration-150"
            >
              Back to Home
            </a>
          </div>
        </section>
      </div>
    </main>
  );
}