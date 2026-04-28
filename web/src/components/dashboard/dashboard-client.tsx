"use client";

import { useState, useMemo } from "react";
import { Eye, EyeOff } from "lucide-react";
import { EXPENSE_CATEGORIES } from "@/lib/constants";
import { formatCurrency } from "@/lib/utils";
import { StatCard } from "@/components/dashboard/stat-card";
import { CategoryDonut } from "@/components/dashboard/category-donut";
import { MonthlyTrend } from "@/components/dashboard/monthly-trend";
import { RecentTransactions } from "@/components/dashboard/recent-transactions";
import { AccountBalances } from "@/components/dashboard/account-balances";
import { TopMerchants } from "@/components/dashboard/top-merchants";
import { SubscriptionList } from "@/components/dashboard/subscription-list";

// ── Types ─────────────────────────────────────────────────────────────────────

interface CatRow {
  category: string | null;
  month: string | null;
  spent: number | null;
}

interface TxnRow {
  id: string;
  date: string;
  merchant: string | null;
  description: string;
  category: string | null;
  amount: number;
  account_name?: string;
}

interface MerchantRow {
  merchant_name: string | null;
  total_spent: number | null;
  transaction_count: number | null;
  category: string | null;
}

interface AccountRow {
  id: string;
  name: string;
  account_type: string;
  institution: string;
  balance: number | null;
}

interface SubRow {
  id: string | null;
  merchant: string | null;
  current_amount: number | null;
  frequency: string | null;
  next_expected_at: string | null;
  status: string | null;
}

interface SubCost {
  monthly_total: number | null;
  active_count: number | null;
}

interface DashboardClientProps {
  allCatData: CatRow[];
  allTransactions: TxnRow[];
  allMerchants: MerchantRow[];
  activeYearMonth: string;
  netWorth: number;
  activeSpend: number;
  spendDelta: number | null;
  spendLabel: string;
  subCost: SubCost | null;
  subs: SubRow[];
  accountBalances: AccountRow[];
  lifetimeSpending: number;
}

// ── Filter chip header ────────────────────────────────────────────────────────

interface FilterChip {
  label: string;
  onClear: () => void;
}

function PanelHeader({
  label,
  filters,
}: {
  label: string;
  filters?: FilterChip[];
}) {
  const active = filters?.filter((f) => f.label) ?? [];
  return (
    <div className="flex items-center justify-between mb-4">
      <p className="text-xs tracking-[0.15em] uppercase text-ash-400 font-code">
        {label}
      </p>
      {active.length > 0 && (
        <div className="flex items-center gap-1">
          {active.map((f) => (
            <button
              key={f.label}
              onClick={f.onClear}
              className="flex items-center gap-1 text-[10px] font-code text-[#C9A84C] border border-[#C9A84C]/40 px-1.5 py-0.5 hover:bg-[#C9A84C]/5 transition-colors"
            >
              × {f.label}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}

// ── Helpers ───────────────────────────────────────────────────────────────────

function monthLabel(ym: string): string {
  // ym = "YYYY-MM"
  return new Date(ym + "-01T12:00:00").toLocaleDateString("en-CA", {
    month: "short",
    year: "numeric",
  });
}

// ── Main component ────────────────────────────────────────────────────────────

export function DashboardClient({
  allCatData,
  allTransactions,
  allMerchants,
  activeYearMonth,
  netWorth,
  activeSpend,
  spendDelta,
  spendLabel,
  subCost,
  subs,
  accountBalances,
  lifetimeSpending,
}: DashboardClientProps) {
  const [activeCategory, setActiveCategory] = useState<string | null>(null);
  const [activeMonth, setActiveMonth] = useState<string | null>(null);
  const [revealed, setRevealed] = useState(false);
  const [netWorthRevealed, setNetWorthRevealed] = useState(false);
  const [trendMonths, setTrendMonths] = useState<number | null>(6); // null = all time

  // ── Derived: Category Donut ──────────────────────────────────────────────
  // If a month is selected, show that month's breakdown; else the default month.
  const donutData = useMemo(() => {
    const targetMonth = activeMonth ?? activeYearMonth;
    return allCatData
      .filter(
        (r) =>
          r.month?.startsWith(targetMonth) &&
          r.category &&
          EXPENSE_CATEGORIES.has(r.category) &&
          (r.spent ?? 0) > 0
      )
      .sort((a, b) => (b.spent ?? 0) - (a.spent ?? 0))
      .map((r) => ({ category: r.category!, spent: r.spent ?? 0 }));
  }, [allCatData, activeMonth, activeYearMonth]);

  // ── Derived: Monthly Trend ───────────────────────────────────────────────
  // If a category is selected, show only that category's monthly spend.
  const trendData = useMemo(() => {
    const source = activeCategory
      ? allCatData.filter((r) => r.category === activeCategory)
      : allCatData.filter((r) => r.category && EXPENSE_CATEGORIES.has(r.category));
    const map = new Map<string, number>();
    for (const row of source) {
      if (!row.month) continue;
      const ym = row.month.slice(0, 7);
      map.set(ym, (map.get(ym) ?? 0) + (row.spent ?? 0));
    }
    const sorted = Array.from(map.entries()).sort(([a], [b]) => a.localeCompare(b));
    const sliced = trendMonths !== null ? sorted.slice(-trendMonths) : sorted;
    return sliced.map(([month, spent]) => ({ month: month + "-01", spent }));
  }, [allCatData, activeCategory, trendMonths]);

  // ── Derived: Recent Transactions ─────────────────────────────────────────
  const filteredTxns = useMemo(() => {
    return allTransactions
      .filter((t) => !activeCategory || t.category === activeCategory)
      .filter((t) => !activeMonth || t.date?.startsWith(activeMonth))
      .slice(0, 15);
  }, [allTransactions, activeCategory, activeMonth]);

  // ── Derived: Top Merchants ───────────────────────────────────────────────
  const filteredMerchants = useMemo(() => {
    if (activeCategory) {
      return allMerchants.filter((m) => m.category === activeCategory).slice(0, 8);
    }
    // Merge same-name merchants across categories (view groups by merchant+category)
    const merged = new Map<string, MerchantRow>();
    for (const m of allMerchants) {
      const key = m.merchant_name ?? "";
      const existing = merged.get(key);
      if (existing) {
        merged.set(key, {
          ...existing,
          total_spent: (existing.total_spent ?? 0) + (m.total_spent ?? 0),
          transaction_count: (existing.transaction_count ?? 0) + (m.transaction_count ?? 0),
        });
      } else {
        merged.set(key, { ...m });
      }
    }
    return Array.from(merged.values())
      .sort((a, b) => (b.total_spent ?? 0) - (a.total_spent ?? 0))
      .slice(0, 8);
  }, [allMerchants, activeCategory]);

  // ── Toggle handlers ──────────────────────────────────────────────────────
  const handleCategoryClick = (category: string | null) => {
    setActiveCategory((prev) => (prev === category ? null : category));
  };

  const handleMonthClick = (month: string | null) => {
    setActiveMonth((prev) => (prev === month ? null : month));
  };

  // ── Chip helpers ─────────────────────────────────────────────────────────
  const categoryChip: FilterChip | null = activeCategory
    ? { label: activeCategory, onClear: () => setActiveCategory(null) }
    : null;
  const monthChip: FilterChip | null = activeMonth
    ? { label: monthLabel(activeMonth), onClear: () => setActiveMonth(null) }
    : null;

  return (
    <div className="grid grid-cols-12 gap-4">

      {/* ── Row 1: Stat cards ── */}
      <div className="col-span-12 md:col-span-5 bg-white border border-ash-200 p-5 flex flex-col justify-between">
        <div className="flex items-center justify-between mb-3">
          <p className="text-xs tracking-[0.15em] uppercase text-ash-400 font-code">
            Net Worth
          </p>
          <button
            onClick={() => setNetWorthRevealed((r) => !r)}
            aria-label={netWorthRevealed ? "Hide net worth" : "Show net worth"}
            className="text-ash-300 hover:text-ash-500 transition-colors"
          >
            {netWorthRevealed ? <EyeOff size={15} /> : <Eye size={15} />}
          </button>
        </div>
        <div>
          <p
            className="font-code text-3xl font-semibold leading-none transition-colors duration-300"
            style={{ color: netWorthRevealed ? "#C9A84C" : "#A3A3A3" }}
          >
            {netWorthRevealed
              ? formatCurrency(netWorth)
              : formatCurrency(netWorth).replace(/[0-9]/g, "●")}
          </p>
          <p className="text-xs font-code text-ash-400 mt-2">across all accounts</p>
        </div>
      </div>

      <StatCard
        className="col-span-12 sm:col-span-6 md:col-span-4"
        label={spendLabel}
        value={formatCurrency(activeSpend)}
        sub={
          spendDelta !== null
            ? `${spendDelta >= 0 ? "+" : ""}${spendDelta.toFixed(1)}% vs last month`
            : undefined
        }
        subPositive={spendDelta !== null && spendDelta < 0}
      />

      <StatCard
        className="col-span-12 sm:col-span-6 md:col-span-3"
        label="Subscriptions"
        value={subCost?.monthly_total ? formatCurrency(subCost.monthly_total) : "—"}
        sub={subCost?.active_count ? `${subCost.active_count} active` : "None detected"}
      />

      {/* ── Row 2: Charts ── */}
      <div className="col-span-12 md:col-span-5 bg-white border border-ash-200 p-5">
        <PanelHeader
          label="Spending by Category"
          filters={monthChip ? [monthChip] : []}
        />
        <div className="h-[280px]">
          {donutData.length > 0 ? (
            <CategoryDonut
              data={donutData}
              onCategoryClick={handleCategoryClick}
              activeCategory={activeCategory}
            />
          ) : (
            <div className="h-full flex items-center justify-center">
              <p className="text-ash-400 text-sm font-code">No data this month</p>
            </div>
          )}
        </div>
      </div>

      <div className="col-span-12 md:col-span-7 bg-white border border-ash-200 p-5">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <p className="text-xs tracking-[0.15em] uppercase text-ash-400 font-code">
              Monthly Spending Trend
            </p>
            {categoryChip && (
              <button
                onClick={categoryChip.onClear}
                className="flex items-center gap-1 text-[10px] font-code text-[#C9A84C] border border-[#C9A84C]/40 px-1.5 py-0.5 hover:bg-[#C9A84C]/5 transition-colors"
              >
                × {categoryChip.label}
              </button>
            )}
          </div>
          <div className="flex items-center gap-0.5">
            {([6, 12, null] as const).map((n) => (
              <button
                key={n ?? "all"}
                onClick={() => setTrendMonths(n)}
                className={`text-[10px] font-code px-2 py-0.5 transition-colors ${
                  trendMonths === n
                    ? "bg-ink text-paper"
                    : "text-ash-400 hover:text-ink border border-ash-200 hover:border-ash-400"
                }`}
              >
                {n === null ? "All" : `${n}M`}
              </button>
            ))}
          </div>
        </div>
        <div className="h-[280px]">
          <MonthlyTrend
            data={trendData}
            onMonthClick={handleMonthClick}
            activeMonth={activeMonth}
          />
        </div>
      </div>

      {/* ── Row 3: Recent Transactions ── */}
      <div className="col-span-12 bg-white border border-ash-200">
        <div className="px-5 pt-5 pb-3 border-b border-ash-100">
          <PanelHeader
            label="Recent Transactions"
            filters={[
              ...(categoryChip ? [categoryChip] : []),
              ...(monthChip ? [monthChip] : []),
            ]}
          />
        </div>
        <RecentTransactions transactions={filteredTxns} />
      </div>

      {/* ── Row 4: Accounts / Top Merchants / Subscriptions ── */}
      <div className="col-span-12 md:col-span-4 bg-white border border-ash-200 p-5">
        <p className="text-xs tracking-[0.15em] uppercase text-ash-400 font-code mb-4">
          Account Balances
        </p>
        <AccountBalances accounts={accountBalances} hidden={!netWorthRevealed} />
      </div>

      <div className="col-span-12 md:col-span-4 bg-white border border-ash-200 p-5">
        <PanelHeader
          label="Top Merchants"
          filters={categoryChip ? [categoryChip] : []}
        />
        <TopMerchants merchants={filteredMerchants} />
      </div>

      <div className="col-span-12 md:col-span-4 bg-white border border-ash-200 p-5">
        <p className="text-xs tracking-[0.15em] uppercase text-ash-400 font-code mb-4">
          Subscriptions
        </p>
        <SubscriptionList subscriptions={subs} />
      </div>

      {/* ── Lifetime Spending easter egg ── */}
      <div className="col-span-12 border border-ash-200 bg-white px-5 py-4 flex items-center justify-between">
        <div>
          <p className="text-xs tracking-[0.15em] uppercase text-ash-400 font-code">
            Lifetime Spending
          </p>
          <p className="text-[11px] font-code text-ash-300 mt-0.5">since day one</p>
        </div>
        <div className="flex items-center gap-2.5">
          <span
            className="font-code text-2xl font-semibold transition-colors duration-300"
            style={{
              color: revealed ? "#C9A84C" : "#A3A3A3",
              letterSpacing: revealed ? undefined : "0.04em",
            }}
          >
            {revealed
              ? formatCurrency(lifetimeSpending)
              : formatCurrency(lifetimeSpending).replace(/[0-9]/g, "●")}
          </span>
          <button
            onClick={() => setRevealed((r) => !r)}
            aria-label={revealed ? "Hide lifetime spending" : "Show lifetime spending"}
            className="text-ash-300 hover:text-ash-500 transition-colors"
          >
            {revealed ? <EyeOff size={15} /> : <Eye size={15} />}
          </button>
        </div>
      </div>

    </div>
  );
}
