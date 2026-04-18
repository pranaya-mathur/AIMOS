"use client";

import Link from "next/link";
import { startTransition, useCallback, useEffect, useState } from "react";
import { listCampaigns, type CampaignSummary } from "@/lib/api/campaign";
import { STATUS_LABEL, statusBadgeClass } from "@/lib/campaign-status";

export function CampaignList() {
  const [rows, setRows] = useState<CampaignSummary[]>([]);
  const [err, setErr] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  const load = useCallback(() => {
    setErr(null);
    setLoading(true);
    void listCampaigns(100)
      .then(setRows)
      .catch((e) =>
        setErr(e instanceof Error ? e.message : "Failed to load campaigns"),
      )
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    startTransition(() => void load());
  }, [load]);

  return (
    <div className="space-y-4">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <p className="text-sm text-slate-400">
          Review status, open a campaign, then approve, reject, or re-run the
          pipeline.
        </p>
        <div className="flex flex-wrap gap-2">
          <button
            type="button"
            onClick={load}
            className="rounded-xl border border-white/[0.1] px-4 py-2 text-sm text-slate-300 hover:bg-white/[0.06]"
          >
            Refresh
          </button>
          <Link
            href="/campaign"
            className="rounded-xl bg-violet-600 px-4 py-2 text-sm font-medium text-white hover:bg-violet-700"
          >
            New campaign
          </Link>
        </div>
      </div>

      {err && (
        <p className="text-sm text-red-400" role="alert">
          {err}
        </p>
      )}

      {loading ? (
        <p className="text-sm text-slate-500">Loading…</p>
      ) : rows.length === 0 ? (
        <p className="text-sm text-slate-500">
          No campaigns yet.{" "}
          <Link href="/campaign" className="text-violet-400 hover:underline">
            Create one
          </Link>
          .
        </p>
      ) : (
        <div className="overflow-x-auto rounded-2xl border border-white/[0.06]">
          <table className="w-full min-w-[640px] text-left text-sm">
            <thead className="border-b border-white/[0.06] bg-white/[0.04] text-xs uppercase tracking-wide text-slate-500">
              <tr>
                <th className="px-4 py-3 font-medium">Name</th>
                <th className="px-4 py-3 font-medium">Status</th>
                <th className="px-4 py-3 font-medium">Created</th>
                <th className="px-4 py-3 font-medium text-right">Open</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-white/[0.06]">
              {rows.map((r) => (
                <tr key={r.id} className="hover:bg-white/[0.03]">
                  <td className="px-4 py-3 text-slate-200">
                    {r.name?.trim() || (
                      <span className="text-slate-500">{r.id.slice(0, 8)}…</span>
                    )}
                  </td>
                  <td className="px-4 py-3">
                    <span
                      className={`inline-flex rounded-full px-2.5 py-0.5 text-xs font-medium ${statusBadgeClass(r.status)}`}
                    >
                      {STATUS_LABEL[r.status] ?? r.status}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-slate-500">
                    {r.created_at
                      ? new Date(r.created_at).toLocaleString()
                      : "—"}
                  </td>
                  <td className="px-4 py-3 text-right">
                    <Link
                      href={`/campaigns/${r.id}`}
                      className="text-violet-400 hover:text-violet-300"
                    >
                      View →
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
