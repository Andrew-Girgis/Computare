"use client";

import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
} from "recharts";
import { formatCurrency, formatMonth } from "@/lib/utils";

interface MonthPoint {
  month: string;
  spent: number;
}

interface Props {
  data: MonthPoint[];
  onMonthClick?: (month: string | null) => void;
  activeMonth?: string | null;
}

export function MonthlyTrend({ data, onMonthClick, activeMonth }: Props) {
  if (!data.length) {
    return (
      <div className="h-full flex items-center justify-center">
        <p className="text-ash-400 text-sm font-code">No trend data yet</p>
      </div>
    );
  }

  return (
    <ResponsiveContainer width="100%" height="100%">
      <AreaChart
        data={data}
        margin={{ top: 4, right: 4, bottom: 0, left: 0 }}
        style={{ cursor: onMonthClick ? "pointer" : "default" }}
        onClick={(chartData) => {
          if (!onMonthClick || !chartData?.activeLabel) return;
          const label = chartData.activeLabel;
          if (typeof label !== "string") return;
          // activeLabel is "YYYY-MM-01" — extract "YYYY-MM"
          const clicked = label.slice(0, 7);
          onMonthClick(activeMonth === clicked ? null : clicked);
        }}
      >
        <defs>
          <linearGradient id="spendGrad" x1="0" y1="0" x2="0" y2="1">
            <stop offset="5%" stopColor="#4A7C5C" stopOpacity={0.3} />
            <stop offset="95%" stopColor="#4A7C5C" stopOpacity={0} />
          </linearGradient>
        </defs>
        <CartesianGrid strokeDasharray="3 3" stroke="#E5E5E5" vertical={false} />
        <XAxis
          dataKey="month"
          tickFormatter={formatMonth}
          tick={{ fontSize: 11, fontFamily: "var(--font-code)", fill: "#A3A3A3" }}
          axisLine={false}
          tickLine={false}
          dy={6}
        />
        <YAxis
          tickFormatter={(v) => formatCurrency(v, true)}
          tick={{ fontSize: 11, fontFamily: "var(--font-code)", fill: "#A3A3A3" }}
          axisLine={false}
          tickLine={false}
          width={64}
        />
        <Tooltip
          content={({ active, payload, label }) => {
            if (!active || !payload?.length) return null;
            return (
              <div className="bg-ink text-paper px-3 py-2 text-xs font-code shadow-lg">
                <p className="text-white/60 mb-0.5">{typeof label === "string" ? formatMonth(label) : label}</p>
                <p className="text-[#4A7C5C] font-semibold">
                  {formatCurrency(payload[0].value as number)}
                </p>
              </div>
            );
          }}
        />
        {/* Gold reference line on selected month */}
        {activeMonth && (
          <ReferenceLine
            x={activeMonth + "-01"}
            stroke="#C9A84C"
            strokeWidth={1.5}
            strokeDasharray="4 3"
          />
        )}
        <Area
          type="monotone"
          dataKey="spent"
          stroke="#4A7C5C"
          strokeWidth={2}
          fill="url(#spendGrad)"
          dot={{ fill: "#4A7C5C", strokeWidth: 0, r: 3 }}
          activeDot={{ fill: "#C9A84C", strokeWidth: 0, r: 4 }}
        />
      </AreaChart>
    </ResponsiveContainer>
  );
}
