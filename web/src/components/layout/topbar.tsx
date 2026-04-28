export function Topbar({ title, subtitle }: { title: string; subtitle?: string }) {
  return (
    <header className="h-14 border-b border-ash-200 flex items-center justify-between px-6 bg-paper shrink-0">
      <div className="flex items-center gap-3">
        <p className="text-sm text-ash-600 font-body">{title}</p>
        {subtitle && (
          <span className="text-xs font-code text-ash-400 border border-ash-200 px-2 py-0.5">
            {subtitle}
          </span>
        )}
      </div>
      <div className="flex items-center gap-3">
        <div className="w-7 h-7 bg-[#1A3A2A] rounded-full flex items-center justify-center">
          <span className="text-[#C9A84C] text-xs font-serif italic">C</span>
        </div>
      </div>
    </header>
  );
}
