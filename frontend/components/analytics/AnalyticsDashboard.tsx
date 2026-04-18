"use client";

import Link from "next/link";
import { startTransition, useCallback, useEffect, useState } from "react";
import {
  getGlobalAnalytics,
  getUsageAnalytics,
  getUsageMe,
  type GlobalAnalytics,
  type UsageAnalytics,
  type UsageMe,
} from "@/lib/api/analytics";
import { MetricCard } from "@/components/dashboard/MetricCard";

function fmtUsd(n: number): string {
  return n.toLocaleString(undefined, {
    style: "currency",
    currency: "USD",
    minimumFractionDigits: 2,
    maximumFractionDigits: 4,
  });
}

function fmtPct(n: number): string {
  return `${(n * 100).toFixed(2)}%`;
}

export function AnalyticsDashboard() {
  const [global_, setGlobal] = useState<GlobalAnalytics | null>(null);
  const [usageAgg, setUsageAgg] = useState<UsageAnalytics | null>(null);
  const [usageMe, setUsageMe] = useState<UsageMe | null>(null);
  const [err, setErr] = useState<string | null>(null);

  const load = useCallback(() => {
    setErr(null);
    void Promise.all([
      getGlobalAnalytics().catch(() => null),
      getUsageAnalytics().catch(() => null),
      getUsageMe().catch(() => null),
    ]).then(([g, u, m]) => {
      setGlobal(g);
      setUsageAgg(u);
      setUsageMe(m);
    });
  }, []);

  useEffect(() => {
    startTransition(() => void load());
  }, [load]);

  const g = global_?.summary;
  const note = usageMe?.note;

  return (
    <div className="space-y-10">
      <p className="text-sm text-slate-400">
        Data from <code className="text-slate-500">GET /analytics/*</code> and{" "}
        <code className="text-slate-500">GET /usage/me</code>. Spend and
        impressions appear when{" "}
        <code className="text-slate-500">CampaignMetric</code> rows exist.
      </p>

      {note && (
        <p className="rounded-xl border border-amber-500/30 bg-amber-500/10 px-4 py-2 text-sm text-amber-200/90">
          {note}
        </p>
      )}

      {err && (
        <p className="text-sm text-red-400" role="alert">
          {err}
        </p>
      )}

      <section>
        <h2 className="mb-4 text-sm font-medium uppercase tracking-wide text-slate-500">
          Performance (aggregated)
        </h2>
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
          <MetricCard
            title="Campaigns (visible)"
            value={global_ ? String(global_.campaign_count) : "—"}
            change="All-time count in scope"
            changeTone="neutral"
          />
          <MetricCard
            title="Total spend"
            value={g ? fmtUsd(g.total_spend) : "—"}
            change="From campaign metrics"
            changeTone="neutral"
          />
          <MetricCard
            title="Impressions"
            value={g ? g.total_impressions.toLocaleString() : "—"}
            change={`CTR ${g ? fmtPct(g.ctr) : "—"}`}
            changeTone="neutral"
          />
          <MetricCard
            title="Conversions"
            value={g ? g.total_conversions.toLocaleString() : "—"}
            change={`CVR ${g ? fmtPct(g.cvr) : "—"}`}
            changeTone="neutral"
          />
        </div>
      </section>

      <section>
        <h2 className="mb-4 text-sm font-medium uppercase tracking-wide text-slate-500">
          AI usage & cost
        </h2>
        <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
          <MetricCard
            title="Tokens (all events)"
            value={
              usageAgg ? usageAgg.total_tokens.toLocaleString() : "—"
            }
            change="OpenAI + providers in usage_events"
            changeTone="neutral"
          />
          <MetricCard
            title="Est. cost (usage_events)"
            value={
              usageAgg ? fmtUsd(usageAgg.total_cost_usd) : "—"
            }
            change="Sum of recorded cost_usd"
            changeTone="neutral"
          />
          <MetricCard
            title="Est. cost (month, user)"
            value={
              usageMe
                ? `$${Number(usageMe.estimated_openai_cost_usd).toFixed(4)}`
                : "—"
            }
            change="UTC month from /usage/me"
            changeTone="neutral"
          />
        </div>

        {usageMe && (
          <div className="mt-4 rounded-2xl border border-white/[0.06] bg-white/[0.04] p-4 text-sm backdrop-blur-sm">
            <p className="text-slate-400">
              Period: {usageMe.period_utc.start.slice(0, 10)} →{" "}
              {usageMe.period_utc.end.slice(0, 10)} (UTC)
            </p>
            <div className="mt-3 grid gap-2 sm:grid-cols-2">
              <p className="text-slate-300">
                Campaigns:{" "}
                <strong>{usageMe.campaigns.used}</strong>
                {usageMe.campaigns.limit != null
                  ? ` / ${usageMe.campaigns.limit}`
                  : " (no limit)"}{" "}
                {usageMe.campaigns.remaining != null
                  ? `· left ${usageMe.campaigns.remaining}`
                  : ""}
              </p>
              <p className="text-slate-300">
                Tokens:{" "}
                <strong>{usageMe.tokens.used.toLocaleString()}</strong>
                {usageMe.tokens.limit != null
                  ? ` / ${usageMe.tokens.limit.toLocaleString()}`
                  : " (no limit)"}{" "}
                {usageMe.tokens.remaining != null
                  ? `· left ${usageMe.tokens.remaining.toLocaleString()}`
                  : ""}
              </p>
            </div>
          </div>
        )}

        {usageAgg && Object.keys(usageAgg.breakdown).length > 0 && (
          <div className="mt-4 overflow-x-auto rounded-2xl border border-white/[0.06]">
            <table className="w-full min-w-[480px] text-left text-sm">
              <thead className="border-b border-white/[0.06] bg-white/[0.04] text-xs uppercase text-slate-500">
                <tr>
                  <th className="px-4 py-2">Provider / model</th>
                  <th className="px-4 py-2">Tokens</th>
                  <th className="px-4 py-2">Cost (USD)</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/[0.06]">
                {Object.entries(usageAgg.breakdown).map(([k, v]) => (
                  <tr key={k} className="hover:bg-white/[0.02]">
                    <td className="px-4 py-2 font-mono text-xs text-slate-400">
                      {k}
                    </td>
                    <td className="px-4 py-2 text-slate-400">
                      {v.tokens.toLocaleString()}
                    </td>
                    <td className="px-4 py-2 text-slate-400">
                      {fmtUsd(v.cost)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>

      <section className="rounded-2xl border border-white/[0.06] bg-white/[0.03] p-4 backdrop-blur-sm">
        <h3 className="text-sm font-medium text-slate-300">
          Per-campaign analytics
        </h3>
        <p className="mt-1 text-sm text-slate-500">
          Open any campaign → <strong className="text-slate-300">Campaign analytics</strong> for spend,
          leads, and daily rows (
          <code className="text-slate-400">GET /analytics/campaign/{"{id}"}</code>
          ).
        </p>
        <Link
          href="/campaigns"
          className="mt-3 inline-block text-sm text-violet-400 hover:text-violet-300"
        >
          Go to campaigns →
        </Link>
      </section>

      <div className="flex flex-wrap gap-2">
        <button
          type="button"
          onClick={load}
          className="rounded-xl border border-white/[0.12] px-4 py-2 text-sm text-slate-300 hover:bg-white/[0.06]"
        >
          Refresh
        </button>
      </div>
    </div>
  );
}
