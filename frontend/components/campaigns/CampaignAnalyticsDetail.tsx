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
  type CampaignAnalytics,
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
  const [err, setErr] = useState<string | null>(null);

  const load = useCallback(() => {
    setErr(null);
    startTransition(() => {
      void getCampaignAnalytics(campaignId)
        .then(setData)
        .catch((e) =>
          setErr(e instanceof Error ? e.message : "Failed to load analytics"),
        );
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
