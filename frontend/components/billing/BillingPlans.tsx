"use client";

import Link from "next/link";
import { startTransition, useEffect, useState } from "react";
import { createCheckoutSession } from "@/lib/api/billing";
import { listCampaigns, type CampaignSummary } from "@/lib/api/campaign";
import { getUsageMe, type UsageMe } from "@/lib/api/analytics";
import { PLAN_TIERS } from "@/lib/plan-tiers";

export function BillingPlans() {
  const [campaigns, setCampaigns] = useState<CampaignSummary[]>([]);
  const [usage, setUsage] = useState<UsageMe | null>(null);
  const [campaignId, setCampaignId] = useState("");
  const [priceId, setPriceId] = useState("");
  const [err, setErr] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    startTransition(() => {
      void listCampaigns(100)
        .then((rows) => {
          setCampaigns(rows);
        })
        .catch(() => {});
      void getUsageMe()
        .then(setUsage)
        .catch(() => setUsage(null));
    });
  }, []);

  useEffect(() => {
    if (campaigns.length > 0 && !campaignId) {
      setCampaignId(campaigns[0].id);
    }
  }, [campaigns, campaignId]);

  async function pay() {
    if (!campaignId.trim()) {
      setErr("Choose a campaign to attach this payment to.");
      return;
    }
    setErr(null);
    setBusy(true);
    try {
      const origin =
        typeof window !== "undefined" ? window.location.origin : "";
      const success_url = `${origin}/billing/success?campaign_id=${encodeURIComponent(campaignId)}`;
      const cancel_url = `${origin}/billing/cancel`;
      const res = await createCheckoutSession({
        campaign_id: campaignId.trim(),
        success_url,
        cancel_url,
        price_id: priceId.trim() || null,
      });
      window.location.href = res.url;
    } catch (e) {
      setErr(
        e instanceof Error ? e.message : "Checkout failed — is Stripe configured?",
      );
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="space-y-10">
      <section>
        <h2 className="text-lg font-semibold text-slate-900">Your plan & quotas</h2>
        <p className="mt-1 max-w-2xl text-sm text-slate-600">
          After payment, Stripe webhook updates campaign status to{" "}
          <code className="text-slate-500">paid</code> and applies quota rules to
          your user based on the Price ID (see backend{" "}
          <code className="text-slate-500">get_quotas_for_price</code>).
        </p>
        {usage && (
          <div className="mt-4 rounded-2xl border border-slate-200 bg-slate-50 p-4 text-sm">
            <p className="text-slate-600">
              UTC month: {usage.period_utc.start.slice(0, 10)} →{" "}
              {usage.period_utc.end.slice(0, 10)}
            </p>
            <div className="mt-2 grid gap-2 sm:grid-cols-2">
              <p className="text-slate-800">
                Campaigns:{" "}
                <strong>{usage.campaigns.used}</strong>
                {usage.campaigns.limit != null
                  ? ` / ${usage.campaigns.limit}`
                  : ""}{" "}
                {usage.campaigns.remaining != null
                  ? `(remaining ${usage.campaigns.remaining})`
                  : ""}
              </p>
              <p className="text-slate-800">
                Tokens: <strong>{usage.tokens.used.toLocaleString()}</strong>
                {usage.tokens.limit != null
                  ? ` / ${usage.tokens.limit.toLocaleString()}`
                  : ""}
              </p>
            </div>
            {usage.note && (
              <p className="mt-2 text-xs text-amber-800">{usage.note}</p>
            )}
          </div>
        )}
      </section>

      <section>
        <h2 className="mb-4 text-sm font-medium uppercase tracking-wide text-slate-500">
          Tiers (configure Stripe Price IDs)
        </h2>
        <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
          {PLAN_TIERS.map((p) => (
            <div
              key={p.slug}
              className="rounded-2xl border border-slate-200 bg-white p-4"
            >
              <h3 className="font-semibold text-slate-900">{p.name}</h3>
              <p className="mt-1 text-sm text-slate-600">{p.tagline}</p>
              <ul className="mt-3 space-y-1 text-sm text-slate-700">
                <li>Campaigns: {p.campaigns}</li>
                <li>Tokens: {p.tokens}</li>
              </ul>
              <p className="mt-3 text-xs text-slate-500">{p.priceIdHint}</p>
            </div>
          ))}
        </div>
      </section>

      <section className="rounded-2xl border border-violet-200 bg-white p-6">
        <h2 className="text-lg font-semibold text-slate-900">Pay with Stripe</h2>
        <p className="mt-1 text-sm text-slate-600">
          Requires <code className="text-slate-500">STRIPE_SECRET_KEY</code> and{" "}
          <code className="text-slate-500">STRIPE_DEFAULT_PRICE_ID</code> (or
          paste a Price ID below). Campaign must exist — pick one or create from{" "}
          <Link href="/campaign" className="text-violet-600 hover:underline">
            New campaign
          </Link>
          .
        </p>
        <div className="mt-6 max-w-lg space-y-4">
          <label className="block text-sm text-slate-600">
            Campaign
            <select
              value={campaignId}
              onChange={(e) => setCampaignId(e.target.value)}
              className="mt-1 w-full rounded-xl border border-slate-200 bg-white p-3 text-slate-900 shadow-sm"
            >
              <option value="">Select campaign…</option>
              {campaigns.map((c) => (
                <option key={c.id} value={c.id}>
                  {(c.name || c.id.slice(0, 8)) + "…"} — {c.status}
                </option>
              ))}
            </select>
          </label>
          <label className="block text-sm text-slate-600">
            Stripe Price ID (optional override)
            <input
              value={priceId}
              onChange={(e) => setPriceId(e.target.value)}
              placeholder="price_… or leave empty for STRIPE_DEFAULT_PRICE_ID"
              className="mt-1 w-full rounded-xl border border-slate-200 bg-slate-50 p-3 font-mono text-sm text-slate-900 placeholder:text-slate-400 focus:border-violet-400 focus:bg-white focus:outline-none focus:ring-2 focus:ring-violet-500/15"
            />
          </label>
        </div>
        {err && (
          <p className="mt-4 text-sm text-red-600" role="alert">
            {err}
          </p>
        )}
        <button
          type="button"
          disabled={busy || !campaignId}
          onClick={() => void pay()}
          className="mt-6 rounded-xl bg-violet-600 px-6 py-3 font-medium text-white hover:bg-violet-700 disabled:cursor-not-allowed disabled:opacity-50"
        >
          {busy ? "Redirecting…" : "Continue to Stripe Checkout"}
        </button>
      </section>
    </div>
  );
}
