"use client";

import { useEffect, useState } from "react";
import { listCreatives, updateCreative, approveCreative, type AdCreative } from "@/lib/api/creatives";
import { getMediaAssets, type MediaAsset } from "@/lib/api/media";

export default function CreativeStudioPage() {
  const [creatives, setCreatives] = useState<AdCreative[]>([]);
  const [assets, setAssets] = useState<MediaAsset[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([listCreatives(), getMediaAssets()])
      .then(([cData, aData]) => {
        setCreatives(cData);
        setAssets(aData);
      })
      .finally(() => setLoading(false));
  }, []);

  const handleApprove = async (id: string) => {
    try {
      await approveCreative(id);
      setCreatives(creatives.map(c => c.id === id ? { ...c, status: "approved" } : c));
    } catch (e) {
      alert("Approval failed.");
    }
  };

  const toggleFavorite = async (id: string, current: string) => {
    const next = current === "true" ? "false" : "true";
    try {
      await updateCreative(id, { is_favorite: next });
      setCreatives(creatives.map(c => c.id === id ? { ...c, is_favorite: next } : c));
    } catch (e) {
      alert("Failed to update favorite status.");
    }
  };

  if (loading) return <div className="p-20 text-center font-medium text-slate-400">Loading your creative variations...</div>;

  return (
    <div className="p-10 max-w-7xl mx-auto">
      <header className="mb-12">
        <h1 className="text-4xl font-black text-slate-900 tracking-tight">Creative Studio</h1>
        <p className="text-slate-500 mt-2 font-medium">Review AI variations, edit copy, and approve assets for launch.</p>
      </header>

      {creatives.length === 0 ? (
        <div className="rounded-[3rem] border-2 border-dashed border-slate-200 p-20 text-center">
          <p className="text-slate-400 font-bold">No variations found. Run a campaign to generate creatives.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {creatives.map((c) => (
            <div key={c.id} className="group relative rounded-[2.5rem] border border-slate-100 bg-white p-8 shadow-sm transition-all hover:shadow-2xl hover:border-violet-100">
              {/* Status Badge */}
              <div className="flex justify-between items-start mb-6">
                <span className={`px-3 py-1 rounded-full text-[10px] font-black uppercase tracking-widest ${
                  c.status === "approved" ? "bg-emerald-100 text-emerald-600" : "bg-slate-100 text-slate-400"
                }`}>
                  {c.status}
                </span>
                <button 
                  onClick={() => toggleFavorite(c.id, c.is_favorite)}
                  className={`text-lg transition-colors ${c.is_favorite === "true" ? "text-amber-400" : "text-slate-200 hover:text-amber-200"}`}
                >
                  ★
                </button>
              </div>

              {/* Mock Ad Preview */}
              <div className="aspect-[4/5] rounded-[2rem] bg-slate-50 mb-8 overflow-hidden relative border border-slate-50">
                {assets.find(a => a.id === c.media_asset_id)?.url ? (
                  <img src={assets.find(a => a.id === c.media_asset_id)?.url} alt="Ad content" className="w-full h-full object-cover" />
                ) : (
                  <div className="w-full h-full flex flex-col items-center justify-center text-slate-300">
                    <span className="text-4xl mb-2">🖼️</span>
                    <span className="text-[10px] font-black uppercase tracking-widest">Image Pending</span>
                  </div>
                )}
                
                {/* Ad Copy Overlay (Simulated) */}
                <div className="absolute bottom-0 left-0 right-0 p-6 bg-gradient-to-t from-black/80 to-transparent text-white">
                  <h3 className="text-lg font-bold mb-1 truncate">{c.headline}</h3>
                  <p className="text-xs opacity-80 line-clamp-2">{c.body_copy}</p>
                </div>
              </div>

              <div className="space-y-4">
                <div className="p-4 rounded-2xl bg-slate-50 border border-slate-100">
                   <p className="text-[10px] font-black uppercase tracking-widest text-slate-400 mb-1">Headline</p>
                   <p className="text-sm font-bold text-slate-900">{c.headline}</p>
                </div>
                <div className="p-4 rounded-2xl bg-slate-50 border border-slate-100">
                   <p className="text-[10px] font-black uppercase tracking-widest text-slate-400 mb-1">Primary CTA</p>
                   <p className="text-sm font-bold text-slate-900">{c.cta_text}</p>
                </div>
              </div>

              <div className="mt-8 pt-6 border-t border-slate-50">
                <button 
                  onClick={() => handleApprove(c.id)}
                  disabled={c.status === "approved"}
                  className={`w-full rounded-2xl py-4 text-xs font-bold uppercase tracking-widest transition-all ${
                    c.status === "approved" 
                      ? "bg-emerald-500 text-white" 
                      : "bg-slate-900 text-white hover:bg-slate-800"
                  }`}
                >
                  {c.status === "approved" ? "✓ Approved for Launch" : "Approve Variation"}
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
