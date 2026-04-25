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
import { resumeCampaign } from "@/lib/api/orchestration";

type Props = { campaignId: string };

export function CampaignDetail({ campaignId }: Props) {
  const router = useRouter();
  const [c, setC] = useState<CampaignResponse | null>(null);
  const [err, setErr] = useState<string | null>(null);
  const [busy, setBusy] = useState<string | null>(null);
  const [feedback, setFeedback] = useState("");

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
        <Link href="/campaigns" className="text-violet-400 hover:underline">
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
  const ao = c.orchestration_metadata as Record<string, unknown> | undefined;
  const predictive = ao?.["predictive_benchmarker"] as
    | Record<string, unknown>
    | undefined;

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
            className="text-sm text-violet-400 hover:text-violet-300"
          >
            ← All campaigns
          </Link>
          <h1 className="mt-2 text-xl font-semibold text-white">
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
              className="text-sm text-violet-400 hover:text-violet-300"
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

      <section className="rounded-2xl border border-white/[0.06] bg-[rgba(15,15,25,0.55)] p-4 backdrop-blur-xl">
        <h2 className="text-sm font-medium uppercase tracking-wide text-slate-500">
          Review & actions
        </h2>
        <p className="mt-2 text-xs text-slate-400">
          Approve sends the campaign to <strong>Active</strong> (ready to
          launch). Reject marks it <strong>Rejected</strong>. Send back sets{" "}
          <strong>Draft</strong> for edits. Re-run clears output and runs the
          14-agent pipeline again.
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
                className="rounded-xl border border-white/[0.12] px-4 py-2 text-sm text-slate-200 hover:bg-white/[0.06] disabled:opacity-50"
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
              className="rounded-xl border border-white/[0.12] px-4 py-2 text-sm text-slate-200 hover:bg-white/[0.06] disabled:opacity-50"
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
            className="rounded-xl border border-white/[0.12] px-4 py-2 text-sm text-slate-300 hover:bg-white/[0.06] disabled:opacity-50"
          >
            Refresh
          </button>
        </div>
        {c.status === "processing" && c.celery_task_id && (
          <p className="mt-3 text-xs text-yellow-200/90">
            Job running… task <code className="text-slate-400">{c.celery_task_id}</code>
          </p>
        )}
        
        {c.status === "awaiting_feedback" && (
           <div className="mt-6 p-6 bg-violet-600 rounded-3xl shadow-2xl border-2 border-violet-400">
               <div className="flex items-center gap-3 mb-4">
                   <div className="w-2 h-2 bg-white rounded-full animate-ping"></div>
                   <h3 className="text-sm font-black uppercase tracking-widest text-white">Human Intervention Required</h3>
               </div>
               <p className="text-sm text-violet-100 mb-6 font-medium leading-relaxed">
                   The AI Orchestrator has paused for your guidance. 
                   {c.orchestration_metadata?.refinement_context && (
                       <span className="block mt-2 p-3 bg-violet-700/50 rounded-xl border border-violet-500/50 italic text-violet-200">
                           AI Reasoning: {c.orchestration_metadata.refinement_context}
                       </span>
                   )}
               </p>
               <div className="space-y-4">
                   <textarea 
                        value={feedback}
                        onChange={(e) => setFeedback(e.target.value)}
                        placeholder="Provide your guidance to the AI (e.g., 'Make the tone more aggressive and focus on security benefits')..."
                        className="w-full bg-violet-800/50 border-none rounded-2xl p-4 text-white text-sm font-medium placeholder:text-violet-300 focus:ring-2 focus:ring-white h-32"
                   />
                   <button 
                        disabled={!!busy || !feedback.trim()}
                        onClick={() => act("resume", () => resumeCampaign(c.id, feedback))}
                        className="w-full py-4 rounded-2xl bg-white text-[10px] font-black uppercase tracking-widest text-violet-600 shadow-xl hover:scale-[1.02] transition-transform disabled:opacity-50"
                   >
                       {busy === "resume" ? "Resuming..." : "Resume AI Loop →"}
                   </button>
               </div>
           </div>
        )}

        {/* Hardened 2.0: Predictive Performance Outlook (Option A) */}
        {predictive && (
            <div className="mt-8 grid grid-cols-1 md:grid-cols-3 gap-6">
                {Boolean(predictive.predicted_ctr) && (
                    <div className="rounded-3xl border border-white/[0.06] bg-white/[0.04] p-6 shadow-sm transition-all hover:border-white/[0.1]">
                        <span className="text-[10px] font-black uppercase tracking-widest text-slate-500">Predicted CTR</span>
                        <div className="mt-2 text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-violet-600 to-indigo-600">
                            {String(predictive.predicted_ctr)}
                        </div>
                        <div className="mt-1 text-xs font-medium text-slate-500">Industry Avg: {String(predictive.industry_comparison ?? "—")}</div>
                    </div>
                )}
                {Boolean(predictive.predicted_cpl) && (
                    <div className="rounded-3xl border border-white/[0.06] bg-white/[0.04] p-6 shadow-sm transition-all hover:border-white/[0.1]">
                        <span className="text-[10px] font-black uppercase tracking-widest text-slate-500">Predicted CPL</span>
                        <div className="mt-2 text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-emerald-600 to-teal-600">
                            {String(predictive.predicted_cpl)}
                        </div>
                        <div className="mt-1 text-xs font-medium text-slate-500">Outlook: {String(predictive.performance_outlook ?? "—")}</div>
                    </div>
                )}
                <div className="flex flex-col justify-center rounded-3xl border border-white/[0.08] bg-[#0c0c14] p-6 shadow-xl">
                    <span className="text-[10px] font-black uppercase tracking-widest text-slate-500">Confidence Score</span>
                    <div className="mt-2 flex items-end gap-2 text-3xl font-bold text-white">
                        {String(predictive.confidence_score ?? 0)}%
                        <div className="mb-1 w-12 h-1 bg-slate-800 rounded-full overflow-hidden">
                            <div 
                                className="h-full bg-violet-500" 
                                style={{ width: `${Number(predictive.confidence_score ?? 0)}%` }}
                            ></div>
                        </div>
                    </div>
                </div>
            </div>
        )}
      </section>

      <section>
        <h2 className="mb-2 text-sm font-medium uppercase tracking-wide text-slate-500">
          Pipeline
        </h2>
        <p className="mb-3 text-sm text-slate-400">{headline}</p>
        <div className="overflow-x-auto rounded-2xl border border-white/[0.06] bg-white/[0.03] p-4">
          <Pipeline steps={steps} />
        </div>
      </section>

      <section className="grid gap-6 lg:grid-cols-2">
        <div>
          <h2 className="mb-2 text-sm font-medium uppercase tracking-wide text-slate-500">
            Input brief
          </h2>
          <pre className="max-h-80 overflow-auto rounded-2xl border border-white/[0.06] bg-[rgba(10,10,16,0.9)] p-4 text-xs text-slate-300">
            {JSON.stringify(c.input ?? {}, null, 2)}
          </pre>
          <button
            type="button"
            onClick={() => router.push("/campaign")}
            className="mt-3 text-sm text-violet-400 hover:text-violet-300"
          >
            Open new campaign builder →
          </button>
        </div>
        <div>
          <h2 className="mb-2 text-sm font-medium uppercase tracking-wide text-slate-500">
            Output
          </h2>
          <pre className="max-h-96 overflow-auto rounded-2xl border border-white/[0.06] bg-[rgba(10,10,16,0.9)] p-4 text-xs text-slate-300">
            {outStr}
          </pre>
        </div>
      </section>
    </div>
  );
}
