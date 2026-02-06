import { ScrollReveal } from "@/components/marketing/scroll-reveal";
import Link from "next/link";

export const metadata = {
  title: "Computare — The Terminal",
};

const CATEGORIES_TREE = `categories/
├── food-and-dining/
│   ├── coffee-and-cafes
│   ├── fast-food
│   ├── restaurants
│   ├── delivery
│   └── convenience
├── retail-and-shopping/
│   ├── groceries
│   ├── alcohol
│   ├── clothing
│   ├── electronics
│   └── ... (5 more)
├── entertainment/
│   ├── gaming
│   ├── streaming
│   └── ... (3 more)
├── transportation/
├── bills-and-utilities/
├── healthcare/
├── housing/
├── income/
├── transfers/
├── investment/
├── education/
├── personal-care/
└── ai-and-software/

13 categories, 33 subcategories`;

export default function DesignThree() {
  return (
    <main className="bg-[#0D1A14] text-[#8BAF9E] min-h-screen font-code selection:bg-sage selection:text-ink">
      {/* ── Navigation ── */}
      <nav className="fixed top-0 inset-x-0 z-50 bg-[#0D1A14]/95 border-b border-sage/10">
        <div className="max-w-[1000px] mx-auto px-5 md:px-8 h-12 flex items-center justify-between text-sm">
          <Link href="/" className="text-paper">
            computare
          </Link>
          <div className="flex items-center gap-6 text-sage/60">
            <a
              href="#pipeline"
              className="hover:text-sage transition-colors duration-150 hidden sm:block"
            >
              src
            </a>
            <a
              href="#schema"
              className="hover:text-sage transition-colors duration-150 hidden sm:block"
            >
              schema
            </a>
            <a
              href="https://github.com/computare/computare"
              target="_blank"
              rel="noopener noreferrer"
              className="text-gold hover:text-paper transition-colors duration-150"
            >
              github
            </a>
          </div>
        </div>
      </nav>

      {/* ── Hero ── */}
      <section className="min-h-screen flex items-center justify-center px-5 md:px-8 pt-12">
        <div className="max-w-[720px] w-full c-hero">
          <pre className="text-sage/30 text-xs md:text-sm leading-relaxed select-none" aria-hidden="true">{`┌──────────────────────────────────────────────────────┐`}</pre>
          <pre className="text-sage/30 text-xs md:text-sm select-none" aria-hidden="true">{`│                                                      │`}</pre>
          <div className="px-4 md:px-6 py-6 md:py-8">
            <h1 className="text-paper text-3xl md:text-5xl font-bold tracking-tight leading-tight">
              COMPUTARE
            </h1>
            <div className="w-16 h-px bg-sage/30 my-4" />
            <p className="text-lg md:text-xl text-sage/80 leading-relaxed">
              The open financial layer.
            </p>
            <div className="mt-8 space-y-1">
              <p>
                <span className="text-gold">$</span> computare --version
              </p>
              <p className="text-sage/50">
                computare v1.0.0 (postgresql 17, fastapi, next.js 16)
              </p>
              <p className="mt-4">
                <span className="text-gold">$</span> computare status
              </p>
              <p className="text-sage/50">
                institutions: 3 (scotiabank, wealthsimple, amex)
              </p>
              <p className="text-sage/50">
                categories:&nbsp;&nbsp; 13 top-level, 33 subcategories
              </p>
              <p className="text-sage/50">
                pipeline:&nbsp;&nbsp;&nbsp;&nbsp; extract → categorize → store
              </p>
              <p className="text-sage/50">
                license:&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; MIT
              </p>
              <p className="mt-4">
                <span className="text-gold">$</span>{" "}
                <span className="c-cursor" />
              </p>
            </div>
          </div>
          <pre className="text-sage/30 text-xs md:text-sm select-none" aria-hidden="true">{`│                                                      │`}</pre>
          <pre className="text-sage/30 text-xs md:text-sm select-none" aria-hidden="true">{`└──────────────────────────────────────────────────────┘`}</pre>
        </div>
      </section>

      {/* ── Philosophy ── */}
      <section className="py-20 md:py-28 px-5 md:px-8">
        <div className="max-w-[720px] mx-auto space-y-4">
          {[
            "Open-source by default.",
            "Data ownership is non-negotiable.",
            "Transparency over convenience.",
            "Built for the long term.",
          ].map((statement, i) => (
            <ScrollReveal key={i} delay={i * 60}>
              <p className="text-paper/90 text-lg md:text-xl">
                <span className="text-sage/40 mr-3">&gt;</span>
                {statement}
              </p>
            </ScrollReveal>
          ))}
        </div>
      </section>

      {/* ── Pipeline ── */}
      <section
        id="pipeline"
        className="py-20 md:py-28 px-5 md:px-8 border-t border-sage/10"
      >
        <div className="max-w-[720px] mx-auto">
          <ScrollReveal>
            <p className="text-sage/40 text-xs mb-8">
              # How the extraction pipeline works
            </p>
          </ScrollReveal>

          <div className="space-y-8">
            <ScrollReveal delay={60}>
              <div className="border border-sage/15 p-5">
                <p className="text-gold text-sm mb-3">STEP 01 — EXTRACT</p>
                <pre className="text-sm leading-relaxed whitespace-pre-wrap">{`$ computare extract \\
    --source scotiabank \\
    --file ~/statements/2025-jan.pdf

[████████████████████████████] 100%
→ 47 transactions extracted
→ confidence: 94.2% (pdfplumber)
→ fallback: none required`}</pre>
              </div>
            </ScrollReveal>

            <ScrollReveal delay={120}>
              <div className="border border-sage/15 p-5">
                <p className="text-gold text-sm mb-3">
                  STEP 02 — CATEGORIZE
                </p>
                <pre className="text-sm leading-relaxed whitespace-pre-wrap">{`$ computare categorize --strategy tiered

Tier 1 (rules):    23 matched   [free]
Tier 2 (cache):    18 matched   [free]
Tier 3 (llm):       6 matched   [batched]
─────────────────────────────
→ 47/47 categorized
→ cache hit rate: 87.2%`}</pre>
              </div>
            </ScrollReveal>

            <ScrollReveal delay={180}>
              <div className="border border-sage/15 p-5">
                <p className="text-gold text-sm mb-3">STEP 03 — STORE</p>
                <pre className="text-sm leading-relaxed whitespace-pre-wrap">{`$ computare store --target supabase

→ 47 rows inserted into transactions
→ RLS policies: active
→ materialized views: refreshed (9)
→ export: available (csv, json, sql)`}</pre>
              </div>
            </ScrollReveal>
          </div>
        </div>
      </section>

      {/* ── Categories ── */}
      <section
        id="schema"
        className="py-20 md:py-28 px-5 md:px-8 border-t border-sage/10"
      >
        <div className="max-w-[720px] mx-auto">
          <ScrollReveal>
            <p className="text-sage/40 text-xs mb-8">
              # Category taxonomy
            </p>
          </ScrollReveal>
          <ScrollReveal delay={60}>
            <pre className="text-sm leading-relaxed text-sage/70 overflow-x-auto">
              {CATEGORIES_TREE}
            </pre>
          </ScrollReveal>
        </div>
      </section>

      {/* ── Data Ownership ── */}
      <section className="py-20 md:py-28 px-5 md:px-8 border-t border-sage/10">
        <div className="max-w-[720px] mx-auto">
          <ScrollReveal>
            <p className="text-sage/40 text-xs mb-8">
              # Data ownership
            </p>
          </ScrollReveal>
          <ScrollReveal delay={60}>
            <pre className="text-sm leading-relaxed border border-sage/15 p-5 whitespace-pre-wrap">{`┌─ DATA OWNERSHIP ─────────────────────────────────┐
│                                                   │
│  • Self-host the full stack on your servers       │
│  • Export: CSV, JSON, SQL dump                    │
│  • No credential scraping — ever                  │
│  • Row-level security on every table              │
│  • PostgreSQL 17 — query your data directly       │
│  • 9 materialized views for fast dashboards       │
│                                                   │
│  Your database. Your infrastructure. Your data.   │
│                                                   │
└───────────────────────────────────────────────────┘`}</pre>
          </ScrollReveal>
        </div>
      </section>

      {/* ── Open Source ── */}
      <section className="py-20 md:py-28 px-5 md:px-8 border-t border-sage/10">
        <div className="max-w-[720px] mx-auto">
          <ScrollReveal>
            <p className="text-sage/40 text-xs mb-8"># Install</p>
          </ScrollReveal>
          <ScrollReveal delay={60}>
            <div className="space-y-1">
              <p>
                <span className="text-gold">$</span>{" "}
                <span className="text-paper">
                  git clone https://github.com/computare/computare
                </span>
              </p>
              <p>
                <span className="text-gold">$</span>{" "}
                <span className="text-paper">cd computare</span>
              </p>
              <p>
                <span className="text-gold">$</span>{" "}
                <span className="text-paper">python -m venv .venv</span>
              </p>
              <p>
                <span className="text-gold">$</span>{" "}
                <span className="text-paper">pip install -e .</span>
              </p>
              <p>
                <span className="text-gold">$</span>{" "}
                <span className="text-paper">supabase start</span>
              </p>
              <p>
                <span className="text-gold">$</span>{" "}
                <span className="text-paper">
                  uvicorn computare.api.app:app --reload
                </span>
              </p>
            </div>
          </ScrollReveal>
          <ScrollReveal delay={120}>
            <p className="text-sage/40 mt-8 text-sm">
              License: MIT — read every line.
            </p>
          </ScrollReveal>
        </div>
      </section>

      {/* ── Vision ── */}
      <section className="py-20 md:py-28 px-5 md:px-8 border-t border-sage/10">
        <div className="max-w-[720px] mx-auto space-y-3">
          <ScrollReveal>
            <p className="text-paper text-lg md:text-xl">
              <span className="text-sage/40 mr-3">&gt;</span>
              Years of financial history.
            </p>
          </ScrollReveal>
          <ScrollReveal delay={60}>
            <p className="text-paper text-lg md:text-xl">
              <span className="text-sage/40 mr-3">&gt;</span>
              Not quick wins.
            </p>
          </ScrollReveal>
          <ScrollReveal delay={120}>
            <p className="text-paper text-lg md:text-xl">
              <span className="text-sage/40 mr-3">&gt;</span>
              Not budgeting gimmicks.
            </p>
          </ScrollReveal>
          <ScrollReveal delay={180}>
            <p className="text-paper text-lg md:text-xl font-bold">
              <span className="text-sage/40 mr-3">&gt;</span>
              Infrastructure.
            </p>
          </ScrollReveal>
        </div>
      </section>

      {/* ── CTA ── */}
      <section className="py-20 md:py-28 px-5 md:px-8 border-t border-sage/10">
        <div className="max-w-[720px] mx-auto text-center">
          <ScrollReveal>
            <p className="text-paper text-xl md:text-2xl mb-8">
              Own your financial data.
            </p>
          </ScrollReveal>
          <ScrollReveal delay={80}>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <a
                href="https://github.com/computare/computare"
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center justify-center border border-sage/30 text-paper px-8 py-3 text-sm hover:bg-sage/10 transition-colors duration-150"
              >
                <span className="text-gold mr-2">$</span> git clone
                computare
              </a>
              <a
                href="/docs"
                className="inline-flex items-center justify-center text-sage/60 px-8 py-3 text-sm hover:text-paper transition-colors duration-150"
              >
                man computare &rarr;
              </a>
            </div>
          </ScrollReveal>
        </div>
      </section>

      {/* ── Footer ── */}
      <footer className="py-6 px-5 md:px-8 border-t border-sage/10">
        <div className="max-w-[720px] mx-auto flex items-center justify-between text-xs text-sage/30">
          <p>computare v1.0.0 — MIT License — 2026</p>
          <a
            href="https://github.com/computare/computare"
            target="_blank"
            rel="noopener noreferrer"
            className="hover:text-sage transition-colors duration-150"
          >
            src
          </a>
        </div>
      </footer>
    </main>
  );
}
