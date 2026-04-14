"use client";

import { useEffect, useState } from "react";
import { getOrgConfig, updateOrgConfig, type WhitelabelConfig } from "@/lib/api/org";

export default function WhitelabelSettingsPage() {
  const [config, setConfig] = useState<WhitelabelConfig>({
    site_name: "AIMOS Enterprise",
    primary_color: "#6d28d9",
    logo_url: ""
  });
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    getOrgConfig()
      .then(setConfig)
      .finally(() => setLoading(false));
  }, []);

  const save = async () => {
    setSaving(true);
    try {
      await updateOrgConfig(config);
      alert("Platform settings updated. Refresh to see changes.");
    } catch (e) {
      alert("Failed to update whitelabel settings.");
    } finally {
      setSaving(false);
    }
  };

  if (loading) return <div className="p-10 text-center font-medium text-slate-500">Retrieving platform identity...</div>;

  return (
    <div className="mx-auto max-w-4xl p-8 space-y-12 pb-32">
      <header className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-4xl font-extrabold tracking-tight text-slate-900">Platform Whitelabeling</h1>
          <p className="text-slate-500 mt-2 text-lg">Customize the look and feel for all users in your organization.</p>
        </div>
        <button
          onClick={save}
          disabled={saving}
          className="rounded-full bg-slate-900 px-8 py-3 font-bold text-white shadow-lg transition-transform hover:scale-105 active:scale-95 disabled:opacity-50"
        >
          {saving ? "Saving..." : "Deploy UI Changes"}
        </button>
      </header>

      <div className="grid grid-cols-1 gap-8 md:grid-cols-2">
        {/* Basic Brand Info */}
        <section className="space-y-6 rounded-[2rem] border border-slate-200 bg-white p-10 shadow-sm">
          <h2 className="text-2xl font-bold text-slate-800 italic underline underline-offset-8 decoration-violet-200">1. Identity</h2>
          <div className="space-y-4">
            <div>
              <label className="block text-xs font-black uppercase tracking-widest text-slate-400 mb-2">Internal Site Name</label>
              <input
                type="text"
                className="w-full rounded-2xl border border-slate-100 bg-slate-50 p-4 text-slate-900 font-bold focus:ring-2 focus:ring-violet-600 outline-none"
                value={config.site_name || ""}
                onChange={(e) => setConfig({ ...config, site_name: e.target.value })}
                placeholder="e.g. My Agency OS"
              />
            </div>
            <div>
              <label className="block text-xs font-black uppercase tracking-widest text-slate-400 mb-2">Logo URL (Icon)</label>
              <input
                type="text"
                className="w-full rounded-2xl border border-slate-100 bg-slate-50 p-4 text-slate-900 outline-none focus:ring-2 focus:ring-violet-600"
                value={config.logo_url || ""}
                onChange={(e) => setConfig({ ...config, logo_url: e.target.value })}
                placeholder="https://..."
              />
            </div>
          </div>
        </section>

        {/* Visual Styling */}
        <section className="space-y-6 rounded-[2rem] border border-slate-200 bg-white p-10 shadow-sm">
          <h2 className="text-2xl font-bold text-slate-800 italic underline underline-offset-8 decoration-violet-200">2. Visual DNA</h2>
          <div className="space-y-4">
             <div>
              <label className="block text-xs font-black uppercase tracking-widest text-slate-400 mb-2">Primary Accent Color</label>
              <div className="flex items-center gap-4">
                <input
                    type="color"
                    className="h-14 w-14 cursor-pointer rounded-xl border-none p-0"
                    value={config.primary_color || "#6d28d9"}
                    onChange={(e) => setConfig({ ...config, primary_color: e.target.value })}
                />
                <input
                    type="text"
                    className="flex-1 rounded-2xl border border-slate-100 bg-slate-50 p-4 font-mono text-sm outline-none focus:ring-2 focus:ring-violet-600"
                    value={config.primary_color || ""}
                    onChange={(e) => setConfig({ ...config, primary_color: e.target.value })}
                />
              </div>
             </div>
             
             {/* Live Preview Sample */}
             <div className="mt-8 rounded-3xl p-6 bg-slate-50 border border-slate-100">
                <p className="text-[10px] font-black uppercase tracking-widest text-slate-400 mb-4">Live Token Preview</p>
                <div className="flex gap-3">
                    <div className="h-8 w-8 rounded-full shadow-inner" style={{ backgroundColor: config.primary_color }} />
                    <div className={`h-8 flex-1 rounded-full`} style={{ opacity: 0.2, backgroundColor: config.primary_color }} />
                    <div className={`h-8 flex-1 rounded-full`} style={{ opacity: 0.1, backgroundColor: config.primary_color }} />
                </div>
             </div>
          </div>
        </section>
      </div>

      {/* Audit & Compliance Disclaimer */}
      <footer className="rounded-[2rem] bg-slate-900 p-10 text-white flex items-center gap-8">
        <div className="h-20 w-20 rounded-full bg-white/10 flex items-center justify-center shrink-0">
            <span className="text-3xl font-black">!</span>
        </div>
        <div>
            <h3 className="text-lg font-bold">Whitelabeling & Compliance</h3>
            <p className="text-sm text-slate-400 mt-1 max-w-2xl">
                Changes made here affect the public-facing dashboard for all users in your organization. All UI updates are logged in the 
                <strong> Secure Audit Trail</strong> for compliance monitoring.
            </p>
        </div>
      </footer>
    </div>
  );
}
