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
        <Link href={`/campaigns/${campaignId}`} className="text-violet-400 hover:text-violet-300">
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
          className="text-sm text-violet-400 hover:text-violet-300"
        >
          ← Campaign detail
        </Link>
        <h1 className="mt-2 text-xl font-semibold text-white">
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
          <p className="rounded-2xl border border-dashed border-white/[0.1] bg-white/[0.02] p-6 text-center text-sm text-slate-500">
            Scanning rival ad libraries… Intelligence will appear here shortly.
          </p>
        ) : (
          <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
            {competitors.map((c) => (
              <div key={c.id} className="rounded-2xl border border-white/[0.06] bg-white/[0.04] p-4 shadow-sm backdrop-blur-sm">
                <div className="mb-2 flex items-center justify-between">
                    <h3 className="font-bold text-slate-200">{c.name}</h3>
                    <span className={`rounded-full px-2 py-0.5 text-[9px] font-black uppercase tracking-widest ${
                        c.threat_level > 70 ? 'bg-rose-500/15 text-rose-300' : 
                        c.threat_level > 40 ? 'bg-amber-500/15 text-amber-300' : 'bg-emerald-500/15 text-emerald-300'
                    }`}>
                        Threat: {c.threat_level}/100
                    </span>
                </div>
                <p className="mb-3 text-xs italic leading-relaxed text-slate-400">"{c.positioning}"</p>
                <div className="space-y-1">
                    <p className="text-[10px] font-bold uppercase tracking-tighter text-slate-500">Observed Hooks:</p>
                    <div className="flex flex-wrap gap-1">
                        {(c.ad_hooks || []).slice(0, 3).map((hook: string, idx: number) => (
                            <span key={idx} className="rounded bg-white/[0.06] px-2 py-0.5 text-[9px] text-slate-400">
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
          <p className="rounded-2xl border border-white/[0.06] bg-white/[0.03] p-6 text-sm text-slate-500">
            No metrics yet — performance appears when the optimization / metrics
            pipeline writes <code className="text-slate-400">CampaignMetric</code>{" "}
            rows for this campaign.
          </p>
        ) : (
          <div className="overflow-x-auto rounded-2xl border border-white/[0.06]">
            <table className="w-full min-w-[520px] text-left text-sm">
              <thead className="border-b border-white/[0.06] bg-white/[0.04] text-xs uppercase text-slate-500">
                <tr>
                  <th className="px-4 py-2">Day</th>
                  <th className="px-4 py-2">Platform</th>
                  <th className="px-4 py-2">Spend</th>
                  <th className="px-4 py-2">Conversions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/[0.06]">
                {data.daily_performance.map((row) => (
                  <tr key={`${row.day}-${row.platform}`} className="hover:bg-white/[0.02]">
                    <td className="px-4 py-2 text-slate-300">{row.day}</td>
                    <td className="px-4 py-2 font-mono text-xs text-slate-500">
                      {row.platform}
                    </td>
                    <td className="px-4 py-2 text-slate-300">
                      {fmtUsd(row.spend)}
                    </td>
                    <td className="px-4 py-2 text-slate-300">
                      {row.conversions}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>

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
          <p className="rounded-2xl border border-dashed border-white/[0.1] bg-white/[0.02] p-8 text-center text-sm font-medium text-slate-500">
            AI Growth Engine is monitoring traffic patterns. No directives issued yet.
          </p>
        ) : (
          <div className="space-y-4">
             {directives.map((d) => (
                 <div key={d.id} className="group relative overflow-hidden rounded-3xl border border-white/[0.06] bg-white/[0.04] p-5 shadow-sm backdrop-blur-sm transition-all hover:border-white/[0.1]">
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
                                 <span className={`rounded-full px-2 py-0.5 text-[9px] font-black uppercase tracking-tighter ${
                                     d.directive_type === 'scale' ? 'bg-emerald-500/15 text-emerald-300' : 
                                     d.directive_type === 'pause' ? 'bg-rose-500/15 text-rose-300' : 'bg-white/[0.08] text-slate-300'
                                 }`}>
                                     {d.directive_type}
                                 </span>
                                 <span className="text-xs text-slate-400 font-medium">
                                     {new Date(d.created_at).toLocaleDateString()}
                                 </span>
                             </div>
                             <p className="mb-1 text-sm font-bold leading-tight text-slate-200">{d.description}</p>
                             <div className="flex items-center gap-4 text-[10px] font-medium text-slate-500">
                                 <span className="flex items-center gap-1">
                                     Risk: <span className={d.risk_score < 30 ? 'text-emerald-400' : 'text-amber-400'}>{d.risk_score}/100</span>
                                 </span>
                                 <span className="flex items-center gap-1">
                                     Confidence: <span className="text-violet-400">{d.confidence}%</span>
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
                                    className="rounded-lg bg-rose-500/15 px-3 py-1 text-[9px] font-black uppercase tracking-widest text-rose-300 transition-colors hover:bg-rose-500/25"
                                 >
                                     Abort Autopilot →
                                 </button>
                             )}

                             {d.status === 'pending' && (
                                 <button className="pointer-events-none text-[10px] font-black uppercase tracking-widest text-violet-400 underline underline-offset-4 opacity-50">
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
        className="rounded-xl border border-white/[0.12] px-4 py-2 text-sm text-slate-300 hover:bg-white/[0.06]"
      >
        Refresh
      </button>
    </div>
  );
}
