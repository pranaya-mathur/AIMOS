"use client";

import { startTransition, useCallback, useEffect, useState } from "react";
import {
  getLaunchStatus,
  launchEmail,
  launchGoogle,
  launchMeta,
  launchSms,
  launchSocial,
  launchWhatsApp,
  type LaunchStatus,
} from "@/lib/api/launch";
import { getSubscription, type SubscriptionInfo } from "@/lib/api/billing";
import { TaskStatusPoller } from "@/components/jobs/TaskStatusPoller";
import { swaggerUrl } from "@/lib/services-config";
import Link from "next/link";

function inputClass() {
  return "mt-1 w-full rounded-xl border border-slate-200 bg-white p-2.5 text-sm text-slate-900 placeholder:text-slate-400 focus:border-violet-400 focus:outline-none focus:ring-2 focus:ring-violet-500/15";
}

export function LaunchCenter() {
  const [status, setStatus] = useState<LaunchStatus | null>(null);
  const [subscription, setSubscription] = useState<SubscriptionInfo | null>(null);
  const [taskId, setTaskId] = useState<string | null>(null);
  const [err, setErr] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  const loadStatus = useCallback(() => {
    startTransition(() => {
      void getLaunchStatus()
        .then(setStatus)
        .catch(() => setStatus(null));
      void getSubscription()
        .then(setSubscription)
        .catch(() => setSubscription(null));
    });
  }, []);

  useEffect(() => {
    loadStatus();
  }, [loadStatus]);

  async function run<T>(fn: () => Promise<T & { task_id?: string }>) {
    setErr(null);
    setBusy(true);
    setTaskId(null);
    try {
      const res = await fn();
      if (res && typeof res === "object" && "task_id" in res && res.task_id) {
        setTaskId(String(res.task_id));
      }
    } catch (e) {
      setErr(e instanceof Error ? e.message : "Request failed");
    } finally {
      setBusy(false);
    }
  }

  const [metaName, setMetaName] = useState("AIMOS draft campaign");
  const [waTo, setWaTo] = useState("");
  const [waBody, setWaBody] = useState("");
  const [gName, setGName] = useState("");
  const [gCustomer, setGCustomer] = useState("");
  const [xText, setXText] = useState("");
  const [emTo, setEmTo] = useState("");
  const [emSub, setEmSub] = useState("");
  const [emBody, setEmBody] = useState("");
  const [smsTo, setSmsTo] = useState("");
  const [smsBody, setSmsBody] = useState("");

  const userTier = subscription?.tier || "free";
  const isFree = userTier === "free";

  function PremiumGuard({
    platform,
    children,
  }: {
    platform: string;
    children: React.ReactNode;
  }) {
    // Only Professional+ can launch to Meta, Google, Email, SMS
    const premiumPaths = ["Meta", "Google Ads", "Email", "SMS"];
    const isPremium = premiumPaths.includes(platform);

    if (isPremium && isFree) {
      return (
        <div className="relative overflow-hidden rounded-2xl border border-violet-100 bg-violet-50/30 p-4">
          <div className="flex items-center justify-between">
            <h3 className="font-medium text-slate-800">{platform}</h3>
            <span className="rounded-full bg-violet-100 px-2 py-0.5 text-[10px] font-bold uppercase tracking-wider text-violet-600">
              Professional Plan
            </span>
          </div>
          <p className="mt-2 text-sm text-slate-600">
            Launch to {platform} is a premium feature. Upgrade your plan to unlock
            ad networks and direct engagement.
          </p>
          <Link
            href="/billing"
            className="mt-3 inline-block text-sm font-semibold text-violet-600 hover:underline"
          >
            Upgrade to Professional →
          </Link>
        </div>
      );
    }

    return (
      <section className="rounded-2xl border border-slate-200 bg-white p-4">
        {children}
      </section>
    );
  }

  return (
    <div className="space-y-10">
      <section>
        <div className="flex flex-wrap items-center justify-between gap-2">
          <h2 className="text-lg font-semibold text-slate-900">
            Integration status
          </h2>
          <button
            type="button"
            onClick={loadStatus}
            className="rounded-lg border border-slate-200 bg-white px-3 py-1.5 text-sm text-slate-700 shadow-sm hover:bg-slate-50"
          >
            Refresh
          </button>
        </div>
        <p className="mt-1 text-sm text-slate-500">
          Boolean flags from env (see{" "}
          <a href={swaggerUrl()} className="text-violet-600 hover:underline">
            Swagger
          </a>{" "}
          <code className="text-slate-500">GET /launch/status</code>).
        </p>
        <pre className="mt-3 max-h-48 overflow-auto rounded-xl border border-slate-200 bg-white p-3 text-xs text-slate-600">
          {status ? JSON.stringify(status, null, 2) : "Loading…"}
        </pre>
      </section>

      {err && (
        <p className="text-sm text-red-400" role="alert">
          {err}
        </p>
      )}

      <PremiumGuard platform="Meta">
        <h3 className="font-medium text-slate-800">Meta marketing</h3>
        <div className="mt-3 grid gap-3 sm:grid-cols-2">
          <label className="text-sm text-slate-600">
            Campaign name
            <input
              value={metaName}
              onChange={(e) => setMetaName(e.target.value)}
              className={inputClass()}
            />
          </label>
        </div>
        <button
          type="button"
          disabled={busy}
          onClick={() =>
            void run(() => launchMeta({ name: metaName.trim() || "Campaign" }))
          }
          className="mt-3 rounded-xl bg-violet-600 px-4 py-2 text-sm font-medium text-white hover:bg-violet-700 disabled:opacity-50"
        >
          Queue Meta (async)
        </button>
      </PremiumGuard>

      <section className="rounded-2xl border border-slate-200 bg-white p-4">
        <h3 className="font-medium text-slate-800">WhatsApp</h3>
        <label className="mt-3 block text-sm text-slate-600">
          To (E.164, no +)
          <input
            value={waTo}
            onChange={(e) => setWaTo(e.target.value)}
            placeholder="15551234567"
            className={inputClass()}
          />
        </label>
        <label className="mt-3 block text-sm text-slate-600">
          Message
          <textarea
            value={waBody}
            onChange={(e) => setWaBody(e.target.value)}
            rows={3}
            className={inputClass()}
          />
        </label>
        <button
          type="button"
          disabled={busy || !waTo.trim()}
          onClick={() =>
            void run(() =>
              launchWhatsApp({ to_e164: waTo.trim(), body: waBody.trim() || " " }),
            )
          }
          className="mt-3 rounded-xl bg-violet-600 px-4 py-2 text-sm font-medium text-white hover:bg-violet-700 disabled:opacity-50"
        >
          Send WhatsApp (async)
        </button>
      </section>

      <PremiumGuard platform="Google Ads">
        <h3 className="font-medium text-slate-800">Google Ads</h3>
        <div className="mt-3 grid gap-3 sm:grid-cols-2">
          <label className="text-sm text-slate-600">
            Campaign name
            <input
              value={gName}
              onChange={(e) => setGName(e.target.value)}
              className={inputClass()}
            />
          </label>
          <label className="text-sm text-slate-600">
            Customer ID (optional)
            <input
              value={gCustomer}
              onChange={(e) => setGCustomer(e.target.value)}
              className={inputClass()}
            />
          </label>
        </div>
        <button
          type="button"
          disabled={busy || !gName.trim()}
          onClick={() =>
            void run(() =>
              launchGoogle({
                campaign_name: gName.trim(),
                customer_id: gCustomer.trim() || null,
              }),
            )
          }
          className="mt-3 rounded-xl bg-violet-600 px-4 py-2 text-sm font-medium text-white hover:bg-violet-700 disabled:opacity-50"
        >
          Queue Google Ads (async)
        </button>
      </PremiumGuard>

      <section className="rounded-2xl border border-slate-200 bg-white p-4">
        <h3 className="font-medium text-slate-800">X (Twitter)</h3>
        <label className="mt-3 block text-sm text-slate-600">
          Post text
          <textarea
            value={xText}
            onChange={(e) => setXText(e.target.value)}
            rows={3}
            className={inputClass()}
          />
        </label>
        <button
          type="button"
          disabled={busy || !xText.trim()}
          onClick={() => void run(() => launchSocial({ text: xText.trim() }))}
          className="mt-3 rounded-xl bg-violet-600 px-4 py-2 text-sm font-medium text-white hover:bg-violet-700 disabled:opacity-50"
        >
          Post (async)
        </button>
      </section>

      <PremiumGuard platform="Email">
        <h3 className="font-medium text-slate-800">Email</h3>
        <div className="mt-3 grid gap-3 sm:grid-cols-2">
          <label className="text-sm text-slate-600 sm:col-span-2">
            To
            <input
              type="email"
              value={emTo}
              onChange={(e) => setEmTo(e.target.value)}
              className={inputClass()}
            />
          </label>
          <label className="text-sm text-slate-600 sm:col-span-2">
            Subject
            <input
              value={emSub}
              onChange={(e) => setEmSub(e.target.value)}
              className={inputClass()}
            />
          </label>
          <label className="text-sm text-slate-600 sm:col-span-2">
            Body
            <textarea
              value={emBody}
              onChange={(e) => setEmBody(e.target.value)}
              rows={4}
              className={inputClass()}
            />
          </label>
        </div>
        <button
          type="button"
          disabled={busy || !emTo.trim()}
          onClick={() =>
            void run(() =>
              launchEmail({
                to_email: emTo.trim(),
                subject: emSub.trim() || "(no subject)",
                body: emBody.trim() || " ",
              }),
            )
          }
          className="mt-3 rounded-xl bg-violet-600 px-4 py-2 text-sm font-medium text-white hover:bg-violet-700 disabled:opacity-50"
        >
          Send email (async)
        </button>
      </PremiumGuard>

      <PremiumGuard platform="SMS">
        <h3 className="font-medium text-slate-800">SMS</h3>
        <label className="mt-3 block text-sm text-slate-600">
          To phone
          <input
            value={smsTo}
            onChange={(e) => setSmsTo(e.target.value)}
            className={inputClass()}
          />
        </label>
        <label className="mt-3 block text-sm text-slate-600">
          Body
          <textarea
            value={smsBody}
            onChange={(e) => setSmsBody(e.target.value)}
            rows={3}
            className={inputClass()}
          />
        </label>
        <button
          type="button"
          disabled={busy || !smsTo.trim()}
          onClick={() =>
            void run(() =>
              launchSms({
                to_phone: smsTo.trim(),
                body: smsBody.trim() || " ",
              }),
            )
          }
          className="mt-3 rounded-xl bg-violet-600 px-4 py-2 text-sm font-medium text-white hover:bg-violet-700 disabled:opacity-50"
        >
          Send SMS (async)
        </button>
      </PremiumGuard>

      <TaskStatusPoller taskId={taskId} />
    </div>
  );
}
