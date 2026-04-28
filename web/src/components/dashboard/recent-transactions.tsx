import { formatCurrency, formatDate } from "@/lib/utils";
import { CATEGORY_COLORS } from "@/lib/constants";

interface Transaction {
  id: string;
  date: string;
  merchant: string | null;
  description: string;
  category: string | null;
  amount: number;
  account_name?: string;
}

export function RecentTransactions({ transactions }: { transactions: Transaction[] }) {
  if (!transactions.length) {
    return (
      <div className="py-8 text-center">
        <p className="text-ash-400 text-sm font-code">No transactions yet</p>
      </div>
    );
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-ash-200">
            <th className="text-left py-2 px-4 text-xs tracking-[0.15em] uppercase text-ash-400 font-code font-normal">
              Date
            </th>
            <th className="text-left py-2 px-4 text-xs tracking-[0.15em] uppercase text-ash-400 font-code font-normal">
              Merchant
            </th>
            <th className="text-left py-2 px-4 text-xs tracking-[0.15em] uppercase text-ash-400 font-code font-normal hidden md:table-cell">
              Category
            </th>
            <th className="text-left py-2 px-4 text-xs tracking-[0.15em] uppercase text-ash-400 font-code font-normal hidden lg:table-cell">
              Account
            </th>
            <th className="text-right py-2 px-4 text-xs tracking-[0.15em] uppercase text-ash-400 font-code font-normal">
              Amount
            </th>
          </tr>
        </thead>
        <tbody>
          {transactions.map((txn) => {
            const catColor = txn.category
              ? CATEGORY_COLORS[txn.category]
              : "#A3A3A3";
            return (
              <tr
                key={txn.id}
                className="border-b border-ash-100 hover:bg-ash-100/50 transition-colors duration-100"
              >
                <td className="py-2.5 px-4 font-code text-xs text-ash-400 whitespace-nowrap">
                  {formatDate(txn.date)}
                </td>
                <td className="py-2.5 px-4 font-body text-sm text-ink max-w-[200px] truncate">
                  {txn.merchant || txn.description}
                </td>
                <td className="py-2.5 px-4 hidden md:table-cell">
                  {txn.category ? (
                    <span
                      className="inline-flex items-center gap-1.5 text-xs font-code px-2 py-0.5"
                      style={{ color: catColor, backgroundColor: catColor + "18" }}
                    >
                      {txn.category}
                    </span>
                  ) : (
                    <span className="text-xs text-ash-300 font-code">—</span>
                  )}
                </td>
                <td className="py-2.5 px-4 hidden lg:table-cell">
                  <span className="text-xs text-ash-400 font-code">
                    {txn.account_name ?? "—"}
                  </span>
                </td>
                <td
                  className={`py-2.5 px-4 font-code text-sm text-right whitespace-nowrap ${
                    txn.amount >= 0 ? "text-[#4A7C5C]" : "text-ink"
                  }`}
                >
                  {formatCurrency(txn.amount)}
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
