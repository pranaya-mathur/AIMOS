"use client";

import { useEffect, useState } from "react";
import { getGlobalAnalytics, type GlobalAnalytics } from "@/lib/api/analytics";
import { BrandBrainWidget } from "@/components/dashboard/BrandBrainWidget";
import { DashboardPipeline } from "@/components/dashboard/DashboardPipeline";

export default function DashboardPage() {
  const [data, setData] = useState<GlobalAnalytics | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getGlobalAnalytics()
      .then(setData)
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="p-10 text-center font-medium text-slate-500">Initializing Control Tower...</div>;

  const stats = data?.summary;

  return (
    <div className="mx-auto max-w-7xl p-8 space-y-10 pb-32">
      <header className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-4xl font-extrabold tracking-tight text-slate-900">Command Tower</h1>
          <p className="text-slate-500 mt-2 text-lg">Real-time performance across your entire marketing ecosystem.</p>
        </div>
        <div className="flex items-center gap-2 rounded-full bg-emerald-50 px-4 py-2 border border-emerald-100">
            <div className="h-2 w-2 rounded-full bg-emerald-500 animate-pulse" />
            <span className="text-xs font-bold uppercase tracking-widest text-emerald-600">Live Optimization Active</span>
        </div>
      </header>
      
      <BrandBrainWidget />

      {/* Main Stats Grid */}
      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
        {[
          { label: "Est. ROI", value: `${(stats?.roi || 0).toLocaleString(undefined, {style: 'percent'})}`, color: "text-violet-600", desc: "Return on Ad Spend" },
          { label: "Total Spend", value: `$${(stats?.total_spend || 0).toLocaleString()}`, color: "text-slate-900", desc: "Investment to date" },
          { label: "Est. Revenue", value: `$${(stats?.estimated_revenue || 0).toLocaleString()}`, color: "text-emerald-600", desc: "Attributed growth" },
          { label: "Active Leads", value: `${(stats?.total_leads || 0).toLocaleString()}`, color: "text-fuchsia-600", desc: "Qualified prospects" },
        ].map((s) => (
          <div key={s.label} className="group rounded-[2rem] border border-slate-200 bg-white p-8 transition-all hover:shadow-lg hover:-translate-y-1">
            <span className="text-xs font-black uppercase tracking-widest text-slate-400">{s.label}</span>
            <div className={`mt-2 text-4xl font-black ${s.color}`}>{s.value}</div>
            <p className="mt-2 text-sm text-slate-500">{s.desc}</p>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 gap-8 lg:grid-cols-3">
        {/* Performance Trends Chart Placeholder */}
        <section className="lg:col-span-2 rounded-[2.5rem] border border-slate-200 bg-white p-10 shadow-sm relative overflow-hidden">
            <div className="relative z-10">
                <h2 className="text-2xl font-bold text-slate-900">Conversion Trends</h2>
                <p className="text-slate-500 mb-8">Daily trend for leads vs. conversions.</p>
                
                <div className="flex h-64 items-end justify-between gap-2 px-4">
                    {[40, 60, 45, 80, 55, 90, 70, 85, 95, 65, 50, 75, 80, 85].map((h, i) => (
                        <div key={i} className="flex-1 group/bar relative">
                            <div 
                                className="w-full bg-violet-100 rounded-t-lg transition-all group-hover/bar:bg-violet-600 group-hover/bar:h-[105%]" 
                                style={{ height: `${h}%` }}
                            />
                            <div className="absolute inset-0 flex items-center justify-center opacity-0 group-hover/bar:opacity-100 transition-opacity pointer-events-none">
                                <span className="text-[10px] font-bold bg-slate-900 text-white px-2 py-1 rounded shadow-xl -mt-20">+{h}%</span>
                            </div>
                        </div>
                    ))}
                </div>
                <div className="mt-4 flex justify-between text-[10px] font-black uppercase tracking-widest text-slate-300">
                    <span>30 Days Ago</span>
                    <span>Today</span>
                </div>
            </div>
            <div className="absolute bottom-0 right-0 opacity-5 pointer-events-none">
                <span className="text-[15rem] font-black leading-none">AI</span>
            </div>
        </section>

        {/* Brand Integration Pipeline */}
        <section className="lg:col-span-3">
            <DashboardPipeline />
        </section>

        {/* AI Recommendations */}
        <section className="rounded-[2.5rem] bg-slate-900 p-10 text-white shadow-2xl">
            <h2 className="text-2xl font-bold">AI Directives</h2>
            <p className="text-slate-400 mb-8">Optimization engine output.</p>
            
            <div className="space-y-6">
                {[
                    { title: "Boost Google Spend", desc: "Meta CPL is 15% higher than Google this week; reallocating budget is advised.", type: "Budget" },
                    { title: "A/B Test Creative #4", desc: "Static image banners are outperforming video by 2.3x for 'Awareness' goal.", type: "Creative" },
                    { title: "High-Intent Hotspots", desc: "leads from 'Tier 1 Cities' shows 3x conversion score; target specifically.", type: "Audience" }
                ].map((r) => (
                    <div key={r.title} className="group relative rounded-2xl border border-white/10 bg-white/5 p-6 transition-all hover:bg-white/10">
                        <span className="text-[10px] font-black uppercase tracking-widest text-violet-400">{r.type}</span>
                        <h3 className="mt-1 font-bold">{r.title}</h3>
                        <p className="mt-1 text-sm text-slate-400 group-hover:text-slate-300">{r.desc}</p>
                    </div>
                ))}
            </div>
            
            <button className="mt-8 w-full rounded-2xl bg-white py-4 text-sm font-bold uppercase tracking-widest text-slate-900 transition-transform active:scale-95">
                Apply All Optimizations
            </button>
        </section>
      </div>
    </div>
  );
}
