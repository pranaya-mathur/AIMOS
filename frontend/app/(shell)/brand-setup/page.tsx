"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { getBrand, upsertBrand, generateLogo, generateBrandKit, type BrandData } from "@/lib/api/brand";
import { Sparkles, Save, Globe, Target, DollarSign, PenTool, Image as ImageIcon, ChevronRight } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";

export default function BrandSetupPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [generatingLogo, setGeneratingLogo] = useState(false);
  const [generatingKit, setGeneratingKit] = useState(false);
  const [brandKit, setBrandKit] = useState<any>(null);

  const [formData, setFormData] = useState<BrandData>({
    name: "",
    category: "",
    description: "",
    website_url: "",
    social_links: { instagram: "", facebook: "", youtube: "" },
    target_audience: { age: "", gender: "", location: "", interests: "" },
    product_details: [],
    pricing_range: "mid",
  });

  useEffect(() => {
    getBrand()
      .then((data) => {
        if (data.name) {
            setFormData((prev) => ({ ...prev, ...data }));
            if (data.ai_generated_kit) setBrandKit(data.ai_generated_kit);
        }
      })
      .finally(() => setLoading(false));
  }, []);

  const save = async () => {
    setSaving(true);
    try {
      await upsertBrand(formData);
      router.push("/");
    } catch (e) {
      alert("Failed to save brand details.");
    } finally {
      setSaving(false);
    }
  };

  const handleGenerateLogo = async () => {
    setGeneratingLogo(true);
    try {
      const res = await generateLogo();
      setFormData(prev => ({ ...prev, logo_url: res.logo_url }));
    } catch (e) {
      alert("AI logo generation failed.");
    } finally {
      setGeneratingLogo(false);
    }
  };

  const handleGenerateKit = async () => {
    setGeneratingKit(true);
    try {
      const res = await generateBrandKit();
      setBrandKit(res.brand_kit);
      if (!formData.description && res.brand_kit.brand_narrative) {
        setFormData(prev => ({ ...prev, description: res.brand_kit.brand_narrative }));
      }
    } catch (e) {
      alert("AI brand kit generation failed.");
    } finally {
      setGeneratingKit(false);
    }
  };

  if (loading) return (
    <div className="flex flex-col items-center justify-center min-h-[60vh] gap-4">
      <div className="h-12 w-12 rounded-full border-4 border-primary/20 border-t-primary animate-spin" />
      <p className="text-mono-premium animate-pulse">Initializing Brand Neural Profile...</p>
    </div>
  );

  return (
    <motion.div 
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="mx-auto max-w-6xl p-8 space-y-12 pb-32"
    >
      <header className="flex flex-col gap-6 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-5xl font-black text-white tracking-tighter uppercase italic">Brand Identity</h1>
          <p className="text-slate-400 mt-2 font-medium italic">Defining the autonomous representation of your market presence.</p>
        </div>
        <div className="flex gap-4">
          <button
            onClick={handleGenerateKit}
            disabled={generatingKit || !formData.name}
            className="group relative overflow-hidden rounded-2xl bg-primary/10 border border-primary/20 px-6 py-3 font-black text-primary uppercase tracking-widest shadow-[0_0_20px_rgba(139,92,246,0.1)] transition-all hover:bg-primary/20 hover:scale-105 active:scale-95 disabled:opacity-50"
          >
            <div className="flex items-center gap-2">
               {generatingKit ? <div className="h-4 w-4 animate-spin border-2 border-primary border-t-transparent rounded-full" /> : <Sparkles className="h-4 w-4" />}
               <span>{generatingKit ? "Developing..." : "AI Intelligence"}</span>
            </div>
          </button>
          <button
            onClick={save}
            disabled={saving}
            className="rounded-2xl bg-white px-8 py-3 font-black text-black uppercase tracking-widest transition-transform hover:scale-105 active:scale-95 disabled:opacity-50"
          >
            <div className="flex items-center gap-2">
              <Save className="h-4 w-4" />
              <span>{saving ? "Storing..." : "Sync Node"}</span>
            </div>
          </button>
        </div>
      </header>

      <AnimatePresence>
        {brandKit && (
          <motion.section 
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="glass-panel rounded-[3rem] p-10 relative overflow-hidden group border-primary/20 bg-primary/5"
          >
            <div className="absolute -top-24 -right-24 h-64 w-64 rounded-full bg-primary/10 blur-[100px] group-hover:bg-primary/20 transition-all duration-1000" />
            
            <h2 className="text-2xl font-black text-white uppercase italic tracking-tighter mb-8 flex items-center gap-3">
              <Sparkles className="h-6 w-6 text-primary" /> Generated Brand Strategy Node
            </h2>
            <div className="grid grid-cols-1 gap-8 md:grid-cols-2 relative z-10">
              <div className="space-y-3 p-6 rounded-2xl bg-white/[0.03] border border-white/[0.06]">
                <h3 className="text-mono-premium">Synthesized Narrative</h3>
                <p className="text-sm font-medium text-slate-300 leading-relaxed italic">"{brandKit.brand_narrative}"</p>
              </div>
              <div className="space-y-3 p-6 rounded-2xl bg-white/[0.03] border border-white/[0.06]">
                <h3 className="text-mono-premium">Tone Protocol</h3>
                <p className="text-lg font-black text-white uppercase tracking-tight">{brandKit.brand_voice}</p>
                <div className="flex flex-wrap gap-2 pt-2">
                  {brandKit.tone_guidelines?.slice(0, 3).map((t: string) => (
                    <span key={t} className="rounded-full bg-primary/10 border border-primary/20 px-3 py-1 text-[10px] font-black text-primary uppercase">{t}</span>
                  ))}
                </div>
              </div>
            </div>
          </motion.section>
        )}
      </AnimatePresence>

      <div className="grid grid-cols-1 gap-12 lg:grid-cols-3 items-start">
        {/* Visual & Core Side */}
        <div className="lg:col-span-1 space-y-12">
            <section className="glass-panel rounded-[3rem] p-10 space-y-8">
                <div className="flex items-center justify-between">
                    <h2 className="text-xl font-black text-white uppercase italic tracking-tighter">Visual Core</h2>
                    <button 
                        onClick={handleGenerateLogo}
                        disabled={generatingLogo || !formData.name}
                        className="text-mono-premium text-primary hover:text-white transition-colors disabled:opacity-30"
                    >
                        {generatingLogo ? "Rendering..." : "Generate Logo"}
                    </button>
                </div>
                <div className="flex flex-col items-center gap-8">
                    <div className="relative h-56 w-56 rounded-[3rem] border border-white/10 bg-white/[0.02] overflow-hidden shadow-2xl group cursor-pointer hover:border-primary/40 transition-all">
                        {formData.logo_url ? (
                            <img src={formData.logo_url} alt="Brand Logo" className="h-full w-full object-cover group-hover:scale-110 transition-transform duration-700" />
                        ) : (
                            <div className="flex h-full w-full items-center justify-center text-white/5">
                                <ImageIcon className="h-16 w-16" />
                            </div>
                        )}
                        {generatingLogo && (
                            <div className="absolute inset-0 flex items-center justify-center bg-black/40 backdrop-blur-md">
                                <div className="h-10 w-10 animate-spin rounded-full border-4 border-primary border-t-transparent shadow-[0_0_20px_rgba(139,92,246,0.5)]" />
                            </div>
                        )}
                    </div>
                    <div className="w-full space-y-2">
                        <label className="text-mono-premium block">Resource Pointer (Logo URL)</label>
                        <input
                            type="text"
                            value={formData.logo_url || ""}
                            onChange={(e) => setFormData({ ...formData, logo_url: e.target.value })}
                            className="w-full rounded-xl border border-white/[0.08] bg-white/[0.02] p-4 text-xs font-mono text-slate-400 outline-none focus:ring-2 focus:ring-primary/50"
                            placeholder="https://cdn.aimos.io/..."
                        />
                    </div>
                </div>
            </section>

            <section className="glass-panel rounded-[3rem] p-10 space-y-6">
                <h2 className="text-xl font-black text-white uppercase italic tracking-tighter">Pricing Node</h2>
                <div className="grid grid-cols-3 gap-2 p-1 bg-white/[0.04] rounded-2xl border border-white/[0.08]">
                    {["budget", "mid", "premium"].map((tier) => (
                        <button
                            key={tier}
                            onClick={() => setFormData({ ...formData, pricing_range: tier })}
                            className={`rounded-xl py-3 text-[10px] font-black uppercase tracking-widest transition-all ${
                                formData.pricing_range === tier
                                    ? "bg-primary text-white shadow-[0_0_15px_rgba(139,92,246,0.3)]"
                                    : "text-slate-500 hover:text-white"
                            }`}
                        >
                            {tier}
                        </button>
                    ))}
                </div>
            </section>
        </div>

        {/* Content & Targeting Side */}
        <div className="lg:col-span-2 space-y-12">
            <section className="glass-panel rounded-[3rem] p-10 space-y-8">
                <h2 className="text-xl font-black text-white uppercase italic tracking-tighter flex items-center gap-3">
                    <PenTool className="h-5 w-5 text-primary" /> Core DNA
                </h2>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                    <div className="space-y-4">
                        <label className="text-mono-premium block">Business Identifier</label>
                        <input
                            type="text"
                            value={formData.name}
                            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                            className="w-full rounded-2xl border border-white/[0.08] bg-white/[0.02] p-4 text-white outline-none focus:ring-2 focus:ring-primary/50"
                            placeholder="e.g. SOLARA LUXURY"
                        />
                    </div>
                    <div className="space-y-4">
                        <label className="text-mono-premium block">Industry Vertical</label>
                        <input
                            type="text"
                            value={formData.category}
                            onChange={(e) => setFormData({ ...formData, category: e.target.value })}
                            className="w-full rounded-2xl border border-white/[0.08] bg-white/[0.02] p-4 text-white outline-none focus:ring-2 focus:ring-primary/50"
                            placeholder="e.g. Sustainable Fashion"
                        />
                    </div>
                    <div className="md:col-span-2 space-y-4">
                        <label className="text-mono-premium block">Brand Narrative / Mission</label>
                        <textarea
                            value={formData.description}
                            onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                            rows={4}
                            className="w-full rounded-2xl border border-white/[0.08] bg-white/[0.02] p-4 text-white outline-none focus:ring-2 focus:ring-primary/50 leading-relaxed"
                            placeholder="A high-tech approach to classic heritage..."
                        />
                    </div>
                </div>
            </section>

            <section className="glass-panel rounded-[3rem] p-10 space-y-8">
                <h2 className="text-xl font-black text-white uppercase italic tracking-tighter flex items-center gap-3">
                    <Target className="h-5 w-5 text-emerald-400" /> Target Resonance
                </h2>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-8">
                    <div className="space-y-4">
                        <label className="text-mono-premium block">Age Demographics</label>
                        <input
                            type="text"
                            value={formData.target_audience?.age || ""}
                            onChange={(e) => setFormData({ ...formData, target_audience: { ...formData.target_audience, age: e.target.value }})}
                            className="w-full rounded-2xl border border-white/[0.08] bg-white/[0.02] p-4 text-white outline-none focus:ring-2 focus:ring-primary/50"
                            placeholder="e.g. 25-45 Gen Z"
                        />
                    </div>
                    <div className="space-y-4">
                        <label className="text-mono-premium block">Location Parameters</label>
                        <input
                            type="text"
                            value={formData.target_audience?.location || ""}
                            onChange={(e) => setFormData({ ...formData, target_audience: { ...formData.target_audience, location: e.target.value }})}
                            className="w-full rounded-2xl border border-white/[0.08] bg-white/[0.02] p-4 text-white outline-none focus:ring-2 focus:ring-primary/50"
                            placeholder="e.g. USA, UK Markets"
                        />
                    </div>
                    <div className="md:col-span-2 space-y-4">
                        <label className="text-mono-premium block">Core Resonance Points (Interests)</label>
                        <input
                            type="text"
                            value={formData.target_audience?.interests || ""}
                            onChange={(e) => setFormData({ ...formData, target_audience: { ...formData.target_audience, interests: e.target.value }})}
                            className="w-full rounded-2xl border border-white/[0.08] bg-white/[0.02] p-4 text-white outline-none focus:ring-2 focus:ring-primary/50"
                            placeholder="e.g. Luxury, Travel, Ethics"
                        />
                    </div>
                </div>
            </section>

            <section className="glass-panel rounded-[3rem] p-10 space-y-8">
                <h2 className="text-xl font-black text-white uppercase italic tracking-tighter flex items-center gap-3">
                    <Globe className="h-5 w-5 text-sky-400" /> Digital Reach
                </h2>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-8">
                    <div className="md:col-span-2 space-y-4">
                        <label className="text-mono-premium block">Nexus URL (Website)</label>
                        <input
                            type="url"
                            value={formData.website_url}
                            onChange={(e) => setFormData({ ...formData, website_url: e.target.value })}
                            className="w-full rounded-2xl border border-white/[0.08] bg-white/[0.02] p-4 text-white outline-none focus:ring-2 focus:ring-primary/50"
                            placeholder="https://aimos.io"
                        />
                    </div>
                    {["instagram", "facebook", "youtube"].map((platform) => (
                        <div key={platform} className="space-y-3">
                            <label className="text-mono-premium block capitalize">{platform} Handle</label>
                            <input
                                type="text"
                                value={formData.social_links?.[platform] || ""}
                                onChange={(e) => setFormData({ ...formData, social_links: { ...formData.social_links, [platform]: e.target.value }})}
                                className="w-full rounded-2xl border border-white/[0.08] bg-white/[0.02] p-4 text-white outline-none focus:ring-2 focus:ring-primary/50"
                                placeholder="@aimos_global"
                            />
                        </div>
                    ))}
                </div>
            </section>
        </div>
      </div>
    </motion.div>
  );
}
