"use client";

import { useState } from "react";
import { generateBanner } from "@/lib/api/creatives";
import { Sparkles, Download, Wand2, Layout, Image as ImageIcon, Loader2, RefreshCw } from "lucide-react";

export function BannerStudio() {
  const [productName, setProductName] = useState("");
  const [features, setFeatures] = useState("");
  const [style, setStyle] = useState("luxury");
  const [bannerUrl, setBannerUrl] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const styles = [
    { id: "luxury", label: "Luxury", icon: "✨" },
    { id: "modern", label: "Modern", icon: "🏙️" },
    { id: "minimal", label: "Minimal", icon: "⚪" },
    { id: "nature", label: "Nature", icon: "🌿" },
    { id: "cinematic", label: "Cinematic", icon: "🎬" },
    { id: "urban", label: "Urban", icon: "🌆" },
    { id: "night", label: "Night", icon: "🌙" },
    { id: "dramatic", label: "Dramatic", icon: "⚡" },
  ];


  async function handleGenerate(forceNew = false) {
    if (!productName || !features) {
      setError("Please provide a product name and features.");
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const res = await generateBanner({
        product_name: productName,
        features: features,
        style: style,
      });
      setBannerUrl(res.banner_url);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Generation failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start animate-in fade-in slide-in-from-bottom-4 duration-700">
      {/* Configuration Panel */}
      <div className="lg:col-span-5 space-y-6">
        <div className="glass-panel p-8 rounded-[2.5rem] border-white/[0.08] relative overflow-hidden group">
          <div className="absolute inset-0 bg-gradient-to-br from-primary/5 to-transparent pointer-events-none" />

          <div className="relative z-10 space-y-8">
            <div className="flex items-center gap-3">
              <div className="p-3 rounded-2xl bg-primary/10 border border-primary/20">
                <Wand2 className="h-6 w-6 text-primary" />
              </div>
              <div>
                <h3 className="text-xl font-bold text-white tracking-tight">Banner Architect</h3>
                <p className="text-xs text-slate-500 font-bold uppercase tracking-widest">Sovereign Engine v6.0</p>
              </div>
            </div>

            <div className="space-y-5">
              {/* Product Name */}
              <div className="space-y-2">
                <label className="text-[10px] font-black uppercase tracking-widest text-slate-400">Product Name</label>
                <input
                  type="text"
                  placeholder="e.g. Nomad Pro Luggage"
                  value={productName}
                  onChange={(e) => setProductName(e.target.value)}
                  className="w-full h-14 px-5 rounded-2xl bg-white/[0.03] border border-white/[0.08] text-white focus:border-primary/50 focus:ring-4 focus:ring-primary/10 transition-all outline-none"
                />
              </div>

              {/* Features */}
              <div className="space-y-2">
                <label className="text-[10px] font-black uppercase tracking-widest text-slate-400">Key Features & Context</label>
                <textarea
                  placeholder="Describe the product context and key selling points..."
                  value={features}
                  onChange={(e) => setFeatures(e.target.value)}
                  rows={4}
                  className="w-full p-5 rounded-2xl bg-white/[0.03] border border-white/[0.08] text-white focus:border-primary/50 focus:ring-4 focus:ring-primary/10 transition-all outline-none resize-none"
                />
              </div>

              {/* Aesthetic Style */}
              <div className="space-y-2">
                <label className="text-[10px] font-black uppercase tracking-widest text-slate-400">Aesthetic Style</label>
                <div className="grid grid-cols-4 gap-2">
                  {styles.map((s) => (
                    <button
                      key={s.id}
                      onClick={() => setStyle(s.id)}
                      className={`py-3 px-2 rounded-xl border text-[10px] font-bold transition-all flex flex-col items-center gap-1 ${
                        style === s.id
                          ? "bg-primary border-primary text-white shadow-[0_0_20px_rgba(139,92,246,0.3)]"
                          : "bg-white/[0.02] border-white/[0.06] text-slate-400 hover:bg-white/[0.05] hover:border-white/[0.12]"
                      }`}
                    >
                      <span className="text-base">{s.icon}</span>
                      {s.label}
                    </button>
                  ))}
                </div>
              </div>

            </div>

            {error && (
              <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-400 text-xs font-medium">
                {error}
              </div>
            )}

            {/* Action Buttons */}
            <div className="flex gap-3">
              <button
                onClick={() => handleGenerate()}
                disabled={loading}
                className="flex-1 group relative overflow-hidden h-16 rounded-[2rem] bg-primary text-white font-black uppercase tracking-widest hover:shadow-[0_0_40px_rgba(139,92,246,0.4)] transition-all disabled:opacity-50"
              >
                <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/10 to-transparent translate-x-[-100%] group-hover:translate-x-[100%] duration-1000 transition-transform" />
                <div className="flex items-center justify-center gap-3">
                  {loading ? (
                    <>
                      <Loader2 className="h-5 w-5 animate-spin" />
                      <span>Orchestrating...</span>
                    </>
                  ) : (
                    <>
                      <Sparkles className="h-5 w-5" />
                      <span>Generate</span>
                    </>
                  )}
                </div>
              </button>

              {bannerUrl && !loading && (
                <button
                  onClick={() => handleGenerate(true)}
                  title="Regenerate with new seed"
                  className="h-16 w-16 rounded-[2rem] bg-white/[0.05] border border-white/[0.1] text-slate-400 hover:text-white hover:bg-white/[0.1] hover:border-white/[0.2] transition-all flex items-center justify-center"
                >
                  <RefreshCw className="h-5 w-5" />
                </button>
              )}
            </div>
          </div>
        </div>

        {/* Config Info */}
        <div className="p-6 rounded-[2rem] border border-dashed border-white/[0.08] bg-white/[0.01]">
          <div className="flex items-center gap-3 mb-4">
            <Layout className="h-4 w-4 text-slate-500" />
            <span className="text-[10px] font-black uppercase tracking-widest text-slate-500">Global Configuration</span>
          </div>
          <div className="flex items-center justify-between text-[11px] font-medium text-slate-400">
            <span>Ratio: <span className="text-white">16:9</span></span>
            <span>Res: <span className="text-white">1280×720</span></span>
            <span>Steps: <span className="text-emerald-400">20</span></span>
            <span>Model: <span className="text-primary">Juggernaut XL</span></span>
          </div>
        </div>
      </div>

      {/* Preview Panel */}
      <div className="lg:col-span-7 space-y-6 h-full">
        <div className="glass-panel min-h-[500px] flex flex-col rounded-[2.5rem] border-white/[0.08] overflow-hidden relative">
          <div className="p-6 border-b border-white/[0.06] flex items-center justify-between shrink-0 bg-white/[0.02]">
            <div className="flex items-center gap-2">
              <div className="h-2 w-2 rounded-full bg-emerald-400 animate-pulse" />
              <span className="text-[10px] font-black uppercase tracking-widest text-slate-400">Live Preview Output</span>
            </div>
            {bannerUrl && (
              <a
                href={bannerUrl}
                download={`${productName.replace(/\s+/g, '-').toLowerCase()}-banner.png`}
                className="flex items-center gap-2 px-4 py-2 rounded-full bg-white/[0.05] border border-white/[0.1] text-[10px] font-black text-white hover:bg-white/[0.1] transition-all"
              >
                <Download className="h-3 w-3" />
                Download Asset
              </a>
            )}
          </div>

          <div className="flex-grow flex items-center justify-center p-8 bg-[#0a0a0B] relative">
            {bannerUrl ? (
              <div className="relative group/image w-full max-w-4xl shadow-[0_32px_64px_-16px_rgba(0,0,0,0.6)] rounded-2xl overflow-hidden animate-in zoom-in-95 duration-500">
                <img
                  src={bannerUrl}
                  alt="Generated Banner"
                  className="w-full h-auto"
                />
                <div className="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent opacity-0 group-hover/image:opacity-100 transition-opacity flex items-end p-6">
                  <p className="text-[10px] font-bold text-white/70 tracking-widest uppercase italic">
                    Cinematic AI-Generated Production · Engine v6.0
                  </p>
                </div>
              </div>
            ) : (
              <div className="flex flex-col items-center gap-6 opacity-20">
                <div className="p-8 rounded-full bg-white/[0.05] border border-white/[0.1]">
                  <ImageIcon className="h-16 w-16 text-slate-400" />
                </div>
                <div className="text-center space-y-2">
                  <p className="text-[10px] font-black uppercase tracking-[0.3em] text-slate-400">Awaiting Signal</p>
                  <p className="text-sm text-slate-600 max-w-xs leading-relaxed">
                    Configure your product, choose a style and scene, then generate.
                  </p>
                </div>
              </div>
            )}

            {loading && (
              <div className="absolute inset-0 bg-black/60 backdrop-blur-sm flex flex-col items-center justify-center gap-6 z-20">
                <div className="relative">
                  <div className="h-24 w-24 rounded-full border-[3px] border-primary/20 border-t-primary animate-spin" />
                  <Sparkles className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 h-8 w-8 text-primary animate-pulse" />
                </div>
                <div className="text-center">
                  <h4 className="text-lg font-black text-white tracking-[0.2em] uppercase italic">Synthesizing...</h4>
                  <p className="text-[10px] font-bold text-slate-500 tracking-widest uppercase mt-2">Local Sovereign Node Active · 20-Step Render</p>
                </div>
              </div>
            )}
          </div>

          <div className="p-4 border-t border-white/[0.06] flex items-center justify-center gap-8 bg-white/[0.01]">
            <div className="flex items-center gap-2 opacity-30">
              <div className="h-1.5 w-1.5 rounded-full bg-slate-500" />
              <span className="text-[8px] font-black uppercase tracking-tighter text-slate-500">Cinematic Diversity</span>
            </div>
            <div className="flex items-center gap-2 opacity-30">
              <div className="h-1.5 w-1.5 rounded-full bg-slate-500" />
              <span className="text-[8px] font-black uppercase tracking-tighter text-slate-500">Commercial Ready</span>
            </div>
            <div className="flex items-center gap-2 opacity-30">
              <div className="h-1.5 w-1.5 rounded-full bg-slate-500" />
              <span className="text-[8px] font-black uppercase tracking-tighter text-slate-500">No Watermarks</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
