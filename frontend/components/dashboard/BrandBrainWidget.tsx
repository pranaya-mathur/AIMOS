"use client";

import { useEffect, useState } from "react";
import { getBrand } from "@/lib/api/brand";
import Link from "next/link";

export function BrandBrainWidget() {
  const [brand, setBrand] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getBrand()
      .then(setBrand)
      .catch(() => setBrand(null))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="h-32 animate-pulse bg-slate-100 rounded-2xl" />;
  if (!brand) return null;

  return (
    <section>
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-mono-premium opacity-60">
          Brand Brain (Unified Context)
        </h2>
        <Link href="/onboarding" className="text-[10px] font-black text-primary uppercase tracking-[0.2em] hover:text-white transition-colors">
          Refine Strategy // Protocol v2
        </Link>
      </div>
      <div className="glass-panel group relative overflow-hidden rounded-[2.5rem] p-8 border-white/[0.08]">
        <div className="absolute top-0 right-0 p-8 opacity-5 group-hover:opacity-10 transition-opacity">
            <svg className="w-32 h-32 text-primary" fill="currentColor" viewBox="0 0 24 24">
                <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z" />
            </svg>
        </div>
        
        <div className="relative z-10 grid grid-cols-1 md:grid-cols-3 gap-10">
          <div className="space-y-2">
            <p className="text-mono-premium">Industry & Vertical</p>
            <p className="text-xl font-black text-white italic tracking-tighter uppercase">{brand.industry || "General"} Node · <span className="text-primary">{brand.business_type}</span></p>
          </div>
          <div className="space-y-2">
            <p className="text-mono-premium">Primary Objective</p>
            <p className="text-xl font-black text-white italic tracking-tighter uppercase">{brand.primary_goal}</p>
          </div>
          <div className="space-y-2">
            <p className="text-mono-premium">Resource Allocation</p>
            <p className="text-xl font-black text-white italic tracking-tighter uppercase font-mono">${brand.monthly_budget?.toLocaleString()}</p>
          </div>
        </div>
        
        <div className="mt-8 pt-8 border-t border-white/[0.04] grid grid-cols-1 md:grid-cols-2 gap-8">
            <div className="flex items-center gap-4 group/item">
                <div className="p-3 bg-emerald-500/10 rounded-2xl text-emerald-400 border border-emerald-500/20 shadow-[0_0_15px_rgba(16,185,129,0.1)] group-hover/item:scale-110 transition-transform">
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
                </div>
                <div>
                    <p className="text-mono-premium !text-emerald-500/60">Market Grounding</p>
                    <p className="text-sm font-bold text-white tracking-tight">Spy Agent monitoring rivals</p>
                </div>
            </div>
            <div className="flex items-center gap-4 group/item">
                <div className="p-3 bg-primary/10 rounded-2xl text-primary border border-primary/20 shadow-[0_0_15px_rgba(139,92,246,0.1)] group-hover/item:scale-110 transition-transform">
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 10V3L4 14h7v7l9-11h-7z" /></svg>
                </div>
                <div>
                    <p className="text-mono-premium !text-primary/60">Dynamic Context</p>
                    <p className="text-sm font-bold text-white tracking-tight">Injected into all agents</p>
                </div>
            </div>
        </div>
      </div>
    </section>
  );
}
