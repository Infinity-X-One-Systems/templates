"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { clsx } from "clsx";

const navItems = [
  { href: "/dashboard", label: "Overview" },
  { href: "/dashboard/agents", label: "Agents" },
  { href: "/dashboard/workflows", label: "Workflows" },
  { href: "/dashboard/settings", label: "Settings" },
];

export function DashboardLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  return (
    <div className="flex min-h-screen">
      <aside className="w-64 bg-gray-900 text-white p-6 flex flex-col gap-2">
        <Link href="/" className="text-xl font-bold text-indigo-400 mb-6">
          Infinity X One
        </Link>
        {navItems.map((item) => (
          <Link
            key={item.href}
            href={item.href}
            className={clsx(
              "px-3 py-2 rounded-md text-sm font-medium transition-colors",
              pathname === item.href
                ? "bg-indigo-600 text-white"
                : "text-gray-300 hover:bg-gray-700"
            )}
          >
            {item.label}
          </Link>
        ))}
      </aside>
      <main className="flex-1 p-8 bg-gray-50 dark:bg-gray-900">{children}</main>
    </div>
  );
}
