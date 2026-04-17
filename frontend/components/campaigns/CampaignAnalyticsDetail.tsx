"use client";

import Link from "next/link";
import {
  startTransition,
  useCallback,
  useEffect,
  useState,
} from "react";
import {
  getCampaignAnalytics,
  getOptimizationDirectives,
  type CampaignAnalytics,
  type OptimizationDirective,
} from "@/lib/api/analytics";
import { MetricCard } from "@/components/dashboard/MetricCard";

type Props = { campaignId: string };

function fmtUsd(n: number): string {
  return n.toLocaleString(undefined, {
    style: "currency",
    currency: "USD",
    minimumFractionDigits: 2,
    maximumFractionDigits: 4,
  });
}

export function CampaignAnalyticsDetail({ campaignId }: Props) {
  const [data, setData] = useState<CampaignAnalytics | null>(null);
  const [directives, setDirectives] = useState<OptimizationDirective[]>([]);
  const [competitors, setCompetitors] = useState<any[]>([]);
  const [err, setErr] = useState<string | null>(null);

  const load = useCallback(() => {
    setErr(null);
    startTransition(() => {
      void getCampaignAnalytics(campaignId)
        .then(setData)
        .catch((e) =>
          setErr(e instanceof Error ? e.message : "Failed to load analytics"),
        );
      void getOptimizationDirectives(campaignId)
        .then(setDirectives)
        .catch(console.error);
      
      // Phase 2: Competitor Intel
      void fetch(`/api/analytics/competitors/${campaignId}`)
        .then(res => res.json())
        .then(setCompetitors)
        .catch(console.error);
    });
  }, [campaignId]);

  useEffect(() => {
    startTransition(() => void load());
  }, [load]);

  if (err && !data) {
    return (
      <div className="space-y-4">
        <p className="text-red-400">{err}</p>
        <Link href={`/campaigns/${campaignId}`} className="text-violet-600">
          ← Back to campaign
        </Link>
      </div>
    );
  }

  if (!data) {
    return <p className="text-slate-500">Loading…</p>;
  }

  return (
    <div className="space-y-8">
      <div>
        <Link
          href={`/campaigns/${campaignId}`}
          className="text-sm text-violet-600 hover:text-violet-700"
        >
          ← Campaign detail
        </Link>
        <h1 className="mt-2 text-xl font-semibold">
          Analytics · {data.campaign_name?.trim() || data.campaign_id.slice(0, 8)}…
        </h1>
        <p className="mt-1 font-mono text-xs text-slate-500">{data.campaign_id}</p>
      </div>

      {err && (
        <p className="text-sm text-amber-400" role="alert">
          {err}
        </p>
      )}

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <MetricCard
          title="Total spend"
          value={fmtUsd(data.total_spend)}
          change="CampaignMetric rows"
          changeTone="neutral"
        />
        <MetricCard
          title="Leads"
          value={String(data.total_leads)}
          change="Linked to this campaign"
          changeTone="neutral"
        />
        <MetricCard
          title="Cost / lead"
          value={
            data.total_leads > 0 ? fmtUsd(data.cost_per_lead) : "—"
          }
          change={data.total_leads === 0 ? "No leads yet" : ""}
          changeTone="neutral"
        />
        <MetricCard
          title="Daily rows"
          value={String(data.daily_performance.length)}
          change="Ingested snapshots"
          changeTone="neutral"
        />
      </div>

      <section>
        <h2 className="mb-3 text-sm font-medium uppercase tracking-wide text-slate-500">
          Market Intelligence (Spy Agent)
        </h2>
        {competitors.length === 0 ? (
          <p className="rounded-2xl border border-dashed border-slate-300 bg-slate-50 p-6 text-center text-sm text-slate-500">
            Scanning rival ad libraries… Intelligence will appear here shortly.
          </p>
        ) : (
          <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
            {competitors.map((c) => (
              <div key={c.id} className="p-4 bg-white border border-slate-200 rounded-2xl shadow-sm">
                <div className="flex items-center justify-between mb-2">
                    <h3 className="font-bold text-slate-800">{c.name}</h3>
                    <span className={`px-2 py-0.5 rounded-full text-[9px] font-black uppercase tracking-widest ${
                        c.threat_level > 70 ? 'bg-red-100 text-red-600' : 
                        c.threat_level > 40 ? 'bg-amber-100 text-amber-600' : 'bg-emerald-100 text-emerald-600'
                    }`}>
                        Threat: {c.threat_level}/100
                    </span>
                </div>
                <p className="text-xs text-slate-600 mb-3 leading-relaxed italic">"{c.positioning}"</p>
                <div className="space-y-1">
                    <p className="text-[10px] font-bold text-slate-400 uppercase tracking-tighter">Observed Hooks:</p>
                    <div className="flex flex-wrap gap-1">
                        {(c.ad_hooks || []).slice(0, 3).map((hook: string, idx: number) => (
                            <span key={idx} className="px-2 py-0.5 bg-slate-100 text-slate-600 rounded text-[9px]">
                                {hook}
                            </span>
                        ))}
                    </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </section>

      <section>
        <h2 className="mb-3 text-sm font-medium uppercase tracking-wide text-slate-500">
          Daily performance
        </h2>
        {data.daily_performance.length === 0 ? (
          <p className="rounded-2xl border border-slate-200 bg-white p-6 text-sm text-slate-500">
            No metrics yet — performance appears when the optimization / metrics
            pipeline writes <code className="text-slate-600">CampaignMetric</code>{" "}
            rows for this campaign.
          </p>
        ) : (
          <div className="overflow-x-auto rounded-2xl border border-slate-200">
            <table className="w-full min-w-[520px] text-left text-sm">
              <thead className="border-b border-slate-200 bg-white text-xs uppercase text-slate-500">
                <tr>
                  <th className="px-4 py-2">Day</th>
                  <th className="px-4 py-2">Platform</th>
                  <th className="px-4 py-2">Spend</th>
                  <th className="px-4 py-2">Conversions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-200">
                {data.daily_performance.map((row) => (
                  <tr key={`${row.day}-${row.platform}`}>
                    <td className="px-4 py-2 text-slate-700">{row.day}</td>
                    <td className="px-4 py-2 font-mono text-xs text-slate-600">
                      {row.platform}
                    </td>
                    <td className="px-4 py-2 text-slate-700">
                      {fmtUsd(row.spend)}
                    </td>
                    <td className="px-4 py-2 text-slate-700">
                      {row.conversions}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      <section>
        <div className="flex items-center justify-between mb-4">
             <h2 className="text-sm font-medium uppercase tracking-wide text-slate-500">
                Optimization History
            </h2>
            <div className="flex items-center gap-2">
                <div className="w-2 h-2 bg-emerald-500 rounded-full animate-pulse"></div>
                <span className="text-[10px] font-bold text-slate-400 uppercase tracking-tighter">Autopilot Monitoring Active</span>
            </div>
        </div>
        
        {directives.length === 0 ? (
          <p className="rounded-2xl border border-dashed border-slate-300 bg-slate-50 p-8 text-center text-sm text-slate-500 font-medium">
            AI Growth Engine is monitoring traffic patterns. No directives issued yet.
          </p>
        ) : (
          <div className="space-y-4">
             {directives.map((d) => (
                 <div key={d.id} className="relative p-5 bg-white border border-slate-200 rounded-3xl shadow-sm hover:shadow-md transition-all group overflow-hidden">
                     {d.execution_mode === "autopilot" && d.status === "applied" && (
                         <div className="absolute top-0 right-0 px-4 py-1.5 bg-violet-600 text-[10px] font-black uppercase tracking-widest text-white rounded-bl-2xl shadow-lg">
                             Autonomous Autopilot Applied
                         </div>
                     )}
                     
                     {d.status === "scheduled" && (
                         <div className="absolute top-0 right-0 px-4 py-1.5 bg-amber-500 text-[10px] font-black uppercase tracking-widest text-white rounded-bl-2xl shadow-lg animate-pulse">
                             Pending Auto-Execution (5m Grace Window)
                         </div>
                     )}
                     
                     <div className="flex items-start justify-between">
                         <div className="max-w-[70%]">
                             <div className="flex items-center gap-2 mb-2">
                                 <span className={`px-2 py-0.5 rounded-full text-[9px] font-black uppercase tracking-tighter ${
                                     d.directive_type === 'scale' ? 'bg-emerald-100 text-emerald-700' : 
                                     d.directive_type === 'pause' ? 'bg-red-100 text-red-700' : 'bg-slate-100 text-slate-700'
                                 }`}>
                                     {d.directive_type}
                                 </span>
                                 <span className="text-xs text-slate-400 font-medium">
                                     {new Date(d.created_at).toLocaleDateString()}
                                 </span>
                             </div>
                             <p className="text-sm text-slate-800 font-bold leading-tight mb-1">{d.description}</p>
                             <div className="flex items-center gap-4 text-[10px] text-slate-500 font-medium">
                                 <span className="flex items-center gap-1">
                                     Risk: <span className={d.risk_score < 30 ? 'text-emerald-600' : 'text-amber-600'}>{d.risk_score}/100</span>
                                 </span>
                                 <span className="flex items-center gap-1">
                                     Confidence: <span className="text-violet-600">{d.confidence}%</span>
                                 </span>
                             </div>
                         </div>
                         <div className="flex flex-col items-end gap-2">
                             <span className={`text-[10px] font-black uppercase tracking-widest ${
                                 d.status === 'applied' ? 'text-emerald-500' : 
                                 d.status === 'rejected' || d.status === 'dismissed' ? 'text-red-400' : 
                                 d.status === 'scheduled' ? 'text-amber-500' : 'text-amber-500'
                             }`}>
                                 {d.status}
                             </span>
                             
                             {d.status === 'scheduled' && (
                                 <button 
                                    onClick={() => {
                                        window.confirm("Abort this autonomous action?") && 
                                        fetch(`/api/analytics/directives/${d.id}`, { method: 'DELETE' }).then(() => load());
                                    }}
                                    className="px-3 py-1 bg-red-50 rounded-lg text-[9px] font-black uppercase tracking-widest text-red-600 hover:bg-red-100 transition-colors"
                                 >
                                     Abort Autopilot →
                                 </button>
                             )}

                             {d.status === 'pending' && (
                                 <button className="text-[10px] font-black uppercase tracking-widest text-violet-600 hover:text-violet-700 underline underline-offset-4 pointer-events-none opacity-50">
                                     Manual Review Required
                                 </button>
                             )}
                         </div>
                     </div>
                 </div>
             ))}
          </div>
        )}
      </section>

      <button
        type="button"
        onClick={load}
        className="rounded-xl border border-slate-300 px-4 py-2 text-sm text-slate-700 hover:bg-slate-100"
      >
        Refresh
      </button>
    </div>
  );
}
