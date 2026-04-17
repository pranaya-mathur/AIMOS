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
        <h2 className="text-lg font-semibold text-slate-900">Agency Branding</h2>
        <div className="mt-4 space-y-4">
             <div className="space-y-1">
                 <label className="text-[10px] font-black uppercase tracking-widest text-slate-400">Site Name</label>
                 <input 
                    type="text" 
                    placeholder="AIMOS Enterprise"
                    className="w-full rounded-2xl bg-slate-50 border border-slate-100 p-4 text-sm font-medium" 
                 />
             </div>
             <div className="space-y-1">
                 <label className="text-[10px] font-black uppercase tracking-widest text-slate-400">Logo URL</label>
                 <input 
                    type="text" 
                    placeholder="https://..."
                    className="w-full rounded-2xl bg-slate-50 border border-slate-100 p-4 text-sm font-medium" 
                 />
             </div>
             <div className="flex items-center gap-4">
                 <div className="space-y-1 flex-1">
                    <label className="text-[10px] font-black uppercase tracking-widest text-slate-400">Primary Brand Color</label>
                    <input 
                        type="color" 
                        className="w-full h-12 rounded-2xl cursor-pointer" 
                    />
                 </div>
                 <button className="h-12 px-8 mt-5 rounded-2xl bg-slate-900 text-white text-[10px] font-black uppercase tracking-widest">Save Branding</button>
             </div>
        </div>
      </section>

      <section>
        <h2 className="text-lg font-semibold text-slate-900">Governance & Security</h2>
        <ul className="mt-4 space-y-2 text-sm text-slate-600">
          <li className="flex items-center justify-between p-4 rounded-2xl bg-slate-50 border border-slate-100">
             <div>
                <span className="block font-bold">Multi-Seat Team</span>
                <span className="text-[10px] text-slate-400 font-medium">Manage members and seats</span>
             </div>
             <Link href="/settings/team" className="text-violet-600 font-bold hover:underline">Manage Team →</Link>
          </li>
          <li className="flex items-center justify-between p-4 rounded-2xl bg-slate-50 border border-slate-100">
             <span>Enterprise Audit Trail</span>
             <Link href="/settings/audit" className="text-violet-600 font-bold hover:underline">View History →</Link>
          </li>
          <li>
            <a
              href={swaggerUrl()}
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center justify-between p-4 rounded-2xl bg-slate-50 border border-slate-100 text-slate-600 hover:text-violet-600"
            >
              <span>API docs (Swagger)</span>
              <span className="opacity-40">↗</span>
            </a>
          </li>
        </ul>
      </section>
    </div>
  );
}
