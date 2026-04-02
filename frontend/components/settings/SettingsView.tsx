"use client";

import Link from "next/link";
import { startTransition, useEffect, useState } from "react";
import { getMe, type MeResponse } from "@/lib/api/auth-profile";
import { swaggerUrl } from "@/lib/services-config";

export function SettingsView() {
  const [me, setMe] = useState<MeResponse | null>(null);
  const [err, setErr] = useState<string | null>(null);

  useEffect(() => {
    startTransition(() => {
      void getMe()
        .then(setMe)
        .catch((e) =>
          setErr(e instanceof Error ? e.message : "Could not load profile"),
        );
    });
  }, []);

  return (
    <div className="mx-auto max-w-xl space-y-8">
      <section>
        <h2 className="text-lg font-semibold text-slate-900">Account</h2>
        {err && (
          <p className="mt-2 text-sm text-red-600" role="alert">
            {err}
          </p>
        )}
        {!me && !err && (
          <p className="mt-2 text-sm text-slate-500">Loading…</p>
        )}
        {me && (
          <dl className="mt-4 space-y-2 text-sm">
            <div className="flex justify-between gap-4 border-b border-slate-200 py-2">
              <dt className="text-slate-500">Email</dt>
              <dd className="text-slate-800">{me.email ?? "—"}</dd>
            </div>
            <div className="flex justify-between gap-4 border-b border-slate-200 py-2">
              <dt className="text-slate-500">Role</dt>
              <dd className="text-slate-800">{me.role ?? "—"}</dd>
            </div>
            <div className="flex justify-between gap-4 border-b border-slate-200 py-2">
              <dt className="text-slate-500">Name</dt>
              <dd className="text-slate-800">{me.full_name ?? "—"}</dd>
            </div>
            <div className="flex justify-between gap-4 py-2">
              <dt className="text-slate-500">User ID</dt>
              <dd className="break-all font-mono text-xs text-slate-600">
                {me.id ?? "—"}
              </dd>
            </div>
            {me.note && (
              <p className="rounded-lg border border-amber-200 bg-amber-50 px-3 py-2 text-xs text-amber-900">
                {me.note}
              </p>
            )}
          </dl>
        )}
      </section>

      <section>
        <h2 className="text-lg font-semibold text-slate-900">Shortcuts</h2>
        <ul className="mt-3 space-y-2 text-sm text-violet-600">
          <li>
            <Link href="/billing" className="hover:text-violet-700">
              Billing & plans
            </Link>
          </li>
          <li>
            <Link href="/analytics" className="hover:text-violet-700">
              Analytics
            </Link>
          </li>
          <li>
            <a
              href={swaggerUrl()}
              target="_blank"
              rel="noopener noreferrer"
              className="hover:text-violet-700"
            >
              API docs (Swagger)
            </a>
          </li>
        </ul>
      </section>
    </div>
  );
}
