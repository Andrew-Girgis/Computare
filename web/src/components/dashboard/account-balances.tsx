import { formatCurrency } from "@/lib/utils";

interface Account {
  id: string;
  name: string;
  account_type: string;
  institution: string;
  balance: number | null;
}

const TYPE_LABEL: Record<string, string> = {
  chequing: "Chequing",
  credit_card: "Credit Card",
  tfsa: "TFSA",
  rrsp: "RRSP",
  non_registered: "Non-Reg.",
  spending: "Cash",
  crypto: "Crypto",
  savings: "Savings",
};

export function AccountBalances({
  accounts,
  hidden = false,
}: {
  accounts: Account[];
  hidden?: boolean;
}) {
  if (!accounts.length) {
    return (
      <p className="text-ash-400 text-sm font-code py-4">No accounts yet</p>
    );
  }

  return (
    <div className="space-y-2">
      {accounts.map((acct) => (
        <div key={acct.id} className="flex items-center justify-between py-2 border-b border-ash-100 last:border-0">
          <div className="min-w-0">
            <p className="text-sm font-body text-ink truncate">{acct.name}</p>
            <p className="text-xs font-code text-ash-400">
              {acct.institution} · {TYPE_LABEL[acct.account_type] ?? acct.account_type}
            </p>
          </div>
          <p
            className={`font-code text-sm font-semibold shrink-0 ml-3 transition-colors duration-300 ${
              hidden
                ? "text-ash-300"
                : acct.balance === null
                ? "text-ash-300"
                : acct.balance >= 0
                ? "text-ink"
                : "text-red-500"
            }`}
          >
            {hidden
              ? (acct.balance === null ? "—" : formatCurrency(acct.balance).replace(/[0-9]/g, "●"))
              : (acct.balance === null ? "—" : formatCurrency(acct.balance))}
          </p>
        </div>
      ))}
    </div>
  );
}
