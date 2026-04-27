"use client";

import Link from "next/link";
import { useCallback, useEffect, useState } from "react";
import {
  createCampaign,
  getCampaign,
  rememberLastCampaignId,
} from "@/lib/api/campaign";
import { useJobPoller } from "@/hooks/useJobPoller";

export function CampaignBuilder() {
  const [name, setName] = useState("");
  const [product, setProduct] = useState("");
  const [audience, setAudience] = useState("");
  const [track, setTrack] = useState("full");
  const [error, setError] = useState<string | null>(null);
  const [output, setOutput] = useState<string>("");
  const [campaignId, setCampaignId] = useState<string | null>(null);
  const { state: jobState, start, reset } = useJobPoller();

  const TRACKS = [
    { id: "full", label: "End-to-End", desc: "Full 14-agent orchestration", icon: "🚀", pro: false },
    { id: "strategy", label: "Strategy Only", desc: "Market intel & positioning", icon: "📊", pro: false },
    { id: "creative", label: "Creative Hub", desc: "Content & ad layouts", icon: "🎨", pro: true },
    { id: "launch", label: "Launch/Sales", desc: "Leads & social media", icon: "🔗", pro: true },
  ];

  useEffect(() => {
    if (jobState.phase !== "success" || !campaignId) return;
    let cancelled = false;
    void getCampaign(campaignId)
      .then((c) => {
        if (!cancelled) {
          setOutput(JSON.stringify(c.output ?? c, null, 2));
        }
      })
      .catch((e) => {
        if (!cancelled) {
          setError(e instanceof Error ? e.message : "Failed to load campaign");
        }
      });
    return () => {
      cancelled = true;
    };
  }, [jobState.phase, campaignId]);

  const onGenerate = useCallback(async () => {
    setError(null);
    setOutput("");
    setCampaignId(null);
    reset();
    try {
      const res = await createCampaign({
        name: name.trim() || undefined,
        track,
        input: {
          product: product.trim(),
          audience: audience.trim(),
        },
      });
      setCampaignId(res.campaign_id);
      rememberLastCampaignId(res.campaign_id);
      start(res.task_id);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Request failed");
    }
  }, [audience, name, product, track, reset, start]);

  const busy = jobState.phase === "polling";

  return (
    <div className="space-y-4">
      <p className="text-sm text-slate-400">
        <Link href="/campaigns" className="text-violet-400 hover:text-violet-300">
          ← All campaigns
        </Link>
        <span className="text-slate-400"> · </span>
        After generation, open the campaign to approve, reject, or re-run.
      </p>
    <div className="flex flex-col gap-6 lg:flex-row">
      <div className="w-full shrink-0 space-y-4 lg:w-[400px]">
        <div>
          <label className="mb-2 block text-xs font-bold uppercase tracking-wider text-slate-500">Campaign Identity</label>
          <input
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="Campaign name (optional)"
            className="w-full rounded-xl border border-white/[0.1] bg-white/[0.04] p-3 text-slate-100 placeholder:text-slate-500 focus:border-violet-500/50 focus:outline-none focus:ring-2 focus:ring-violet-500/20"
          />
        </div>
        <div className="grid gap-4 sm:grid-cols-2">
            <div>
              <label className="mb-2 block text-xs font-bold uppercase tracking-wider text-slate-500">Product</label>
              <input
                value={product}
                onChange={(e) => setProduct(e.target.value)}
                placeholder="e.g. Acme SaaS"
                className="w-full rounded-xl border border-white/[0.1] bg-white/[0.04] p-3 text-slate-100 placeholder:text-slate-500 focus:border-violet-500/50 focus:outline-none focus:ring-2 focus:ring-violet-500/20"
              />
            </div>
            <div>
               <label className="mb-2 block text-xs font-bold uppercase tracking-wider text-slate-500">Audience</label>
               <input
                 value={audience}
                 onChange={(e) => setAudience(e.target.value)}
                 placeholder="e.g. CMOs in US"
                 className="w-full rounded-xl border border-white/[0.1] bg-white/[0.04] p-3 text-slate-100 placeholder:text-slate-500 focus:border-violet-500/50 focus:outline-none focus:ring-2 focus:ring-violet-500/20"
               />
            </div>
        </div>

        <div>
          <label className="mb-2 block text-xs font-bold uppercase tracking-wider text-slate-500">Selection of Track (Job Scope)</label>
          <div className="grid grid-cols-2 gap-2">
              {TRACKS.map(t => (
                  <button
                    key={t.id}
                    type="button"
                    onClick={() => setTrack(t.id)}
                    className={`relative flex flex-col items-start rounded-xl border p-3 text-left transition-all ${
                        track === t.id 
                        ? 'border-violet-500 bg-violet-500/10' 
                        : 'border-white/[0.06] bg-white/[0.02] hover:bg-white/[0.06]'
                    }`}
                  >
                        {t.pro && (
                            <span className="absolute top-1 right-1 rounded-full bg-amber-500/20 px-1.5 py-0.5 text-[8px] font-black uppercase tracking-tighter text-amber-300">Pro</span>
                        )}
                        <span className="mb-1 text-lg">{t.icon}</span>
                        <span className="text-xs font-bold text-slate-200">{t.label}</span>
                        <span className="text-[10px] text-slate-500">{t.desc}</span>
                  </button>
              ))}
          </div>
        </div>

        <button
          type="button"
          disabled={busy}
          onClick={() => void onGenerate()}
          className="w-full rounded-xl bg-violet-600 py-3 font-medium text-white shadow-lg shadow-violet-600/20 transition-all hover:bg-violet-700 active:scale-[0.98] disabled:cursor-not-allowed disabled:opacity-50"
        >
          {busy ? "Generating…" : `Run Orbit: ${track.toUpperCase()}`}
        </button>
        {error && (
          <div className="rounded-xl border border-rose-500/25 bg-rose-500/10 p-3">
            <p className="text-sm text-rose-300" role="alert">
              {error}
            </p>
            {error.toLowerCase().includes("quota") && (
              <Link
                href="/billing"
                className="mt-2 block text-xs font-semibold text-rose-200 hover:underline"
              >
                Upgrade your plan to increase limits →
              </Link>
            )}
          </div>
        )}
        {jobState.phase === "failure" && (
          <div className="rounded-xl border border-rose-500/25 bg-rose-500/10 p-3">
            <p className="text-sm text-rose-300" role="alert">
              {jobState.message}
            </p>
            {jobState.message?.toLowerCase().includes("quota") && (
              <Link
                href="/billing"
                className="mt-2 block text-xs font-semibold text-rose-200 hover:underline"
              >
                Increase your token quota →
              </Link>
            )}
          </div>
        )}
        {jobState.phase === "polling" && (
          <p className="text-sm text-amber-400">Pipeline running…</p>
        )}
      </div>

      <div className="min-h-[280px] flex-1 rounded-2xl border border-white/[0.06] bg-white/[0.03] p-4 lg:min-h-[420px]">
        <p className="text-sm text-slate-400">Generated output</p>
        <pre className="mt-3 max-h-[min(60vh,520px)] overflow-auto whitespace-pre-wrap break-words text-sm text-slate-300">
          {output || "—"}
        </pre>
      </div>
    </div>
    </div>
  );
}
