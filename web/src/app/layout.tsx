import { Analytics } from "@vercel/analytics/next";
import type { Metadata } from "next";
import {
  Geist,
  Geist_Mono,
  Instrument_Serif,
  Hanken_Grotesk,
  JetBrains_Mono,
} from "next/font/google";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

const instrumentSerif = Instrument_Serif({
  variable: "--font-instrument",
  subsets: ["latin"],
  weight: "400",
  style: ["normal", "italic"],
});

const hankenGrotesk = Hanken_Grotesk({
  variable: "--font-hanken",
  subsets: ["latin"],
});

const jetbrainsMono = JetBrains_Mono({
  variable: "--font-jetbrains",
  subsets: ["latin"],
});

const SITE_URL = "https://computare.finance";

export const metadata: Metadata = {
  metadataBase: new URL(SITE_URL),
  title: {
    default: "Computare — Open-Source Personal Finance for Canadians",
    template: "%s | Computare",
  },
  description:
    "Open-source personal finance platform for Canadians. Import Scotiabank, Wealthsimple, and American Express statements. Self-host, categorize with AI, and own your financial data — no credential scraping, no lock-in.",
  keywords: [
    "personal finance",
    "open source",
    "self-hosted",
    "Canadian banking",
    "Scotiabank",
    "Wealthsimple",
    "American Express",
    "bank statement parser",
    "expense tracker",
    "budget app",
    "financial data platform",
    "data ownership",
    "Supabase",
    "PostgreSQL",
  ],
  authors: [{ name: "Computare" }],
  creator: "Computare",
  openGraph: {
    type: "website",
    locale: "en_CA",
    url: SITE_URL,
    siteName: "Computare",
    title: "Computare — Open-Source Personal Finance for Canadians",
    description:
      "Import bank statements, categorize spending with AI, and self-host your financial history. Supports Scotiabank, Wealthsimple, and American Express.",
  },
  twitter: {
    card: "summary_large_image",
    title: "Computare — Open-Source Personal Finance for Canadians",
    description:
      "Import bank statements, categorize spending with AI, and self-host your financial history.",
  },
  robots: {
    index: true,
    follow: true,
  },
  alternates: {
    canonical: SITE_URL,
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <head>
        <noscript>
          <style
            dangerouslySetInnerHTML={{
              __html: `.c-reveal{opacity:1!important;transform:none!important}.c-hero>*{opacity:1!important;animation:none!important}`,
            }}
          />
        </noscript>
      </head>
      <body
        className={`${geistSans.variable} ${geistMono.variable} ${instrumentSerif.variable} ${hankenGrotesk.variable} ${jetbrainsMono.variable} antialiased`}
      >
        {children}
        <Analytics />
      </body>
    </html>
  );
}
