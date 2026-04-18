"use client";

import React, { useEffect, useState } from "react";
import { Command } from "cmdk";
import { motion, AnimatePresence } from "framer-motion";
import { useRouter } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import {
  Rocket,
  Search,
  LayoutDashboard,
  Target,
  Activity,
  Settings,
  Brain,
  Zap,
  LogOut,
  Sparkles,
  ChevronRight,
  Monitor,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { listCampaigns } from "@/lib/api/campaign";
import { getLandingPages } from "@/lib/api/leads";

export function CommandBar() {
  const [open, setOpen] = useState(false);
  const router = useRouter();

  // Fetch searchable entities
  const { data: campaigns } = useQuery({
    queryKey: ["search-campaigns"],
    queryFn: () => listCampaigns(10),
    enabled: open,
  });

  const { data: pages } = useQuery({
    queryKey: ["search-pages"],
    queryFn: getLandingPages,
    enabled: open,
  });

  // Toggle open/close with Cmd+K
  useEffect(() => {
    const down = (e: KeyboardEvent) => {
      if (e.key === "k" && (e.metaKey || e.ctrlKey)) {
        e.preventDefault();
        setOpen((open) => !open);
      }
    };

    const handleToggle = () => setOpen((o) => !o);

    document.addEventListener("keydown", down);
    window.addEventListener("toggle-command-bar" as any, handleToggle);
    return () => {
      document.removeEventListener("keydown", down);
      window.removeEventListener("toggle-command-bar" as any, handleToggle);
    };
  }, []);

  const runCommand = (command: () => void) => {
    setOpen(false);
    command();
  };

  return (
    <AnimatePresence>
      {open && (
        <div className="fixed inset-0 z-[100] flex items-start justify-center pt-[15vh]">
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={() => setOpen(false)}
            className="absolute inset-0 bg-black/60 backdrop-blur-md"
          />

          {/* Command Menu */}
          <motion.div
            initial={{ opacity: 0, scale: 0.95, y: -20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95, y: -20 }}
            transition={{ duration: 0.2, ease: [0.16, 1, 0.3, 1] }}
            className="relative w-full max-w-[640px] overflow-hidden rounded-[2rem] border border-white/10 bg-[rgba(15,15,30,0.85)] shadow-[0_32px_128px_-16px_rgba(0,0,0,0.8)] backdrop-blur-3xl"
          >
            <Command className="flex flex-col h-full">
              <div className="flex items-center border-b border-white/5 px-6 py-5">
                <Search className="mr-4 h-5 w-5 text-slate-500" />
                <Command.Input
                  autoFocus
                  placeholder="Enter command or target name..."
                  className="w-full bg-transparent text-lg text-white placeholder-slate-500 outline-none font-medium"
                />
                <div className="flex items-center gap-1.5 rounded-lg bg-white/5 px-2 py-1 border border-white/10">
                  <span className="text-[10px] font-black text-slate-400 uppercase">Esc</span>
                </div>
              </div>

              <Command.List className="max-h-[450px] overflow-y-auto px-4 pb-4 pt-2 scrollbar-none">
                <Command.Empty className="flex flex-col items-center justify-center py-10 text-slate-500">
                   <Brain className="h-10 w-10 mb-4 opacity-10 animate-pulse text-primary" />
                   <p className="text-sm">No neural matches found.</p>
                </Command.Empty>

                <Command.Group heading={<span className="text-mono-premium ml-2 mb-2 block opacity-40">Protocols & Navigation</span>}>
                  <Item
                    onSelect={() => runCommand(() => router.push("/"))}
                    icon={<LayoutDashboard className="h-4 w-4" />}
                  >
                    Control Tower (Home)
                  </Item>
                  <Item
                    onSelect={() => runCommand(() => router.push("/campaigns"))}
                    icon={<Rocket className="h-4 w-4" />}
                  >
                    Campaign Management
                  </Item>
                  <Item
                    onSelect={() => runCommand(() => router.push("/creatives"))}
                    icon={<Sparkles className="h-4 w-4" />}
                  >
                    Creative Studio
                  </Item>
                  <Item
                    onSelect={() => runCommand(() => router.push("/analytics"))}
                    icon={<Activity className="h-4 w-4" />}
                  >
                    Quantum Analytics
                  </Item>
                  <Item
                    onSelect={() => runCommand(() => router.push("/settings"))}
                    icon={<Settings className="h-4 w-4" />}
                  >
                    System Settings
                  </Item>
                </Command.Group>

                {campaigns && campaigns.length > 0 && (
                  <Command.Group heading={<span className="text-mono-premium ml-2 mb-2 mt-4 block opacity-40">Active Campaigns</span>}>
                    {campaigns.map((c) => (
                      <Item
                        key={c.id}
                        onSelect={() => runCommand(() => router.push(`/campaigns/${c.id}`))}
                        icon={<Target className="h-4 w-4 text-emerald-400" />}
                      >
                        {c.name || "Unnamed Campaign"}
                        <span className="ml-2 text-[10px] opacity-40">#{c.id.slice(-4)}</span>
                      </Item>
                    ))}
                  </Command.Group>
                )}

                {pages && pages.length > 0 && (
                  <Command.Group heading={<span className="text-mono-premium ml-2 mb-2 mt-4 block opacity-40">Deployed Pages</span>}>
                    {pages.map((p) => (
                      <Item
                        key={p.id}
                        onSelect={() => runCommand(() => router.push(`/leads/pages/${p.id}`))}
                        icon={<Monitor className="h-4 w-4 text-primary" />}
                      >
                        {p.title}
                        <span className="ml-2 text-[10px] opacity-40">/{p.slug}</span>
                      </Item>
                    ))}
                  </Command.Group>
                )}

                <Command.Group heading={<span className="text-mono-premium ml-2 mb-2 mt-4 block opacity-40">Quick Actions</span>}>
                  <Item
                    onSelect={() => runCommand(() => window.dispatchEvent(new CustomEvent('toggle-copilot')))}
                    icon={<Zap className="h-4 w-4 text-amber-400" />}
                  >
                    Initialize AI Co-pilot
                  </Item>
                  <Item
                    onSelect={() => runCommand(() => router.push("/login"))}
                    icon={<LogOut className="h-4 w-4 text-rose-400" />}
                    className="hover:bg-rose-500/10"
                  >
                    Terminate Session
                  </Item>
                </Command.Group>
              </Command.List>

              <div className="flex h-12 items-center border-t border-white/5 bg-white/[0.02] px-6 text-[10px] font-black uppercase tracking-widest text-slate-500">
                <span className="flex items-center gap-1">
                   <ChevronRight className="h-3 w-3" /> Select
                </span>
                <span className="mx-4 h-1 w-1 rounded-full bg-white/10" />
                <span className="flex items-center gap-1">
                   Search across <span className="text-primary">12 global nodes</span>
                </span>
              </div>
            </Command>
          </motion.div>
        </div>
      )}
    </AnimatePresence>
  );
}

function Item({
  children,
  onSelect,
  icon,
  className,
}: {
  children: React.ReactNode;
  onSelect: () => void;
  icon?: React.ReactNode;
  className?: string;
}) {
  return (
    <Command.Item
      onSelect={onSelect}
      className={cn(
        "flex cursor-pointer items-center gap-4 rounded-xl px-4 py-3 text-sm text-slate-300 transition-all aria-selected:bg-white/5 aria-selected:text-white group",
        className
      )}
    >
      <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-white/5 border border-white/5 group-aria-selected:border-primary/40 group-aria-selected:bg-primary/10 transition-colors">
        {icon}
      </div>
      <div className="flex-1 font-medium">{children}</div>
      <div className="opacity-0 group-aria-selected:opacity-60 transition-opacity">
         <ChevronRight className="h-3 w-3" />
      </div>
    </Command.Item>
  );
}
