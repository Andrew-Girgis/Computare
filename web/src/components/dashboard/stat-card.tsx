import { cn } from "@/lib/utils";

interface Props {
  label: string;
  value: string;
  sub?: string;
  subPositive?: boolean;
  accent?: boolean;
  className?: string;
}

export function StatCard({ label, value, sub, subPositive, accent, className }: Props) {
  return (
    <div
      className={cn(
        "bg-white border border-ash-200 p-5 flex flex-col justify-between",
        className
      )}
    >
      <p className="text-xs tracking-[0.15em] uppercase text-ash-400 font-code mb-3">
        {label}
      </p>
      <div>
        <p
          className={cn(
            "font-code text-2xl font-semibold leading-none",
            accent ? "text-[#C9A84C]" : "text-ink"
          )}
        >
          {value}
        </p>
        {sub && (
          <p
            className={cn(
              "text-xs font-code mt-2",
              subPositive ? "text-[#4A7C5C]" : "text-ash-400"
            )}
          >
            {sub}
          </p>
        )}
      </div>
    </div>
  );
}
