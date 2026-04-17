"use client";

import { useEffect, useState } from "react";
import { getGlobalAnalytics, getOptimizationDirectives, applyOptimizationDirective, type OptimizationDirective, type AnalyticsSummary } from "@/lib/api/analytics";

export default function GrowthDashboard() {
  const [summary, setSummary] = useState<AnalyticsSummary | null>(null);
  const [directives, setDirectives] = useState<OptimizationDirective[]>([]);
  const [loading, setLoading] = useState(true);
  const [applying, setApplying] = useState<string | null>(null);

  useEffect(() => {
    load();
  }, []);

  const load = async () => {
    setLoading(true);
    try {
      const [gData, dData] = await Promise.all([
        getGlobalAnalytics(),
        getOptimizationDirectives()
      ]);
      setSummary(gData.summary);
      setDirectives(dData);
    } finally {
      setLoading(false);
    }
  };

  const handleApply = async (id: string) => {
    setApplying(id);
    try {
      await applyOptimizationDirective(id);
      setDirectives(directives.map(d => d.id === id ? { ...d, status: "applied" } : d));
    } catch (e) {
      alert("Failed to apply directive.");
    } finally {
      setApplying(null);
    }
  };

  const handleRevert = async (id: string) => {
    setApplying(id);
    try {
      const { revertOptimizationDirective } = await import("@/lib/api/analytics");
      await revertOptimizationDirective(id);
      setDirectives(directives.map(d => d.id === id ? { ...d, status: "reverted" } : d));
    } catch (e) {
      alert("Failed to revert directive.");
    } finally {
      setApplying(null);
    }
  };

  if (loading) return <div className="p-20 text-center font-medium text-slate-400">Connecting to Growth Engine...</div>;

  return (
    <div className="p-10 max-w-7xl mx-auto">
      <header className="mb-12">
        <h1 className="text-4xl font-black text-slate-900 tracking-tight">Growth Engine</h1>
        <p className="text-slate-500 mt-2 font-medium">Closed-loop AI optimization for your active campaigns.</p>
      </header>

      {/* Metric Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-12">
        {[
          { label: "Total Spend", value: `$${summary?.total_spend.toLocaleString()}`, color: "text-slate-900" },
          { label: "Avg CPL", value: `$${summary?.cpl.toFixed(2)}`, color: "text-violet-600" },
          { label: "Conversions", value: summary?.total_conversions, color: "text-emerald-600" },
          { label: "AI ROI", value: `${(summary?.roi || 0 * 100).toFixed(1)}%`, color: "text-indigo-600" }
        ].map((m, i) => (
          <div key={i} className="rounded-3xl bg-white border border-slate-100 p-8 shadow-sm">
            <span className="text-[10px] font-black uppercase tracking-widest text-slate-400 block mb-2">{m.label}</span>
            <span className={`text-3xl font-black ${m.color}`}>{m.value}</span>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-12">
        {/* Directives Feed */}
        <div className="lg:col-span-2">
            <h2 className="text-xl font-bold text-slate-900 mb-8 flex items-center gap-2">
                <span className="text-violet-600">⚡</span> Active AI Directives
            </h2>
            
            {directives.filter(d => d.status === 'pending').length === 0 ? (
                <div className="rounded-[3rem] border-2 border-dashed border-slate-100 p-16 text-center">
                    <p className="text-slate-300 font-bold">Your campaigns are currently optimal. No new directives.</p>
                </div>
            ) : (
                <div className="space-y-6">
                    {directives.filter(d => d.status === 'pending').map(d => (
                        <div key={d.id} className="rounded-[2.5rem] bg-white border border-slate-100 p-8 shadow-sm transition-all hover:shadow-xl hover:border-violet-100 flex items-center gap-8">
                            <div className={`h-16 w-16 shrink-0 rounded-3xl flex items-center justify-center text-2xl ${
                                d.type === 'scale' ? "bg-emerald-50 text-emerald-600" : 
                                d.type === 'pause' ? "bg-red-50 text-red-600" : 
                                "bg-violet-50 text-violet-600"
                            }`}>
                                {d.type === 'scale' ? "📈" : d.type === 'pause' ? "🛑" : "✨"}
                            </div>
                            <div className="flex-1">
                                <span className="text-[10px] font-black uppercase tracking-[0.2em] text-violet-400 mb-1 block">AI Recommendation</span>
                                <p className="text-slate-800 font-bold leading-relaxed">{d.description}</p>
                                <span className="text-[10px] text-slate-300 font-medium mt-2 block italic">Detected {new Date(d.created_at).toLocaleDateString()}</span>
                            </div>
                            <div className="flex gap-3">
                                <button 
                                    onClick={() => handleApply(d.id)}
                                    disabled={applying === d.id}
                                    className="px-8 py-4 rounded-2xl bg-slate-900 text-xs font-bold uppercase tracking-widest text-white shadow-xl hover:bg-slate-800 disabled:opacity-50"
                                >
                                    {applying === d.id ? "Applying..." : "Apply"}
                                </button>
                            </div>
                        </div>
                    ))}
                </div>
            )}

            {/* History Link */}
            <div className="mt-12 pt-8 border-t border-slate-100">
                 <h3 className="text-sm font-black uppercase tracking-widest text-slate-300 mb-6 underline decoration-slate-200 decoration-4 underline-offset-8">Applied & Locked</h3>
                 <div className="space-y-6">
                    {directives.filter(d => d.status === 'applied' || d.status === 'reverted').map(d => (
                         <div key={d.id} className={`flex items-center justify-between p-6 rounded-[2rem] border ${d.status === 'reverted' ? 'bg-slate-50 border-slate-200 opacity-50' : 'bg-white border-slate-100'}`}>
                            <div className="flex items-center gap-4">
                                <span className={d.status === 'reverted' ? 'text-slate-400' : 'text-emerald-500'}>{d.status === 'reverted' ? '↩' : '✓'}</span>
                                <p className="text-sm font-medium text-slate-600 line-clamp-1">{d.description}</p>
                            </div>
                            {d.status === 'applied' && (
                                <button 
                                    onClick={() => handleRevert(d.id)}
                                    disabled={applying === d.id}
                                    className="text-[10px] font-black uppercase tracking-widest text-violet-600 hover:text-violet-800 disabled:opacity-50"
                                >
                                    {applying === d.id ? "Undo..." : "Undo / Revert"}
                                </button>
                            )}
                            {d.status === 'reverted' && (
                                <span className="text-[10px] font-black uppercase tracking-widest text-slate-400 italic">Reverted</span>
                            )}
                         </div>
                    ))}
                 </div>
            </div>
        </div>

        {/* Sidebar Insights */}
        <div>
             <div className="rounded-[2.5rem] bg-indigo-600 p-8 text-white shadow-2xl relative overflow-hidden">
                <div className="relative z-10">
                    <h3 className="text-xl font-black mb-4">Growth Intelligence</h3>
                    <p className="text-sm opacity-80 leading-relaxed mb-8">The AI engine is currently analyzing data from the last 7 days. CTR is up 12% across your dental vertical.</p>
                    <div className="pt-6 border-t border-white/20">
                        <span className="text-[10px] font-black uppercase tracking-widest opacity-60 block mb-3">Model Accuracy</span>
                        <div className="h-2 w-full bg-white/10 rounded-full overflow-hidden">
                            <div className="h-full bg-white w-[94%]" />
                        </div>
                        <span className="text-right block text-[10px] font-bold mt-2">94%</span>
                    </div>
                </div>
                <div className="absolute -right-4 -bottom-4 text-9xl opacity-10">🚀</div>
             </div>
        </div>
      </div>
    </div>
  );
}
