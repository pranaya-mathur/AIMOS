"use client";

import Link from "next/link";
import { useSearchParams } from "next/navigation";

export function BillingSuccess() {
  const sp = useSearchParams();
  const campaignId = sp.get("campaign_id");
  const sessionId = sp.get("session_id");

  return (
    <div className="mx-auto max-w-lg space-y-4 text-center">
      <h1 className="text-2xl font-semibold text-green-400">Payment started</h1>
      <p className="text-sm text-slate-600">
        If you completed checkout in Stripe, the webhook will mark your
        campaign <code className="text-slate-500">paid</code> and update quotas.
        This can take a few seconds.
      </p>
      {sessionId && (
        <p className="font-mono text-xs text-slate-500">
          Session: {sessionId.slice(0, 24)}…
        </p>
      )}
      <div className="flex flex-col gap-3 pt-4 sm:flex-row sm:justify-center">
        {campaignId && (
          <Link
            href={`/campaigns/${campaignId}`}
            className="rounded-xl bg-violet-600 px-5 py-2.5 text-sm font-medium text-white hover:bg-violet-700"
          >
            Open campaign
          </Link>
        )}
        <Link
          href="/campaigns"
          className="rounded-xl border border-slate-300 px-5 py-2.5 text-sm text-slate-700 hover:bg-slate-100"
        >
          All campaigns
        </Link>
        <Link
          href="/billing"
          className="rounded-xl border border-slate-300 px-5 py-2.5 text-sm text-slate-700 hover:bg-slate-100"
        >
          Billing
        </Link>
      </div>
    </div>
  );
}
