"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  ArrowLeftRight,
  Landmark,
  Tag,
  RefreshCcw,
  Receipt,
  Settings,
} from "lucide-react";
import { DASHBOARD_ROUTES } from "@/lib/constants";

const ICONS = {
  LayoutDashboard,
  ArrowLeftRight,
  Landmark,
  Tag,
  RefreshCcw,
  Receipt,
  Settings,
} as const;

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="w-[220px] shrink-0 flex flex-col h-screen sticky top-0 bg-[#1A3A2A] border-r border-white/5">
      {/* Brand */}
      <div className="px-5 h-14 flex items-center border-b border-white/10">
        <Link href="/" className="font-serif italic text-xl text-[#C9A84C] tracking-tight">
          Computare
        </Link>
      </div>

      {/* Nav */}
      <nav className="flex-1 px-3 py-3 overflow-y-auto">
        <p className="text-[10px] tracking-[0.2em] uppercase text-white/25 px-3 mb-2 mt-1">
          Overview
        </p>
        {DASHBOARD_ROUTES.slice(0, 1).map((route) => {
          const Icon = ICONS[route.icon as keyof typeof ICONS];
          const isActive = pathname === route.href;
          return (
            <SidebarLink key={route.href} href={route.href} icon={Icon} label={route.name} isActive={isActive} />
          );
        })}

        <p className="text-[10px] tracking-[0.2em] uppercase text-white/25 px-3 mb-2 mt-4">
          Finance
        </p>
        {DASHBOARD_ROUTES.slice(1, 5).map((route) => {
          const Icon = ICONS[route.icon as keyof typeof ICONS];
          const isActive = pathname === route.href || pathname.startsWith(route.href + "/");
          return (
            <SidebarLink key={route.href} href={route.href} icon={Icon} label={route.name} isActive={isActive} />
          );
        })}

        <p className="text-[10px] tracking-[0.2em] uppercase text-white/25 px-3 mb-2 mt-4">
          More
        </p>
        {DASHBOARD_ROUTES.slice(5).map((route) => {
          const Icon = ICONS[route.icon as keyof typeof ICONS];
          const isActive = pathname === route.href || pathname.startsWith(route.href + "/");
          return (
            <SidebarLink key={route.href} href={route.href} icon={Icon} label={route.name} isActive={isActive} />
          );
        })}
      </nav>

      {/* Footer */}
      <div className="px-5 py-4 border-t border-white/10">
        <p className="font-code text-[10px] text-white/25">v0.1.0 · local</p>
      </div>
    </aside>
  );
}

function SidebarLink({
  href,
  icon: Icon,
  label,
  isActive,
}: {
  href: string;
  icon: React.ComponentType<{ size?: number; strokeWidth?: number }>;
  label: string;
  isActive: boolean;
}) {
  return (
    <Link
      href={href}
      className={`flex items-center gap-2.5 px-3 py-2 rounded text-sm transition-all duration-150 mb-0.5 ${
        isActive
          ? "bg-white/10 text-[#C9A84C]"
          : "text-white/50 hover:text-white/85 hover:bg-white/5"
      }`}
    >
      <Icon size={14} strokeWidth={isActive ? 2 : 1.5} />
      <span className="font-body">{label}</span>
      {isActive && (
        <div className="ml-auto w-1 h-1 rounded-full bg-[#C9A84C]" />
      )}
    </Link>
  );
}
