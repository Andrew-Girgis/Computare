export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="flex min-h-screen">
      {/* TODO: Sidebar navigation */}
      <aside className="w-64 border-r p-4 hidden md:block">
        <p className="font-semibold">Computare</p>
      </aside>
      <main className="flex-1 p-6">{children}</main>
    </div>
  );
}
