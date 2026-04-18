"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { deleteMediaAsset, getMediaAssets, type MediaAsset } from "@/lib/api/media";

export default function MediaAssetsPage() {
  const [assets, setAssets] = useState<MediaAsset[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState("all");

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const data = await getMediaAssets();
      setAssets(data);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  const remove = async (id: string) => {
    if (!confirm("Are you sure you want to delete this asset?")) return;
    try {
      await deleteMediaAsset(id);
      setAssets((prev) => prev.filter((a) => a.id !== id));
    } catch {
      alert("Failed to delete asset.");
    }
  };

  const filtered = assets.filter((a) => {
    if (filter === "all") return true;
    return a.asset_type === filter;
  });

  if (loading) {
    return (
      <div className="p-10 text-center font-medium text-slate-500">
        Scanning vault…
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-7xl space-y-10 p-8 pb-32">
      <header className="flex flex-col gap-6 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-4xl font-extrabold tracking-tight text-white">
            Media assets
          </h1>
          <p className="mt-2 text-lg text-slate-400">
            AI-generated files from media jobs.{" "}
            <Link
              href="/media-studio"
              className="text-violet-400 hover:text-violet-300"
            >
              Open Media Studio →
            </Link>
          </p>
        </div>
        <div className="flex rounded-2xl border border-white/[0.08] bg-white/[0.04] p-1">
          {["all", "image", "video", "audio"].map((t) => (
            <button
              key={t}
              type="button"
              onClick={() => setFilter(t)}
              className={`rounded-xl px-6 py-2 text-xs font-black uppercase tracking-widest transition-all ${
                filter === t
                  ? "bg-violet-600 text-white shadow-md"
                  : "text-slate-500 hover:text-slate-300"
              }`}
            >
              {t}
            </button>
          ))}
        </div>
      </header>

      {filtered.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-32 text-center">
          <div className="mb-6 flex h-24 w-24 items-center justify-center rounded-full border border-white/[0.08] bg-white/[0.04]">
            <span className="text-4xl">📦</span>
          </div>
          <h2 className="text-2xl font-bold text-slate-400">No assets found</h2>
          <p className="mt-2 text-slate-500">
            Run jobs from Media Studio or campaigns to populate this library.
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-8 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
          {filtered.map((asset) => (
            <div
              key={asset.id}
              className="group relative overflow-hidden rounded-[2rem] border border-white/[0.08] bg-white/[0.04] transition-all hover:-translate-y-1 hover:border-white/[0.12]"
            >
              <div className="relative flex aspect-square items-center justify-center bg-black/20">
                {asset.asset_type === "image" ? (
                  <img
                    src={asset.url}
                    alt="AI creative"
                    className="h-full w-full object-cover"
                  />
                ) : asset.asset_type === "video" ? (
                  <div className="flex flex-col items-center gap-3">
                    <span className="text-4xl">🎬</span>
                    <span className="text-[10px] font-bold uppercase tracking-widest text-slate-500">
                      Video
                    </span>
                  </div>
                ) : (
                  <div className="flex flex-col items-center gap-3">
                    <span className="text-4xl">🎙️</span>
                    <span className="text-[10px] font-bold uppercase tracking-widest text-slate-500">
                      Audio
                    </span>
                  </div>
                )}

                <div className="absolute inset-0 flex items-center justify-center gap-4 bg-black/70 opacity-0 transition-opacity group-hover:opacity-100">
                  <a
                    href={asset.url}
                    target="_blank"
                    rel="noreferrer"
                    className="rounded-full bg-white px-5 py-2 text-xs font-bold text-slate-900 transition-transform active:scale-95"
                  >
                    View
                  </a>
                  <button
                    type="button"
                    onClick={() => void remove(asset.id)}
                    className="rounded-full border border-rose-500/50 bg-rose-500/20 px-5 py-2 text-xs font-bold text-rose-200 backdrop-blur-md transition-transform active:scale-95"
                  >
                    Delete
                  </button>
                </div>
              </div>
              <div className="p-5">
                <div className="flex items-center justify-between">
                  <span className="text-[10px] font-black uppercase tracking-widest text-violet-400">
                    {asset.provider}
                  </span>
                  <span className="text-[10px] font-bold text-slate-500">
                    {new Date(asset.created_at).toLocaleDateString()}
                  </span>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
