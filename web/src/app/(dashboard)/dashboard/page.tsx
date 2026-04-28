import { createAdminClient } from "@/lib/supabase/server-admin";
import { Topbar } from "@/components/layout/topbar";
import { DashboardClient } from "@/components/dashboard/dashboard-client";
import { EXPENSE_CATEGORIES } from "@/lib/constants";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Dashboard",
  robots: { index: false, follow: false },
};

export default async function DashboardPage() {
  const supabase = await createAdminClient();

  // Use the latest transaction date as the reference point so balances and
  // spending always reflect actual data, not today's (possibly ahead) date.
  const { data: latestTxn } = await supabase
    .from("transactions")
    .select("date")
    .order("date", { ascending: false })
    .limit(1)
    .single();

  const dataDate = latestTxn?.date ?? new Date().toISOString().split("T")[0];
  // "YYYY-MM" derived from data date — robust against timezone suffixes
  const dataMonthDate = new Date(dataDate + "T12:00:00");
  const dataYearMonth = `${dataMonthDate.getFullYear()}-${String(dataMonthDate.getMonth() + 1).padStart(2, "0")}`;

  // Fetch all data in parallel
  const [
    netWorthRes,
    categoryRes,
    subCostRes,
    subsRes,
    txnsRes,
    accountsRes,
    merchantRes,
    lifetimeRes,
  ] = await Promise.all([
    supabase.rpc("get_total_balance", { p_date: dataDate }),
    supabase
      .from("monthly_spending_by_category")
      .select("category, month, spent")
      .order("month", { ascending: true }),
    supabase.from("monthly_subscription_cost").select("monthly_total, active_count").single(),
    supabase
      .from("active_subscriptions")
      .select("id, merchant, current_amount, frequency, next_expected_at, status")
      .order("next_expected_at", { ascending: true })
      .limit(8),
    supabase
      .from("transactions")
      .select("id, date, merchant, description, category, amount, account_id, accounts(name)")
      .order("date", { ascending: false })
      .limit(200),
    supabase
      .from("accounts")
      .select("id, name, account_type, is_active, institutions(name)")
      .eq("is_active", true),
    supabase
      .from("merchant_summary")
      .select("merchant_name, total_spent, transaction_count, category")
      .not("category", "in", "(Transfers,Income,Investment)")
      .order("total_spent", { ascending: false })
      .limit(20),
    supabase.rpc("get_lifetime_spending"),
  ]);

  // --- Net Worth ---
  const netWorth = (netWorthRes.data as number | null) ?? 0;

  // --- Spending: find most recent month with data, fall back gracefully ---
  const allCatData = categoryRes.data ?? [];

  // Get all unique months that have expense data, sorted descending
  const expenseMonths = Array.from(
    new Set(
      allCatData
        .filter((r) => r.category && EXPENSE_CATEGORIES.has(r.category) && (r.spent ?? 0) > 0)
        .map((r) => r.month?.slice(0, 7))
        .filter(Boolean)
    )
  ).sort((a, b) => b!.localeCompare(a!)) as string[];

  // Use the data month if it has data, otherwise the most recent month that does
  const activeYearMonth = expenseMonths.includes(dataYearMonth)
    ? dataYearMonth
    : (expenseMonths[0] ?? dataYearMonth);
  const prevYearMonth = expenseMonths[expenseMonths.indexOf(activeYearMonth) + 1] ?? null;

  const activeCats = allCatData.filter(
    (r) => r.month?.startsWith(activeYearMonth) && r.category && EXPENSE_CATEGORIES.has(r.category)
  );
  const prevCats = prevYearMonth
    ? allCatData.filter(
        (r) => r.month?.startsWith(prevYearMonth) && r.category && EXPENSE_CATEGORIES.has(r.category)
      )
    : [];

  const activeSpend = activeCats.reduce((s, r) => s + (r.spent ?? 0), 0);
  const prevSpend = prevCats.reduce((s, r) => s + (r.spent ?? 0), 0);
  const spendDelta =
    prevSpend > 0 ? ((activeSpend - prevSpend) / prevSpend) * 100 : null;

  // Label shows which month is actually displayed
  const isDataMonth = activeYearMonth === dataYearMonth;
  const spendLabel = isDataMonth
    ? `Spent in ${new Date(dataYearMonth + "-01T12:00:00").toLocaleDateString("en-CA", { month: "long", year: "numeric" })}`
    : `Spent in ${new Date(activeYearMonth + "-01T12:00:00").toLocaleDateString("en-CA", { month: "long", year: "numeric" })}`;

  // --- Subscriptions ---
  const subCost = subCostRes.data;
  const subs = subsRes.data ?? [];

  // --- Transactions with account name (200 rows for client-side filtering) ---
  const allTransactions = (txnsRes.data ?? []).map((t) => ({
    id: t.id,
    date: t.date,
    merchant: t.merchant,
    description: t.description,
    category: t.category,
    amount: t.amount,
    account_name: Array.isArray(t.accounts)
      ? t.accounts[0]?.name
      : (t.accounts as { name: string } | null)?.name,
  }));

  // --- Account balances ---
  const rawAccounts = accountsRes.data ?? [];
  const accountBalances = await Promise.all(
    rawAccounts.map(async (acct) => {
      const { data: bal } = await supabase.rpc("get_account_balance", {
        p_account_id: acct.id,
        p_date: dataDate,
      });
      const inst = Array.isArray(acct.institutions)
        ? acct.institutions[0]?.name
        : (acct.institutions as { name: string } | null)?.name;
      return {
        id: acct.id,
        name: acct.name,
        account_type: acct.account_type,
        institution: inst ?? "Unknown",
        balance: (bal as number | null) ?? null,
      };
    })
  );

  // Deduplicate by name as a safety net (fixed at DB level, but guard here too)
  const seenAccountNames = new Set<string>();
  const dedupedAccounts = accountBalances
    .sort((a, b) => Math.abs(b.balance ?? 0) - Math.abs(a.balance ?? 0))
    .filter((acct) => {
      if (seenAccountNames.has(acct.name)) return false;
      seenAccountNames.add(acct.name);
      return true;
    })
    .sort((a, b) => a.institution.localeCompare(b.institution) || a.name.localeCompare(b.name))
    .filter((acct) => (acct.balance ?? 0) !== 0);

  // --- Merchants (positive total_spent = SUM(ABS(amount)), view already filters debits) ---
  const allMerchants = merchantRes.data ?? [];

  // --- Lifetime spending (easter egg) ---
  const lifetimeSpending = (lifetimeRes.data as number | null) ?? 0;

  return (
    <div className="flex flex-col min-h-full">
      <Topbar title="Overview" subtitle={`data as of ${dataDate}`} />
      <div className="flex-1 p-6">
        <DashboardClient
          allCatData={allCatData}
          allTransactions={allTransactions}
          allMerchants={allMerchants}
          activeYearMonth={activeYearMonth}
          netWorth={netWorth}
          activeSpend={activeSpend}
          spendDelta={spendDelta}
          spendLabel={spendLabel}
          subCost={subCost}
          subs={subs}
          accountBalances={dedupedAccounts}
          lifetimeSpending={lifetimeSpending}
        />
      </div>
    </div>
  );
}
