import { ScrollReveal } from "@/components/marketing/scroll-reveal";
import { ScrollTypewriterSequence } from "@/components/marketing/scroll-typewriter";
import { ShineHeadline } from "@/components/marketing/shine-headline";
import { ASCIIAnimation } from "@/components/marketing/ascii-animation";
import { Counter } from "@/components/marketing/counter";
import Link from "next/link";

export const metadata = {
  title: "Computare — Open-Source Personal Finance",
};

export default function Home() {
  return (
    <main className="bg-paper text-ink min-h-screen selection:bg-ink selection:text-paper">
      {/* ── Navigation ── */}
      <nav className="fixed top-0 inset-x-0 z-50 bg-paper border-b border-ash-200">
        <div className="max-w-[1280px] mx-auto px-5 md:px-10 lg:px-20 h-14 flex items-center justify-between">
          <Link href="/" className="font-serif italic text-lg">
            Computare
          </Link>
          <div className="flex items-center gap-6 text-sm text-ash-600">
            <a
              href="#how"
              className="hidden sm:block hover:text-ink transition-colors duration-150"
            >
              How it works
            </a>
            <a
              href="#open-source"
              className="hidden sm:block hover:text-ink transition-colors duration-150"
            >
              Open source
            </a>
            <a
              href="https://github.com/Andrew-Girgis/Computare"
              target="_blank"
              rel="noopener noreferrer"
              className="hover:text-ink transition-colors duration-150"
            >
              GitHub
            </a>
          </div>
        </div>
      </nav>

      {/* ── Hero ── */}
      <section className="min-h-screen flex flex-col items-center justify-center px-5 md:px-10 lg:px-20 c-hero relative overflow-hidden">
        {/* ASCII art animation — centered behind hero */}
        <div
          className="absolute inset-0 flex items-center justify-start pointer-events-none select-none overflow-hidden"
          aria-hidden="true"
        >
          <ASCIIAnimation
            className="hidden md:block text-ink/35 md:text-sm lg:text-base leading-[1.15] whitespace-pre -translate-x-1/8"
            fps={12}
          />
          <ASCIIAnimation
            className="block md:hidden text-ink/35 text-xs leading-[1.15] whitespace-pre -translate-x-1/8 -translate-y-7/8"
            fps={12}
            basePath="/ascii/soj_ascii_frames_mobile"
          />
        </div>

        <ShineHeadline className="font-serif italic text-7xl md:text-[96px] leading-[0.95] tracking-[-0.03em] text-center relative cursor-default">
          Computare
        </ShineHeadline>
        <div className="w-[120px] h-px bg-gold my-10 md:my-12 relative" />
        <p className="text-ash-600 text-lg md:text-xl max-w-md text-center leading-relaxed relative">
          Your financial data, on your terms.
        </p>
        <p className="text-ash-400 text-sm mt-4 max-w-sm text-center leading-relaxed relative">
          Open-source personal finance infrastructure for Canadians who want
          long-term visibility without giving up control.
        </p>
      </section>

      {/* ── Philosophy ── */}
      <section className="py-24 md:py-32 lg:py-40 px-5 md:px-10 lg:px-20">
        <div className="max-w-[800px] mx-auto">
          <ScrollTypewriterSequence
            lines={[
              "Open-source by default.",
              "Data ownership is non-negotiable.",
              "Built for the long term.",
            ]}
            className="space-y-20 md:space-y-28"
            lineClassName="font-serif italic text-3xl md:text-[40px] leading-[1.25] tracking-[-0.02em]"
          />
        </div>
      </section>

      {/* ── Divider ── */}
      <div className="max-w-[1280px] mx-auto px-5 md:px-10 lg:px-20">
        <div className="h-px bg-ash-200" />
      </div>

      {/* ── How It Works ── */}
      <section id="how" className="py-24 md:py-32 lg:py-40 px-5 md:px-10 lg:px-20">
        <div className="max-w-[1280px] mx-auto">
          <ScrollReveal>
            <p className="text-xs tracking-[0.25em] uppercase text-ash-400 mb-16 md:mb-20">
              How it works
            </p>
          </ScrollReveal>
          <div className="grid md:grid-cols-3 gap-12 md:gap-16">
            {[
              {
                num: "01",
                title: "Extract",
                desc: "PDFs and CSVs from Scotiabank, Wealthsimple, and American Express. Position-based extraction with AI vision fallback.",
              },
              {
                num: "02",
                title: "Categorize",
                desc: "3-tier pipeline: description rules first, merchant cache second, LLM third. Most transactions resolve from cache at zero cost.",
              },
              {
                num: "03",
                title: "Store",
                desc: "PostgreSQL with row-level security, 9 materialized views, and full export capability. Self-host or use managed hosting.",
              },
            ].map((step, i) => (
              <ScrollReveal key={step.num} delay={i * 80}>
                <div>
                  <span className="font-code text-gold text-sm">
                    {step.num}
                  </span>
                  <h3 className="font-serif text-2xl md:text-3xl mt-3 mb-4">
                    {step.title}
                  </h3>
                  <p className="text-ash-600 leading-relaxed text-[15px]">
                    {step.desc}
                  </p>
                </div>
              </ScrollReveal>
            ))}
          </div>
        </div>
      </section>

      {/* ── Statistics ── */}
      <section className="py-16 md:py-24 px-5 md:px-10 lg:px-20 bg-ash-100">
        <div className="max-w-[1280px] mx-auto">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8 md:gap-12">
            {[
              { value: 13, suffix: "", label: "Categories" },
              { value: 33, suffix: "", label: "Subcategories" },
              { value: 3, suffix: "", label: "Institutions" },
              { value: 9, suffix: "", label: "Materialized views" },
            ].map((stat) => (
              <ScrollReveal key={stat.label}>
                <div className="text-center">
                  <p className="font-code text-3xl md:text-4xl text-ink">
                    <Counter target={stat.value} suffix={stat.suffix} />
                  </p>
                  <p className="text-ash-400 text-sm mt-2">{stat.label}</p>
                </div>
              </ScrollReveal>
            ))}
          </div>
        </div>
      </section>

      {/* ── Data Ownership ── */}
      <section className="py-24 md:py-32 lg:py-40 px-5 md:px-10 lg:px-20">
        <div className="max-w-[1280px] mx-auto">
          <ScrollReveal>
            <h2 className="font-serif text-4xl md:text-5xl tracking-[-0.02em] mb-16 md:mb-20 max-w-[600px]">
              Your data never leaves your control.
            </h2>
          </ScrollReveal>
          <div className="grid md:grid-cols-3 gap-12 md:gap-16">
            {[
              {
                title: "Self-host everything",
                desc: "Run Computare on your own infrastructure. Supabase, PostgreSQL, and the extraction pipeline — all under your roof.",
              },
              {
                title: "Export without limits",
                desc: "CSV, JSON, SQL. Your data is never locked in. Move it, query it, pipe it into whatever you need.",
              },
              {
                title: "No credential scraping",
                desc: "We never ask for your bank passwords. Upload your own statements. Keep your credentials where they belong.",
              },
            ].map((item, i) => (
              <ScrollReveal key={item.title} delay={i * 80}>
                <div>
                  <h3 className="font-serif text-xl mb-3">{item.title}</h3>
                  <p className="text-ash-600 leading-relaxed text-[15px]">
                    {item.desc}
                  </p>
                </div>
              </ScrollReveal>
            ))}
          </div>
        </div>
      </section>

      {/* ── Divider ── */}
      <div className="max-w-[1280px] mx-auto px-5 md:px-10 lg:px-20">
        <div className="h-px bg-ash-200" />
      </div>

      {/* ── Open Source ── */}
      <section
        id="open-source"
        className="py-24 md:py-32 lg:py-40 px-5 md:px-10 lg:px-20"
      >
        <div className="max-w-[800px] mx-auto">
          <ScrollReveal>
            <p className="text-xs tracking-[0.25em] uppercase text-ash-400 mb-8">
              Open Source
            </p>
          </ScrollReveal>
          <ScrollReveal delay={80}>
            <h2 className="font-serif text-3xl md:text-4xl tracking-[-0.02em] mb-8">
              MIT Licensed. Read every line.
            </h2>
          </ScrollReveal>
          <ScrollReveal delay={160}>
            <p className="text-ash-600 leading-relaxed mb-10 max-w-[520px]">
              Computare is built in the open. Fork it. Modify it. Host it. No
              black boxes, no hidden data flows, no surprise monetisation.
            </p>
          </ScrollReveal>
          <ScrollReveal delay={240}>
            <div className="bg-ink text-paper p-6 font-code text-sm leading-relaxed">
              <p className="text-ash-400">
                <span className="text-sage">$</span> git clone
                https://github.com/Andrew-Girgis/Computare
              </p>
              <p className="text-ash-400">
                <span className="text-sage">$</span> cd Computare
              </p>
              <p className="text-ash-400">
                <span className="text-sage">$</span> docker-compose up
              </p>
            </div>
          </ScrollReveal>
        </div>
      </section>

      {/* ── Vision ── */}
      <section className="py-24 md:py-32 lg:py-40 px-5 md:px-10 lg:px-20">
        <div className="max-w-[800px] mx-auto text-center">
          <ScrollReveal>
            <blockquote className="font-serif italic text-3xl md:text-[40px] leading-[1.25] tracking-[-0.02em]">
              Built for years of financial history, not quick wins.
            </blockquote>
          </ScrollReveal>
          <ScrollReveal delay={100}>
            <p className="text-ash-600 leading-relaxed mt-10 max-w-md mx-auto">
              Track a decade of transactions across every account. Computare
              treats your financial data as infrastructure — not as a
              feature to be gated or a product to be monetised.
            </p>
          </ScrollReveal>
        </div>
      </section>

      {/* ── CTA ── */}
      <section className="py-24 md:py-32 px-5 md:px-10 lg:px-20 border-t border-ash-200">
        <div className="max-w-[800px] mx-auto text-center">
          <ScrollReveal>
            <h2 className="font-serif text-3xl md:text-4xl tracking-[-0.02em] mb-8">
              Own your financial history.
            </h2>
          </ScrollReveal>
          <ScrollReveal delay={100}>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <a
                href="https://github.com/Andrew-Girgis/Computare"
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center justify-center bg-ink text-paper px-8 py-3 text-sm hover:bg-ash-800 transition-colors duration-150"
              >
                View on GitHub
              </a>
              <a
                href="/docs"
                className="inline-flex items-center justify-center border border-ash-200 text-ink px-8 py-3 text-sm hover:border-ash-400 transition-colors duration-150"
              >
                Read Documentation
              </a>
            </div>
          </ScrollReveal>
        </div>
      </section>

      {/* ── Footer ── */}
      <footer className="py-8 px-5 md:px-10 lg:px-20 border-t border-ash-200">
        <div className="max-w-[1280px] mx-auto flex flex-col sm:flex-row items-center justify-between gap-4 text-sm text-ash-400">
          <p>&copy; 2026 Computare. MIT License.</p>
          <a
            href="https://github.com/Andrew-Girgis/Computare"
            target="_blank"
            rel="noopener noreferrer"
            className="hover:text-ink transition-colors duration-150"
          >
            GitHub
          </a>
        </div>
      </footer>
    </main>
  );
}
