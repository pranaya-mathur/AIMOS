"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useState } from "react";
import { useBranding } from "@/lib/hooks/useBranding";
import { NavActions } from "./NavActions";
import { AICopilotSidebar } from "./AICopilotSidebar";
import { CommandBar } from "./CommandBar";

const nav = [

  { href: "/", label: "Home", icon: "🏠" },
  { href: "/campaigns", label: "Campaigns", icon: "📋" },
  { href: "/launch", label: "Launch", icon: "🚀" },
  { href: "/analytics/growth", label: "Growth Engine", icon: "📈" },
  { href: "/media-studio", label: "Media", icon: "🎬" },
  { href: "/creatives", label: "Creative Studio", icon: "🎨" },
  { href: "/leads/pages", label: "Capture Pages", icon: "🕸️" },
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
  if (pathname.startsWith("/analytics/growth")) return "Growth engine";
  if (pathname.startsWith("/analytics")) return "Analytics";
  if (pathname.startsWith("/launch")) return "Launch";
  if (pathname.startsWith("/media-studio")) return "Media studio";
  if (pathname.startsWith("/creatives")) return "Creative studio";
  if (pathname.startsWith("/leads/pages")) return "Capture pages";
  if (pathname.startsWith("/settings")) return "Settings";
  if (pathname.startsWith("/campaign")) return "New campaign";
  if (pathname.startsWith("/library")) return "Library";
  if (pathname.startsWith("/media-assets")) return "Media assets";
  return "Dashboard";
}

export function ControlTowerShell({
  children,
}: {
  children: React.ReactNode;
}) {
  const pathname = usePathname();
  const [mobileNavOpen, setMobileNavOpen] = useState(false);
  const { logoUrl, siteName, primaryColor } = useBranding();

  return (
    <div className="flex min-h-screen bg-[#0a0a12] text-slate-200 overflow-hidden font-sans">
      {/* Mobile overlay */}
      {mobileNavOpen && (
        <button
          type="button"
          className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm md:hidden transition-opacity duration-300"
          aria-label="Close menu"
          onClick={() => setMobileNavOpen(false)}
        />
      )}

      {/* ─── Sidebar ─── */}
      <aside
        className={[
          "z-50 flex h-screen max-h-screen w-[5rem] shrink-0 flex-col items-center overflow-hidden py-6",
          "bg-[#08080f] border-r border-white/[0.04]",
          "fixed inset-y-0 left-0 transition-transform duration-300 ease-in-out md:static md:translate-x-0",
          mobileNavOpen ? "translate-x-0" : "-translate-x-full md:translate-x-0",
        ].join(" ")}
      >
        {/* Ambient top glow */}
        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-24 h-40 bg-violet-500/10 rounded-full blur-3xl pointer-events-none" />

        {/* Logo */}
        <Link
          href="/"
          className="relative z-10 mb-8 flex h-11 w-11 items-center justify-center rounded-2xl text-xl text-white shadow-[0_0_20px_rgba(139,92,246,0.25)] overflow-hidden transition-all duration-300 hover:scale-110 hover:shadow-[0_0_30px_rgba(139,92,246,0.45)]"
          style={{ background: `linear-gradient(135deg, ${primaryColor || '#8b5cf6'}, #4338ca)` }}
          aria-label={`${siteName} home`}
          onClick={() => setMobileNavOpen(false)}
        >
          {logoUrl ? <img src={logoUrl} alt={siteName} className="w-full h-full object-cover" /> : "⚡"}
        </Link>

        {/* Nav items */}
        <nav className="relative z-10 flex min-h-0 flex-1 flex-col items-center gap-1.5 overflow-y-auto px-2 py-2">
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
                  "group relative flex h-11 w-11 items-center justify-center rounded-xl text-lg transition-all duration-200",
                  active
                    ? "bg-violet-500/15 text-violet-400 ring-1 ring-violet-500/25"
                    : "text-slate-500 hover:bg-white/[0.04] hover:text-slate-300",
                ].join(" ")}
                aria-label={label}
                onClick={() => setMobileNavOpen(false)}
              >
                {active && (
                  <div className="absolute -left-[0.65rem] top-1/2 h-5 w-[3px] -translate-y-1/2 rounded-r-full bg-violet-500 shadow-[0_0_8px_rgba(139,92,246,0.6)]" />
                )}
                <span className="relative z-10 group-hover:scale-110 transition-transform duration-200">{icon}</span>
              </Link>
            );
          })}
        </nav>
      </aside>

      {/* ─── Main content ─── */}
      <div className="flex min-w-0 flex-1 flex-col relative overflow-hidden">
        {/* Header */}
        <header className="sticky top-0 z-40 flex h-20 shrink-0 items-center justify-between border-b border-white/[0.04] bg-[#030303]/40 backdrop-blur-[24px] px-6 md:h-24 md:px-12">
          <div className="flex items-center gap-6">
            <button
              type="button"
              className="rounded-xl p-2 text-slate-500 hover:bg-white/[0.06] hover:text-slate-300 md:hidden transition-colors"
              aria-expanded={mobileNavOpen}
              aria-label="Open menu"
              onClick={() => setMobileNavOpen((o) => !o)}
            >
              <span className="text-xl" aria-hidden>☰</span>
            </button>
            <div>
              <h1 className="text-2xl font-black tracking-tighter text-white uppercase font-serif italic mb-0.5">
                {titleForPath(pathname)}
              </h1>
              <div className="flex items-center gap-2">
                <span className="flex h-1.5 w-1.5 rounded-full bg-primary animate-pulse shadow-[0_0_8px_rgba(139,92,246,0.6)]" />
                <span className="text-mono-premium opacity-60">System Synchronized</span>
              </div>
            </div>
          </div>

          <div className="flex items-center gap-6">
            {/* Search/Command Trigger */}
            <div 
              id="command-bar-trigger"
              className="flex items-center gap-3 px-4 py-2 bg-white/[0.03] border border-white/[0.08] rounded-2xl cursor-pointer hover:bg-white/[0.06] transition-all group"
              onClick={() => {
                window.dispatchEvent(new CustomEvent('toggle-command-bar'));
              }}
            >
               <span className="text-slate-500 group-hover:text-slate-300 transition-colors">⌘K</span>
               <span className="text-xs font-bold text-slate-600 group-hover:text-slate-400 transition-colors">Quick Command</span>
            </div>
            <NavActions />
          </div>
        </header>

        {/* Page canvas */}
        <main className="flex-1 overflow-y-auto p-6 md:p-12 relative scrollbar-hide">
          <div className="relative z-10 max-w-[1400px] mx-auto">
            {children}
          </div>
        </main>
      </div>
      
      {/* Global Command Bar */}
      <CommandBar />

      {/* AI Co-pilot Sidebar */}
      <AICopilotSidebar />
    </div>
  );
}

