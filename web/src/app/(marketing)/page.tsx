import { ScrollReveal } from "@/components/marketing/scroll-reveal";
import { ScrollTypewriterSequence } from "@/components/marketing/scroll-typewriter";
import { ShineHeadline } from "@/components/marketing/shine-headline";
import { ASCIIAnimation } from "@/components/marketing/ascii-animation";
import { Counter } from "@/components/marketing/counter";
import Link from "next/link";
import type { Metadata } from "next";

const SITE_URL = "https://computare.finance";

export const metadata: Metadata = {
  title: "Open-Source Personal Finance for Canadians",
  description:
    "Import Scotiabank, Wealthsimple, and American Express statements. Self-host your financial data, categorize spending with AI, and own your history — no credential scraping, no lock-in.",
  alternates: {
    canonical: SITE_URL,
  },
  openGraph: {
    title: "Computare — Open-Source Personal Finance for Canadians",
    description:
      "Import bank statements, categorize spending with AI, and self-host your financial history. Supports Scotiabank, Wealthsimple, and American Express.",
    url: SITE_URL,
    type: "website",
  },
  twitter: {
    card: "summary_large_image",
    title: "Computare — Open-Source Personal Finance for Canadians",
    description:
      "Import bank statements, categorize spending with AI, and self-host your financial history.",
  },
};

function JsonLd() {
  const schema = [
    {
      "@context": "https://schema.org",
      "@type": "WebSite",
      name: "Computare",
      url: SITE_URL,
      description:
        "Open-source personal finance platform for Canadians. Import bank statements, categorize spending with AI, and self-host your financial data.",
    },
    {
      "@context": "https://schema.org",
      "@type": "SoftwareApplication",
      name: "Computare",
      url: SITE_URL,
      applicationCategory: "FinanceApplication",
      operatingSystem: "Web",
      license: "https://opensource.org/licenses/MIT",
      offers: {
        "@type": "Offer",
        price: "0",
        priceCurrency: "CAD",
      },
      description:
        "Open-source personal finance platform that extracts transactions from Canadian bank statements, categorizes them with AI, detects subscriptions, and stores everything in PostgreSQL. Self-host or use managed hosting.",
      featureList: [
        "PDF and CSV statement extraction",
        "3-tier AI categorization pipeline",
        "Subscription detection",
        "Self-hosted PostgreSQL storage",
        "Row-level security",
        "Full data export (CSV, JSON, SQL)",
        "Scotiabank, Wealthsimple, and American Express support",
      ].join(", "),
    },
    {
      "@context": "https://schema.org",
      "@type": "Organization",
      name: "Computare",
      url: SITE_URL,
      logo: `${SITE_URL}/favicon.ico`,
    },
  ];

  return (
    <script
      type="application/ld+json"
      dangerouslySetInnerHTML={{ __html: JSON.stringify(schema) }}
    />
  );
}

export default function Home() {
  return (
    <main className="bg-paper text-ink min-h-screen selection:bg-ink selection:text-paper">
      <JsonLd />

      {/* ── Navigation ── */}
      <nav className="fixed top-0 inset-x-0 z-50 bg-paper/80 backdrop-blur-md border-b border-ash-200">
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
              href="#institutions"
              className="hidden sm:block hover:text-ink transition-colors duration-150"
            >
              Institutions
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
              className="hidden sm:inline-flex items-center gap-1.5 hover:text-ink transition-colors duration-150"
            >
              <svg
                viewBox="0 0 16 16"
                fill="currentColor"
                className="w-4 h-4"
                aria-hidden="true"
              >
                <path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0016 8c0-4.42-3.58-8-8-8z" />
              </svg>
              <span className="hidden md:inline">GitHub</span>
            </a>
            <Link
              href="/docs"
              className="hidden sm:inline-flex items-center justify-center border border-ash-200 text-ink px-3 py-1 text-xs hover:border-ash-400 transition-colors duration-150"
            >
              Docs
            </Link>
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
          Open-source personal finance for Canadians.
        </p>
        <p className="text-ash-400 text-sm mt-4 max-w-lg text-center leading-relaxed relative">
          Import bank statements from Scotiabank, Wealthsimple, and American
          Express. Categorize spending with AI. Self-host your financial history
          — no credential scraping, no lock-in.
        </p>
        <div className="flex flex-col sm:flex-row gap-3 mt-10 relative">
          <a
            href="#how"
            className="inline-flex items-center justify-center border border-ash-200 text-ink px-8 py-3 text-sm hover:border-ash-400 transition-colors duration-150"
          >
            How it works
          </a>
        </div>
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
                desc: "PDFs and CSVs from Scotiabank, Wealthsimple, and American Express. Position-based extraction with AI vision fallback for low-confidence scans.",
              },
              {
                num: "02",
                title: "Categorize",
                desc: "3-tier pipeline: description rules first, merchant cache second, LLM third. Most transactions resolve from cache at zero cost. 13 categories, 33 subcategories.",
              },
              {
                num: "03",
                title: "Store",
                desc: "PostgreSQL with row-level security, 9 materialized views, and full export to CSV, JSON, or SQL. Self-host or use managed hosting.",
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

      {/* ── Supported Institutions ── */}
      <section
        id="institutions"
        className="py-24 md:py-32 lg:py-40 px-5 md:px-10 lg:px-20"
      >
        <div className="max-w-[1280px] mx-auto">
          <ScrollReveal>
            <p className="text-xs tracking-[0.25em] uppercase text-ash-400 mb-8">
              Supported Institutions
            </p>
          </ScrollReveal>
          <ScrollReveal delay={80}>
            <h2 className="font-serif text-3xl md:text-4xl tracking-[-0.02em] mb-12">
              Built for Canadian banking.
            </h2>
          </ScrollReveal>
          <div className="grid md:grid-cols-3 gap-12 md:gap-16">
            {[
              {
                name: "Scotiabank",
                types: "Chequing, Credit Card, iTRADE",
                format: "PDF statements",
                desc: "Position-based word extraction with AI vision fallback for low-confidence scans. Supports statement formats from 2018 onward.",
              },
              {
                name: "Wealthsimple",
                types: "TFSA, Spending, Credit Card, Crypto",
                format: "CSV exports",
                desc: "Direct CSV parsing for all account types. Clean data, zero ambiguity, full transaction history.",
              },
              {
                name: "American Express",
                types: "Credit Card",
                format: "Year-end CSV summaries",
                desc: "Structured year-end summaries parsed directly. Complete annual spending at a glance.",
              },
            ].map((inst, i) => (
              <ScrollReveal key={inst.name} delay={i * 80}>
                <div className="border border-ash-200 p-6">
                  <h3 className="font-serif text-xl mb-1">{inst.name}</h3>
                  <p className="text-ash-400 text-xs mb-3">
                    {inst.types} &middot; {inst.format}
                  </p>
                  <p className="text-ash-600 leading-relaxed text-[15px]">
                    {inst.desc}
                  </p>
                </div>
              </ScrollReveal>
            ))}
          </div>
        </div>
      </section>

      {/* ── Data Ownership ── */}
      <section className="py-24 md:py-32 lg:py-40 px-5 md:px-10 lg:px-20 bg-ash-100">
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
                desc: "Run Computare on your own infrastructure. Supabase, PostgreSQL, and the extraction pipeline — all under your roof. No third-party data access.",
              },
              {
                title: "Export without limits",
                desc: "CSV, JSON, SQL. Your data is never locked in. Move it, query it, pipe it into whatever tools you need.",
              },
              {
                title: "No credential scraping",
                desc: "Computare never asks for your bank passwords. You upload your own statements. Your credentials stay where they belong — with you.",
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

      {/* ── Privacy & Data Flow ── */}
      <section className="py-24 md:py-32 lg:py-40 px-5 md:px-10 lg:px-20">
        <div className="max-w-[1280px] mx-auto">
          <ScrollReveal>
            <p className="text-xs tracking-[0.25em] uppercase text-ash-400 mb-8">
              Privacy
            </p>
          </ScrollReveal>
          <ScrollReveal delay={80}>
            <h2 className="font-serif text-3xl md:text-4xl tracking-[-0.02em] mb-12">
              What stays local. What doesn&apos;t.
            </h2>
          </ScrollReveal>
          <div className="grid md:grid-cols-3 gap-12 md:gap-16">
            <ScrollReveal delay={0}>
              <div>
                <h3 className="font-serif text-xl mb-3 text-sage">
                  Always local
                </h3>
                <ul className="text-ash-600 text-[15px] leading-relaxed space-y-2">
                  <li>Your bank statements and CSV files</li>
                  <li>Transaction data in your PostgreSQL database</li>
                  <li>Category rules and merchant cache</li>
                  <li>Dashboard and visualizations</li>
                </ul>
              </div>
            </ScrollReveal>
            <ScrollReveal delay={80}>
              <div>
                <h3 className="font-serif text-xl mb-3 text-gold">
                  Sent to LLM
                </h3>
                <ul className="text-ash-600 text-[15px] leading-relaxed space-y-2">
                  <li>
                    Transaction descriptions only when rules and cache miss
                  </li>
                  <li>No amounts, no account numbers, no personal info</li>
                  <li>Covers ~15% of transactions after initial cache fill</li>
                </ul>
              </div>
            </ScrollReveal>
            <ScrollReveal delay={160}>
              <div>
                <h3 className="font-serif text-xl mb-3 text-ink">
                  Never leaves
                </h3>
                <ul className="text-ash-600 text-[15px] leading-relaxed space-y-2">
                  <li>Bank credentials — Computare never asks for them</li>
                  <li>Full transaction amounts over the network</li>
                  <li>Personally identifiable information</li>
                  <li>Anything you don&apos;t upload yourself</li>
                </ul>
              </div>
            </ScrollReveal>
          </div>
        </div>
      </section>

      {/* ── Divider ── */}
      <div className="max-w-[1280px] mx-auto px-5 md:px-10 lg:px-20">
        <div className="h-px bg-ash-200" />
      </div>

      {/* ── Why Computare ── */}
      <section className="py-24 md:py-32 lg:py-40 px-5 md:px-10 lg:px-20">
        <div className="max-w-[800px] mx-auto">
          <ScrollReveal>
            <p className="text-xs tracking-[0.25em] uppercase text-ash-400 mb-8">
              Why Computare
            </p>
          </ScrollReveal>
          <ScrollReveal delay={80}>
            <h2 className="font-serif text-3xl md:text-4xl tracking-[-0.02em] mb-12">
              Not another Mint replacement.
            </h2>
          </ScrollReveal>
          <div className="space-y-8">
            {[
              {
                vs: "Mint / YNAB",
                us: "Computare",
                their: "Requires bank login credentials via Plaid or similar scraping services. Your data lives on their servers.",
                ours:
                  "You upload your own statements. No credentials shared. Data lives in your own database.",
              },
              {
                vs: "Plaid aggregation",
                us: "Computare",
                their: "Third-party service reads your transactions. You depend on their uptime and pricing.",
                ours:
                  "Self-hosted extraction pipeline. Position-based parsing runs locally. AI categorization is optional and only for cache misses.",
              },
              {
                vs: "Closed finance apps",
                us: "Computare",
                their: "Data export is limited or nonexistent. Switching tools means starting over.",
                ours:
                  "Full export to CSV, JSON, or SQL. Your data is always portable. MIT licensed — fork it, modify it, host it.",
              },
            ].map((row, i) => (
              <ScrollReveal key={row.vs} delay={i * 80}>
                <div className="grid md:grid-cols-2 gap-6 md:gap-12">
                  <div className="border-l-2 border-ash-200 pl-4">
                    <p className="text-xs tracking-[0.2em] uppercase text-ash-400 mb-1">
                      {row.vs}
                    </p>
                    <p className="text-ash-600 text-[15px] leading-relaxed">
                      {row.their}
                    </p>
                  </div>
                  <div className="border-l-2 border-forest pl-4">
                    <p className="text-xs tracking-[0.2em] uppercase text-forest mb-1">
                      {row.us}
                    </p>
                    <p className="text-ink text-[15px] leading-relaxed">
                      {row.ours}
                    </p>
                  </div>
                </div>
              </ScrollReveal>
            ))}
          </div>
        </div>
      </section>

      {/* ── Open Source ── */}
      <section
        id="open-source"
        className="py-24 md:py-32 lg:py-40 px-5 md:px-10 lg:px-20 bg-ash-100"
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
                <span className="text-sage">$</span> computare init
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
          <p>&copy; {new Date().getFullYear()} Computare. MIT License.</p>
          <div className="flex items-center gap-6">
            <a
              href="/docs"
              className="hover:text-ink transition-colors duration-150"
            >
              Docs
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
      </footer>
    </main>
  );
}