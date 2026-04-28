import { formatCurrency } from "@/lib/utils";

interface Subscription {
  id: string | null;
  merchant: string | null;
  current_amount: number | null;
  frequency: string | null;
  next_expected_at: string | null;
  status: string | null;
}

function daysUntil(dateStr: string | null): number | null {
  if (!dateStr) return null;
  const diff = new Date(dateStr).getTime() - Date.now();
  return Math.ceil(diff / (1000 * 60 * 60 * 24));
}

export function SubscriptionList({ subscriptions }: { subscriptions: Subscription[] }) {
  if (!subscriptions.length) {
    return (
      <p className="text-ash-400 text-sm font-code py-4">
        No subscriptions detected yet
      </p>
    );
  }

  return (
    <div className="space-y-2">
      {subscriptions.map((sub, i) => {
        const days = daysUntil(sub.next_expected_at);
        const soon = days !== null && days <= 7;

        return (
          <div
            key={sub.id ?? i}
            className="flex items-center justify-between py-2 border-b border-ash-100 last:border-0"
          >
            <div className="min-w-0">
              <p className="text-sm font-body text-ink truncate">
                {sub.merchant ?? "Unknown"}
              </p>
              <p className="text-xs font-code text-ash-400">
                {sub.frequency ?? "monthly"}
                {days !== null && (
                  <span className={soon ? "text-[#C9A84C] ml-2" : "text-ash-300 ml-2"}>
                    · {days <= 0 ? "due" : `${days}d`}
                  </span>
                )}
              </p>
            </div>
            <p className="font-code text-sm text-ink shrink-0 ml-3">
              {sub.current_amount !== null
                ? formatCurrency(Math.abs(sub.current_amount))
                : "—"}
            </p>
          </div>
        );
      })}
    </div>
  );
}
