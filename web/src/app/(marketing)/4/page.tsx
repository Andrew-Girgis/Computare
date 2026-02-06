import { ScrollReveal } from "@/components/marketing/scroll-reveal";
import { Counter } from "@/components/marketing/counter";
import Link from "next/link";

export const metadata = {
  title: "Computare — The Broadsheet",
};

export default function DesignFour() {
  return (
    <main className="bg-paper text-ink min-h-screen selection:bg-forest selection:text-paper">
      {/* ── Masthead ── */}
      <nav className="fixed top-0 inset-x-0 z-50 bg-paper border-b border-ink">
        <div className="max-w-[1200px] mx-auto px-5 md:px-10 h-12 flex items-center justify-between">
          <span className="text-xs tracking-[0.4em] uppercase font-medium">
            Computare
          </span>
          <span className="text-xs text-ash-400 hidden sm:block">
            No. 01 &mdash; February 2026
          </span>
          <a
            href="https://github.com/computare/computare"
            target="_blank"
            rel="noopener noreferrer"
            className="text-xs text-ash-600 hover:text-ink transition-colors duration-150"
          >
            Source &rarr;
          </a>
        </div>
      </nav>

      {/* ── Hero ── */}
      <section className="pt-24 md:pt-32 pb-12 md:pb-16 px-5 md:px-10 border-b border-ink">
        <div className="max-w-[1200px] mx-auto c-hero">
          <p className="text-xs tracking-[0.3em] uppercase text-ash-400 mb-6 md:mb-8">
            Open-source personal finance
          </p>
          <h1 className="font-serif text-[clamp(3rem,8vw,7rem)] leading-[0.9] tracking-[-0.04em] max-w-[900px]">
            The Open Financial Layer
          </h1>
          <div className="h-px bg-ink mt-8 md:mt-12" />
          <div className="grid md:grid-cols-3 gap-8 mt-8 md:mt-10">
            <div className="md:col-span-1">
              <p className="text-ash-600 text-[15px] leading-relaxed">
                Computare gives you true ownership over your financial data.
                Extract, categorize, store, and export — on your terms.
              </p>
            </div>
            <div className="md:col-span-1 flex justify-center">
              <img
                src="/media/flying-money.gif"
                alt="Dithered currency animation"
                width={240}
                height={240}
                className="w-40 md:w-60 opacity-80 mix-blend-multiply"
                loading="eager"
              />
            </div>
            <div className="md:col-span-1">
              <div className="font-code text-sm space-y-2 text-ash-600">
                <p>
                  <span className="text-ash-400">Categories</span>{" "}
                  <span className="float-right tabular-nums">
                    <Counter target={13} />
                  </span>
                </p>
                <p>
                  <span className="text-ash-400">Subcategories</span>{" "}
                  <span className="float-right tabular-nums">
                    <Counter target={33} />
                  </span>
                </p>
                <p>
                  <span className="text-ash-400">Institutions</span>{" "}
                  <span className="float-right tabular-nums">
                    <Counter target={3} />
                  </span>
                </p>
                <p>
                  <span className="text-ash-400">Views</span>{" "}
                  <span className="float-right tabular-nums">
                    <Counter target={9} />
                  </span>
                </p>
                <div className="h-px bg-ash-200 mt-4" />
                <p className="text-xs text-ash-400 pt-2">
                  Scotiabank &middot; Wealthsimple &middot; American Express
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ── Section 01: Philosophy ── */}
      <section className="py-16 md:py-24 px-5 md:px-10 border-b border-ash-200">
        <div className="max-w-[1200px] mx-auto">
          <ScrollReveal>
            <div className="grid md:grid-cols-12 gap-8 md:gap-12">
              <div className="md:col-span-2">
                <span className="font-serif text-6xl md:text-8xl text-ash-200 leading-none">
                  01
                </span>
              </div>
              <div className="md:col-span-5">
                <p className="text-xs tracking-[0.2em] uppercase text-ash-400 mb-4">
                  What We Believe
                </p>
                <p className="text-[15px] leading-relaxed text-ash-600">
                  Traditional finance apps scrape your credentials and lock
                  your data behind their walls. They monetise your
                  transaction history and make it impossible to leave.
                  Computare inverts this entirely.
                </p>
                <p className="text-[15px] leading-relaxed text-ash-600 mt-4">
                  You upload your own statements. You own the database. You
                  choose where it lives. The code is open for anyone to read,
                  fork, and modify.
                </p>
              </div>
              <div className="md:col-span-5">
                <blockquote className="font-serif italic text-2xl md:text-3xl leading-[1.3] tracking-[-0.01em] border-l-2 border-gold pl-6">
                  Financial data is personal infrastructure — not a
                  product to be monetised.
                </blockquote>
              </div>
            </div>
          </ScrollReveal>
        </div>
      </section>

      {/* ── Section 02: How It Works ── */}
      <section className="py-16 md:py-24 px-5 md:px-10 border-b border-ash-200">
        <div className="max-w-[1200px] mx-auto">
          <ScrollReveal>
            <div className="grid md:grid-cols-12 gap-8 md:gap-12 mb-12 md:mb-16">
              <div className="md:col-span-2">
                <span className="font-serif text-6xl md:text-8xl text-ash-200 leading-none">
                  02
                </span>
              </div>
              <div className="md:col-span-10">
                <p className="text-xs tracking-[0.2em] uppercase text-ash-400 mb-2">
                  The Pipeline
                </p>
                <h2 className="font-serif text-3xl md:text-4xl tracking-[-0.02em]">
                  Three stages. Zero credential sharing.
                </h2>
              </div>
            </div>
          </ScrollReveal>
          <div className="grid md:grid-cols-3 gap-px bg-ash-200">
            {[
              {
                title: "Extract",
                desc: "Position-based PDF extraction for Scotiabank. CSV parsing for Wealthsimple and American Express. Claude AI vision fallback for low-confidence pages.",
                tech: "pdfplumber + Claude Vision",
              },
              {
                title: "Categorize",
                desc: "Description rules catch known patterns for free. Merchant cache resolves repeats at zero cost. GPT-4o-mini handles the remainder in batches.",
                tech: "LangChain + GPT-4o-mini",
              },
              {
                title: "Store",
                desc: "PostgreSQL with row-level security. 9 materialized views for instant dashboard queries. Full export to CSV, JSON, or SQL dump.",
                tech: "Supabase + FastAPI",
              },
            ].map((step, i) => (
              <ScrollReveal key={step.title} delay={i * 80}>
                <div className="bg-paper p-6 md:p-8 h-full">
                  <h3 className="font-serif text-xl mb-3">{step.title}</h3>
                  <p className="text-ash-600 text-[15px] leading-relaxed mb-6">
                    {step.desc}
                  </p>
                  <p className="font-code text-xs text-ash-400 pt-4 border-t border-ash-200">
                    {step.tech}
                  </p>
                </div>
              </ScrollReveal>
            ))}
          </div>
        </div>
      </section>

      {/* ── Section 03: Data Ownership ── */}
      <section className="py-16 md:py-24 px-5 md:px-10 border-b border-ash-200">
        <div className="max-w-[1200px] mx-auto">
          <ScrollReveal>
            <div className="grid md:grid-cols-12 gap-8 md:gap-12 mb-12 md:mb-16">
              <div className="md:col-span-2">
                <span className="font-serif text-6xl md:text-8xl text-ash-200 leading-none">
                  03
                </span>
              </div>
              <div className="md:col-span-10">
                <p className="text-xs tracking-[0.2em] uppercase text-ash-400 mb-2">
                  Ownership
                </p>
                <h2 className="font-serif text-3xl md:text-4xl tracking-[-0.02em]">
                  Your data never leaves your control.
                </h2>
              </div>
            </div>
          </ScrollReveal>
          <div className="grid md:grid-cols-2 gap-x-12 gap-y-8">
            {[
              {
                title: "Self-host everything",
                desc: "Run the full stack on your own servers. Supabase, PostgreSQL, and the extraction pipeline.",
              },
              {
                title: "Export without limits",
                desc: "CSV, JSON, SQL dump. No lock-in, no rate limits, no premium tier required.",
              },
              {
                title: "No credential scraping",
                desc: "Upload your own bank statements. We never ask for or store your bank login.",
              },
              {
                title: "Row-level security",
                desc: "PostgreSQL RLS on every table. Your data is isolated and protected by default.",
              },
            ].map((item, i) => (
              <ScrollReveal key={item.title} delay={i * 60}>
                <div className="flex gap-4">
                  <div className="w-1 bg-gold shrink-0 mt-1" style={{ height: 16 }} />
                  <div>
                    <h3 className="font-medium text-sm mb-1">{item.title}</h3>
                    <p className="text-ash-600 text-[15px] leading-relaxed">
                      {item.desc}
                    </p>
                  </div>
                </div>
              </ScrollReveal>
            ))}
          </div>
        </div>
      </section>

      {/* ── Section 04: Open Source ── */}
      <section className="py-16 md:py-24 px-5 md:px-10 border-b border-ash-200">
        <div className="max-w-[1200px] mx-auto">
          <ScrollReveal>
            <div className="grid md:grid-cols-12 gap-8 md:gap-12">
              <div className="md:col-span-2">
                <span className="font-serif text-6xl md:text-8xl text-ash-200 leading-none">
                  04
                </span>
              </div>
              <div className="md:col-span-5">
                <p className="text-xs tracking-[0.2em] uppercase text-ash-400 mb-4">
                  Open Source
                </p>
                <h2 className="font-serif text-2xl md:text-3xl tracking-[-0.02em] mb-4">
                  MIT Licensed. Read every line.
                </h2>
                <p className="text-ash-600 text-[15px] leading-relaxed">
                  Computare is built in the open. No black boxes, no hidden
                  data flows, no surprise monetisation. Fork it. Modify it.
                  Host it. It&apos;s yours.
                </p>
              </div>
              <div className="md:col-span-5">
                <div className="bg-ink text-paper p-5 font-code text-sm leading-loose">
                  <p>
                    <span className="text-sage">$</span> git clone
                    https://github.com/computare/computare
                  </p>
                  <p>
                    <span className="text-sage">$</span> cd computare
                  </p>
                  <p>
                    <span className="text-sage">$</span> supabase start
                  </p>
                  <p>
                    <span className="text-sage">$</span> pnpm dev
                  </p>
                </div>
              </div>
            </div>
          </ScrollReveal>
        </div>
      </section>

      {/* ── Section 05: Vision ── */}
      <section className="py-16 md:py-24 px-5 md:px-10 border-b border-ash-200">
        <div className="max-w-[1200px] mx-auto">
          <ScrollReveal>
            <div className="grid md:grid-cols-12 gap-8 md:gap-12">
              <div className="md:col-span-2">
                <span className="font-serif text-6xl md:text-8xl text-ash-200 leading-none">
                  05
                </span>
              </div>
              <div className="md:col-span-8">
                <blockquote className="font-serif italic text-3xl md:text-[40px] leading-[1.25] tracking-[-0.02em]">
                  Built for years of financial history, not quick wins.
                </blockquote>
                <p className="text-ash-600 text-[15px] leading-relaxed mt-6 max-w-lg">
                  Track a decade of transactions across every account.
                  Computare is the open financial layer — designed to hold a
                  lifetime of data and grow with you.
                </p>
              </div>
            </div>
          </ScrollReveal>
        </div>
      </section>

      {/* ── CTA ── */}
      <section className="bg-ink text-paper py-16 md:py-24 px-5 md:px-10">
        <div className="max-w-[1200px] mx-auto text-center">
          <ScrollReveal>
            <h2 className="font-serif text-3xl md:text-5xl tracking-[-0.02em] mb-4">
              Start owning your financial data.
            </h2>
            <p className="text-ash-400 mb-10">
              Self-host in under five minutes. Free and open-source.
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
                className="inline-flex items-center justify-center border border-ash-800 text-ash-400 px-8 py-3 text-sm hover:border-ash-600 hover:text-paper transition-colors duration-150"
              >
                Documentation
              </a>
            </div>
          </ScrollReveal>
        </div>
      </section>

      {/* ── Footer ── */}
      <footer className="bg-ink text-ash-600 py-8 px-5 md:px-10 border-t border-white/5">
        <div className="max-w-[1200px] mx-auto flex flex-col sm:flex-row items-center justify-between gap-4 text-xs">
          <p className="tracking-[0.2em] uppercase">
            Computare &mdash; Est. 2026
          </p>
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
            <span>MIT License</span>
          </div>
        </div>
      </footer>
    </main>
  );
}
