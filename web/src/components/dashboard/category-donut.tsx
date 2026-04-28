"use client";

import {
  PieChart,
  Pie,
  Cell,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from "recharts";
import { CATEGORY_COLORS } from "@/lib/constants";
import { formatCurrency } from "@/lib/utils";

interface CategorySpend {
  category: string;
  spent: number;
}

interface Props {
  data: CategorySpend[];
  onCategoryClick?: (category: string | null) => void;
  activeCategory?: string | null;
}

const RADIAN = Math.PI / 180;

function CustomLabel({
  cx = 0,
  cy = 0,
  midAngle = 0,
  innerRadius = 0,
  outerRadius = 0,
  percent = 0,
}: {
  cx?: number;
  cy?: number;
  midAngle?: number;
  innerRadius?: number;
  outerRadius?: number;
  percent?: number;
}) {
  if (percent < 0.05) return null;
  const radius = innerRadius + (outerRadius - innerRadius) * 0.5;
  const x = cx + radius * Math.cos(-midAngle * RADIAN);
  const y = cy + radius * Math.sin(-midAngle * RADIAN);
  return (
    <text
      x={x}
      y={y}
      fill="white"
      textAnchor="middle"
      dominantBaseline="central"
      fontSize={11}
      fontFamily="var(--font-code)"
    >
      {(percent * 100).toFixed(0)}%
    </text>
  );
}

export function CategoryDonut({ data, onCategoryClick, activeCategory }: Props) {
  const top = data.slice(0, 7);
  const isFiltering = activeCategory !== null && activeCategory !== undefined;

  return (
    <ResponsiveContainer width="100%" height="100%">
      <PieChart>
        <Pie
          data={top}
          cx="50%"
          cy="45%"
          innerRadius="38%"
          outerRadius="65%"
          dataKey="spent"
          nameKey="category"
          labelLine={false}
          label={CustomLabel}
          strokeWidth={2}
          stroke="var(--color-paper)"
          style={{ cursor: onCategoryClick ? "pointer" : "default" }}
          onClick={(entry) => {
            if (!onCategoryClick) return;
            const clicked = (entry as CategorySpend).category;
            onCategoryClick(activeCategory === clicked ? null : clicked);
          }}
        >
          {top.map((entry) => (
            <Cell
              key={entry.category}
              fill={CATEGORY_COLORS[entry.category] ?? "#A3A3A3"}
              opacity={isFiltering && activeCategory !== entry.category ? 0.25 : 1}
            />
          ))}
        </Pie>
        <Tooltip
          content={({ active, payload }) => {
            if (!active || !payload?.length) return null;
            const d = payload[0].payload as CategorySpend;
            return (
              <div className="bg-ink text-paper px-3 py-2 text-xs font-code shadow-lg">
                <p className="text-white/70 mb-0.5">{d.category}</p>
                <p className="text-[#C9A84C] font-semibold">
                  {formatCurrency(d.spent)}
                </p>
              </div>
            );
          }}
        />
        <Legend
          iconType="circle"
          iconSize={7}
          formatter={(value) => (
            <span
              className="text-xs font-body"
              style={{
                color:
                  isFiltering && activeCategory !== value
                    ? "#C0C0C0"
                    : "#6B7280",
              }}
            >
              {value}
            </span>
          )}
          wrapperStyle={{ paddingTop: 12 }}
        />
      </PieChart>
    </ResponsiveContainer>
  );
}
