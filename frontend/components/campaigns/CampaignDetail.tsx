"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useCallback, useEffect, useState } from "react";
import { Pipeline } from "@/components/pipeline/Pipeline";
import {
  getCampaign,
  patchCampaign,
  rememberLastCampaignId,
  rerunCampaign,
  type CampaignResponse,
} from "@/lib/api/campaign";
import { STATUS_LABEL, statusBadgeClass } from "@/lib/campaign-status";
import { mapAgentStepsFromCampaign } from "@/lib/pipeline/map-agent-steps";

type Props = { campaignId: string };

export function CampaignDetail({ campaignId }: Props) {
  const router = useRouter();
  const [c, setC] = useState<CampaignResponse | null>(null);
  const [err, setErr] = useState<string | null>(null);
  const [busy, setBusy] = useState<string | null>(null);

  const load = useCallback(() => {
    setErr(null);
    return getCampaign(campaignId)
      .then((row) => {
        setC(row);
        rememberLastCampaignId(row.id);
      })
      .catch((e) => {
        setErr(e instanceof Error ? e.message : "Failed to load");
        setC(null);
      });
  }, [campaignId]);

  useEffect(() => {
    void load();
  }, [load]);

  useEffect(() => {
    if (!c || c.status !== "processing") return;
    const id = setInterval(() => void load(), 3000);
    return () => clearInterval(id);
  }, [c?.status, load, c]);

  async function act(
    label: string,
    fn: () => Promise<unknown>,
  ): Promise<void> {
    setBusy(label);
    setErr(null);
    try {
      await fn();
      await load();
    } catch (e) {
      setErr(e instanceof Error ? e.message : "Action failed");
    } finally {
      setBusy(null);
    }
  }

  if (err && !c) {
    return (
      <div className="space-y-4">
        <p className="text-red-400">{err}</p>
        <Link href="/campaigns" className="text-violet-600 hover:underline">
          ← Back to campaigns
        </Link>
      </div>
    );
  }

  if (!c) {
    return <p className="text-slate-500">Loading…</p>;
  }

  const { steps, headline } = mapAgentStepsFromCampaign(c);
  const outStr =
    c.output != null ? JSON.stringify(c.output, null, 2) : "—";

  const canRerun =
    c.status !== "processing" &&
    ["completed", "failed", "rejected", "draft", "paused", "active"].includes(
      c.status,
    );

  return (
    <div className="space-y-8">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <Link
            href="/campaigns"
            className="text-sm text-violet-600 hover:text-violet-700"
          >
            ← All campaigns
          </Link>
          <h1 className="mt-2 text-xl font-semibold">
            {c.name?.trim() || `Campaign ${c.id.slice(0, 8)}…`}
          </h1>
          <p className="mt-1 font-mono text-xs text-slate-500">{c.id}</p>
          <div className="mt-3 flex flex-wrap items-center gap-3">
            <span
              className={`inline-flex rounded-full px-3 py-1 text-xs font-medium ${statusBadgeClass(c.status)}`}
            >
              {STATUS_LABEL[c.status] ?? c.status}
            </span>
            <Link
              href={`/campaigns/${c.id}/analytics`}
              className="text-sm text-violet-600 hover:text-violet-700"
            >
              Campaign analytics →
            </Link>
          </div>
        </div>
      </div>

      {err && (
        <p className="text-sm text-red-400" role="alert">
          {err}
        </p>
      )}

      <section className="rounded-2xl border border-slate-200 bg-white p-4">
        <h2 className="text-sm font-medium uppercase tracking-wide text-slate-500">
          Review & actions
        </h2>
        <p className="mt-2 text-xs text-slate-500">
          Approve sends the campaign to <strong>Active</strong> (ready to
          launch). Reject marks it <strong>Rejected</strong>. Send back sets{" "}
          <strong>Draft</strong> for edits. Re-run clears output and runs the
          12-agent pipeline again.
        </p>
        <div className="mt-4 flex flex-wrap gap-2">
          {c.status === "completed" && (
            <>
              <button
                type="button"
                disabled={!!busy}
                onClick={() =>
                  void act("approve", () =>
                    patchCampaign(c.id, { status: "active" }),
                  )
                }
                className="rounded-xl bg-emerald-600 px-4 py-2 text-sm font-medium text-white hover:bg-emerald-500 disabled:opacity-50"
              >
                {busy === "approve" ? "…" : "Approve (activate)"}
              </button>
              <button
                type="button"
                disabled={!!busy}
                onClick={() =>
                  void act("reject", () =>
                    patchCampaign(c.id, { status: "rejected" }),
                  )
                }
                className="rounded-xl bg-red-600/90 px-4 py-2 text-sm font-medium text-white hover:bg-red-500 disabled:opacity-50"
              >
                {busy === "reject" ? "…" : "Reject"}
              </button>
              <button
                type="button"
                disabled={!!busy}
                onClick={() =>
                  void act("draft", () =>
                    patchCampaign(c.id, { status: "draft" }),
                  )
                }
                className="rounded-xl border border-slate-300 px-4 py-2 text-sm text-slate-800 hover:bg-slate-100 disabled:opacity-50"
              >
                {busy === "draft" ? "…" : "Send back to draft"}
              </button>
            </>
          )}
          {c.status === "active" && (
            <button
              type="button"
              disabled={!!busy}
              onClick={() =>
                void act("pause", () => patchCampaign(c.id, { status: "paused" }))
              }
              className="rounded-xl border border-slate-300 px-4 py-2 text-sm text-slate-800 hover:bg-slate-100 disabled:opacity-50"
            >
              {busy === "pause" ? "…" : "Pause"}
            </button>
          )}
          {c.status === "paused" && (
            <button
              type="button"
              disabled={!!busy}
              onClick={() =>
                void act("resume", () =>
                  patchCampaign(c.id, { status: "active" }),
                )
              }
              className="rounded-xl bg-emerald-600 px-4 py-2 text-sm font-medium text-white hover:bg-emerald-500 disabled:opacity-50"
            >
              {busy === "resume" ? "…" : "Resume"}
            </button>
          )}
          {canRerun && (
            <button
              type="button"
              disabled={!!busy}
              onClick={() =>
                void act("rerun", async () => {
                  await rerunCampaign(c.id);
                })
              }
              className="rounded-xl bg-violet-600 px-4 py-2 text-sm font-medium text-white hover:bg-violet-700 disabled:opacity-50"
            >
              {busy === "rerun" ? "…" : "Re-run pipeline"}
            </button>
          )}
          <button
            type="button"
            disabled={!!busy}
            onClick={() => void load()}
            className="rounded-xl border border-slate-300 px-4 py-2 text-sm text-slate-700 hover:bg-slate-100 disabled:opacity-50"
          >
            Refresh
          </button>
        </div>
        {c.status === "processing" && c.celery_task_id && (
          <p className="mt-3 text-xs text-yellow-200/90">
            Job running… task <code className="text-slate-600">{c.celery_task_id}</code>
          </p>
        )}
      </section>

      <section>
        <h2 className="mb-2 text-sm font-medium uppercase tracking-wide text-slate-500">
          Pipeline
        </h2>
        <p className="mb-3 text-sm text-slate-600">{headline}</p>
        <div className="overflow-x-auto rounded-2xl border border-slate-200 bg-slate-50 p-4">
          <Pipeline steps={steps} />
        </div>
      </section>

      <section className="grid gap-6 lg:grid-cols-2">
        <div>
          <h2 className="mb-2 text-sm font-medium uppercase tracking-wide text-slate-500">
            Input brief
          </h2>
          <pre className="max-h-80 overflow-auto rounded-2xl border border-slate-200 bg-white p-4 text-xs text-slate-700">
            {JSON.stringify(c.input ?? {}, null, 2)}
          </pre>
          <button
            type="button"
            onClick={() => router.push("/campaign")}
            className="mt-3 text-sm text-violet-600 hover:text-violet-700"
          >
            Open new campaign builder →
          </button>
        </div>
        <div>
          <h2 className="mb-2 text-sm font-medium uppercase tracking-wide text-slate-500">
            Output
          </h2>
          <pre className="max-h-96 overflow-auto rounded-2xl border border-slate-200 bg-white p-4 text-xs text-slate-700">
            {outStr}
          </pre>
        </div>
      </section>
    </div>
  );
}
