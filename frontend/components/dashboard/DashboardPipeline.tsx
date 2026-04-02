"use client";

import { startTransition, useEffect, useMemo, useState } from "react";
import { Pipeline } from "@/components/pipeline/Pipeline";
import {
  getCampaign,
  listCampaigns,
  readLastCampaignId,
  type CampaignResponse,
  type CampaignSummary,
} from "@/lib/api/campaign";
import { mapAgentStepsFromCampaign } from "@/lib/pipeline/map-agent-steps";

function pickFocusCampaign(
  rows: CampaignSummary[],
): CampaignSummary | null {
  if (!rows.length) return null;
  const processing = rows.find((r) => r.status === "processing");
  if (processing) return processing;
  const lastId = readLastCampaignId();
  if (lastId) {
    const byLast = rows.find((r) => r.id === lastId);
    if (byLast) return byLast;
  }
  const completed = rows.find((r) => r.status === "completed");
  if (completed) return completed;
  return rows[0];
}

export function DashboardPipeline() {
  const [list, setList] = useState<CampaignSummary[]>([]);
  const [detail, setDetail] = useState<CampaignResponse | null>(null);
  const [err, setErr] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    void listCampaigns(15)
      .then((rows) => {
        if (!cancelled) setList(rows);
      })
      .catch((e) => {
        if (!cancelled)
          setErr(e instanceof Error ? e.message : "Failed to load campaigns");
      });
    return () => {
      cancelled = true;
    };
  }, []);

  const focus = useMemo(() => pickFocusCampaign(list), [list]);

  useEffect(() => {
    if (!focus) {
      startTransition(() => setDetail(null));
      return;
    }
    let cancelled = false;
    const load = () =>
      getCampaign(focus.id).then((c) => {
        if (!cancelled) setDetail(c);
      });

    void load();

    if (focus.status !== "processing") return;

    const id = setInterval(() => void load(), 3000);
    return () => {
      cancelled = true;
      clearInterval(id);
    };
  }, [focus]);

  const { steps, headline } = mapAgentStepsFromCampaign(detail);

  return (
    <section>
      <h2 className="mb-4 text-sm font-medium uppercase tracking-wide text-slate-500">
        Agent pipeline
      </h2>
      {err && (
        <p className="mb-2 text-sm text-red-400" role="alert">
          {err}
        </p>
      )}
      <div className="rounded-2xl border border-slate-200 bg-slate-50 p-4">
        <div className="mb-3 flex flex-col gap-1 sm:flex-row sm:items-center sm:justify-between">
          <p className="text-sm text-slate-700">{headline}</p>
          {focus && (
            <span className="text-xs text-slate-500">
              Campaign: {focus.name ?? focus.id.slice(0, 8)}… · {focus.status}
            </span>
          )}
        </div>
        <Pipeline steps={steps} />
        {!focus && (
          <p className="mt-4 text-xs text-slate-500">
            Create a campaign to see live 12-agent progress here.
          </p>
        )}
      </div>
    </section>
  );
}
