import { ScrollReveal } from "@/components/marketing/scroll-reveal";
import { Counter } from "@/components/marketing/counter";
import Link from "next/link";

export const metadata = {
  title: "Computare — The Vault",
};

export default function DesignTwo() {
  return (
    <main className="bg-ink text-paper min-h-screen c-grain selection:bg-gold selection:text-ink">
      {/* ── Navigation ── */}
      <nav className="fixed top-0 inset-x-0 z-[10000] bg-ink/95 border-b border-white/5">
        <div className="max-w-[1400px] mx-auto px-5 md:px-10 lg:px-16 h-14 flex items-center justify-between">
          <Link href="/" className="font-serif italic text-lg text-paper">
            Computare
          </Link>
          <div className="flex items-center gap-8 text-sm">
            <a
              href="#features"
              className="text-ash-400 hover:text-paper transition-colors duration-150 hidden sm:block"
            >
              Features
            </a>
            <a
              href="#ownership"
              className="text-ash-400 hover:text-paper transition-colors duration-150 hidden sm:block"
            >
              Ownership
            </a>
            <a
              href="https://github.com/computare/computare"
              target="_blank"
              rel="noopener noreferrer"
              className="text-gold hover:text-paper transition-colors duration-150"
            >
              GitHub &rarr;
            </a>
          </div>
        </div>
      </nav>

      {/* ── Hero ── */}
      <section className="min-h-screen flex items-center px-5 md:px-10 lg:px-16 pt-14">
        <div className="max-w-[1400px] mx-auto w-full grid lg:grid-cols-2 gap-12 lg:gap-20 items-center">
          <div className="c-hero">
            <p className="text-xs tracking-[0.3em] uppercase text-ash-400 mb-6">
              Open-source financial infrastructure
            </p>
            <h1 className="font-serif text-5xl md:text-7xl lg:text-[80px] leading-[0.95] tracking-[-0.03em]">
              Computare
            </h1>
            <p className="text-ash-400 text-lg md:text-xl leading-relaxed mt-6 max-w-lg">
              Track your finances without giving them away.
            </p>
            <div className="flex flex-wrap gap-4 mt-10">
              <a
                href="https://github.com/computare/computare"
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center justify-center bg-paper text-ink px-7 py-3 text-sm font-medium hover:bg-ash-200 transition-colors duration-150"
              >
                Get Started
              </a>
              <a
                href="#features"
                className="inline-flex items-center justify-center border border-ash-800 text-ash-400 px-7 py-3 text-sm hover:border-ash-600 hover:text-paper transition-colors duration-150"
              >
                Learn more
              </a>
            </div>
          </div>
          <div className="flex justify-center lg:justify-end">
            <div className="relative">
              <div
                className="absolute inset-0 c-halftone text-white/[0.03]"
                aria-hidden="true"
              />
              <img
                src="/media/flipping-coin.gif"
                alt="Dithered coin animation representing financial data"
                width={400}
                height={400}
                className="relative w-64 md:w-80 lg:w-[400px] mix-blend-screen opacity-90"
                loading="eager"
              />
            </div>
          </div>
        </div>
      </section>

      {/* ── Philosophy ── */}
      <section className="py-24 md:py-32 lg:py-40 bg-forest">
        <div className="max-w-[1400px] mx-auto px-5 md:px-10 lg:px-16 grid md:grid-cols-2 gap-12 md:gap-20">
          <ScrollReveal>
            <h2 className="font-serif italic text-3xl md:text-[44px] leading-[1.2] tracking-[-0.02em]">
              Financial data is personal infrastructure&nbsp;&mdash; not a
              product to be{" "}
              <span className="text-gold">monetised</span>.
            </h2>
          </ScrollReveal>
          <ScrollReveal delay={100}>
            <div className="space-y-6 text-white/70 leading-relaxed">
              <p>
                Traditional finance apps scrape your credentials and lock your
                data behind their walls. They monetise your transaction history
                and make it impossible to leave.
              </p>
              <p>
                Computare inverts this. You upload your own statements. You own
                the database. You choose where it lives. The code is open for
                anyone to audit.
              </p>
            </div>
          </ScrollReveal>
        </div>
      </section>

      {/* ── How It Works ── */}
      <section
        id="features"
        className="py-24 md:py-32 lg:py-40 px-5 md:px-10 lg:px-16"
      >
        <div className="max-w-[1400px] mx-auto">
          <ScrollReveal>
            <p className="text-xs tracking-[0.3em] uppercase text-ash-600 mb-4">
              Pipeline
            </p>
            <h2 className="font-serif text-3xl md:text-4xl tracking-[-0.02em] mb-16 md:mb-20">
              Three stages. Zero credential sharing.
            </h2>
          </ScrollReveal>
          <div className="grid md:grid-cols-3 gap-6">
            {[
              {
                num: "01",
                title: "Extract",
                desc: "Position-based PDF extraction for Scotiabank. CSV parsing for Wealthsimple and American Express. Claude AI vision fallback when confidence drops.",
                detail: "pdfplumber + Claude Vision",
              },
              {
                num: "02",
                title: "Categorize",
                desc: "Description rules catch known patterns for free. Merchant cache resolves repeats at zero cost. GPT-4o-mini handles the rest in batches.",
                detail: "13 categories, 33 subcategories",
              },
              {
                num: "03",
                title: "Store",
                desc: "PostgreSQL with row-level security. 9 materialized views for instant dashboard queries. Full export to CSV, JSON, or SQL dump.",
                detail: "Supabase + FastAPI",
              },
            ].map((step, i) => (
              <ScrollReveal key={step.num} delay={i * 80}>
                <div className="border border-white/10 p-6 md:p-8 h-full flex flex-col">
                  <span className="font-code text-gold text-sm">
                    {step.num}
                  </span>
                  <h3 className="font-serif text-2xl mt-4 mb-4">
                    {step.title}
                  </h3>
                  <p className="text-ash-400 text-[15px] leading-relaxed flex-1">
                    {step.desc}
                  </p>
                  <p className="font-code text-xs text-ash-600 mt-6 pt-4 border-t border-white/5">
                    {step.detail}
                  </p>
                </div>
              </ScrollReveal>
            ))}
          </div>
        </div>
      </section>

      {/* ── Statistics Bar ── */}
      <section className="py-12 md:py-16 px-5 md:px-10 lg:px-16 border-y border-white/5">
        <div className="max-w-[1400px] mx-auto grid grid-cols-2 md:grid-cols-4 gap-8">
          {[
            { value: 13, label: "Categories" },
            { value: 33, label: "Subcategories" },
            { value: 3, label: "Institutions" },
            { value: 9, label: "Views" },
          ].map((stat) => (
            <div key={stat.label} className="text-center">
              <p className="font-code text-3xl text-paper">
                <Counter target={stat.value} />
              </p>
              <p className="text-ash-600 text-xs tracking-wider uppercase mt-1">
                {stat.label}
              </p>
            </div>
          ))}
        </div>
      </section>

      {/* ── Data Ownership ── */}
      <section
        id="ownership"
        className="py-24 md:py-32 lg:py-40 px-5 md:px-10 lg:px-16"
      >
        <div className="max-w-[1400px] mx-auto">
          <ScrollReveal>
            <h2 className="font-serif text-3xl md:text-5xl tracking-[-0.02em] mb-16 md:mb-20 max-w-[700px]">
              Your data. Your servers.{" "}
              <span className="text-gold">Your terms.</span>
            </h2>
          </ScrollReveal>
          <div className="grid sm:grid-cols-2 gap-px bg-white/5">
            {[
              {
                title: "Self-host on your infrastructure",
                desc: "Run the full stack — database, API, extraction pipeline — anywhere you want.",
              },
              {
                title: "Export without restrictions",
                desc: "CSV, JSON, SQL. No lock-in. No rate limits. No premium tier required.",
              },
              {
                title: "No credential scraping",
                desc: "Upload your own statements. We never touch your bank login.",
              },
              {
                title: "Row-level security",
                desc: "PostgreSQL RLS on every table. Multi-tenant ready from day one.",
              },
            ].map((item, i) => (
              <ScrollReveal key={item.title} delay={i * 60}>
                <div className="bg-ink p-6 md:p-8">
                  <h3 className="font-serif text-lg mb-3">{item.title}</h3>
                  <p className="text-ash-400 text-[15px] leading-relaxed">
                    {item.desc}
                  </p>
                </div>
              </ScrollReveal>
            ))}
          </div>
        </div>
      </section>

      {/* ── Open Source ── */}
      <section className="py-24 md:py-32 lg:py-40 px-5 md:px-10 lg:px-16 bg-ash-900">
        <div className="max-w-[800px] mx-auto">
          <ScrollReveal>
            <p className="text-xs tracking-[0.3em] uppercase text-ash-600 mb-6">
              Open Source
            </p>
            <h2 className="font-serif text-3xl md:text-4xl tracking-[-0.02em] mb-6">
              Built in the open.
            </h2>
            <p className="text-ash-400 leading-relaxed mb-10">
              MIT Licensed. Fork it. Modify it. Host it. No black boxes, no
              hidden data flows, no surprise monetisation.
            </p>
          </ScrollReveal>
          <ScrollReveal delay={100}>
            <div className="bg-ink border border-white/10 p-6 font-code text-sm leading-loose">
              <p>
                <span className="text-sage">$</span>{" "}
                <span className="text-ash-400">
                  git clone https://github.com/computare/computare
                </span>
              </p>
              <p>
                <span className="text-sage">$</span>{" "}
                <span className="text-ash-400">cd computare</span>
              </p>
              <p>
                <span className="text-sage">$</span>{" "}
                <span className="text-ash-400">supabase start</span>
              </p>
              <p>
                <span className="text-sage">$</span>{" "}
                <span className="text-ash-400">
                  uvicorn computare.api.app:app --reload
                </span>
              </p>
            </div>
          </ScrollReveal>
        </div>
      </section>

      {/* ── Vision ── */}
      <section className="py-24 md:py-32 lg:py-40 px-5 md:px-10 lg:px-16 relative overflow-hidden">
        <div className="absolute inset-0 flex items-center justify-center opacity-[0.06] pointer-events-none">
          <img
            src="/media/flying-money.gif"
            alt=""
            className="w-[600px] mix-blend-screen"
            aria-hidden="true"
          />
        </div>
        <div className="max-w-[800px] mx-auto text-center relative">
          <ScrollReveal>
            <blockquote className="font-serif italic text-3xl md:text-[44px] leading-[1.2] tracking-[-0.02em]">
              Built for years of financial history, not quick wins.
            </blockquote>
          </ScrollReveal>
          <ScrollReveal delay={100}>
            <p className="text-ash-400 leading-relaxed mt-8 max-w-md mx-auto">
              Computare is the open financial layer — designed to hold a
              lifetime of transactions and grow with you across every account
              and institution.
            </p>
          </ScrollReveal>
        </div>
      </section>

      {/* ── CTA ── */}
      <section className="py-24 md:py-32 px-5 md:px-10 lg:px-16 bg-forest">
        <div className="max-w-[800px] mx-auto text-center">
          <ScrollReveal>
            <h2 className="font-serif text-3xl md:text-5xl tracking-[-0.02em] mb-4">
              Own your financial history.
            </h2>
            <p className="text-white/60 mb-10">
              Start self-hosting in under five minutes.
            </p>
          </ScrollReveal>
          <ScrollReveal delay={100}>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <a
                href="https://github.com/computare/computare"
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center justify-center bg-paper text-ink px-8 py-3 text-sm font-medium hover:bg-ash-200 transition-colors duration-150"
              >
                View on GitHub
              </a>
              <a
                href="/docs"
                className="inline-flex items-center justify-center border border-white/20 text-paper px-8 py-3 text-sm hover:border-white/40 transition-colors duration-150"
              >
                Documentation
              </a>
            </div>
          </ScrollReveal>
        </div>
      </section>

      {/* ── Footer ── */}
      <footer className="py-8 px-5 md:px-10 lg:px-16 border-t border-white/5">
        <div className="max-w-[1400px] mx-auto flex flex-col sm:flex-row items-center justify-between gap-4 text-sm text-ash-600">
          <p>&copy; 2026 Computare. MIT License.</p>
          <div className="flex gap-6">
            <a
              href="https://github.com/computare/computare"
              target="_blank"
              rel="noopener noreferrer"
              className="hover:text-paper transition-colors duration-150"
            >
              GitHub
            </a>
            <a
              href="/docs"
              className="hover:text-paper transition-colors duration-150"
            >
              Docs
            </a>
          </div>
        </div>
      </footer>
    </main>
  );
}
