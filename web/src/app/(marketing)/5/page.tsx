import { ScrollReveal } from "@/components/marketing/scroll-reveal";
import { Counter } from "@/components/marketing/counter";
import Link from "next/link";

export const metadata = {
  title: "Computare — The Monument",
};

export default function DesignFive() {
  return (
    <main className="min-h-screen selection:bg-gold selection:text-ink">
      {/* ── Navigation ── */}
      <nav className="fixed top-0 inset-x-0 z-50 bg-ink border-b border-white/10">
        <div className="max-w-[1400px] mx-auto px-5 md:px-10 lg:px-16 h-14 flex items-center justify-between">
          <Link href="/" className="font-serif text-paper text-xl">
            C
          </Link>
          <div className="flex items-center gap-8 text-sm text-ash-400">
            <a
              href="#about"
              className="hover:text-paper transition-colors duration-150 hidden sm:block"
            >
              About
            </a>
            <a
              href="#system"
              className="hover:text-paper transition-colors duration-150 hidden sm:block"
            >
              System
            </a>
            <a
              href="https://github.com/computare/computare"
              target="_blank"
              rel="noopener noreferrer"
              className="text-paper hover:text-gold transition-colors duration-150"
            >
              GitHub
            </a>
          </div>
        </div>
      </nav>

      {/* ══ SECTION 01: Hero (Black) ══ */}
      <section className="bg-ink text-paper min-h-screen flex items-end relative overflow-hidden px-5 md:px-10 lg:px-16 pb-16 md:pb-24 pt-14">
        <div className="absolute top-20 right-10 md:right-16 font-serif text-[clamp(8rem,20vw,16rem)] leading-none text-white/[0.03] select-none pointer-events-none">
          01
        </div>
        <div className="max-w-[1400px] mx-auto w-full c-hero">
          <div className="h-px bg-white/10 mb-8 md:mb-12" />
          <div className="grid lg:grid-cols-12 gap-8 lg:gap-12 items-end">
            <div className="lg:col-span-8">
              <p className="text-xs tracking-[0.3em] uppercase text-ash-600 mb-6">
                Open-source financial infrastructure
              </p>
              <h1 className="font-serif text-[clamp(3.5rem,9vw,8rem)] leading-[0.88] tracking-[-0.04em] uppercase">
                Computare
              </h1>
            </div>
            <div className="lg:col-span-4 flex flex-col items-start lg:items-end gap-6">
              <p className="text-ash-400 text-[15px] leading-relaxed max-w-sm lg:text-right">
                Your financial data, on your terms. Extract, categorize, and
                store — without surrendering control.
              </p>
              <div className="border border-white/20 p-3">
                <img
                  src="/media/flipping-coin.gif"
                  alt="Dithered coin"
                  width={120}
                  height={120}
                  className="w-20 md:w-[120px] opacity-80"
                  loading="eager"
                />
              </div>
            </div>
          </div>
          <div className="h-px bg-white/10 mt-8 md:mt-12" />
        </div>
      </section>

      {/* ══ SECTION 02: Philosophy (White) ══ */}
      <section
        id="about"
        className="bg-paper text-ink py-24 md:py-32 lg:py-40 px-5 md:px-10 lg:px-16 relative overflow-hidden"
      >
        <div className="absolute top-8 right-10 md:right-16 font-serif text-[clamp(8rem,20vw,16rem)] leading-none text-ash-100 select-none pointer-events-none">
          02
        </div>
        <div className="max-w-[1400px] mx-auto relative">
          <div className="max-w-[800px] space-y-10">
            <ScrollReveal>
              <p className="font-serif text-3xl md:text-[40px] leading-[1.25] tracking-[-0.02em] border-l-2 border-gold pl-6 md:pl-8">
                Open-source by default.
              </p>
            </ScrollReveal>
            <ScrollReveal delay={80}>
              <p className="font-serif text-3xl md:text-[40px] leading-[1.25] tracking-[-0.02em] border-l-2 border-gold pl-6 md:pl-8">
                Your data, your servers, your terms.
              </p>
            </ScrollReveal>
            <ScrollReveal delay={160}>
              <p className="font-serif text-3xl md:text-[40px] leading-[1.25] tracking-[-0.02em] border-l-2 border-gold pl-6 md:pl-8">
                Built for decades of financial history.
              </p>
            </ScrollReveal>
          </div>
        </div>
      </section>

      {/* ══ SECTION 03: How It Works (Black) ══ */}
      <section
        id="system"
        className="bg-ink text-paper py-24 md:py-32 lg:py-40 px-5 md:px-10 lg:px-16 relative overflow-hidden"
      >
        <div className="absolute top-8 right-10 md:right-16 font-serif text-[clamp(8rem,20vw,16rem)] leading-none text-white/[0.03] select-none pointer-events-none">
          03
        </div>
        <div className="max-w-[1400px] mx-auto">
          <ScrollReveal>
            <div className="flex items-baseline gap-4 mb-16 md:mb-20">
              <div className="h-px bg-white/20 flex-1" />
              <h2 className="font-serif text-3xl md:text-4xl tracking-[-0.02em] shrink-0">
                The Pipeline
              </h2>
              <div className="h-px bg-white/20 flex-1" />
            </div>
          </ScrollReveal>
          <div className="grid md:grid-cols-3 gap-4 md:gap-6">
            {[
              {
                num: "01",
                title: "Extract",
                desc: "PDFs and CSVs from Scotiabank, Wealthsimple, and American Express. AI vision fallback when confidence drops.",
                tech: "pdfplumber + Claude Vision",
              },
              {
                num: "02",
                title: "Categorize",
                desc: "Description rules, merchant cache, then GPT-4o-mini. Most transactions resolve from cache at zero cost.",
                tech: "13 categories, 33 subcategories",
              },
              {
                num: "03",
                title: "Store",
                desc: "PostgreSQL with RLS, 9 materialized views, full export. Self-host or use managed hosting.",
                tech: "Supabase + FastAPI REST API",
              },
            ].map((step, i) => (
              <ScrollReveal key={step.num} delay={i * 80}>
                <div
                  className="border border-white/10 p-6 md:p-8 h-full relative"
                  style={{ marginTop: `${i * 24}px` }}
                >
                  <span className="font-code text-gold text-xs">
                    {step.num}
                  </span>
                  <h3 className="font-serif text-2xl md:text-3xl mt-3 mb-4">
                    {step.title}
                  </h3>
                  <p className="text-ash-400 text-[15px] leading-relaxed">
                    {step.desc}
                  </p>
                  <p className="font-code text-xs text-ash-600 mt-6 pt-4 border-t border-white/5">
                    {step.tech}
                  </p>
                </div>
              </ScrollReveal>
            ))}
          </div>
        </div>
      </section>

      {/* ══ SECTION 04: Data Ownership (White) ══ */}
      <section className="bg-paper text-ink py-24 md:py-32 lg:py-40 px-5 md:px-10 lg:px-16 relative overflow-hidden">
        <div className="absolute top-8 right-10 md:right-16 font-serif text-[clamp(8rem,20vw,16rem)] leading-none text-ash-100 select-none pointer-events-none">
          04
        </div>
        <div className="max-w-[1400px] mx-auto">
          <div className="grid lg:grid-cols-2 gap-12 lg:gap-20">
            <ScrollReveal>
              <h2 className="font-serif text-4xl md:text-5xl tracking-[-0.02em] leading-[1.1]">
                Your data never leaves your control.
              </h2>
            </ScrollReveal>
            <ScrollReveal delay={100}>
              <div className="space-y-6">
                {[
                  {
                    title: "Self-host everything",
                    desc: "Run Computare on your own infrastructure — database, API, extraction pipeline.",
                  },
                  {
                    title: "Export without limits",
                    desc: "CSV, JSON, SQL dump. No lock-in. No rate limits. No premium tier.",
                  },
                  {
                    title: "No credential scraping",
                    desc: "Upload your own statements. We never ask for your bank login.",
                  },
                  {
                    title: "Row-level security",
                    desc: "PostgreSQL RLS on every table. Multi-tenant isolation by default.",
                  },
                ].map((item) => (
                  <div
                    key={item.title}
                    className="flex gap-4 pb-6 border-b border-ash-200 last:border-0 last:pb-0"
                  >
                    <div className="w-2 h-2 bg-gold rounded-full mt-2 shrink-0" />
                    <div>
                      <h3 className="font-medium text-sm mb-1">
                        {item.title}
                      </h3>
                      <p className="text-ash-600 text-[15px] leading-relaxed">
                        {item.desc}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            </ScrollReveal>
          </div>
        </div>
      </section>

      {/* ══ SECTION 05: Open Source (Green) ══ */}
      <section className="bg-forest text-paper py-24 md:py-32 lg:py-40 px-5 md:px-10 lg:px-16 relative overflow-hidden">
        <div className="absolute top-8 right-10 md:right-16 font-serif text-[clamp(8rem,20vw,16rem)] leading-none text-white/[0.04] select-none pointer-events-none">
          05
        </div>
        <div className="max-w-[1400px] mx-auto">
          <div className="grid lg:grid-cols-2 gap-12 lg:gap-20">
            <ScrollReveal>
              <p className="text-xs tracking-[0.3em] uppercase text-white/40 mb-4">
                Open Source
              </p>
              <h2 className="font-serif text-3xl md:text-4xl tracking-[-0.02em] mb-6">
                MIT Licensed. Read every line.
              </h2>
              <p className="text-white/60 leading-relaxed max-w-lg">
                Computare is built in the open. No black boxes, no hidden data
                flows, no surprise monetisation. Fork it. Modify it. Host it.
              </p>
            </ScrollReveal>
            <ScrollReveal delay={100}>
              <div className="bg-ink/50 border border-white/10 p-6 font-code text-sm leading-loose">
                <p>
                  <span className="text-gold">$</span>{" "}
                  <span className="text-white/80">
                    git clone https://github.com/computare/computare
                  </span>
                </p>
                <p>
                  <span className="text-gold">$</span>{" "}
                  <span className="text-white/80">cd computare</span>
                </p>
                <p>
                  <span className="text-gold">$</span>{" "}
                  <span className="text-white/80">pip install -e .</span>
                </p>
                <p>
                  <span className="text-gold">$</span>{" "}
                  <span className="text-white/80">supabase start</span>
                </p>
                <p>
                  <span className="text-gold">$</span>{" "}
                  <span className="text-white/80">pnpm dev</span>
                </p>
              </div>
            </ScrollReveal>
          </div>
        </div>
      </section>

      {/* ══ SECTION 06: Vision (Black) ══ */}
      <section className="bg-ink text-paper py-24 md:py-32 lg:py-40 px-5 md:px-10 lg:px-16 relative overflow-hidden">
        <div className="absolute top-8 right-10 md:right-16 font-serif text-[clamp(8rem,20vw,16rem)] leading-none text-white/[0.03] select-none pointer-events-none">
          06
        </div>
        <div className="absolute inset-0 flex items-center justify-center opacity-[0.04] pointer-events-none">
          <img
            src="/media/flying-money.gif"
            alt=""
            className="w-[500px]"
            aria-hidden="true"
          />
        </div>
        <div className="max-w-[800px] mx-auto text-center relative">
          <ScrollReveal>
            <blockquote className="font-serif italic text-3xl md:text-[48px] leading-[1.15] tracking-[-0.02em]">
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

      {/* ══ SECTION 07: Statistics + CTA (White) ══ */}
      <section className="bg-paper text-ink py-24 md:py-32 lg:py-40 px-5 md:px-10 lg:px-16 relative overflow-hidden">
        <div className="absolute top-8 right-10 md:right-16 font-serif text-[clamp(8rem,20vw,16rem)] leading-none text-ash-100 select-none pointer-events-none">
          07
        </div>
        <div className="max-w-[1400px] mx-auto">
          {/* Stats */}
          <ScrollReveal>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-8 md:gap-12 mb-20 md:mb-28">
              {[
                { value: 13, label: "Categories" },
                { value: 33, label: "Subcategories" },
                { value: 3, label: "Institutions" },
                { value: 9, label: "Materialized Views" },
              ].map((stat) => (
                <div key={stat.label} className="text-center">
                  <p className="font-code text-4xl md:text-5xl text-ink">
                    <Counter target={stat.value} />
                  </p>
                  <p className="text-ash-400 text-xs tracking-wider uppercase mt-2">
                    {stat.label}
                  </p>
                </div>
              ))}
            </div>
          </ScrollReveal>

          {/* CTA */}
          <div className="h-px bg-ink mb-16 md:mb-20" />
          <ScrollReveal>
            <div className="text-center">
              <h2 className="font-serif text-4xl md:text-5xl tracking-[-0.02em] mb-4">
                Own your financial history.
              </h2>
              <p className="text-ash-600 mb-10">
                Free. Open-source. Self-hostable.
              </p>
              <div className="flex flex-col sm:flex-row gap-4 justify-center">
                <a
                  href="https://github.com/computare/computare"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center justify-center bg-ink text-paper px-8 py-3 text-sm font-medium hover:bg-ash-800 transition-colors duration-150"
                >
                  View on GitHub
                </a>
                <a
                  href="/docs"
                  className="inline-flex items-center justify-center border border-ash-200 text-ink px-8 py-3 text-sm hover:border-ash-400 transition-colors duration-150"
                >
                  Documentation
                </a>
              </div>
            </div>
          </ScrollReveal>
        </div>
      </section>

      {/* ── Footer ── */}
      <footer className="bg-ink text-ash-600 py-8 px-5 md:px-10 lg:px-16">
        <div className="max-w-[1400px] mx-auto flex flex-col sm:flex-row items-center justify-between gap-4 text-sm">
          <div className="flex items-center gap-3">
            <span className="font-serif text-paper text-lg">C</span>
            <span className="text-xs text-ash-600">
              &copy; 2026 Computare. MIT License.
            </span>
          </div>
          <div className="flex gap-6 text-xs">
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
