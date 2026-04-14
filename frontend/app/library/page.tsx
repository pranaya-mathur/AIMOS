"use client";

import { useEffect, useState } from "react";
import { getMediaAssets, deleteMediaAsset, type MediaAsset } from "@/lib/api/media";

export default function AssetLibraryPage() {
  const [assets, setAssets] = useState<MediaAsset[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState("all");

  useEffect(() => {
    load();
  }, []);

  const load = async () => {
    setLoading(true);
    try {
      const data = await getMediaAssets();
      setAssets(data);
    } finally {
      setLoading(false);
    }
  };

  const remove = async (id: string) => {
    if (!confirm("Are you sure you want to delete this asset?")) return;
    try {
      await deleteMediaAsset(id);
      setAssets(assets.filter((a) => a.id !== id));
    } catch (e) {
      alert("Failed to delete asset.");
    }
  };

  const filtered = assets.filter((a) => {
    if (filter === "all") return true;
    return a.asset_type === filter;
  });

  if (loading) return <div className="p-10 text-center text-slate-500 font-medium">Scanning vault...</div>;

  return (
    <div className="mx-auto max-w-7xl p-8 space-y-10 pb-32">
      <header className="flex flex-col gap-6 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-4xl font-extrabold tracking-tight text-slate-900">Asset Library</h1>
          <p className="text-slate-500 mt-2 text-lg">Every AI-generated creative, curated in one place.</p>
        </div>
        <div className="flex bg-slate-100 p-1 rounded-2xl">
          {["all", "image", "video", "audio"].map((t) => (
            <button
              key={t}
              onClick={() => setFilter(t)}
              className={`px-6 py-2 rounded-xl text-xs font-black uppercase tracking-widest transition-all ${
                filter === t ? "bg-white text-violet-600 shadow-sm" : "text-slate-400 hover:text-slate-600"
              }`}
            >
              {t}
            </button>
          ))}
        </div>
      </header>

      {filtered.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-32 text-center">
            <div className="h-24 w-24 rounded-full bg-slate-100 flex items-center justify-center mb-6">
                <span className="text-4xl">📦</span>
            </div>
          <h2 className="text-2xl font-bold text-slate-400">No assets found</h2>
          <p className="text-slate-400 mt-2">Start a campaign or generate a brand kit to fill your library.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-8 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
          {filtered.map((asset) => (
            <div key={asset.id} className="group relative overflow-hidden rounded-[2rem] border border-slate-200 bg-white transition-all hover:-translate-y-1 hover:shadow-xl">
              <div className="aspect-square relative flex items-center justify-center bg-slate-50">
                {asset.asset_type === "image" ? (
                  <img src={asset.url} alt="AI Creative" className="h-full w-full object-cover" />
                ) : asset.asset_type === "video" ? (
                  <div className="flex flex-col items-center gap-3">
                    <span className="text-4xl">🎬</span>
                    <span className="text-[10px] font-bold uppercase tracking-widest text-slate-400">Video Content</span>
                  </div>
                ) : (
                  <div className="flex flex-col items-center gap-3">
                    <span className="text-4xl">🎙️</span>
                    <span className="text-[10px] font-bold uppercase tracking-widest text-slate-400">AI Voiceover</span>
                  </div>
                )}
                
                {/* Hover Overlay */}
                <div className="absolute inset-0 flex items-center justify-center gap-4 bg-black/60 opacity-0 transition-opacity group-hover:opacity-100">
                    <a 
                        href={asset.url} 
                        target="_blank" 
                        rel="noreferrer"
                        className="rounded-full bg-white px-5 py-2 text-xs font-bold text-slate-900 transition-transform active:scale-95"
                    >
                        View Full
                    </a>
                    <button 
                        onClick={() => remove(asset.id)}
                        className="rounded-full bg-red-500/20 backdrop-blur-md border border-red-500/50 px-5 py-2 text-xs font-bold text-red-500 transition-transform active:scale-95"
                    >
                        Delete
                    </button>
                </div>
              </div>
              <div className="p-5">
                 <div className="flex items-center justify-between">
                    <span className="text-[10px] font-black uppercase tracking-widest text-violet-600">
                        {asset.provider}
                    </span>
                    <span className="text-[10px] font-bold text-slate-400">
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
