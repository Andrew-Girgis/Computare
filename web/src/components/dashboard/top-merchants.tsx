import { formatCurrency } from "@/lib/utils";
import { CATEGORY_COLORS } from "@/lib/constants";

interface Merchant {
  merchant_name: string | null;
  total_spent: number | null;
  transaction_count: number | null;
  category: string | null;
}

export function TopMerchants({ merchants }: { merchants: Merchant[] }) {
  if (!merchants.length) {
    return (
      <p className="text-ash-400 text-sm font-code py-4">No merchant data yet</p>
    );
  }

  const maxSpend = Math.max(...merchants.map((m) => Math.abs(m.total_spent ?? 0)));

  return (
    <div className="space-y-2.5">
      {merchants.map((m, i) => {
        const spent = Math.abs(m.total_spent ?? 0);
        const pct = maxSpend > 0 ? (spent / maxSpend) * 100 : 0;
        const catColor = m.category ? CATEGORY_COLORS[m.category] : "#A3A3A3";

        return (
          <div key={m.merchant_name ?? i}>
            <div className="flex items-center justify-between mb-1">
              <div className="flex items-center gap-2 min-w-0">
                <span className="font-code text-[10px] text-ash-300 w-4 shrink-0">
                  {String(i + 1).padStart(2, "0")}
                </span>
                <span className="text-sm font-body text-ink truncate">
                  {m.merchant_name ?? "Unknown"}
                </span>
              </div>
              <span className="font-code text-xs text-ash-600 shrink-0 ml-2">
                {formatCurrency(spent, true)}
              </span>
            </div>
            <div className="ml-6 h-0.5 bg-ash-100 rounded-full overflow-hidden">
              <div
                className="h-full rounded-full transition-all duration-500"
                style={{ width: `${pct}%`, backgroundColor: catColor }}
              />
            </div>
          </div>
        );
      })}
    </div>
  );
}
