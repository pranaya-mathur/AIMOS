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
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-sm font-medium uppercase tracking-wide text-slate-500">
          Brand Brain (Unified Context)
        </h2>
        <Link href="/onboarding" className="text-[10px] font-bold text-violet-600 uppercase hover:underline">
          Refine Strategy →
        </Link>
      </div>
      <div className="group relative overflow-hidden rounded-[2rem] border border-white/40 bg-white/60 p-6 shadow-xl backdrop-blur-xl transition-all hover:shadow-2xl">
        <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity">
            <svg className="w-20 h-20 text-violet-600" fill="currentColor" viewBox="0 0 24 24">
                <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z" />
            </svg>
        </div>
        
        <div className="relative z-10 grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="space-y-1">
            <p className="text-[10px] font-black uppercase tracking-widest text-slate-400">Industry & Type</p>
            <p className="text-lg font-bold text-slate-800">{brand.industry || "General"} · {brand.business_type}</p>
          </div>
          <div className="space-y-1">
            <p className="text-[10px] font-black uppercase tracking-widest text-slate-400">Primary Goal</p>
            <p className="text-lg font-bold text-violet-600">{brand.primary_goal}</p>
          </div>
          <div className="space-y-1">
            <p className="text-[10px] font-black uppercase tracking-widest text-slate-400">Monthly Budget</p>
            <p className="text-lg font-bold text-slate-800">${brand.monthly_budget?.toLocaleString()}</p>
          </div>
        </div>
        
        <div className="mt-6 pt-6 border-t border-slate-100 grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="flex items-center gap-3">
                <div className="p-2 bg-emerald-50 rounded-xl text-emerald-600">
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
                </div>
                <div>
                    <p className="text-[10px] font-bold text-slate-400 uppercase tracking-tighter">Market Grounding</p>
                    <p className="text-xs font-medium text-slate-600">Spy Agent monitoring rivals</p>
                </div>
            </div>
            <div className="flex items-center gap-3">
                <div className="p-2 bg-violet-50 rounded-xl text-violet-600">
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 10V3L4 14h7v7l9-11h-7z" /></svg>
                </div>
                <div>
                    <p className="text-[10px] font-bold text-slate-400 uppercase tracking-tighter">Dynamic Context</p>
                    <p className="text-xs font-medium text-slate-600">Injected into all 12 agents</p>
                </div>
            </div>
        </div>
      </div>
    </section>
  );
}
