/**
 * Category colors — matches the `categories.color` column in the database
 * and the CATEGORY_COLORS dict in computare/categorizer/categories.py.
 */
export const CATEGORY_COLORS: Record<string, string> = {
  "Food & Dining": "#FF6B6B",
  Transportation: "#4ECDC4",
  "Retail & Shopping": "#45B7D1",
  "Bills & Utilities": "#FFEAA7",
  Healthcare: "#E84393",
  Entertainment: "#96CEB4",
  Housing: "#FFD93D",
  Income: "#6BCB77",
  Transfers: "#B07CC6",
  Investment: "#9B59B6",
  Education: "#3498DB",
  "Personal Care": "#E91E63",
  "AI & Software Services": "#00BCD4",
};

export const DASHBOARD_ROUTES = [
  { name: "Overview", href: "/dashboard", icon: "LayoutDashboard" },
  { name: "Transactions", href: "/transactions", icon: "ArrowLeftRight" },
  { name: "Accounts", href: "/accounts", icon: "Landmark" },
  { name: "Categories", href: "/categories", icon: "Tag" },
  { name: "Subscriptions", href: "/subscriptions", icon: "RefreshCcw" },
  { name: "Receipts", href: "/receipts", icon: "Receipt" },
  { name: "Settings", href: "/settings", icon: "Settings" },
] as const;
