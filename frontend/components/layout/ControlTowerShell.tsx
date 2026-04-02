"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useState } from "react";
import { NavActions } from "./NavActions";

const nav = [
  { href: "/", label: "Home", icon: "🏠" },
  { href: "/campaigns", label: "Campaigns", icon: "📋" },
  { href: "/analytics", label: "Analytics", icon: "📈" },
  { href: "/services", label: "Services", icon: "🧩" },
  { href: "/launch", label: "Launch", icon: "🚀" },
  { href: "/media-studio", label: "Media", icon: "🎬" },
  { href: "/billing", label: "Billing", icon: "💳" },
  { href: "/library", label: "Library", icon: "📚" },
  { href: "/settings", label: "Settings", icon: "⚙️" },
  { href: "/campaign", label: "New", icon: "🎯" },
] as const;

function titleForPath(pathname: string): string {
  if (/^\/campaigns\/[^/]+\/analytics/.test(pathname))
    return "Campaign analytics";
  if (pathname.startsWith("/billing")) return "Billing";
  if (pathname.startsWith("/campaigns/")) return "Campaign";
  if (pathname.startsWith("/campaigns")) return "Campaigns";
  if (pathname.startsWith("/analytics")) return "Analytics";
  if (pathname.startsWith("/services")) return "Services";
  if (pathname.startsWith("/launch")) return "Launch";
  if (pathname.startsWith("/media-studio")) return "Media studio";
  if (pathname.startsWith("/settings")) return "Settings";
  if (pathname.startsWith("/campaign")) return "New campaign";
  if (pathname.startsWith("/library")) return "Library";
  return "Dashboard";
}

export function ControlTowerShell({
  children,
}: {
  children: React.ReactNode;
}) {
  const pathname = usePathname();
  const [mobileNavOpen, setMobileNavOpen] = useState(false);

  return (
    <div className="flex min-h-screen bg-slate-50 text-slate-900">
      {mobileNavOpen && (
        <button
          type="button"
          className="fixed inset-0 z-30 bg-slate-900/40 backdrop-blur-sm md:hidden"
          aria-label="Close menu"
          onClick={() => setMobileNavOpen(false)}
        />
      )}

      <aside
        className={[
          "z-40 flex h-screen max-h-screen w-[4.5rem] shrink-0 flex-col items-center overflow-hidden border-r border-slate-200 bg-white py-4 shadow-sm",
          "fixed inset-y-0 left-0 transition-transform md:static md:translate-x-0",
          mobileNavOpen ? "translate-x-0" : "-translate-x-full md:translate-x-0",
        ].join(" ")}
      >
        <Link
          href="/"
          className="mb-4 flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-violet-600 to-indigo-600 text-lg text-white shadow-md"
          aria-label="AIMOS home"
          onClick={() => setMobileNavOpen(false)}
        >
          ⚡
        </Link>
        <nav className="flex min-h-0 flex-1 flex-col items-center gap-1 overflow-y-auto px-1 py-1">
          {nav.map(({ href, label, icon }) => {
            const active =
              href === "/"
                ? pathname === "/"
                : href === "/campaign"
                  ? pathname === "/campaign"
                  : pathname.startsWith(href);
            return (
              <Link
                key={href}
                href={href}
                title={label}
                className={[
                  "flex h-10 w-10 items-center justify-center rounded-xl text-lg transition-colors",
                  active
                    ? "bg-violet-100 text-violet-700 shadow-sm"
                    : "text-slate-500 hover:bg-slate-100 hover:text-slate-800",
                ].join(" ")}
                aria-label={label}
                onClick={() => setMobileNavOpen(false)}
              >
                {icon}
              </Link>
            );
          })}
        </nav>
      </aside>

      <div className="flex min-w-0 flex-1 flex-col md:pl-0">
        <header className="flex h-14 shrink-0 items-center justify-between border-b border-slate-200 bg-white px-4 shadow-sm md:h-16 md:px-6">
          <div className="flex items-center gap-3">
            <button
              type="button"
              className="rounded-lg p-2 text-slate-500 hover:bg-slate-100 hover:text-slate-800 md:hidden"
              aria-expanded={mobileNavOpen}
              aria-label="Open menu"
              onClick={() => setMobileNavOpen((o) => !o)}
            >
              <span className="text-lg" aria-hidden>
                ☰
              </span>
            </button>
            <h1 className="text-lg font-semibold tracking-tight text-slate-900">
              {titleForPath(pathname)}
            </h1>
          </div>
          <NavActions />
        </header>

        <main className="flex-1 overflow-y-auto p-4 md:p-8">{children}</main>
      </div>
    </div>
  );
}
